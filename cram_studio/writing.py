"""Source-grounded Writing plans and exact item checking. No collection writes."""
from __future__ import annotations
import hashlib
import html
import json
import re
import unicodedata
from functools import lru_cache
from html.parser import HTMLParser
from .content import clean,choice_text

MAX_TEXT=20000
MAX_ITEMS=100
BLOCKS={'p','div','li','br','h1','h2','h3','h4','tr','blockquote'}

class Source(HTMLParser):
    """Map visible text to safe HTML tokens; keep list/heading/inline markup."""
    def __init__(self,value):
        super().__init__(convert_charrefs=True)
        self.tokens=[];self.text='';self.lists=[];self.stack=[]
        self.feed(clean(value));self.close()
    def newline(self):
        if self.text and not self.text.endswith('\n'):
            self.tokens.append(('gap','\n',len(self.text)));self.text+='\n'
    def handle_starttag(self,tag,attrs):
        if tag in BLOCKS:self.newline()
        self.tokens.append(('tag',self.get_starttag_text(),len(self.text)))
        if tag=='li':self.stack.append(len(self.text))
    def handle_endtag(self,tag):
        if tag=='li' and self.stack:self.lists.append([self.stack.pop(),len(self.text)])
        self.tokens.append(('tag','</'+tag+'>',len(self.text)))
        if tag in BLOCKS:self.newline()
    def handle_data(self,text):
        self.tokens.append(('text',text,len(self.text)));self.text+=text

def trim_span(text,start,end):
    while start<end and text[start].isspace():start+=1
    while end>start and text[end-1].isspace():end-=1
    return start,end

def full_span(text):
    a,b=trim_span(text,0,len(text))
    # Final sentence punctuation is shown, not something the learner must type.
    while b>a and text[b-1] in '.!?。':b-=1
    return trim_span(text,a,b)

def source(question):
    return Source(question['slots'][0].get('answer_html') or html.escape(question['slots'][0]['answer']))

def plan_key(question):
    payload=[('cloze-group-2' if question.get('_cloze_group') else 2),question['clue'],question['slots'][0].get('answer_html'),question['slots'][0]['answer']]
    return 'writing:'+hashlib.sha256(json.dumps(payload,ensure_ascii=False).encode()).hexdigest()

def _layout(value,connectors=()):
    """Only presentation separators/labels, never unknown content or negation."""
    value=unicodedata.normalize('NFKC',value).casefold()
    value=re.sub(r'\s+',' ',value)
    for phrase in sorted(connectors,key=len,reverse=True):
        key=re.sub(r'\s+',' ',unicodedata.normalize('NFKC',phrase).casefold()).strip()
        if key:value=re.sub(r'(?<!\w)'+re.escape(key)+r'(?!\w)',' ',value)
    value=re.sub(r'(?m)^\s*[-*•]\s+', ' ',value)
    value=re.sub(r'\(?\d+[.)]\s*', ' ',value)
    value=re.sub(r'\b(?:and|or|answer(?:s)?|item(?:s)?|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b',' ',value)
    return not re.search(r'[\w+%=<>]',value)

def validate_spans(text,raw):
    if not isinstance(raw,dict) or raw.get('kind') not in ('single','list'):raise ValueError('Invalid answer grouping.')
    spans=raw.get('spans')
    if raw['kind']=='single':return [list(full_span(text))]
    connectors=raw.get('connectors',[])
    if (not isinstance(connectors,list) or len(connectors)>MAX_ITEMS+1 or
            any(not isinstance(v,str) or not v.strip() or len(v)>1000 or v not in text or re.search(r'\d',v) for v in connectors)):
        raise ValueError('Invalid source connector.')
    if not isinstance(spans,list) or not 2<=len(spans)<=MAX_ITEMS:raise ValueError('Invalid enumeration size.')
    out=[];end=0
    for pair in spans:
        if not isinstance(pair,list) or len(pair)!=2 or any(type(n) is not int for n in pair):raise ValueError('Invalid source range.')
        a,b=pair
        if not 0<=a<b<=len(text) or a<end:raise ValueError('Overlapping or out-of-source answers.')
        a,b=trim_span(text,a,b)
        if a==b or not any(c.isalnum() for c in text[a:b]):raise ValueError('Empty answer item.')
        if a and text[a-1].isalnum() and text[a].isalnum() or b<len(text) and text[b-1].isalnum() and text[b].isalnum():raise ValueError('An answer cannot be cut inside a word.')
        if out and not _layout(text[end:a],connectors):raise ValueError('Answer grouping dropped content between items.')
        out.append([a,b]);end=b
    prefix=text[:out[0][0]];suffix=text[end:]
    if prefix.strip() and not _layout(prefix,connectors) and not re.search(r'(?:\b(?:are|include|includes|including|namely|of|following)|:)\s*$',prefix,re.I):raise ValueError('Unrecognized introduction.')
    if not _layout(suffix,connectors):raise ValueError('Answer grouping dropped a trailing item.')
    return out

