"""Read-only Anki sort-column discovery; never changes Browser or deck settings."""
import random

def direction(column):
    try: name=column.DESCRIPTOR.fields_by_name['sorting_cards'].enum_type.values_by_number[column.sorting_cards].name
    except (AttributeError,KeyError): return None
    if 'NOTES' in name: return None
    if name.endswith('DESCENDING'): return False
    if name.endswith('ASCENDING'): return True
    return None

def columns(col):
    try: return [c for c in col.all_browser_columns() if direction(c) is not None]
    except (AttributeError,TypeError): return []

def menu(col):
    return [{'key':c.key,'label':getattr(c,'cards_mode_label','') or c.key} for c in columns(col)]

def native_order(col,query,key,descending=False):
    column=next((c for c in columns(col) if c.key==key),None)
    if column is None: raise ValueError('This Anki version does not support that card order. Choose another order.')
    return list(col.find_cards(query,order=column,reverse=(direction(column)==descending)))

def card_rank(col,query,order,descending,rows,names):
    if order.startswith('anki:'):
        ordered=native_order(col,query,order[5:],descending)
    else:
        due=next((c for c in columns(col) if c.key.casefold() in ('carddue','due')),None)
        if due is None: raise ValueError('Anki’s native Due column is unavailable on this version.')
        ordered=native_order(col,query,due.key,False)
        selected={r[0] for r in rows};ordered=[cid for cid in ordered if cid in selected]
        deck={r[0]:names[r[2]].casefold() for r in rows}
        if order=='deck_due': ordered.sort(key=lambda cid:deck[cid])
        else:
            # Preserve native Due grouping; only break equal queue/due ties.
            metadata={}
            ids=list(selected)
            for offset in range(0,len(ids),500):
                batch=ids[offset:offset+500]
                for cid,queue,due_value in col.db.all('select id,queue,due from cards where id in ('+','.join('?' for _ in batch)+')',*batch):metadata[cid]=(queue,due_value)
            groups={}
            for cid in ordered:groups.setdefault(metadata[cid],[]).append(cid)
            ordered=[]
            for group in groups.values():
                if order=='due_random':random.SystemRandom().shuffle(group)
                elif order=='due_deck':group.sort(key=lambda cid:deck[cid])
                else:raise ValueError('Invalid question order.')
                ordered.extend(group)
    return {str(cid):i for i,cid in enumerate(ordered)}

def arrange(questions,order):
    """Anki-style random note/card-type orders, without constructing a scheduler queue."""
    rng=random.SystemRandom()
    if order=='random_notes':
        notes={}
        for q in questions:notes.setdefault(q['nid'],[]).append(q)
        groups=list(notes.values());rng.shuffle(groups);questions[:]=[q for group in groups for q in group]
    elif order in ('card_type','card_type_random'):
        if order.endswith('random'):rng.shuffle(questions)
        questions.sort(key=lambda q:q.get('ordinal',0))
    elif order=='deck_random_notes':
        groups={}
        for q in questions:groups.setdefault(q['deck'],[]).append(q)
        questions.clear()
        for deck in sorted(groups,key=lambda name:tuple(p.casefold() for p in name.split('::'))):
            group=groups[deck];arrange(group,'random_notes');questions.extend(group)
    else:raise ValueError('Invalid question order.')
