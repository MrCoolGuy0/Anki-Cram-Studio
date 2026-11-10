"""Read-only full-deck generation plan shared by independent/native Cram views."""
from .content import catalog,selected_decks,scoped_rows,snapshot,prepare_choices,studylist_is_basic
from .live_review import review_question
from types import SimpleNamespace

def bulk_config(config):
    decks=config.get('decks',[])
    if not isinstance(decks,list) or not decks or len(decks)>5000:raise ValueError('Select at least one deck.')
    if any(not str(d).isdigit() for d in decks):raise ValueError('Invalid deck selection.')
    return {'decks':list(dict.fromkeys(map(str,decks))),'children':bool(config.get('children',True)),
            'mode':'exam','limit':0,'filters':{},'order':'created_asc','shuffle':False}

def deck_choice_plan(col,config,mappings,model):
    config=bulk_config(config);compiled,count=snapshot(col,config,mappings)
    jobs,_=prepare_choices(compiled['questions'],{},model);sets={job['id']:job for job in jobs}
    cat=catalog(col);models={int(m['id']):m for m in cat['models']}
    # MAIN CRAM can use an Auto/mapped term; native Basic/reversed must follow
    # each actual template. Generate both directions where they differ.
    store=SimpleNamespace(data={'mappings':mappings})
    for row in scoped_rows(col,selected_decks(cat['decks'],config['decks'],config['children'])):
        cid,_,_,_,mid,_=row
        if not studylist_is_basic(models[mid]):continue
        question=review_question(col.get_card(cid),store,col)
        if question:
            more,_=prepare_choices([question],{},model)
            sets.update((job['id'],job) for job in more)
    return {'cards':count,'questions':compiled['available'],'skipped':compiled['skipped'],
            'jobs':list(sets.values()),'sets':len(sets),'model':model}