def source_item_range(text,item,cursor=0):
    """Align harmless model case/spacing changes to original source positions."""
    if not isinstance(item,str) or not item.strip():raise ValueError('Empty source item.')
    item=item.strip()
    # Whitespace/case tolerance must never turn an item into a synonym, a
    # plural variant or a changed number. Display always uses the source span.
    pattern=r'\s+'.join(re.escape(part) for part in item.split())
    for match in re.finditer(pattern,text[cursor:],re.I):
        a,b=cursor+match.start(),cursor+match.end()
        if a and text[a-1].isalnum() and text[a].isalnum():continue
        if b<len(text) and text[b-1].isalnum() and text[b].isalnum():continue
        return [a,b]
    raise ValueError('The grouped item does not occur in the source.')

def grouping_from_items(text,entry):
    """Shared provider decoder; retain source wording and validate full coverage."""
    if entry.get('kind') not in ('single','list'):raise ValueError('Invalid grouping kind.')
    if entry['kind']=='single':return {'kind':'single','spans':[],'connectors':[]}
    items=entry.get('items');connectors=entry.get('connectors',[])
    if not isinstance(items,list) or not 2<=len(items)<=MAX_ITEMS:raise ValueError('Invalid item list.')
    if not isinstance(connectors,list) or len(connectors)>MAX_ITEMS+1:raise ValueError('Invalid connectors.')
    spans=[];cursor=0;kept=[]
    for item in items:
        pair=source_item_range(text,item,cursor);spans.append(pair);cursor=pair[1]
    for phrase in connectors:
        if not isinstance(phrase,str) or len(phrase)>1000:raise ValueError('Invalid connector.')
        # Empty/whitespace fields and punctuation-only gaps contain no words
        # to preserve. Numeric and symbolic details still go through validation.
        if not phrase.strip() or not re.search(r'[\w+%=<>]',phrase):continue
        a,b=source_item_range(text,phrase);kept.append(text[a:b])
    raw={'kind':'list','spans':spans,'connectors':list(dict.fromkeys(kept))}
    validate_spans(text,raw)
    # Connectors may describe only gaps, never overlap/hide an answer item.
    for phrase in raw['connectors']:
        if not any(phrase in text[a:b] for a,b in zip([0]+[p[1] for p in spans],[p[0] for p in spans]+[len(text)])):
            raise ValueError('An answer item is not a connector.')
    return raw

