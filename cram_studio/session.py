"""Independent practice queue and resumable snapshots. No Anki/network calls."""
from __future__ import annotations
import copy
import random
from .content import grade

class PracticeSession:
    def __init__(self,questions,repeat_mistakes=False,rng=None):
        self.rng=rng or random.SystemRandom();self.repeat_mistakes=bool(repeat_mistakes)
        self.questions=[];self.results={}
        for question in questions:
            q=copy.deepcopy(question);q['origin']=q.get('origin',q['id']);q['is_retry']=False
            self.questions.append(q)
        self.original_count=len(self.questions)
    def snapshot(self):
        return copy.deepcopy({'version':1,'questions':self.questions,'results':self.results,
                              'repeat_mistakes':self.repeat_mistakes,'original_count':self.original_count})
    @classmethod
    def restore(cls,data):
        if not isinstance(data,dict) or data.get('version')!=1:raise ValueError('Unsupported saved practice version.')
        questions=data.get('questions');results=data.get('results')
        if not isinstance(questions,list) or not questions or not isinstance(results,dict):raise ValueError('Invalid saved practice queue.')
        if set(results)!={str(i) for i in range(len(results))} or len(results)>len(questions):raise ValueError('Invalid saved practice results.')
        for q in questions:
            if not isinstance(q,dict) or not all(k in q for k in ('id','origin','is_retry','deck','kind','mode','slots','clue')):raise ValueError('Invalid saved question.')
            if q['mode'] not in ('flash','exam','write') or not isinstance(q['slots'],list):raise ValueError('Invalid saved question mode.')
        for i,r in results.items():
            if not isinstance(r,dict) or not isinstance(r.get('picks'),dict) or not 0<=r.get('earned',-1)<=r.get('total',-1):raise ValueError('Invalid saved answer.')
        count=sum(not q['is_retry'] for q in questions)
        if data.get('original_count')!=count:raise ValueError('Invalid saved original count.')
        session=cls.__new__(cls);session.rng=random.SystemRandom();session.questions=copy.deepcopy(questions)
        session.results=copy.deepcopy(results);session.original_count=count;session.repeat_mistakes=bool(data.get('repeat_mistakes'))
        return session
    def submit(self,index,picks):
        key=str(index)
        if key in self.results:return {'index':index,'result':self.results[key],'queued':None,'total':len(self.questions)}
        if type(index) is not int or index!=len(self.results) or not 0<=index<len(self.questions):raise ValueError('Answer the current question first.')
        question=self.questions[index];result=dict(grade(question,picks),picks=copy.deepcopy(picks))
        self.results[key]=result;queued=None
        if self.repeat_mistakes and result['earned']<result['total']:
            retry=copy.deepcopy(question);retry['is_retry']=True
            retry['id']=retry['origin']+'/retry-'+str(len(self.results))
            if retry['mode']=='exam':
                for slot in retry['slots']:
                    options=[slot['answer']]+slot['wrong'];self.rng.shuffle(options)
                    slot['choices']=options;slot['correct']=options.index(slot['answer'])
            # If other questions remain, leave at least one between attempts.
            position=self.rng.randrange(index+2,len(self.questions)+1) if index+1<len(self.questions) else len(self.questions)
            self.questions.insert(position,retry)
            queued={'position':position,'question':retry}
        return {'index':index,'result':result,'queued':queued,'total':len(self.questions)}
    def summary(self):
        if not self.questions or len(self.results)!=len(self.questions):raise ValueError('Complete every question first.')
        first=[];latest={}
        for i,q in enumerate(self.questions):
            result=self.results[str(i)];latest[q['origin']]=result
            if not q['is_retry']:first.append(result)
        return {'earned':sum(r['earned'] for r in first),'total':sum(r['total'] for r in first),
            'questions':self.original_count,'attempts':len(self.questions),'repeat_attempts':len(self.questions)-self.original_count,
            'mastered':sum(r['earned']==r['total'] for r in latest.values()),
            'final_earned':sum(r['earned'] for r in latest.values()),'final_total':sum(r['total'] for r in latest.values()),
            'repeat_enabled':self.repeat_mistakes}
    def originals(self,mistakes=False):
        return [copy.deepcopy(q) for i,q in enumerate(self.questions) if not q['is_retry'] and (not mistakes or self.results[str(i)]['earned']<self.results[str(i)]['total'])]
