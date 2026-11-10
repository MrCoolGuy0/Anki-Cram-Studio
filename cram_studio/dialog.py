from __future__ import annotations
import copy
import json
import os
import random
import threading
import time
import uuid
from pathlib import Path
from aqt.qt import *
from aqt.operations import QueryOp
from aqt.webview import AnkiWebView
from aqt.theme import theme_manager
from aqt.utils import showWarning
from .content import (catalog,snapshot,count_matches,prepare_choices,attach_choices,grade,valid_distractors,
                      studylist_is_basic,studylist_is_io,studylist_basic_fields,cache_key)
from .storage import Store,profile_store
from .ai import client as Gemini
from .ai import PROVIDERS, DEFAULT_MODELS, KEY_ENV, KEY_URLS, KEY_CONSOLES, model_token
from .gemini import AIError,generate_batches
from .session import PracticeSession
from .network_jobs import run_network
from . import writing

class AISettings(QDialog):
    def __init__(self,owner):
        super().__init__(owner); self.owner=owner
        self.closed=False; self.checking=False; self.drafts={}; self.active=owner.store.provider()
        self.finished.connect(lambda *_:setattr(self,'closed',True))
        self.setWindowTitle('MAIN CRAM / ANKI CRAM · AI settings'); self.resize(610,490)
        layout=QVBoxLayout(self)
        self.info=QLabel(); self.info.setWordWrap(True); self.info.setOpenExternalLinks(True); layout.addWidget(self.info)
        form=QFormLayout(); layout.addLayout(form)
        self.provider=QComboBox()
        for value,label in PROVIDERS.items():self.provider.addItem(label,value)
        self.provider.setCurrentIndex(self.provider.findData(self.active));form.addRow('AI provider',self.provider)
        self.key=QLineEdit(); self.key.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow('API key',self.key)
        self.remember=QCheckBox('Save on this Windows account (Windows DPAPI)')
        self.remember.setEnabled(os.name=='nt'); self.remember.setChecked(os.name=='nt'); form.addRow('',self.remember)
        self.key_note=QLabel();self.key_note.setWordWrap(True);form.addRow(self.key_note)
        self.model=QComboBox(); self.model.setEditable(True); form.addRow('Model ID',self.model)
        note=QLabel('Only selected text clues and answers go to the selected provider. Images stay in Anki. Saved results work offline. Refresh models lists availability, not pricing. The add-on never changes provider or model automatically.'); note.setWordWrap(True); layout.addWidget(note)
        row=QHBoxLayout(); layout.addLayout(row)
        self.test=QPushButton('Test connection'); self.refresh=QPushButton('Refresh models'); self.forget_button=QPushButton('Forget saved key')
        for b in (self.test,self.refresh,self.forget_button): row.addWidget(b)
        self.status=QLabel('Ready. Connection testing uses one small API request.'); self.status.setWordWrap(True); layout.addWidget(self.status)
        self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel); layout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.save); self.buttons.rejected.connect(self.reject)
        self.test.clicked.connect(lambda:self.network(False)); self.refresh.clicked.connect(lambda:self.network(True)); self.forget_button.clicked.connect(self.forget)
        self.provider.currentIndexChanged.connect(self.change_provider);self.load_provider()
    def load_provider(self):
        provider=self.active;draft=self.drafts.get(provider,{})
        self.key.setText(draft.get('key',''));self.remember.setChecked(draft.get('remember',os.name=='nt'))
        self.key.setPlaceholderText('A key is already available — leave blank to keep it' if self.owner.store.get_key(provider) else 'Paste your '+PROVIDERS[provider]+' API key here')
        current=draft.get('model',self.owner.store.selected_model(provider));self.model.clear()
        self.model.addItems(list(dict.fromkeys([current]+draft.get('models',[])+[DEFAULT_MODELS[provider]])));self.model.setCurrentText(current)
        url=KEY_URLS[provider]
        extra=' Use a model API key; a Cursor or agent key may not grant model API access.' if provider=='grok' else ''
        self.info.setText('Generate choices once, then practice offline. Create a '+PROVIDERS[provider]+' key at <a href="'+url+'">'+KEY_CONSOLES[provider]+'</a>. Your provider’s quota and charges apply.'+extra+' Review AI choices for accuracy.')
        self.key_note.setText('Keys are stored separately for each provider.' if os.name=='nt' else 'Keys last until Anki closes on this system. For persistent setup, set '+KEY_ENV[provider]+'.')
    def remember_draft(self):
        self.drafts[self.active]={'key':self.key.text(),'remember':self.remember.isChecked(),'model':self.model.currentText(),'models':[self.model.itemText(i) for i in range(self.model.count())]}
    def change_provider(self):
        self.remember_draft();self.active=self.provider.currentData();self.load_provider();self.status.setText('Ready. Connection testing uses one small API request.')
    def forget(self):
        self.owner.store.forget_key(self.active); self.key.clear(); self.key.setPlaceholderText('Paste your API key here')
        self.status.setText('Saved/session key removed. An environment variable, if configured, is managed outside Anki.')
    def client(self): return Gemini(self.key.text().strip() or self.owner.store.get_key(self.active),model_token(self.active,self.model.currentText().strip()))
    def network_controls(self,enabled):
        for widget in (self.test,self.refresh,self.forget_button,self.provider,self.model,self.key,self.remember,self.buttons.button(QDialogButtonBox.StandardButton.Save)):
            widget.setEnabled(enabled)
        self.remember.setEnabled(enabled and os.name=='nt')
    def network(self,models):
        if self.checking:return
        try: client=self.client()
        except Exception as e: self.status.setText(str(e)); return
        self.checking=True;self.network_controls(False); self.status.setText('Checking '+PROVIDERS[self.active]+'…')
        def work(): return client.models() if models else client.test()
        def done(future):
            if self.closed or self.owner.closed: return
            self.checking=False;self.network_controls(True)
            try:
                result=future.result()
                if models:
                    current=self.model.currentText(); self.model.clear(); self.model.addItems(result); self.model.setCurrentText(current)
                    self.status.setText('Models refreshed. Select a model, then test the connection.')
                else: self.status.setText(result)
            except Exception as e: self.status.setText(str(e))
        run_network(self.owner.mw,work,done)
    def save(self):
        if self.checking:return
        try:
            # Validate model syntax even when no key has been entered yet.
            model=Gemini(self.key.text().strip() or self.owner.store.get_key(self.active) or 'validation',model_token(self.active,self.model.currentText().strip())).model
            if self.key.text().strip(): self.owner.store.set_key(self.key.text(),self.remember.isChecked(),provider=self.active)
            previous_model=self.owner.store.data['model'];previous_models=copy.deepcopy(self.owner.store.data['ai_models'])
            try:
                with self.owner.store.lock:self.owner.store.select_provider(self.active,model);self.owner.store.save()
            except Exception:
                self.owner.store.data['model']=previous_model;self.owner.store.data['ai_models']=previous_models;raise
            self.accept()
        except Exception as e: self.status.setText(str(e))

