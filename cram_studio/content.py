"""Read-only collection snapshots and pure question construction. No scheduler calls."""
from __future__ import annotations
import hashlib
import html
import json
import math
import random
import re
import unicodedata
from . import ordering
from html.parser import HTMLParser
from .field_render import (studylist_clean, studylist_cloze_parts, studylist_reveal_parts,
    studylist_is_io, studylist_is_basic, studylist_basic_fields, studylist_role,
    studylist_raw_shapes, studylist_image_size)

PROMPT_VERSION = 4

def safe_font_weight(style):
    """Keep explicit normal weights too: they can override an enclosing <b>."""
    chosen=None;chosen_important=False
    for declaration in style.split(';'):
        property,separator,value=declaration.partition(':')
        if not separator or property.strip().lower()!='font-weight':continue
        match=re.fullmatch(r'\s*(normal|bold|bolder|lighter|[1-9]00|1000)\s*(!\s*important)?\s*',value,re.I)
        if not match:continue
        important=bool(match[2])
        if chosen_important and not important:continue
        weight=match[1].lower();weight={'normal':'400','bold':'700'}.get(weight,weight)
        chosen=weight;chosen_important=important
    return 'font-weight:'+chosen+('!important' if chosen_important else '') if chosen is not None else ''

class SafeHTML(HTMLParser):
    tags = set('p br div span b strong i em u mark sub sup ul ol li blockquote h1 h2 h3 h4 table thead tbody tr td th img hr pre code ruby rt rp'.split())
    void = {'br','img','hr'}
    def __init__(self):
        super().__init__(convert_charrefs=True); self.out=[]
    def handle_starttag(self, tag, attrs):
        if tag not in self.tags: return
        safe=[]
        for k,v in attrs:
            if (tag=='ol' and k=='start' or tag=='li' and k=='value') and v and re.fullmatch(r'-?\d{1,6}',v):
                safe.append(f'{k}="{v}"')
            elif k in ('colspan','rowspan','alt','title') or (tag=='img' and k=='src'):
                v=v or ''
                if k=='src' and (re.match(r'(?i)\s*(?:[a-z]+:|//|/|\\)',v) or '..' in v.split('/')): continue
                safe.append(f'{k}="{html.escape(v,quote=True)}"')
            elif k=='data-blank' and v and v.isdigit():
                safe.append(f'data-blank="{v}"')
            elif k=='class' and v and re.fullmatch(r'ct-blank(?: active)?',v):
                safe.append(f'class="{v}"')
            elif k=='style' and v:
                weight=safe_font_weight(v)
                if weight:safe.append(f'style="{weight}"')
                if re.search(r'background(?:-color)?\s*:',v,re.I) and not re.search(r'background(?:-color)?\s*:\s*(?:transparent|none)',v,re.I): safe.append('class="ct-highlight"')
        self.out.append('<'+tag+(' '+' '.join(safe) if safe else '')+'>')
    def handle_endtag(self,tag):
        if tag in self.tags and tag not in self.void: self.out.append('</'+tag+'>')
    def handle_data(self,data): self.out.append(html.escape(data,quote=False))

def clean(value):
    parser=SafeHTML(); parser.feed(studylist_clean(value)); parser.close()
    return ''.join(parser.out)

def plain(value):
    # Add spacing at block boundaries before stripping markup.
    value=re.sub(r'(?i)</?(?:br|p|div|li|h\d|tr)\b[^>]*>', ' ', clean(value))
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', '',value))).strip()

