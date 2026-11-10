"""Profile-local practice data, atomic writes, and Windows protected key storage."""
from __future__ import annotations
import base64
import copy
import ctypes
import json
import os
import re
import tempfile
import threading
import time
from pathlib import Path

DEFAULT_MODEL='gemini-3.5-flash-lite'
_profile_stores={}

def profile_store(profile):
    key=str(Path(profile).resolve())
    if key not in _profile_stores:_profile_stores[key]=Store(profile)
    return _profile_stores[key]

def clear_profile_stores():
    for store in _profile_stores.values():
        store.session_key='';store.session_keys.clear()
    _profile_stores.clear()

class Store:
    def __init__(self,profile):
        self.path=Path(profile)/'cram_studio'; self.path.mkdir(parents=True,exist_ok=True)
        self.lock=threading.RLock(); self.session_key=''; self.session_keys={}
        self.data={'version':1,'model':DEFAULT_MODEL,'ai_models':{},'mappings':{},'cache':{},'history':[],'sessions':{},'preferences':{'repeat_mistakes':False,'auto_advance':True,'feedback_ms':1000,'text_zoom':1}}
        target=self.path/'practice.json'
        if target.exists():
            try:
                loaded=json.loads(target.read_text(encoding='utf-8'))
                if not isinstance(loaded,dict): raise ValueError('Invalid data')
                for k in self.data:
                    if k in loaded and isinstance(loaded[k],type(self.data[k])): self.data[k]=loaded[k]
            except (OSError,ValueError):
                # Preserve a broken file for recovery; do not silently overwrite it.
                raise ValueError('Cram Studio practice.json could not be read. Rename it to practice.backup.json in your profile/cram_studio folder, then reopen. Your Anki collection is unaffected.')
    def save(self):
        with self.lock: self._atomic(self.path/'practice.json',json.dumps(self.data,ensure_ascii=False).encode())
    def _atomic(self,path,data):
        fd,name=tempfile.mkstemp(prefix='.cram-',dir=self.path)
        try:
            with os.fdopen(fd,'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
            os.replace(name,path)
        finally:
            if os.path.exists(name): os.unlink(name)
    def config(self):
        with self.lock: return copy.deepcopy({k:v for k,v in self.data.items() if k!='cache'})
    def cache(self):
        with self.lock: return copy.deepcopy(self.data['cache'])
    def choice_cache(self,questions,model):
        from .content import cache_key
        keys={cache_key(q,slot,model) for q in questions for slot in q['slots']}
        with self.lock:
            return {key:copy.deepcopy(self.data['cache'][key]) for key in keys if key in self.data['cache']}
    def put(self,values):
        with self.lock:
            cache=self.data['cache']; cache.update(values)
            self.save()
    def history(self,result,session_id=None):
        with self.lock:
            previous=self.data['history'];saved=self.data['sessions'].get(session_id)
            self.data['history']=[result]+self.data['history'][:29]
            if session_id:self.data['sessions'].pop(session_id,None)
            try:self.save()
            except Exception:
                self.data['history']=previous
                if saved is not None:self.data['sessions'][session_id]=saved
                raise
            if session_id:self._remove_session_files(session_id)
    def _session_path(self,session_id,view=False):
        if not isinstance(session_id,str) or not re.fullmatch(r'[a-f0-9]{32}',session_id):raise ValueError('Invalid saved practice ID.')
        return self.path/('session-'+session_id+('.view.json' if view else '.json'))
    def save_session(self,session_id,payload):
        with self.lock:
            self._atomic(self._session_path(session_id),json.dumps(payload,ensure_ascii=False).encode())
            if session_id not in self.data['sessions']:
                questions=payload['practice']['questions']
                self.data['sessions'][session_id]={'id':session_id,'config':copy.deepcopy(payload['config']),
                    'decks':list(dict.fromkeys(q['deck'] for q in questions)),'original_count':payload['practice']['original_count'],
                    'created':time.time()}
                try:self.save()
                except Exception:
                    self.data['sessions'].pop(session_id,None);raise
    def session(self,session_id):
        with self.lock:
            if session_id not in self.data['sessions']:raise ValueError('This saved practice no longer exists.')
            try:
                payload=json.loads(self._session_path(session_id).read_text(encoding='utf-8'))
                view=self.session_view(session_id)
                if not isinstance(payload,dict):raise ValueError('Invalid snapshot')
                return payload,view
            except (OSError,ValueError) as error:raise ValueError('Saved practice could not be read. Its files are preserved; use Reset only if you want to discard it.') from error
    def session_view(self,session_id):
        path=self._session_path(session_id,True)
        if not path.exists():return {}
        value=json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(value,dict):raise ValueError('Invalid saved practice position.')
        return value
    def save_session_view(self,session_id,view):
        with self.lock:
            if session_id not in self.data['sessions']:return
            self._atomic(self._session_path(session_id,True),json.dumps(view,ensure_ascii=False).encode())
    def saved_sessions(self):
        with self.lock:
            saved=[]
            for session_id,meta in self.data['sessions'].items():
                item=copy.deepcopy(meta)
                try:
                    view=self.session_view(session_id);item.update({'answered':view.get('answered',0),'total':view.get('total',meta['original_count']),'updated':view.get('updated',meta['created'])})
                except (OSError,ValueError):item.update({'answered':0,'total':meta['original_count'],'updated':meta['created'],'error':True})
                saved.append(item)
            return sorted(saved,key=lambda item:item['updated'],reverse=True)
    def delete_session(self,session_id):
        with self.lock:
            self._session_path(session_id)
            saved=self.data['sessions'].pop(session_id,None)
            try:self.save()
            except Exception:
                if saved is not None:self.data['sessions'][session_id]=saved
                raise
            self._remove_session_files(session_id)
    def _remove_session_files(self,session_id):
        for view in (False,True):
            try:self._session_path(session_id,view).unlink(missing_ok=True)
            except OSError:pass  # Removed from index atomically; leftovers cannot resume.
    def provider(self):
        from .ai import provider_for
        return provider_for(self.data['model'])
    def provider_label(self):
        from .ai import PROVIDERS
        return PROVIDERS[self.provider()]
    def selected_model(self,provider):
        from .ai import model_id,DEFAULT_MODELS
        if provider==self.provider():return model_id(self.data['model'])
        value=self.data['ai_models'].get(provider,DEFAULT_MODELS[provider])
        return value if isinstance(value,str) and value.strip() else DEFAULT_MODELS[provider]
    def select_provider(self,provider,model):
        from .ai import model_token
        previous=self.provider()
        self.data['ai_models'][previous]=self.selected_model(previous)
        self.data['ai_models'][provider]=model
        self.data['model']=model_token(provider,model)
    def _key_provider(self,provider):
        from .ai import PROVIDERS
        provider=provider or self.provider()
        if provider not in PROVIDERS:raise ValueError('Choose a supported AI provider.')
        return provider
    def _key_path(self,provider):
        return self.path/('key.dpapi' if provider=='gemini' else 'key-'+provider+'.dpapi')
    def get_key(self,provider=None):
        provider=self._key_provider(provider)
        value=self.session_key if provider=='gemini' else self.session_keys.get(provider,'')
        if value:return value
        from .ai import KEY_ENV
        env=os.environ.get(KEY_ENV[provider],'').strip()
        if env:return env
        file=self._key_path(provider)
        if os.name=='nt' and file.exists():
            try:return dpapi(file.read_bytes(),False).decode()
            except Exception:return ''
        return ''
    def get_model_key(self,model):
        from .ai import provider_for
        return self.get_key(provider_for(model))
    def set_key(self,key,persist=False,provider=None):
        provider=self._key_provider(provider);key=key.strip()
        if any(ord(ch)<33 or ord(ch)>126 for ch in key):raise ValueError('The API key must be a single line without spaces or invalid characters.')
        from .ai import KEY_ENV
        env=KEY_ENV[provider]
        if persist and os.name!='nt':raise ValueError(f'Persistent key storage is available on Windows. Use a session key or {env} on this system.')
        file=self._key_path(provider)
        if persist and key:self._atomic(file,dpapi(key.encode(),True))
        elif file.exists():file.unlink()
        if provider=='gemini':self.session_key=key
        else:self.session_keys[provider]=key
    def forget_key(self,provider=None):
        provider=self._key_provider(provider)
        if provider=='gemini':self.session_key=''
        else:self.session_keys.pop(provider,None)
        self._key_path(provider).unlink(missing_ok=True)

def dpapi(data,protect):
    from ctypes import wintypes
    class Blob(ctypes.Structure): _fields_=[('size',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]
    buffer=ctypes.create_string_buffer(data); source=Blob(len(data),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte))); dest=Blob()
    api=ctypes.WinDLL('crypt32',use_last_error=True); kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    fn=api.CryptProtectData if protect else api.CryptUnprotectData
    fn.argtypes=[ctypes.POINTER(Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)]
    fn.restype=wintypes.BOOL; kernel.LocalFree.argtypes=[ctypes.c_void_p]; kernel.LocalFree.restype=ctypes.c_void_p
    if not fn(ctypes.byref(source),None,None,None,None,1,ctypes.byref(dest)): raise OSError('Windows could not protect or unlock this key.')
    try: return ctypes.string_at(dest.data,dest.size)
    finally: kernel.LocalFree(ctypes.cast(dest.data,ctypes.c_void_p))