class MappingDialog(QDialog):
    def __init__(self,owner):
        super().__init__(owner); self.owner=owner; self.widgets=[]; self.setWindowTitle('MAIN CRAM / ANKI CRAM · Field mapping'); self.resize(620,500)
        layout=QVBoxLayout(self); label=QLabel('Choose the answer and clue for each note type. Basic defaults to the shorter field as the answer. Cloze blanks and native image masks are detected automatically.'); label.setWordWrap(True); layout.addWidget(label)
        area=QScrollArea(); area.setWidgetResizable(True); content=QWidget(); form=QVBoxLayout(content)
        saved=owner.store.data['mappings']
        for model in sorted(owner.models,key=lambda m:m['name'].casefold()):
            names=[f['name'] for f in model['flds']]
            if not names or studylist_is_io([],model): continue
            group=QGroupBox(model['name']); row=QFormLayout(group); mid=str(model['id']); mapping=saved.get(mid,{})
            answer=QComboBox(); clue=None
            if model.get('type')==1:
                answer.addItems(names); answer.setCurrentText(mapping.get('text',names[0])); row.addRow('Cloze text field',answer); kind='text'
            elif studylist_is_basic(model):
                answer.addItem('Auto — shorter field is the answer','auto')
                fi,bi=studylist_basic_fields(model)
                for i in (fi,bi): answer.addItem(names[i],names[i])
                answer.setCurrentIndex(max(0,answer.findData(mapping.get('answer','auto')))); row.addRow('Answer',answer); kind='basic'
            else:
                answer.addItems(names); answer.setCurrentText(mapping.get('answer',next((n for n in names if n.casefold() in ('answer','back','term')),names[min(1,len(names)-1)])))
                clue=QComboBox(); clue.addItems(names); clue.setCurrentText(mapping.get('clue',next((n for n in names if n.casefold() in ('question','front','definition')),names[0])))
                row.addRow('Answer',answer); row.addRow('Clue',clue); kind='custom'
            self.widgets.append((mid,kind,answer,clue)); form.addWidget(group)
        form.addStretch(); area.setWidget(content); layout.addWidget(area)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel); layout.addWidget(buttons); buttons.accepted.connect(self.save); buttons.rejected.connect(self.reject)
    def save(self):
        mappings=copy.deepcopy(self.owner.store.data['mappings'])
        for mid,kind,answer,clue in self.widgets:
            if kind=='text': mappings[mid]={'text':answer.currentText()}
            elif kind=='basic': mappings[mid]={'answer':answer.currentData()}
            else:
                if answer.currentText()==clue.currentText(): showWarning('Answer and clue must be different fields.',parent=self); return
                mappings[mid]={'answer':answer.currentText(),'clue':clue.currentText()}
        self.owner.store.data['mappings']=mappings; self.owner.store.save(); self.accept()