class ChoiceText(HTMLParser):
    """Safe visible option text with block breaks and explicit list markers."""
    blocks={'p','div','blockquote','h1','h2','h3','h4','pre','tr'}
    def __init__(self):
        super().__init__(convert_charrefs=True);self.out=[];self.lists=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('ol','ul'):
            self.out.append('\n');self.lists.append([tag,int(attrs.get('start',1))-1])
        elif tag=='li':
            self.out.append('\n')
            if self.lists:
                current=self.lists[-1];current[1]=int(attrs.get('value',current[1]+1))
                self.out.append('  '*(len(self.lists)-1)+(str(current[1])+'. ' if current[0]=='ol' else '• '))
        elif tag=='br' or tag in self.blocks:self.out.append('\n')
        elif tag in ('td','th') and self.out and not self.out[-1].endswith('\n'):self.out.append('\t')
    def handle_endtag(self,tag):
        if tag in ('ol','ul'):
            if self.lists:self.lists.pop()
            self.out.append('\n')
        elif tag=='li' or tag in self.blocks:self.out.append('\n')
    def handle_data(self,data):self.out.append(data)

def choice_text(value):
    parser=ChoiceText();parser.feed(clean(value));parser.close()
    # Collapse horizontal paste spacing, retaining list nesting and explicit lines.
    lines=[]
    for line in ''.join(parser.out).replace('\r\n','\n').replace('\r','\n').split('\n'):
        indent=re.match(r' *',line)[0]
        text=re.sub(r'[^\S\n]+',' ',line).strip()
        if text:lines.append((indent if re.match(r'(?:\d+\.|•)\s',text) else '')+text)
    return '\n'.join(lines).strip()

def normalized(value):
    return re.sub(r'[^\w]+','',unicodedata.normalize('NFKC',plain(value)).casefold())

def cache_key(question, slot, model):
    payload=[PROMPT_VERSION,model,choice_text(question['clue']),slot.get('number',1),slot['answer'],
             [[s.get('number',1),s['answer']] for s in question.get('slots',[])]]
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False).encode()).hexdigest()

# A small, reviewed guard for the reported failure, not a general ontology.
# ISTQB Glossary 3.7 explicitly lists partition testing as a synonym of
# equivalence partitioning. Do not merge equivalence PARTITION (a data class)
# into this group; it is a different concept.
# https://www.ctqb.org/en/downloads/istqb.html?cid=33119&file=files/content/ctqb/downloads/istqb/Glossary-terms-version-3.7.pdf
_CHOICE_SYNONYMS = {'partitiontesting':'equivalencepartitioning'}

def choice_identity(value):
    key=normalized(value)
    return _CHOICE_SYNONYMS.get(key,key)

def contextual_choice_identity(value,context=''):
    """Narrow guards for reported ambiguities; not a universal thesaurus."""
    key=choice_identity(value);stem=plain(context).casefold()
    if re.search(r'\b(?:ipv4|ip addresses?)\b',stem) and key in {
        'depletion','scarcity','shortage','exhaustion','addressdepletion',
        'addressscarcity','addressshortage','addressexhaustion',
        'ipv4addressdepletion','ipv4addressscarcity','ipv4addressshortage','ipv4addressexhaustion'}:
        return 'ipv4-address-supply-ambiguity'
    if re.search(r'\b(?:mtu|maximum transmission unit)\b',stem) and key in {
        'mtu','mtusize','maximumtransmissionunit','maximumtransmissionunitsize'}:
        return 'maximum-transmission-unit'
    if re.search(r'\bfair use\b|\bsection\s*107\b',stem) and key in {
        'copyrightlawof1976','copyrightactof1976','uscopyrightact','uscopyrightlaw',
        'copyrightact1976','copyrightlaw1976','uscopyrightactof1976','uscopyrightlawof1976'}:
        return 'copyright-act-1976-in-fair-use-stem'
    return key

class ChoiceValidationError(ValueError):
    """A fixed, safe-to-display validation reason; never raw model content."""
    pass