def counted_simple_list(question,text):
    """Offline fast path for explicit counts plus unambiguous one-word labels.

    Free-form prose, dates, compounds and unfamiliar connectors stay with the
    shared semantic grouping path; no subject-specific answer dictionary.
    """
    if question.get('_cloze_group') and len(re.findall(r'data-blank=',question['clue']))!=1:return None
    numbers={name:i for i,name in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty'.split())}
    count_words='|'.join(numbers)
    clue=choice_text(question['clue'])
    counts={numbers.get(m[1].casefold(),int(m[1]) if m[1].isdigit() else 0)
            for m in re.finditer(r'\b('+count_words+r'|\d{1,3})\s+(?:[^\W\d_]+\s+){0,4}[^\W\d_]+s\b',clue,re.I)}
    if len(counts)!=1:return None
    count=next(iter(counts))
    if not 2<=count<=MAX_ITEMS or not re.search(r'[,;]|\band\b',text,re.I):return None
    a,b=full_span(text);parts=[];cursor=a
    for match in re.finditer(r'[,;]',text[a:b]):
        end=a+match.start();parts.append(list(trim_span(text,cursor,end)));cursor=a+match.end()
    parts.append(list(trim_span(text,cursor,b)))
    if parts:
        start,end=parts[-1];tail=text[start:end]
        join=re.search(r'\band\s+',tail,re.I)
        if join:
            before=list(trim_span(text,start,start+join.start()))
            after=list(trim_span(text,start+join.end(),end))
            parts=parts[:-1]+([before] if before[0]<before[1] else [])+[after]
    if len(parts)!=count or any(not re.fullmatch(r'[^\W\d_]+(?:[-‐‑][^\W\d_]+)*',text[a:b]) for a,b in parts):return None
    raw={'kind':'list','spans':parts,'connectors':[]}
    try:validate_spans(text,raw)
    except ValueError:return None
    return raw

def cloze_sources(question):
    return [{'kind':'basic','clue':question['clue'],'slots':[slot],'_cloze_group':True} for slot in question['slots']]

def cloze_plan(question,plans):
    items=[];templates={};groups=[];connectors=[]
    if sum(len(plan['items']) for plan in plans)>MAX_ITEMS:
        plans=[build_plan(sub) for sub in cloze_sources(question)]
    for index,plan in enumerate(plans):
        offset=len(items)
        templates[index]=re.sub(r'data-write-item="(\d+)"',lambda m:'data-write-item="'+str(offset+int(m[1]))+'"',plan['template'])
        members=[]
        for member,item in enumerate(plan['items']):
            members.append(len(items));items.append(dict(item,cloze_slot=index,cloze_member=member))
        groups.append({'items':members,'original':plan.get('original','')})
        connectors.extend(plan.get('connectors',[]))
    template=re.sub(r'<span\b[^>]*data-blank=["\'](\d+)["\'][^>]*>.*?</span>',lambda m:templates[int(m[1])],question['clue'],flags=re.S)
    ordered=bool(re.search(r'\b(?:in order|correct order|sequence|sequential|chronological)\b',choice_text(question['clue']),re.I))
    return {'version':1,'template':template,'items':items,'ordered':ordered,'kind':'cloze','source':'cloze','groups':groups,'connectors':list(dict.fromkeys(connectors))}

def build_plan(question,raw=None):
    ordered=bool(re.search(r'\b(?:in order|correct order|sequence|sequential|chronological)\b',choice_text(question['clue']),re.I))
    if question['kind']=='cloze':
        return cloze_plan(question,[build_plan(sub) for sub in cloze_sources(question)])
    src=source(question)
    if len(src.text)>MAX_TEXT:raise ValueError('This answer is too long for Writing mode.')
    spans=validate_spans(src.text,raw or {'kind':'single'})
    items=[{'answer':src.text[a:b],'parts':[]} for a,b in spans]
    output=[]
    for kind,value,start in src.tokens:
        if kind=='tag':output.append(value);continue
        if kind=='gap':continue
        cursor=0;end=start+len(value)
        for i,(a,b) in enumerate(spans):
            lo,hi=max(start,a),min(end,b)
            if lo>=hi:continue
            output.append(html.escape(value[cursor:lo-start],quote=False))
            piece=len(items[i]['parts']);items[i]['parts'].append(value[lo-start:hi-start])
            if piece==0:output.append(f'<span class="ct-blank cram-blank-empty" data-write-item="{i}" data-write-piece="0">\u00a0</span>')
            else:output.append(f'<span data-write-item="{i}" data-write-piece="{piece}" hidden></span>')
            cursor=hi-start
        output.append(html.escape(value[cursor:],quote=False))
    return {'version':1,'template':''.join(output),'items':items,'ordered':ordered,'kind':'list' if len(items)>1 else 'single','source':'automatic' if raw else 'full','original':src.text,'connectors':list(raw.get('connectors',[])) if raw else []}

def automatic(question):
    if question['kind']=='cloze':
        plans=[automatic(sub) for sub in cloze_sources(question)]
        return cloze_plan(question,plans) if all(plans) else None
    src=source(question);text=src.text
    if not text.strip():raise ValueError('The answer has no text to type.')
    # A binary answer followed by its explanation is one response, not a list.
    if re.match(r'^\s*(?:yes|no|true|false)\b',text,re.I):return build_plan(question)
    spans=src.lists
    if not spans:
        lines=list(re.finditer(r'(?m)^\s*(?:\d+[.)]|[-*•])\s+([^\n]+)',text))
        if len(lines)>=2:spans=[[m.start(1),m.end(1)] for m in lines]
    if len(spans)>=2:
        # Explicit list structure already determines complete items offline.
        spans=[list(trim_span(text,*p)) for p in spans]
        try:return build_plan(question,{'kind':'list','spans':spans})
        except ValueError:pass
    counted=counted_simple_list(question,text)
    if counted:return build_plan(question,counted)
    if not re.search(r'[,;\n]|\band\b|\bor\b',text,re.I):return build_plan(question)
    return None

def attach(questions,cache,whole=False,ignore_extra=None):
    jobs=[];changed=[];ready=0;seen=set()
    for q in questions:
        if q['mode']!='write':continue
        was=q.get('ready',False)
        parts=cloze_sources(q) if q['kind']=='cloze' else [q];plans=[]
        for sub in parts:
            plan=automatic(sub)
            if plan is None:
                key=plan_key(sub);raw=cache.get(key)
                try:plan=build_plan(sub,raw) if raw else None
                except (ValueError,TypeError,KeyError):plan=None
                if plan is None and whole:plan=build_plan(sub)
                if plan is None and key not in seen:
                    jobs.append({'id':key,'question':choice_text(q['clue'])[:8000],'text':source(sub).text});seen.add(key)
            plans.append(plan)
        plan=(cloze_plan(q,plans) if q['kind']=='cloze' else plans[0]) if all(plans) else None
        if plan:
            plan['ignore_extra']=bool(ignore_extra if ignore_extra is not None else q.get('writing',{}).get('ignore_extra',False))
            q['writing']=plan;q['ready']=True;ready+=1
            if not was:changed.append(q)
        else:q['ready']=False
    return jobs,ready,changed

def answer_key(value):
    """Presentation tolerance only; displayed/source text is never rewritten."""
    key=unicodedata.normalize('NFKC',value).casefold().replace('ñ','n')
    key=re.sub(r'(?<=[^\W\d_])[-‐‑](?=[^\W\d_])',' ',key)
    key=re.sub(r'\s+',' ',key).strip()
    pairs={'"':'"',"'":"'",'“':'”','‘':'’','«':'»','‹':'›'}
    while len(key)>1 and pairs.get(key[0])==key[-1]:key=key[1:-1].strip()
    return key.replace('’',"'").replace('‘',"'")

IRREGULAR={
    'child':'children','person':'people','man':'men','woman':'women',
    'mouse':'mice','goose':'geese','tooth':'teeth','foot':'feet','ox':'oxen',
    'analysis':'analyses','basis':'bases','crisis':'crises','diagnosis':'diagnoses',
    'hypothesis':'hypotheses','thesis':'theses','axis':'axes','testis':'testes',
    'criterion':'criteria','phenomenon':'phenomena','datum':'data','medium':'media',
    'bacterium':'bacteria','curriculum':'curricula','nucleus':'nuclei',
    'stimulus':'stimuli','fungus':'fungi','alveolus':'alveoli','vertebra':'vertebrae',
    'larva':'larvae','calf':'calves','half':'halves','leaf':'leaves','loaf':'loaves',
    'self':'selves','shelf':'shelves','thief':'thieves','wolf':'wolves',
    'knife':'knives','life':'lives','wife':'wives','tomato':'tomatoes',
    'potato':'potatoes','hero':'heroes','echo':'echoes','mango':'mangoes',
}
INVARIANT={'news','series','species','means','physics','statistics','mathematics',
           'ethics','diabetes','measles','yes','no','not','none','this','that',
           'his','her','has','have','was','is','as','all','any','some','new'}
WORD=re.compile(r'[^\W\d_]+',re.UNICODE)
SINGULAR_ES={'lens','alias','status','campus','virus','apparatus'}

def _plural(word):
    if word in IRREGULAR:return {IRREGULAR[word]}
    if word in INVARIANT or not word.isascii() or not word.isalpha() or len(word)<3:return set()
    if word.endswith(('s','x','z','ch','sh')):plural=word+'es'
    elif word.endswith('y') and word[-2] not in 'aeiou':plural=word[:-1]+'ies'
    else:plural=word+'s'
    return {plural} if plural not in INVARIANT and plural not in IRREGULAR and plural not in SINGULAR_ES else set()

@lru_cache(maxsize=2048)
def word_forms(word):
    forms={word}
    if word in INVARIANT:return frozenset(forms)
    if word in ('mango','mangos','mangoes'):return frozenset(('mango','mangos','mangoes'))
    known=False
    for singular,plural in IRREGULAR.items():
        if word in (singular,plural):forms.update((singular,plural));known=True
    if known:return frozenset(forms)
    bases=set()
    if word not in SINGULAR_ES and not word.endswith(('ss','us','is','ics','ness')):
        candidates=[word[:-3]+'y' if word.endswith('ies') else '',word[:-2] if word.endswith('es') else '',word[:-1] if word.endswith('s') else '']
        for candidate in candidates:
            if candidate and word in _plural(candidate):bases.add(candidate);break
    forms.update(bases or _plural(word))
    return frozenset(forms)

@lru_cache(maxsize=2048)
def answer_variants(value):
    """Only source-verifiable repeated initials, never arbitrary qualifiers."""
    variants=[value]
    def same_initials(phrase,abbreviation):
        if not re.fullmatch(r'[A-Z]{2,12}',abbreviation) or not re.fullmatch(r"[^\W\d_]+(?:[\s'’\-]+[^\W\d_]+)+",phrase):return False
        words=re.findall(r'[^\W\d_]+',phrase)
        if any(w.casefold() in ('no','not','without','except') for w in words):return False
        all_initials=''.join(w[0] for w in words).upper()
        significant=''.join(w[0] for w in words if w.casefold() not in ('a','an','the','of','and','for','in','on','to','by','with')).upper()
        return abbreviation in (all_initials,significant)
    match=re.fullmatch(r'\s*(.+?)\s*\(([^()]+)\)\s*[.!]?\s*',value)
    if match:
        before,inside=(v.strip() for v in match.groups())
        if same_initials(before,inside) or same_initials(inside,before):variants.extend((before,inside))
    return tuple(dict.fromkeys(variants))

def _literal_pattern(value):
    key=answer_key(value);parts=[];previous=None
    structural=bool(re.search(r'[()\[\]{}+*/=<>%]',key))
    for match in re.finditer(r'[^\W\d_]+|\d+(?:\.\d+)?|[^\s]',key):
        token=match[0]
        if token==',' and not structural:continue
        if previous is not None:
            gap=key[previous.end():match.start()]
            if gap and all(c.isspace() or c==',' for c in gap):parts.append(r'\s+' if structural else r'(?:\s+|\s*,\s*)')
            elif previous[0][-1].isalnum() and token[0].isalnum():pass
            else:parts.append(r'\s*')
        if WORD.fullmatch(token):parts.append('(?:'+'|'.join(re.escape(v) for v in sorted(word_forms(token),key=lambda v:(-len(v),v)))+')')
        else:parts.append(re.escape(token))
        previous=match
    if previous is not None and not structural and ',' in key[previous.end():]:parts.append(r',?')
    return ''.join(parts)

@lru_cache(maxsize=2048)
def item_pattern(value):
    return '(?:'+'|'.join(_literal_pattern(v) for v in answer_variants(value))+')'

def equivalent(first,second):
    a,b=answer_key(first),answer_key(second)
    return a==b or bool(a and b and (re.fullmatch(item_pattern(first),b) or re.fullmatch(item_pattern(second),a)))

def reference_extension(key,start,end,answer):
    """Extra-text mode must not turn one numeric reference into another."""
    before,after=key[:start],key[end:]
    if after and after[0] in '+-*/=<>%#@&|':return True
    if before and before[-1] in '+-*/=<>%#@&|':return True
    if not any(c.isdigit() for c in answer):return False
    if re.match(r'(?:\s*[\(\[]\s*\w|[./:+\-*]\w)',after):return True
    if re.search(r'[-+*/]\s*$',before) or re.search(r'\d\s*:\s*$',before):return True
    if before.endswith('.') and len(before)>1 and before[-2].isdigit():return True
    return False

def match_input(plan,value,accepted,target=0):
    if not isinstance(value,str) or len(value)>MAX_TEXT:raise ValueError('Invalid written answer.')
    raw=value.strip();key=answer_key(raw);items=plan['items']
    remaining=[i for i in range(len(items)) if i not in accepted]
    allowed=remaining[:1] if plan['ordered'] else remaining
    if plan['ordered'] and target in remaining:allowed=[target]
    for i in allowed:
        if equivalent(raw,items[i]['answer']):return {'matched':[i],'status':'correct'}
    if plan.get('original') and equivalent(raw,plan['original']) and remaining:
        return {'matched':remaining,'status':'correct'}
    for group in plan.get('groups',[]):
        members=[i for i in group['items'] if i in remaining]
        if members and (not plan['ordered'] or members==remaining[:len(members)]) and equivalent(raw,group['original']):
            return {'matched':members,'status':'correct'}
    if len(items)>1 or plan.get('ignore_extra'):
        # Find entire expected items, then account for EVERY remaining character.
        # This accepts many list layouts without confusing plural suffixes with items.
        found=[];taken=[]
        for i in sorted(remaining,key=lambda n:-len(answer_key(items[n]['answer']))):
            for m in re.finditer(item_pattern(items[i]['answer']),key):
                a,b=m.span()
                if a and (key[a-1].isalnum() or key[a-1]=='_') or b<len(key) and (key[b].isalnum() or key[b]=='_'):continue
                if reference_extension(key,a,b,items[i]['answer']):continue
                if any(a<y and b>x for x,y,_ in taken):continue
                taken.append((a,b,i));break
        taken.sort();cursor=0;safe=bool(taken)
        numeric=any(any(c.isdigit() for c in items[i]['answer']) for _,_,i in taken)
        if numeric:
            gaps=[];last_end=0
            for a,b,_ in taken:
                gap=re.sub(r'^\s*\(?\d+[.)]\s+',' ',key[last_end:a])
                gaps.append(gap);last_end=b
            gaps.append(key[last_end:])
            if any(re.search(r'\d',gap) for gap in gaps):taken=[];safe=False
        for a,b,i in taken:
            if not _layout(key[cursor:a],plan.get('connectors',[])):safe=False;break
            found.append(i);cursor=b
        if plan.get('ignore_extra') and taken:found=[i for _,_,i in taken];safe=True
        if safe and (plan.get('ignore_extra') or _layout(key[cursor:],plan.get('connectors',[]))) and (not plan['ordered'] or found==remaining[:len(found)]):
            return {'matched':found,'status':'correct'}
    for i in allowed:
        expected=answer_key(items[i]['answer'])
        if key and expected.startswith(key) and len(expected)>len(key) and not expected[len(key)].isalnum():
            return {'matched':[],'status':'incomplete'}
    return {'matched':[],'status':'wrong'}

def evaluate(plan,events):
    if not isinstance(events,list) or len(events)>1000:raise ValueError('Too many writing attempts.')
    accepted=[];missed=set();last={'status':'idle','matched':[]}
    for event in events:
        if not isinstance(event,dict):raise ValueError('Invalid writing attempt.')
        target=event.get('target',0)
        if type(target) is not int or not 0<=target<len(plan['items']):raise ValueError('Invalid target item.')
        last=match_input(plan,event.get('text',''),accepted,target)
        if last['status']=='correct':accepted.extend(i for i in last['matched'] if i not in accepted)
        elif last['status']=='wrong':
            remaining=[i for i in range(len(plan['items'])) if i not in accepted]
            if remaining:missed.add(target if target in remaining else remaining[0])
    remaining=[i for i in range(len(plan['items'])) if i not in accepted]
    return {'accepted':accepted,'missed':sorted(missed),'remaining':remaining,'target':remaining[0] if remaining else 0,'last':last,'complete':not remaining}

def grade(question,picks):
    plan=question['writing'];state=evaluate(plan,picks.get('writing',[]))
    if not state['complete'] and picks.get('unknown') is not True:raise ValueError('Complete the answers or reveal the remaining items.')
    correct=[i in state['accepted'] and i not in state['missed'] for i in range(len(plan['items']))]
    return {'earned':sum(correct),'total':len(correct),'correct':correct,'writing_state':state}

def attempt(question,events,text,target):
    new=list(events)+[{'text':text,'target':target}]
    state=evaluate(question['writing'],new)
    return new,state

def generate(client,jobs,store,cancel,progress):
    """A bad grouping falls back to the complete source answer, never invented text."""
    done=0
    offset=0
    while offset<len(jobs):
        if cancel.is_set():return
        batch=jobs[offset:offset+(1 if offset==0 else 5)]
        values=client.group_answers(batch)
        if cancel.is_set():return
        store.put(values);done+=len(batch);offset+=len(batch);progress(done,len(jobs))
