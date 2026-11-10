"""Opt-in presentation for Anki's real Reviewer. No queue, rating or undo implementation.

Anki owns current-card selection, reveal, bottom-bar intervals, rating callbacks,
review operations and undo. This module never calls a scheduler or writes a card.
"""
from __future__ import annotations
from .network_jobs import run_network
import copy
import hashlib
import html
import json
import re
import threading
from .content import (compile_questions,prepare_choices,attach_choices,studylist_is_basic,
                      studylist_basic_fields,studylist_is_io)
from .ai import client as Gemini
from .gemini import generate_batches
from .storage import profile_store
from .appearance import get_appearance
from . import writing

PREFIX='cram_live:'

def review_question(card,store,col,mode='exam'):
    """Extract only the current actual card. Respect native Basic/reversed direction."""
    note=card.note();model=note.note_type();fields=list(note.fields)
    mappings=copy.deepcopy(store.data.get('mappings',{}));mid=str(model['id'])
    templates=model.get('tmpls',[])
    template_index=0 if model.get('type')==1 else card.ord
    template=templates[template_index] if template_index<len(templates) else {}
    if re.search(r'\{\{\s*type:',template.get('qfmt',''),re.I):return None
    if re.search(r'<script\b',template.get('qfmt','')+template.get('afmt',''),re.I) and not studylist_is_io(fields,model):return None
    if studylist_is_basic(model):
        fi,bi=studylist_basic_fields(model);names=[f['name'] for f in model['flds']]
        front=template.get('qfmt','')
        references=[i for i in (fi,bi) if re.search(r'\{\{(?:[^{}]+:)?'+re.escape(names[i])+r'\s*\}\}',front)]
        if front and len(references)!=1:return None
        qi=references[0] if references else (bi if card.ord else fi)
        mappings[mid]={'answer':names[bi if qi==fi else fi]}
    elif model.get('type')!=1 and not studylist_is_io(fields,model):
        mapping=mappings.get(mid,{})
        if not mapping.get('answer') or not mapping.get('clue'):return None
    native={}
    if studylist_is_io(fields,model):
        try:
            response=col.get_image_occlusion_note(note.id)
            native[note.id]=response.note if response.HasField('note') else None
        except Exception:pass
    row=(card.id,note.id,card.did,card.ord,model['id'],'\x1f'.join(fields))
    out=compile_questions([row],{model['id']:model},{card.did:''},{'mode':mode,'shuffle':False,'limit':1},mappings,native)
    q=out['questions'][0] if out['questions'] else None
    media=getattr(col,'media',None)
    if q and media is not None:
        for field in ('picture','clue','extra'):
            if field in q:q[field]=media.escape_media_filenames(q[field])
        for slot in q.get('slots',[]):
            slot['answer_html']=media.escape_media_filenames(slot.get('answer_html',''))
    return q

def fingerprint(card):
    note=card.note();model=note.note_type()
    return hashlib.sha256(json.dumps([card.id,card.ord,list(note.fields),model.get('tmpls',[]),model.get('css','')],ensure_ascii=True).encode()).hexdigest()

def filtered_status(deck):
    if not deck.get('dyn'):return 'Anki reviews · Ratings update your schedule'
    return ('Filtered deck · rescheduling on · Ratings update your schedule' if deck.get('resched',True)
            else 'Filtered deck · rescheduling off · Anki preview, schedule unchanged')