def valid_distractors(answer, wrong, aliases=(), context=''):
    if not isinstance(wrong,list) or len(wrong)!=3: raise ChoiceValidationError('Exactly three wrong choices are required.')
    if not isinstance(aliases,(list,tuple)) or len(aliases)>12: raise ChoiceValidationError('Invalid answer aliases.')
    identity=lambda value:contextual_choice_identity(value,context)
    values=[];answer_key=identity(answer);alias_keys=set();seen=set()
    for alias in aliases:
        if not isinstance(alias,str) or not normalized(alias) or len(alias)>600: raise ChoiceValidationError('Invalid answer alias.')
        alias_keys.add(identity(alias))
    for item in wrong:
        if not isinstance(item,str): raise ChoiceValidationError('Each choice must be text.')
        item=choice_text(item).strip(); key=identity(item)
        if not key:raise ChoiceValidationError('A wrong choice is empty.')
        if len(item)>600:raise ChoiceValidationError('A wrong choice exceeds the 600-character limit.')
        if answer_key=='maximum-transmission-unit' and key in {'maximumtransferunit','maximumtransfersize'}:
            raise ChoiceValidationError('A choice changes the MTU name instead of identifying a distinct parameter.')
        if key==answer_key:raise ChoiceValidationError('A wrong choice repeats the correct answer.')
        if key in alias_keys:raise ChoiceValidationError('A wrong choice is an alias of the correct answer.')
        if key in seen:raise ChoiceValidationError('Two wrong choices repeat the same option.')
        seen.add(key); values.append(item)
    return values

def cloze_question(value, active):
    slots=[]
    def walk(parts):
        out=[]
        for p in parts:
            if isinstance(p,str): out.append(p)
            elif p[0] in active:
                answer=clean(studylist_reveal_parts(p[1]))
                if not plain(answer) and not re.search(r'<img\b',answer,re.I): out.append(walk(p[1])); continue
                n=len(slots)+1
                slots.append({'key':str(n),'ordinal':p[0],'answer':choice_text(answer),'answer_html':answer,'number':n})
                out.append(f'<span class="ct-blank" data-blank="{n-1}">({n}) _____________</span>')
            else: out.append(walk(p[1]))
        return ''.join(out)
    return clean(walk(studylist_cloze_parts(value))),slots

def io_question(fields, model, ordinal, native=None):
    source=studylist_role(fields,model,0,('Occlusion','Occlusions'),0)
    image=clean(studylist_role(fields,model,1,('Image','Picture'),1))
    image_match=re.search(r'<img\b[^>]*>',image,re.I)
    image=image_match[0] if image_match else ''
    header=clean(studylist_role(fields,model,2,('Header','Title','Label')))
    extra=clean(studylist_role(fields,model,3,('Back Extra','Answer','Answer Labels','Extra 1')))
    shapes=studylist_raw_shapes(source); width,height=1000,1000
    if native is not None:
        width,height=studylist_image_size(native.image_data)
        if not shapes and all(hasattr(g,'ordinal') for g in native.occlusions):
            shapes=[{'kind':s.shape,'ordinal':g.ordinal,'props':{p.name:p.value for p in s.properties}}
                    for g in native.occlusions for s in g.shapes]
    def num(p,k,d=0):
        try:
            n=float(p.get(k,d)); return n if math.isfinite(n) else d
        except (ValueError,TypeError): return d
    masks=[]; active_count=0
    for s in shapes:
        p=s['props']; kind=s['kind']; active=s['ordinal']==ordinal
        if kind=='text':
            if active: extra+='<p>'+html.escape(p.get('text',''))+'</p>'
            continue
        if not active and s['ordinal']!=0 and p.get('oi')!='1': continue
        x,y=num(p,'left')*width,num(p,'top')*height
        angle=num(p,'angle')*360/10000
        attrs=f' class="mask {"target" if active else "inactive"}"'
        if angle: attrs+=f' transform="rotate({angle:g} {x:g} {y:g})"'
        if kind=='rect':
            shape=f'<rect x="{x:g}" y="{y:g}" width="{num(p,"width")*width:g}" height="{num(p,"height")*height:g}"{attrs}/>'
        elif kind=='ellipse':
            rx,ry=num(p,'rx')*width,num(p,'ry')*height
            shape=f'<ellipse cx="{x+rx:g}" cy="{y+ry:g}" rx="{rx:g}" ry="{ry:g}"{attrs}/>'
        elif kind=='polygon':
            points=[]
            for pair in p.get('points','').split():
                try:
                    a,b=map(float,pair.split(','))
                    if math.isfinite(a) and math.isfinite(b): points.append((a,b))
                except ValueError: pass
            if not points: continue
            left,top=min(a for a,b in points),min(b for a,b in points)
            points=' '.join(f'{x+(a-left)*width:g},{y+(b-top)*height:g}' for a,b in points)
            shape=f'<polygon points="{points}"{attrs}/>'
        else: continue
        masks.append(shape); active_count+=int(active)
    picture=(f'<div class="io-image">{image}<svg viewBox="0 0 {max(1,width)} {max(1,height)}" preserveAspectRatio="none" aria-hidden="true">'+''.join(masks)+'</svg></div>')
    # Unsupported legacy formats are skipped instead of displaying an unmasked answer.
    if not re.search(r'<img\b',image) or not active_count: return None
    return {'kind':'io','clue':header,'picture':picture,'extra':extra,'slots':[], 'mask_count':active_count}