class CramDialog(QDialog):
    def __init__(self,mw,deck_id=None):
        super().__init__(mw)
        self.mw=mw; self.closed=False; self.models=[]; self.questions=[]; self.results={}; self.started=0; self.finished=False
        self.session_id=None; self.view={}; self.elapsed=0
        self.busy=False; self.generating=False; self.booting=False; self.token=0; self.cancel=threading.Event(); self.initial_deck=str(deck_id) if deck_id else None
        self.store=profile_store(mw.pm.profileFolder())
        self.setWindowTitle('MAIN CRAM · Practice only · Anki schedule unchanged'); self.setMinimumSize(540,440); self.resize(1180,800)
        self.setWindowFlags(Qt.WindowType.Window|Qt.WindowType.WindowTitleHint|Qt.WindowType.WindowSystemMenuHint|Qt.WindowType.WindowMinimizeButtonHint|Qt.WindowType.WindowMaximizeButtonHint|Qt.WindowType.WindowCloseButtonHint)
        layout=QVBoxLayout(self); layout.setContentsMargins(0,0,0,0)
        self.web=AnkiWebView(parent=self,title='cram_studio'); layout.addWidget(self.web); self.web.set_bridge_command(self.bridge,self)
        package=mw.addonManager.addonFromModule(__name__)
        body=(Path(__file__).parent/'web/app.html').read_text(encoding='utf-8')
        self.web.stdHtml(body,css=[f'/_addons/{package}/web/app.css',f'/_addons/{package}/web/appearance.css',f'/_addons/{package}/web/writing.css'],js=[f'/_addons/{package}/web/appearance.js',f'/_addons/{package}/web/writing.js',f'/_addons/{package}/web/app.js'],context=self)
    def emit(self,event,data=None):
        if not self.closed: self.web.eval('window.cram && window.cram.receive('+json.dumps(event)+','+json.dumps(data,ensure_ascii=True)+');')
    def apply_theme(self): self.emit('theme',bool(theme_manager.night_mode))
    def fail(self,error):
        self.busy=False; self.booting=False; self.emit('error',str(error))
    def bootstrap(self):
        if self.closed or self.booting: return
        self.booting=True
        def done(cat):
            self.booting=False
            if self.closed: return
            self.models=cat.pop('models'); config=self.store.config()
            cat.update({'current':self.initial_deck or cat['current'],'settings':{'model':config['model'],'has_key':bool(self.store.get_key()),'provider_name':self.store.provider_label()},'note_types':sorted(m['name'] for m in self.models),'preferences':config['preferences'],'history':config['history'],'saved_sessions':self.store.saved_sessions(),'dark':bool(theme_manager.night_mode),'media':self.mw.serverURL()})
            self.emit('bootstrap',cat)
        QueryOp(parent=self,op=catalog,success=done).failure(self.fail).run_in_background()
    def bridge(self,message):
        if not message.startswith('cram:'): return
        try:
            if len(message)>200000: raise ValueError('Request too large.')
            data=json.loads(message[5:]); action=data.get('action')
            if action in ('restart','grade','write_submit') and data.get('session_id') not in (None,self.session_id):return
            if self.busy and action!='cancel':
                self.emit('notice','Wait for the current operation to finish, or pause generation.'); return
            if action=='ready': self.bootstrap()
            elif action=='view_zoom':
                value=1 if data.get('reset') else self.web.zoomFactor()+max(-.1,min(.1,float(data.get('delta',0))))
                self.web.setZoomFactor(max(.6,min(2,value)))
            elif action=='preview':
                config=data.get('config',{}); request_id=int(data.get('request_id',0))
                def preview_done(result): self.emit('matches',dict(result,request_id=request_id))
                def preview_failed(error): self.emit('matches',{'error':str(error),'request_id':request_id})
                QueryOp(parent=self,op=lambda col:count_matches(col,config),success=preview_done).failure(preview_failed).run_in_background()
            elif action=='preferences':
                for key in ('repeat_mistakes','auto_advance','write_ignore_extra'):
                    if key in data:
                        if not isinstance(data[key],bool): raise ValueError('Invalid study setting.')
                        self.store.data['preferences'][key]=data[key]
                for key,lo,hi in [('feedback_ms',400,5000),('text_zoom',0.6,2.5)]:
                    if key in data:
                        value=float(data[key])
                        if not lo<=value<=hi: raise ValueError('Invalid display setting.')
                        self.store.data['preferences'][key]=value
                self.store.save()
                self.emit('preferences',self.store.config()['preferences'])
            elif action=='settings':
                if self.generating: raise ValueError('Pause generation before changing the model or API key.')
                AISettings(self).exec(); self.emit('settings',{'model':self.store.data['model'],'has_key':bool(self.store.get_key()),'provider_name':self.store.provider_label()})
                if self.questions and not self.started: self.prepared()
            elif action=='mapping': MappingDialog(self).exec()
            elif action=='customize':
                from . import open_customize
                open_customize()
            elif action=='start': self.start(data)
            elif action=='resume': self.resume(data.get('session_id'))
            elif action=='restart':self.restart()
            elif action=='checkpoint':
                if data.get('session_id')==self.session_id:self.save_progress(data.get('view',{}))
            elif action=='reset_progress':
                session_id=data.get('session_id')
                if session_id==self.session_id:
                    self.stop_generation();self.started=0;self.session_id=None;self.questions=[];self.results={}
                self.store.delete_session(session_id);self.bootstrap()
            elif action=='generate': self.generate(False)
            elif action=='cancel': self.cancel.set(); self.emit('notice','Pausing after the current request. Completed batches are saved.')
            elif action=='flash':
                if self.started:
                    index=int(data.get('index',len(self.results)))
                    if index!=len(self.results) or not 0<=index<len(self.questions): raise ValueError('Choose the current unanswered question.')
                    q=self.questions[index];q['mode']='flash'
                    self.save_progress(full=True)
                    self.emit('replace',{'index':index,'question':q})
                else:
                    self.stop_generation()
                    for q in self.questions: q['mode']='flash'
                    self.launch()
            elif action=='launch': self.launch()
            elif action=='grade': self.submit(data)
            elif action=='write_submit':self.write_submit(data)
            elif action=='write_whole':
                self.stop_generation()
                pending=[q for q in self.questions if q['mode']=='write' and not q.get('ready')]
                writing.attach(pending,self.store.cache(),whole=True,ignore_extra=self.config.get('write_ignore_extra',False))
                self.save_progress(full=True);self.emit('choicesReady',{'questions':pending,'done':0,'total':0});self.emit('generationDone',{})
            elif action=='finish': self.finish()
            elif action=='retry': self.retry(bool(data.get('mistakes',True)))
            elif action=='edit': self.edit_choices(int(data['index']))
            elif action=='regenerate': self.generate(True,int(data['index']))
            elif action=='regen_decks':
                if self.generating:raise ValueError('Pause generation before regenerating deck choices.')
                from . import open_deck_choices
                open_deck_choices(data.get('config'))
            elif action=='home':
                self.save_progress(full=True)
                self.stop_generation()
                self.questions=[]; self.results={}; self.started=0; self.session_id=None; self.bootstrap()
        except Exception as error: self.fail(error)
    def start(self,data):
        if self.busy: return
        self.save_progress(full=True)
        self.stop_generation()
        config=data.get('config',{})
        if config.get('mode') not in ('flash','exam','mixed','write'): raise ValueError('Choose a study mode.')
        if not isinstance(config.get('decks'),list) or not config['decks']: raise ValueError('Select at least one deck.')
        if len(config['decks'])>5000: raise ValueError('Too many selected decks.')
        config['limit']=max(0,min(10000,int(config.get('limit',30))))
        for saved in self.store.saved_sessions():
            if self.scope_key(saved['config'])==self.scope_key(config):self.resume(saved['id']);return
        self.config=config;self.session_id=None;self.view={};self.elapsed=0
        config['repeat_mistakes']=bool(self.store.data['preferences'].get('repeat_mistakes',False))
        config['write_ignore_extra']=bool(config.get('write_ignore_extra',self.store.data['preferences'].get('write_ignore_extra',False)))
        self.busy=True; self.started=0; self.finished=False; self.results={}
        self.emit('loading','Building your practice set…')
        mappings=copy.deepcopy(self.store.data['mappings'])
        def done(result):
            if self.closed: return
            self.busy=False; compiled,count=result
            self.questions=compiled['questions']; self.available=compiled['available']; self.skipped=compiled['skipped']; self.card_count=count
            if not self.questions: self.fail('No questions match this deck selection and search. Clear filters or check Field mapping. Unsupported legacy image masks and empty cards are skipped.'); return
            self.prepared()
        QueryOp(parent=self,op=lambda col:snapshot(col,config,mappings),success=done).failure(self.fail).run_in_background()
    def prepared(self):
        if self.config.get('mode')=='write':
            jobs,_,_=writing.attach(self.questions,self.store.cache(),whole=not bool(self.store.get_key()),ignore_extra=self.config.get('write_ignore_extra',False))
            self.launch(partial=True)
            if jobs:self.generate_writing()
            return
        jobs,ready=prepare_choices(self.questions,self.store.choice_cache(self.questions,self.store.data['model']),self.store.data['model']); self.jobs=jobs
        if not jobs: self.launch(); return
        self.emit('prepare',{'questions':len(self.questions),'available':self.available,'skipped':self.skipped,'missing':len(jobs),'cached':ready,'has_key':bool(self.store.get_key()),'provider_name':self.store.provider_label(),'model':self.store.data['model']})
    def generate(self,single=False,index=0):
        if self.busy or self.generating: raise ValueError('A AI request is already running. Pause it before regenerating choices.')
        if not self.questions: return
        if single:
            if not 0<=index<len(self.questions) or str(index) in self.results: raise ValueError('Choices can be changed before answering a question.')
            q=self.questions[index]
            if q['mode']!='exam': return
            jobs,_=prepare_choices([q],{},self.store.data['model'])
        else: jobs,_=prepare_choices(self.questions,self.store.choice_cache(self.questions,self.store.data['model']),self.store.data['model'])
        model=self.store.data['model'];client=Gemini(self.store.get_model_key(model),model)
        if not single and not self.started: self.launch(partial=True)
        self.generating=True; self.cancel=threading.Event(); self.token+=1; token=self.token
        # Finish the first waiting question first, then prepare two bulk batches.
        first=next((q for q in self.questions if q['mode']=='exam' and not q.get('ready',False)),None)
        first_keys={cache_key(first,s,model) for s in first['slots']} if first else set()
        jobs.sort(key=lambda j:j['id'] not in first_keys)
        first_size=sum(j['id'] in first_keys for j in jobs) or None
        self.emit('generating',{'total':len(jobs),'single':single})
        cancel=self.cancel
        def refresh(done,total):
            if self.closed or token!=self.token: return
            if single: self.emit('generationProgress',{'done':done,'total':total});return
            pending=[q for i,q in enumerate(self.questions) if str(i) not in self.results]
            changed=attach_choices(pending,self.store.choice_cache(pending,model),model,partial=True)
            self.save_progress(full=True)
            self.emit('choicesReady',{'questions':changed,'done':done,'total':total})
        def progress(done,total):
            self.mw.taskman.run_on_main(lambda:refresh(done,total))
        def work(): return generate_batches(client,jobs,self.store,cancel,progress,first_size=first_size,
            batch_size=5 if single else 10,parallelism=1 if single else getattr(self.store,'generation_parallelism',2))
        def done(future):
            if self.closed or token!=self.token: return
            self.generating=False
            try:
                future.result()
                if single:
                    attach_choices([self.questions[index]],self.store.choice_cache([self.questions[index]],model),model,force=True);self.clear_saved_picks(index);self.save_progress(full=True); self.emit('replace',{'index':index,'question':self.questions[index]})
                else: refresh(len(jobs),len(jobs))
                self.emit('generationDone',{})
            except Exception as error:
                if not single: refresh(0,len(jobs))
                payload={'message':str(error),'single':single,'active':bool(self.started)}
                self.emit('generationError',payload)
        run_network(self.mw,work,done)
    def write_submit(self,data):
        index=int(data.get('index',-1))
        if not self.started or self.finished or index!=len(self.results) or not 0<=index<len(self.questions):return
        q=self.questions[index]
        if q['mode']!='write' or not q.get('ready'):return
        saved=self.view.setdefault('written',{}).get(str(index),{})
        events=saved.get('events',data.get('events',[]))
        if writing.evaluate(q['writing'],events)['complete']:return
        if not str(data.get('text','')).strip():return
        events,state=writing.attempt(q,events,data.get('text',''),int(data.get('target',0)))
        self.view.setdefault('written',{})[str(index)]={'events':events,'draft':'' if state['last']['status']=='correct' else data.get('text',''),'target':state['target']}
        self.save_progress(full=True)
        self.emit('writeFeedback',{'index':index,'events':events,'state':state})
    def generate_writing(self):
        if self.generating:return
        jobs,_,_=writing.attach(self.questions,self.store.cache(),ignore_extra=self.config.get('write_ignore_extra',False))
        if not jobs:return
        client=Gemini(self.store.get_model_key(self.store.data['model']),self.store.data['model'])
        self.generating=True;self.cancel=threading.Event();self.token+=1;token=self.token;cancel=self.cancel
        self.emit('generating',{'total':len(jobs),'single':False})
        def refresh(done,total,whole=False):
            if self.closed or token!=self.token:return
            pending=[q for i,q in enumerate(self.questions) if str(i) not in self.results]
            _,_,changed=writing.attach(pending,self.store.cache(),whole=whole,ignore_extra=self.config.get('write_ignore_extra',False))
            self.save_progress(full=True);self.emit('choicesReady',{'questions':changed,'done':done,'total':total})
        def progress(done,total):self.mw.taskman.run_on_main(lambda:refresh(done,total))
        def work():return writing.generate(client,jobs,self.store,cancel,progress)
        def done(future):
            if self.closed or token!=self.token:return
            self.generating=False
            try:future.result();refresh(len(jobs),len(jobs),True)
            except Exception as error:
                refresh(0,len(jobs),True);self.emit('notice',str(error))
            self.emit('generationDone',{})
        run_network(self.mw,work,done)
    def stop_generation(self):
        self.cancel.set();self.token+=1;self.generating=False
    def launch(self,partial=False):
        if self.busy: return
        if not self.questions: return
        writing.attach(self.questions,self.store.cache(),whole=not bool(self.store.get_key()),ignore_extra=self.config.get('write_ignore_extra',False))
        attach_choices(self.questions,self.store.choice_cache(self.questions,self.store.data['model']),self.store.data['model'],partial=partial,force=True)
        self.practice=PracticeSession(self.questions,self.config.get('repeat_mistakes',False))
        self.questions=self.practice.questions;self.results=self.practice.results
        self.started=time.time(); self.finished=False;self.elapsed=0;self.view={};self.session_id=uuid.uuid4().hex
        self.save_progress(full=True)
        self.emit('session',self.session_packet())
    @staticmethod
    def scope_key(config):
        value={key:config.get(key) for key in ('mode','limit','children','order','order_desc','filters')}
        if config.get('mode')=='write':value['write_ignore_extra']=bool(config.get('write_ignore_extra',False))
        value['decks']=sorted(set(str(deck) for deck in config.get('decks',[])))
        return json.dumps(value,sort_keys=True)
    def session_packet(self,restored=False):
        if restored:
            for key,value in self.view.get('written',{}).items():
                i=int(key)
                if 0<=i<len(self.questions) and self.questions[i]['mode']=='write':value['state']=writing.evaluate(self.questions[i]['writing'],value.get('events',[]))
        return {'session_id':self.session_id,'questions':self.questions,'results':self.results,'view':self.view if restored else {},
                'restored':restored,'config':self.config,'repeat_mistakes':self.practice.repeat_mistakes,
                'original_count':self.practice.original_count,'skipped':getattr(self,'skipped',0),'available':getattr(self,'available',len(self.questions))}
    def save_progress(self,view=None,full=False):
        if not self.started or self.finished or not self.session_id:return
        if view is not None:
            if not isinstance(view,dict):raise ValueError('Invalid practice position.')
            index=view.get('index',self.view.get('index',len(self.results)))
            if type(index) is not int:raise ValueError('Invalid question position.')
            index=max(0,min(index,len(self.results),len(self.questions)-1))
            picks={}
            for key,values in view.get('picks',{}).items():
                if not str(key).isdigit() or not isinstance(values,list):continue
                i=int(key)
                if not 0<=i<=min(len(self.results),len(self.questions)-1):continue
                slots=self.questions[i]['slots']
                if len(values)!=len(slots):continue
                if all(v is None or type(v) is int and -1<=v<len(slot.get('choices',[])) for v,slot in zip(values,slots)):picks[str(i)]=values
            revealed=[i for i in view.get('revealed',[]) if type(i) is int and 0<=i<=min(len(self.results),len(self.questions)-1)]
            seen=view.get('flashSeen',revealed)
            if not isinstance(seen,list):seen=revealed
            flash_seen=list(dict.fromkeys(i for i in seen if type(i) is int and 0<=i<=min(len(self.results),len(self.questions)-1)
                                          and self.questions[i]['mode']=='flash' and self.questions[i]['kind']!='io'))
            written={}
            for key,value in view.get('written',{}).items():
                if str(key).isdigit() and 0<=int(key)<len(self.questions) and self.questions[int(key)]['mode']=='write' and isinstance(value,dict):
                    events=self.view.get('written',{}).get(str(key),{}).get('events',value.get('events',[]));writing.evaluate(self.questions[int(key)]['writing'],events)
                    written[str(key)]={'events':events,'draft':str(value.get('draft',''))[:20000],'target':max(0,min(99,int(value.get('target',0))))}
            masks={}
            for key,value in view.get('ioMasks',{}).items():
                if not str(key).isdigit() or not isinstance(value,dict):continue
                i=int(key)
                if not 0<=i<=min(len(self.results),len(self.questions)-1) or self.questions[i]['kind']!='io':continue
                count=self.questions[i].get('mask_count',0)
                masks[str(i)]={name:list(dict.fromkeys(n for n in value.get(name,[]) if type(n) is int and 0<=n<count)) for name in ('open','closed')}
                masks[str(i)]['seen']=value.get('seen') is True
            self.view={'written':written,'ioMasks':masks,'index':index,'picks':picks,'revealed':revealed,'flashSeen':flash_seen,'activeSlot':max(0,min(1000,int(view.get('activeSlot',0)))),
                       'zoom':max(.5,min(6,float(view.get('zoom',1)))),'scroll':max(0,min(1000000,float(view.get('scroll',0))))}
        elapsed=max(0,self.elapsed+time.time()-self.started)
        if full:
            self.store.save_session(self.session_id,{'version':1,'practice':self.practice.snapshot(),'config':self.config,'elapsed':elapsed,
                'available':getattr(self,'available',len(self.questions)),'skipped':getattr(self,'skipped',0)})
        self.view.update({'elapsed':elapsed,'answered':len(self.results),'total':len(self.questions),'updated':time.time()})
        self.store.save_session_view(self.session_id,self.view)
    def clear_saved_picks(self,index):
        self.view.get('picks',{}).pop(str(index),None)
    def resume(self,session_id):
        self.save_progress(full=True);self.stop_generation()
        payload,view=self.store.session(session_id)
        practice=PracticeSession.restore(payload.get('practice'))
        self.practice=practice;self.questions=practice.questions;self.results=practice.results;self.config=payload['config']
        self.available=payload.get('available',len(self.questions));self.skipped=payload.get('skipped',0)
        self.session_id=session_id;self.view=view;self.elapsed=max(0,payload.get('elapsed',0),view.get('elapsed',0));self.started=time.time();self.finished=False
        self.save_progress(full=True);self.emit('session',self.session_packet(True))
    def submit(self,data):
        if self.busy: raise ValueError('Wait for the current request to finish.')
        index=int(data['index'])
        if not 0<=index<len(self.questions) or not self.started or self.finished: raise ValueError('No active question.')
        picks=data.get('picks',{})
        if self.questions[index]['mode']=='write':
            events=self.view.get('written',{}).get(str(index),{}).get('events')
            if events is not None:picks=dict(picks,writing=events)
        packet=self.practice.submit(index,picks);self.save_progress(full=True);self.emit('graded',packet)
    def restart(self):
        if not self.started or self.finished or not self.session_id:raise ValueError('No active practice to restart.')
        self.save_progress(full=True)
        self.stop_generation()
        old_id=self.session_id;items=self.practice.originals(False)
        if (self.config.get('order') or ('shuffle' if self.config.get('shuffle',True) else 'created_asc'))=='shuffle' and len(items)>1:
            previous=[q['id'] for q in items];random.SystemRandom().shuffle(items)
            if [q['id'] for q in items]==previous:items[:]=items[1:]+items[:1]
        self.questions=items;self.started=0;self.session_id=None
        self.launch(partial=True)
        self.store.delete_session(old_id)
    def finish(self):
        if len(self.results)!=len(self.questions): raise ValueError('Complete every question first.')
        self.stop_generation()
        result=dict(self.practice.summary(),date=time.strftime('%Y-%m-%d %H:%M'),seconds=max(0,int(self.elapsed+time.time()-self.started)),decks=list(dict.fromkeys(q['deck'] for q in self.questions)))
        if not self.finished: self.store.history(result,self.session_id); self.finished=True
        self.emit('finished',dict(result,results=self.results,history=self.store.config()['history']))
    def retry(self,mistakes):
        if not self.finished: return
        items=self.practice.originals(mistakes)
        if not items: self.emit('notice','You got everything right. Start a new set when you’re ready.'); return
        self.questions=items; self.started=0;self.config['repeat_mistakes']=bool(self.store.data['preferences'].get('repeat_mistakes',False)); self.prepared()
    def edit_choices(self,index):
        if self.generating: raise ValueError('Pause generation before editing choices.')
        if self.busy or not 0<=index<len(self.questions) or str(index) in self.results: return
        q=self.questions[index]
        if q['mode']!='exam': return
        dialog=QDialog(self); dialog.setWindowTitle('Edit wrong choices · correct answer is locked'); dialog.resize(580,480)
        layout=QVBoxLayout(dialog); scroll=QScrollArea(); scroll.setWidgetResizable(True); content=QWidget(); form=QFormLayout(content); widgets=[]
        for slot in q['slots']:
            label=QLabel(f'Blank {slot["number"]} · Correct answer: '+slot['answer']); label.setWordWrap(True); label.setTextFormat(Qt.TextFormat.PlainText); form.addRow(label)
            lines=[]
            for i,wrong in enumerate(slot.get('wrong',['','',''])):
                line=QPlainTextEdit(wrong);line.setMinimumHeight(70);line.setMaximumHeight(130)
                form.addRow(f'Wrong choice {i+1}',line); lines.append(line)
            widgets.append((slot,lines))
        scroll.setWidget(content); layout.addWidget(scroll); error=QLabel(); error.setWordWrap(True); layout.addWidget(error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel); layout.addWidget(buttons); buttons.rejected.connect(dialog.reject)
        def save():
            try:
                values={cache_key(q,s,self.store.data['model']):valid_distractors(s['answer'],[line.toPlainText() for line in lines],context=q['clue']) for s,lines in widgets}
                self.store.put(values); attach_choices([q],self.store.cache(),self.store.data['model'],force=True);self.clear_saved_picks(index);self.save_progress(full=True); dialog.accept(); self.emit('replace',{'index':index,'question':q})
            except Exception as e: error.setText(str(e))
        buttons.accepted.connect(save); dialog.exec()
    def closeEvent(self,event):
        try:self.save_progress(full=True)
        except Exception as error:
            showWarning('Practice progress could not be saved:\n'+str(error),parent=self);event.ignore();return
        self.closed=True; self.token+=1; self.cancel.set(); event.accept()
    def reject(self):
        self.close()