class LiveReviewer:
    def __init__(self,mw,package,shortcut_factory=None,network_runner=None):
        self.mw=mw;self.package=package;self.active=False;self.mode='flash';self.auto_generate=False
        self.current=None;self.epoch=0;self.cancel=threading.Event();self.busy=False;self.worker_id=0
        self._store=None;self.closed=False;self.dialog=None;self.view_zooms=[]
        self.menu_original=None;self.menu_guard=None
        self.writing_focus=False;self.writing_filter=None
        self.mode_packets={};self.card_epoch=0;self.overlay_focus=False
        self.blank_shortcuts={};self.shortcut_factory=shortcut_factory or self.make_blank_shortcut
        self.network_runner=network_runner or run_network
    def install_writing_filter(self):
        if self.writing_filter is not None:return
        try:
            from aqt.qt import QObject,QEvent,Qt
            controller=self
            class InputGuard(QObject):
                def eventFilter(self,obj,event):
                    p=controller.current
                    if (event.type()==QEvent.Type.ShortcutOverride and controller.is_review() and getattr(controller,'overlay_focus',False)
                            and not event.modifiers() & (Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.AltModifier|Qt.KeyboardModifier.MetaModifier)):
                        event.accept();return True
                    if (event.type()==QEvent.Type.ShortcutOverride and controller.can_flip_flashcard()
                            and event.key()==Qt.Key.Key_Space and event.modifiers()==Qt.KeyboardModifier.NoModifier):
                        # Let the card DOM prevent Space's default button action.
                        # The native shortcut wrapper also covers bottom-bar focus.
                        event.accept();return True
                    if (event.type()==QEvent.Type.ShortcutOverride and controller.is_review() and p
                            and p['display']=='write' and p['side']=='question' and controller.writing_focus):
                        modifiers=event.modifiers()
                        if not modifiers & (Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.AltModifier|Qt.KeyboardModifier.MetaModifier):
                            if event.text() or event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter,Qt.Key.Key_Space,Qt.Key.Key_Up,Qt.Key.Key_Down):
                                event.accept();return True
                    return False
            self.writing_filter=InputGuard(self.mw.reviewer.web)
            self.mw.reviewer.web.installEventFilter(self.writing_filter)
        except (ImportError,AttributeError,TypeError):pass
    def make_blank_shortcut(self,key,callback):
        from aqt.qt import QShortcut,QKeySequence,Qt
        shortcut=QShortcut(QKeySequence(key),self.mw)
        shortcut.setContext(Qt.ShortcutContext.WindowShortcut);shortcut.setAutoRepeat(False)
        shortcut.activated.connect(callback)
        return shortcut
    def can_move_blank(self):
        packet=self.current
        return bool(self.is_review() and packet and packet['side']=='question' and packet['display'] in ('exam','write') and packet['question'].get('ready'))
    def can_flip_flashcard(self):
        packet=self.current
        return bool(self.is_review() and packet and packet.get('display') in ('flash','native')
                    and ((getattr(self,'mode','flash')=='flash' and packet.get('mode','flash')=='flash')
                         or (packet.get('display')=='flash' and (packet.get('question') or {}).get('image_answer'))))
    def move_blank(self,delta):
        if self.can_move_blank() and self.mw.reviewer.state=='question':
            self.mw.reviewer.web.eval(f'window.cramNative && window.cramNative.moveBlank({delta});')
    def update_blank_shortcuts(self):
        enabled=self.can_move_blank()
        if enabled and not self.blank_shortcuts:
            for key,delta in (('Up',-1),('Down',1)):
                self.blank_shortcuts[key]=self.shortcut_factory(key,lambda delta=delta:self.move_blank(delta))
        for shortcut in self.blank_shortcuts.values():shortcut.setEnabled(enabled)
    @property
    def store(self):
        if self._store is None:self._store=profile_store(self.mw.pm.profileFolder())
        return self._store
    def is_review(self):return self.active and self.mw.state=='review' and self.mw.col is not None
    def is_fullscreen_review(self):
        if not self.is_review() or not getattr(self.mw,'fullscreen',False):return False
        actual=getattr(self.mw,'isFullScreen',None)
        return not callable(actual) or actual()
    def invalidate(self):
        self.cancel.set();self.epoch+=1;self.current=None;self.writing_focus=False;self.overlay_focus=False;self.update_blank_shortcuts();self.update_bottom_appearance()
    def close(self,*args):
        self.restore_fullscreen_guard()
        self.restore_view_zoom()
        self.active=False;self.closed=True;self.invalidate();self._store=None
        for shortcut in self.blank_shortcuts.values():shortcut.deleteLater()
        self.blank_shortcuts={}
        self.worker_id+=1;self.busy=False
        if self.dialog:self.dialog.reject();self.dialog=None
    def state_change(self,new,old):
        if new not in ('review','resetRequired') and self.active:
            self.restore_fullscreen_guard()
            self.restore_view_zoom()
            self.active=False;self.invalidate()
    def install_fullscreen_guard(self):
        if self.menu_guard is not None:return
        original=getattr(self.mw,'show_menubar',None)
        if not callable(original) or not callable(getattr(self.mw,'hide_menubar',None)):return
        def show_menubar(*args,**kwargs):
            # Anki calls this when the pointer leaves the card webview for the ratings.
            if self.is_fullscreen_review():return self.mw.hide_menubar()
            return original(*args,**kwargs)
        self.menu_original=original;self.menu_guard=show_menubar
        self.mw.show_menubar=show_menubar
    def restore_fullscreen_guard(self):
        if self.menu_guard is not None and getattr(self.mw,'show_menubar',None) is self.menu_guard:
            self.mw.show_menubar=self.menu_original
        self.menu_original=None;self.menu_guard=None
    def restore_view_zoom(self):
        for web,value in self.view_zooms:
            try:web.setZoomFactor(value)
            except (RuntimeError,AttributeError):pass
        self.view_zooms=[]
    def view_zoom(self,data):
        delta=max(-.1,min(.1,float(data.get('delta',0))))
        for web in (self.mw.reviewer.web,getattr(self.mw,'bottomWeb',None)):
            if web is None:continue
            value=web.zoomFactor()
            if not any(saved is web for saved,_ in self.view_zooms):self.view_zooms.append((web,value))
            web.setZoomFactor(1 if data.get('reset') else max(.6,min(2,value+delta)))
    def open(self):
        if not self.mw.col or self.mw.state!='overview':return
        from aqt import gui_hooks
        from aqt.utils import showWarning
        required=('card_will_show','webview_will_set_content','state_shortcuts_will_change')
        if any(getattr(gui_hooks,name,None) is None for name in required):
            showWarning('This Anki version lacks the reviewer hooks needed by ANKI CRAM. Use Study Now or update desktop Anki.',parent=self.mw);return
        from .live_start import LiveStartDialog
        self.closed=False;self.dialog=LiveStartDialog(self)
        accepted=self.dialog.exec();self.dialog=None
        if accepted and self.mw.state=='overview':self.begin(self.mode,self.auto_generate)
    def begin(self,mode,auto_generate=False):
        if mode not in ('flash','exam','write'):raise ValueError('Invalid review interface.')
        self.invalidate();self.closed=False;self.mode=mode;self.auto_generate=bool(auto_generate);self.active=True
        self.install_fullscreen_guard()
        self.install_writing_filter()
        # Invoke exactly the same entry point as the existing Study Now button.
        try:self.mw.overview._linkHandler('study')
        except Exception:
            self.restore_fullscreen_guard();self.active=False;raise
        if self.is_fullscreen_review():
            hide=getattr(self.mw,'hide_menubar',None)
            if callable(hide):hide()
    def web_content(self,content,context):
        reviewer=getattr(self.mw,'reviewer',None)
        if reviewer is None:return
        if context is reviewer:
            content.css.append(f'/_addons/{self.package}/web/live.css')
            content.css.append(f'/_addons/{self.package}/web/appearance.css')
            content.css.append(f'/_addons/{self.package}/web/writing.css')
            content.js.append(f'/_addons/{self.package}/web/appearance.js')
            content.js.append(f'/_addons/{self.package}/web/writing.js')
            content.js.append(f'/_addons/{self.package}/web/live.js')
        elif getattr(context,'reviewer',None) is reviewer and self.active:
            content.css.append(f'/_addons/{self.package}/web/live-bottom.css')
            content.js.append(f'/_addons/{self.package}/web/appearance.js')
            data={'config':{'colors':get_appearance(self.store)['colors']},'view':self.current['display'] if self.current else self.mode}
            content.head=getattr(content,'head','')+'<script>window.cramBottomConfig='+json.dumps(data,ensure_ascii=True)+';</script>'
    def update_bottom_appearance(self,packet=None):
        # Native buttons, intervals and callbacks stay mounted and Anki-owned.
        web=getattr(self.mw,'bottomWeb',None)
        if web is None or not callable(getattr(web,'eval',None)):return
        packet=packet if packet is not None else self.current
        data={'config':{'colors':packet.get('appearance',{}).get('colors',{})} if packet and self.is_review() else {},'view':packet.get('display','') if packet and self.is_review() else ''}
        try:web.eval('window.cramBottomAppearance && window.cramBottomAppearance('+json.dumps(data,ensure_ascii=True)+');')
        except (RuntimeError,AttributeError):pass
    def shortcuts(self,state,keys):
        if state!='review' or not self.active:return
        # Keep native callbacks for grading. Flashcards Space flips; MCQ
        # question Space requests guarded native ans, and 1–4 select options.
        for i,(key,callback) in enumerate(keys):
            if str(key) in ('1','2','3','4'):
                number=int(key)
                def route(original=callback,number=number):
                    q=self.current
                    if self.is_review() and self.mw.reviewer.state=='question' and q and q['display']=='exam' and q.get('question',{}).get('ready'):
                        self.mw.reviewer.web.eval(f'window.cramNative && window.cramNative.choose({number-1});')
                    else:original()
                keys[i]=(key,route)
            elif str(key).lower() in (' ','space'):
                def flip_or_native(original=callback):
                    if self.can_flip_flashcard():
                        if not self.overlay_focus:self.mw.reviewer.web.eval('window.cramNative && window.cramNative.flip();')
                    elif (self.is_review() and self.current and self.current['display']=='exam'
                          and self.current['side']=='question' and self.mw.reviewer.state=='question'):
                        if not self.overlay_focus:self.mw.reviewer.web.eval('window.cramNative && window.cramNative.reveal();')
                    else:original()
                keys[i]=(key,flip_or_native)
        # E, B, 1–4 on the answer side, Ctrl+Z and other rating keys stay native.
    def make_packet(self,card):
        self.invalidate();self.mode_packets={};self.card_epoch=self.epoch
        self.current=self.interface_packet(card,self.mode)
        self.writing_focus=bool(self.current['display']=='write' and self.current['question'].get('ready'))
        return self.current
    def interface_packet(self,card,mode,auto_generate=None):
        auto_generate=self.auto_generate if auto_generate is None else bool(auto_generate)
        key=fingerprint(card);question=None;reason=''
        try:question=review_question(card,self.store,self.mw.col,'write' if mode=='write' else 'exam')
        except Exception:reason='This template uses the original Anki card.'
        display='native'
        if question and question['kind']=='io':display='io'
        elif question and question.get('image_answer'):display='flash'
        elif mode=='write' and question and question['mode']=='write':
            display='write'
            writing.attach([question],self.store.cache(),whole=not (auto_generate and self.store.get_key()),ignore_extra=self.store.data['preferences'].get('write_ignore_extra',False))
        elif mode=='exam' and question and question['mode']=='exam':
            display='exam';attach_choices([question],self.store.choice_cache([question],self.store.data['model']),self.store.data['model'],partial=True)
        elif mode=='flash' and question and question['kind'] in ('basic','cloze'):
            display='flash'
        elif mode=='exam':reason=reason or 'This card uses its original flashcard.'
        deck=self.mw.col.decks.current()
        packet={'cid':str(card.id),'epoch':self.epoch,'card_epoch':self.card_epoch,'mode':mode,'fingerprint':key,'side':'question','display':display,
                      'question':question,'deck':deck.get('name',''),'status':filtered_status(deck),'reason':reason,
                      'auto_generate':auto_generate,'generating':False,'error':''}
        if display=='write':
            packet['writing_events']=[]
            packet['writing_state']=writing.evaluate(question['writing'],[]) if question.get('ready') else None
        packet['text_zoom']=self.store.data['preferences'].get('text_zoom',1)
        packet['appearance']=get_appearance(self.store)
        return packet
    def switch_mode(self,mode):
        if mode not in ('flash','exam','write'):raise ValueError('Invalid review interface.')
        old=self.current;card=getattr(self.mw.reviewer,'card',None)
        if not self.is_review() or not old or not card or str(card.id)!=old['cid']:return
        if self.mw.reviewer.state not in ('question','answer') or fingerprint(card)!=old['fingerprint']:return
        if mode==self.mode:return
        preferences=self.store.data['preferences'];auto_generate=self.auto_generate
        if self.mode=='flash' and mode!='flash' and preferences.get('live_generate_configured'):
            auto_generate=bool(preferences.get('live_generate',False))
        packet=copy.deepcopy(self.mode_packets.get(mode)) or self.interface_packet(card,mode,auto_generate)
        question=packet.get('question')
        if packet['display']=='write' and not question.get('ready'):
            writing.attach([question],self.store.cache(),whole=old['side']=='answer' or not (auto_generate and self.store.get_key()),ignore_extra=self.store.data['preferences'].get('write_ignore_extra',False))
            packet['writing_state']=writing.evaluate(question['writing'],[]) if question.get('ready') else None
        elif packet['display']=='exam':attach_choices([question],self.store.choice_cache([question],self.store.data['model']),self.store.data['model'],partial=True)
        with self.store.lock:
            previous=self.store.data['preferences'].get('live_mode','flash')
            self.store.data['preferences']['live_mode']=mode
            try:self.store.save()
            except Exception:
                self.store.data['preferences']['live_mode']=previous;raise
        self.mode_packets[self.mode]=copy.deepcopy(old)
        self.cancel.set();self.worker_id+=1;self.busy=False;self.epoch+=1;self.mode=mode;self.auto_generate=auto_generate
        packet.update(epoch=self.epoch,side=old['side'],mode=mode,card_epoch=self.card_epoch,
                      text_zoom=old.get('text_zoom',1),appearance=get_appearance(self.store),
                      auto_generate=auto_generate,generating=False,error='',request_choices=False,request_regenerate=False)
        self.current=packet
        self.overlay_focus=False
        self.writing_focus=bool(packet['display']=='write' and packet['side']=='question' and question.get('ready'))
        self.update_blank_shortcuts();self.update_bottom_appearance(packet)
        # Redraw only our presentation. Never invoke Show Answer, Study Now,
        # next-card selection, rating, undo, or a native question/answer callback.
        self.mw.reviewer.web.eval('window.cramNative && window.cramNative.switchMode('+json.dumps(packet,ensure_ascii=True)+');')
    def card_html(self,original,card,kind):
        if not self.is_review() or kind not in ('reviewQuestion','reviewAnswer'):return original
        if card.id!=getattr(self.mw.reviewer.card,'id',None):return original
        try:
            if kind=='reviewQuestion' or not self.current or self.current['cid']!=str(card.id) or self.current['fingerprint']!=fingerprint(card):packet=self.make_packet(card)
            else:packet=self.current
            packet['side']='answer' if kind=='reviewAnswer' else 'question'
            if packet['side']=='answer':
                # Choices are presentation data for the same card, including its
                # revealed view. Let that work finish; other modes still cancel.
                if packet['display']!='exam' or packet['question'].get('ready'):self.cancel.set();packet['generating']=False
                self.writing_focus=False
            return self.render(original,packet)
        except Exception:
            # Preserve the native renderer if an unfamiliar template/API cannot be skinned.
            self.invalidate();return original
    def render(self,original,packet):
        self.update_blank_shortcuts();self.update_bottom_appearance(packet)
        data=html.escape(json.dumps(packet,ensure_ascii=True),quote=True)
        # Native scripts/audio/typing are preserved for original-card flashcards.
        native=original if packet['display']=='native' else ''
        if packet['display'] in ('exam','flash','write') and packet['side']=='answer':native=original
        deck=html.escape(packet['deck'].replace('::',' / '),quote=True)
        return (f'<section id="cram-live" data-packet="{data}">'
            '<header class="cl-header"><span class="cl-brand">ANKI CRAM</span>'
            f'<div class="cl-context"><div class="cl-deck" title="{deck}">{deck}</div>'
            f'<div class="cl-status">{html.escape(packet["status"])}</div></div>'
            '<div class="cl-header-tools"><div class="cl-settings">'
            '<button type="button" class="cl-settings-toggle" data-live-action="settings" title="Settings" aria-label="Settings" aria-haspopup="true" aria-expanded="false" aria-controls="cl-mode-menu">'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M3 7h5m4 0h9M3 17h9m4 0h5"/><circle cx="10" cy="7" r="2"/><circle cx="14" cy="17" r="2"/></svg></button>'
            '<div id="cl-mode-menu" class="cl-mode-menu" role="group" aria-label="Study mode" hidden>'
            '<button type="button" data-live-mode="flash">Flashcards</button>'
            '<button type="button" data-live-mode="write">Writing</button>'
            '<button type="button" data-live-mode="exam">Multiple Choice</button></div></div>'
            '<button type="button" class="cl-exit" data-live-action="exit" title="Exit ANKI CRAM" aria-label="Exit ANKI CRAM">'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div></header>'
            '<div id="cl-stage"><div id="cl-original">'+native+'</div><div id="cl-custom"></div></div>'
            '<div id="cl-notice" role="status"></div></section>'
            '<script>(function(){var run=window.cramNativeShown||(window.cramNativeShown=function(){if(window.cramNative)window.cramNative.mount();});'
            'if(Array.isArray(window.onShownHook)){if(window.onShownHook.indexOf(run)<0)window.onShownHook.push(run);}else setTimeout(run,0);})();</script>')
    def emit(self):
        self.update_blank_shortcuts();self.update_bottom_appearance()
        if self.is_review() and self.current:
            data=json.dumps(self.current,ensure_ascii=True)
            self.mw.reviewer.web.eval('window.cramNative && window.cramNative.receive('+data+');')
    def message(self,handled,message,context):
        if handled[0] or not message.startswith(PREFIX):return handled
        if not self.is_review() or context is not self.mw.reviewer:return handled
        try:
            if len(message)>200000:raise ValueError('Request too large.')
            data=json.loads(message[len(PREFIX):]);packet=self.current
            if not packet or data.get('cid')!=packet['cid'] or data.get('epoch')!=packet['epoch']:return True,None
            action=data.get('action')
            if action=='text_zoom':
                value=float(data.get('value',1))
                if not .6<=value<=2.5:raise ValueError('Invalid text size.')
                with self.store.lock:
                    self.store.data['preferences']['text_zoom']=value;self.store.save()
                packet['text_zoom']=value
            elif action=='view_zoom':self.view_zoom(data)
            elif action=='switch_mode':self.switch_mode(data.get('mode'))
            elif action=='overlay_focus':self.overlay_focus=data.get('open') is True
            elif action=='ready':
                if self.auto_generate and (packet['side']=='question' or (packet['display']=='exam' and not packet['question'].get('ready'))):self.generate()
            elif action=='writing_focus':
                if packet['display']=='write' and packet['side']=='question':self.writing_focus=data.get('focused') is True
            elif action=='write_submit':
                if packet['display']=='write' and packet['side']=='question' and packet['question'].get('ready'):
                    packet['writing_events'],packet['writing_state']=writing.attempt(packet['question'],packet.get('writing_events',[]),data.get('text',''),int(data.get('target',0)))
                    packet['error']=''
                    if packet['writing_state']['complete']:self.writing_focus=False
                    self.emit()
            elif action=='write_whole' and packet['display']=='write' and packet['side']=='question':
                self.cancel.set();self.worker_id+=1;self.busy=False;packet['generating']=False
                writing.attach([packet['question']],self.store.cache(),whole=True,ignore_extra=self.store.data['preferences'].get('write_ignore_extra',False))
                packet['writing_state']=writing.evaluate(packet['question']['writing'],[]);self.emit()
            elif action=='generate':self.generate()
            elif action=='regenerate':self.generate(force=True)
            elif action=='regen_decks':
                if self.busy:raise ValueError('Wait for the current generation request to finish.')
                from . import open_deck_choices
                open_deck_choices({'decks':[str(self.mw.col.decks.current()['id'])],'children':True})
            elif action=='flash' and packet['side']=='question':
                self.cancel.set();packet['display']='native';packet['error']='';packet['generating']=False;packet['request_choices']=False
                # Redraw through Anki, preserving its current card and review timer.
                # The original question already exists in Anki's cached rendering.
                raw=self.mw.reviewer._mungeQA(self.mw.reviewer.card.question())
                rendered=self.render(raw,packet)
                self.mw.reviewer.web.eval('_showQuestion('+json.dumps(rendered,ensure_ascii=True)+',"",document.body.className);')
            elif action=='edit':self.mw.onEditCurrent()
            elif action=='browse':self.mw.onBrowse()
            elif action=='undo':self.mw.undo()
            elif action=='exit':self.mw.moveToState('overview')
        except Exception as error:
            if self.current:self.current['error']=str(error);self.emit()
        return True,None
    def generate_writing(self):
        p=self.current
        if not self.is_review() or not p or p['side']!='question' or p['display']!='write' or self.busy:return
        q=p['question'];store=self.store;was_ready=q.get('ready',False)
        jobs,_,_=writing.attach([q],store.cache(),whole=not bool(store.get_key()),ignore_extra=store.data['preferences'].get('write_ignore_extra',False))
        if not jobs:
            if not was_ready and q.get('ready'):
                p['writing_state']=writing.evaluate(q['writing'],[]);p['generating']=False;p['error']='';self.emit()
            return
        client=Gemini(store.get_model_key(store.data['model']),store.data['model']);self.cancel=threading.Event();cancel=self.cancel;epoch=p['epoch']
        self.busy=True;self.worker_id+=1;worker_id=self.worker_id;p['generating']=True;p['error']='';self.emit()
        def work():return writing.generate(client,jobs,store,cancel,lambda *_:None)
        def done(future):
            if worker_id!=self.worker_id:return
            self.busy=False
            try:future.result();error=''
            except Exception as exc:error=str(exc)
            if not self.is_review() or not self.current:return
            if self.current['epoch']!=epoch:
                if self.auto_generate:self.generate()
                return
            if self.current['side']!='question' or self.current['display']!='write':return
            self.current['generating']=False;self.current['error']=error
            writing.attach([q],store.cache(),whole=True,ignore_extra=store.data['preferences'].get('write_ignore_extra',False))
            self.current['writing_state']=writing.evaluate(q['writing'],[]);self.emit()
        # Gemini must wait on neither Anki's collection nor shared network pool.
        self.network_runner(self.mw,work,done)
    def generate(self,force=False):
        if self.current and self.current['display']=='write':return self.generate_writing()
        packet=self.current
        if (not self.is_review() or not packet or packet['display']!='exam'
                or self.mw.reviewer.state not in ('question','answer') or self.mw.reviewer.state!=packet['side']):return
        question=packet['question'];store=self.store;model=store.data['model']
        packet['request_choices']=True
        if force:packet['request_regenerate']=True
        force=packet.get('request_regenerate',False)
        # A revealed card may acquire missing choices, but reshuffling existing
        # choices would invalidate the picks the user already saw and made.
        if force and packet['side']!='question':packet['request_regenerate']=False;return
        jobs,_=prepare_choices([question],{} if force else store.choice_cache([question],model),model)
        if not jobs:
            packet['generating']=False
            attach_choices([question],store.choice_cache([question],model),model,partial=True);self.emit();return
        if self.busy:
            packet['generating']=True;self.emit();return
        try:client=Gemini(store.get_model_key(model),model)
        except Exception as error:packet['generating']=False;packet['error']=str(error);self.emit();return
        self.cancel=threading.Event();cancel=self.cancel;epoch=packet['epoch'];self.busy=True
        packet['request_regenerate']=False
        self.worker_id+=1;worker_id=self.worker_id;packet['generating']=True;packet['error']='';self.emit()
        def work():return generate_batches(client,jobs,store,cancel,lambda *_:None,first_size=len(jobs))
        def done(future):
            if worker_id!=self.worker_id:return
            self.busy=False
            try:future.result();error=''
            except Exception as exc:error=str(exc)
            if not self.is_review() or not self.current:return
            if self.current['epoch']!=epoch:
                if self.auto_generate or self.current.get('request_choices'):self.generate()
                return
            self.current['generating']=False
            if (self.mw.reviewer.state!=self.current['side'] or self.current['display']!='exam'
                    or (force and self.current['side']!='question')):return
            self.current['error']=error
            attach_choices([question],store.choice_cache([question],model),model,partial=True,force=bool(force and not error))
            if force and not error:self.current['choices_revision']=self.current.get('choices_revision',0)+1
            self.emit()
            if self.current.get('request_regenerate'):self.generate()
        self.network_runner(self.mw,work,done)