def catalog(col):
    try:deck_rows=col.decks.all_names_and_ids(include_filtered=True)
    except TypeError:deck_rows=col.decks.all_names_and_ids()
    filtered={str(deck['id']) for deck in col.decks.all() if deck.get('dyn')} if callable(getattr(col.decks,'all',None)) else set()
    decks=[{'id':str(d.id),'name':d.name,'filtered':str(d.id) in filtered} for d in deck_rows]
    names={d['id']:d['name'] for d in decks};by_name={d['name']:d['id'] for d in decks}
    direct={};totals={};borrowed={};groups=[]
    for did,odid,count in col.db.all('select did,odid,count(*) from cards group by did,odid'):
        did=str(did);home=str(odid or did);members={did,home};ancestors=set()
        groups.append({'did':did,'home':home,'count':count})
        for member in members:
            direct[member]=direct.get(member,0)+count
            parts=names.get(member,'').split('::')
            ancestors.update(by_name[prefix] for i in range(1,len(parts)+1) if (prefix:='::'.join(parts[:i])) in by_name)
        for ancestor in ancestors:totals[ancestor]=totals.get(ancestor,0)+count
        if home!=did:borrowed[home]=borrowed.get(home,0)+count
    for d in decks:
        d.update(count=direct.get(d['id'],0),total_count=totals.get(d['id'],0),borrowed_count=borrowed.get(d['id'],0))
    return {'decks':sorted(decks,key=lambda d:tuple(p.casefold() for p in d['name'].split('::'))),'scope_groups':groups,'models':list(col.models.all()),'current':str(col.decks.get_current_id()),'retrievability_order':retrievability_column(col) is not None,'sort_columns':ordering.menu(col)}

def retrievability_column(col):
    """Discover Anki's native column rather than approximating FSRS recall."""
    try:
        return next((c for c in col.all_browser_columns() if 'retrievability' in c.key.casefold() and 'relative' not in c.key.casefold() and column_direction(c) is not None),None)
    except (AttributeError,TypeError): return None

def column_direction(column):
    # Read the protobuf enum name: do not assume numeric enum values across Anki releases.
    try: name=column.DESCRIPTOR.fields_by_name['sorting_cards'].enum_type.values_by_number[column.sorting_cards].name
    except (AttributeError,KeyError): return None
    if 'NOTES' in name: return None
    if name.endswith('DESCENDING'): return False
    if name.endswith('ASCENDING'): return True
    return None

def native_retrievability_order(col,query,descending=False):
    column=retrievability_column(col)
    if column is None: raise ValueError('This Anki version does not expose retrievability sorting. Choose creation date or update Anki.')
    ascending=column_direction(column)
    return list(col.find_cards(query,order=column,reverse=(ascending==descending)))

def selected_decks(decks, ids, children=True):
    names={d['name'] for d in decks if d['id'] in set(map(str,ids))}
    return [int(d['id']) for d in decks if d['name'] in names or (children and any(d['name'].startswith(n+'::') for n in names))]

def search_query(config):
    """Preserve native Anki search syntax; group clauses before AND combination."""
    filters=config.get('filters',{})
    if not isinstance(filters,dict): raise ValueError('Invalid filters.')
    raw=str(filters.get('search','')).strip()
    if len(raw)>10000: raise ValueError('The search is too long.')
    terms=[raw] if raw else []
    def quoted(prefix,value):
        return '"'+prefix+value.replace('\\','\\\\').replace('"','\\"')+'"'
    for field,prefix in [('tag','tag:'),('note_type','note:')]:
        value=str(filters.get(field,'')).strip()
        if value: terms.append(quoted(prefix,value))
    flag=str(filters.get('flag',''))
    if flag:
        if flag not in tuple(str(i) for i in range(8))+('any',): raise ValueError('Choose a valid card flag.')
        terms.append('-flag:0' if flag=='any' else 'flag:'+flag)
    return ' '.join('('+term+')' for term in terms)

def count_matches(col,config):
    cat=catalog(col);dids=selected_decks(cat['decks'],config.get('decks',[]),config.get('children',True))
    query=search_query(config)
    allowed=set(col.find_cards(query)) if query else None
    seen=set()
    for offset in range(0,len(dids),500):
        batch=dids[offset:offset+500]
        placeholders=','.join('?' for _ in batch)
        ids=col.db.all('select id from cards where did in ('+placeholders+') or odid in ('+placeholders+')',*batch,*batch)
        seen.update(cid for (cid,) in ids)
    return {'count':len(seen if allowed is None else seen&allowed),'total':len(seen),'query':query}

def scoped_rows(col,dids):
    """Read selected home/current deck membership once, including borrowed cards."""
    rows={};selected=set(dids)
    for offset in range(0,len(dids),500):
        batch=dids[offset:offset+500];placeholders=','.join('?' for _ in batch)
        for cid,nid,did,ordinal,mid,fields,odid in col.db.all(
                'select c.id,c.nid,c.did,c.ord,n.mid,n.flds,c.odid from cards c join notes n on n.id=c.nid where c.did in ('+placeholders+') or c.odid in ('+placeholders+') order by c.nid,c.ord,c.id',*batch,*batch):
            rows[cid]=(cid,nid,odid if odid in selected else did,ordinal,mid,fields)
    return list(rows.values())

def snapshot(col, config, mappings):
    cat=catalog(col); dids=selected_decks(cat['decks'],config.get('decks',[]),config.get('children',True))
    if not dids: return {'questions':[],'available':0,'skipped':0},0
    rows=scoped_rows(col,dids)
    query=search_query(config)
    if query:
        matches=set(col.find_cards(query))
        rows=[row for row in rows if row[0] in matches]
    models={int(m['id']):m for m in cat['models']}; names={int(d['id']):d['name'] for d in cat['decks']}
    natives={}
    # Read-only native IO metadata supplies the original image aspect ratio.
    for cid,nid,did,ord_,mid,flds in rows:
        if nid not in natives and studylist_is_io(flds.split('\x1f'),models[mid]):
            try:
                response=col.get_image_occlusion_note(nid)
                natives[nid]=response.note if response.HasField('note') else None
            except Exception: natives[nid]=None
    config=dict(config)
    order=str(config.get('order',''))
    if order.startswith('anki:') or order in ('due_random','due_deck','deck_due'):
        config['_card_rank']=ordering.card_rank(col,query,order,bool(config.get('order_desc',False)),rows,names)
    elif order.startswith('retrievability_'):
        ordered=native_retrievability_order(col,query,config['order'].endswith('_desc'))
        config['_card_rank']={str(cid):i for i,cid in enumerate(ordered)}
    return compile_questions(rows,models,names,config,mappings,natives),len(rows)

def compile_questions(rows,models,names,config,mappings,natives=None):
    mode=config.get('mode','flash'); grouped={}
    for row in sorted(rows,key=lambda r:(r[1],r[3],r[0])): grouped.setdefault(row[1],[]).append(row)
    questions=[]; skipped=0
    for nid, cards in grouped.items():
        cid,_,did,ord_,mid,flds=cards[0]; fields=flds.split('\x1f'); model=models[mid]
        if studylist_is_io(fields,model):
            for card in cards:
                q=io_question(fields,model,card[3]+1,(natives or {}).get(nid))
                if q: questions.append(dict(q,id=f'io:{card[0]}',nid=str(nid),cid=str(card[0]),deck=names[card[2]],mode='flash'))
                else: skipped+=1
            continue
        mapping=mappings.get(str(mid),{}); names_= [f['name'] for f in model['flds']]
        if model.get('type')==1:
            text=fields[names_.index(mapping['text'])] if mapping.get('text') in names_ else next((f for f in fields if re.search(r'\{\{c\d+::',f,re.I)),'')
            if not re.search(r'\{\{c\d+::',text,re.I): text=next((f for f in fields if re.search(r'\{\{c\d+::',f,re.I)),text)
            # A cN card always tests just that number, in every study mode.
            card_groups=[[c] for c in cards]
            for group in card_groups:
                active={c[3]+1 for c in group}; clue,slots=cloze_question(text,active)
                if not slots: skipped+=1; continue
                questions.append({'kind':'cloze','id':f'cloze:{nid}:'+','.join(str(n) for n in sorted(active)), 'nid':str(nid),'cid':str(group[0][0]),'deck':names[group[0][2]], 'clue':clue,'slots':slots,'mode':mode})
        elif len(fields)>=2:
            if studylist_is_basic(model):
                fi,bi=studylist_basic_fields(model)
                choice=mapping.get('answer','auto')
                ai=names_.index(choice) if choice in (names_[fi],names_[bi]) else (fi if len(plain(fields[fi]))<len(plain(fields[bi])) else bi)
                qi=bi if ai==fi else fi
            else:
                # Custom types use explicit mapping, otherwise prefer Answer/Term and Question/Definition.
                answer=mapping.get('answer')
                clue=mapping.get('clue')
                ai=names_.index(answer) if answer in names_ else next((i for i,n in enumerate(names_) if n.casefold() in ('answer','term','back')),1)
                qi=names_.index(clue) if clue in names_ else next((i for i,n in enumerate(names_) if n.casefold() in ('question','definition','front')),0)
            answer,clue=clean(fields[ai]),clean(fields[qi])
            if not plain(answer) and '<img' not in answer: skipped+=1; continue
            if not plain(clue) and '<img' not in clue: skipped+=1; continue
            questions.append({'kind':'basic','id':f'note:{nid}','nid':str(nid),'cid':str(cid),'deck':names[did],'clue':clue,'slots':[{'key':'1','number':1,'answer':choice_text(answer),'answer_html':answer}], 'mode':mode})
        else: skipped+=1
    card_ord={str(row[0]):row[3] for row in rows}
    for q in questions:q['ordinal']=card_ord.get(q['cid'],0)
    order=config.get('order','shuffle' if config.get('shuffle',True) else 'created_asc')
    if order=='shuffle': random.SystemRandom().shuffle(questions)
    elif order in ('random_notes','card_type','card_type_random','deck_random_notes'):ordering.arrange(questions,order)
    elif order in ('created_asc','created_desc'):
        # Note ID is Anki's note creation timestamp; c1 precedes c2 on ties.
        direction=-1 if order=='created_desc' else 1
        questions.sort(key=lambda q:(direction*int(q['nid']),int(q['slots'][0].get('ordinal',1)) if q['slots'] else int(q['cid']),int(q['cid'])))
    elif order in ('retrievability_asc','retrievability_desc','due_random','due_deck','deck_due') or str(order).startswith('anki:'):
        rank=config.get('_card_rank')
        if rank is None: raise ValueError('Retrievability or native card order must be supplied by Anki.')
        questions.sort(key=lambda q:rank.get(q['cid'],len(rank)))
    else: raise ValueError('Choose a valid question order.')
    for i,q in enumerate(questions):
        q['mode']='flash' if q['kind']=='io' or (mode=='mixed' and i%2==0) else ('write' if mode=='write' else 'exam' if mode in ('mixed','exam') else 'flash')
        # Keep the original visual answer; never send it as an empty text job.
        # This is per question, so the following text card keeps the chosen mode.
        if q['kind']!='io' and any(re.search(r'<img\b',s['answer_html'],re.I) for s in q['slots']):
            q['mode']='flash';q['image_answer']=True
            q['fallback']='Image answer: flashcard'
            continue
        if q['kind']!='io' and (not plain(q['clue']) or any(not s['answer'] or len(s['answer'])>(20000 if mode=='write' else 600) or '<img' in s['answer_html'] for s in q['slots'])):
            q['mode']='flash'; q['fallback']='Image or long answer: flashcard'
    limit=max(0,min(10000,int(config.get('limit',30))))
    selected=questions[:limit] if limit else questions
    return {'questions':selected,'available':len(questions),'skipped':skipped}

def question_for_blank(question,slot):
    """AI-only stem: one target marker, other slots filled with correct context."""
    slots=question['slots'];target=next((i for i,item in enumerate(slots) if item is slot),0)
    def replace(match):
        index=int(match[1])
        if index>=len(slots):return match[0]
        return '[TARGET BLANK '+str(slot['number'])+']' if index==target else html.escape(slots[index]['answer'],quote=False)
    resolved=re.sub(r'<span\b[^>]*\bdata-blank=["\'](\d+)["\'][^>]*>.*?</span>',replace,question['clue'],flags=re.I|re.S)
    return choice_text(resolved)[:8000]

def prepare_choices(questions,store,model):
    missing={}; ready=0
    for q in questions:
        if q['mode']!='exam': continue
        for slot in q['slots']:
            key=cache_key(q,slot,model); slot['cache_key']=key
            wrong=store.get(key)
            try: wrong=valid_distractors(slot['answer'],wrong,context=question_for_blank(q,slot))
            except ValueError:
                missing.setdefault(key,{'id':key,'clue':choice_text(q['clue'])[:8000],'question_for_this_blank':question_for_blank(q,slot),'answer':slot['answer'],'blank':slot['number'],
                    'other_blanks':[{'blank':s['number'],'answer':s['answer']} for s in q['slots'] if s is not slot]}); continue
            slot['wrong']=wrong; ready+=1
    return list(missing.values()),ready

def attach_choices(questions,cache,model,partial=False,force=False):
    changed=[]
    for q in questions:
        if q['mode']!='exam': continue
        was_ready=q.get('ready',False)
        ready=True
        for slot in q['slots']:
            if slot.get('choices') and not force: continue
            key=cache_key(q,slot,model)
            try: slot['wrong']=valid_distractors(slot['answer'],cache.get(key),context=question_for_blank(q,slot))
            except ValueError:
                if not partial: raise
                ready=False; continue
            choices=[{'text':slot['answer'],'correct':True}]+[{'text':w,'correct':False} for w in slot['wrong']]
            random.SystemRandom().shuffle(choices)
            slot['choices']=[v['text'] for v in choices]; slot['correct']=next(i for i,v in enumerate(choices) if v['correct'])
        q['ready']=ready
        if ready and not was_ready: changed.append(q)
    return changed

def grade(question,picks):
    if question['mode']=='write':
        from .writing import grade as writing_grade
        return writing_grade(question,picks)
    if question['mode']!='exam':
        value=picks.get('known')
        if not isinstance(value,bool): raise ValueError('Reveal the answer, then mark your recall.')
        return {'earned':int(value),'total':1,'correct':[value]}
    if question.get('ready') is False: raise ValueError('Choices are still being prepared for this question.')
    if picks.get('unknown') is True:
        return {'earned':0,'total':len(question['slots']),'correct':[False]*len(question['slots'])}
    if not isinstance(picks.get('choices'),list) or len(picks['choices'])!=len(question['slots']): raise ValueError('Answer every blank before submitting.')
    correct=[]
    for slot,index in zip(question['slots'],picks['choices']):
        if type(index) is not int or index not in range(4): raise ValueError('Select one of the four choices.')
        correct.append(index==slot['correct'])
    return {'earned':sum(correct),'total':len(correct),'correct':correct}
