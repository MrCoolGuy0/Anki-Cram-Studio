"""Bounded real Qt widget checks using the actual AISettings class, synthetic APIs."""
def main():
    import ast
    import copy
    from concurrent.futures import Future
    import importlib
    import json
    import os
    from pathlib import Path
    import sys
    import tempfile
    import types
    from unittest.mock import patch
    from PyQt6 import QtWidgets
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest
    root=Path(__file__).resolve().parents[1]
    if 'cram_studio' not in sys.modules:
        package=types.ModuleType('cram_studio');package.__path__=[str(root/'cram_studio')];sys.modules['cram_studio']=package
    ai=importlib.import_module('cram_studio.ai');Store=importlib.import_module('cram_studio.storage').Store
    from test_core import FakeResponse
    app=QtWidgets.QApplication.instance() or QtWidgets.QApplication(['provider-settings-qa'])
    pending=[];calls=[]
    def opener(req,timeout):
        calls.append(req.full_url)
        if req.full_url=='https://api.x.ai/v1/responses':
            assert req.get_header('Authorization')=='Bearer xai-fixture'
            body=json.loads(req.data);identity=json.loads(body['input'][1]['content'].split('DATA:\n',1)[1])[0]['id']
            return FakeResponse({'status':'completed','output':[{'type':'message','role':'assistant','content':[
                {'type':'output_text','text':json.dumps({'sets':[{'id':identity,'answer_aliases':[],'wrong':['Lyon','Nice','Bordeaux']}]})}]}]})
        assert req.full_url=='https://api.groq.com/openai/v1/chat/completions'
        assert req.get_header('Authorization')=='Bearer groq-fixture'
        body=json.loads(req.data);identity=json.loads(body['messages'][1]['content'].split('DATA:\n',1)[1])[0]['id']
        return FakeResponse({'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'sets':[{'id':identity,'answer_aliases':[],'wrong':['Lyon','Nice','Bordeaux']}]})}}]})
    def factory(key,model):return ai.client(key,model,opener)
    def network(mw,work,done):pending.append((work,done))
    scope={name:getattr(QtWidgets,name) for name in dir(QtWidgets) if name.startswith('Q')}
    scope.update(os=os,copy=copy,Gemini=factory,PROVIDERS=ai.PROVIDERS,DEFAULT_MODELS=ai.DEFAULT_MODELS,KEY_ENV=ai.KEY_ENV,KEY_URLS=ai.KEY_URLS,KEY_CONSOLES=ai.KEY_CONSOLES,model_token=ai.model_token,run_network=network)
    node=next(n for n in ast.parse((root/'cram_studio/dialog.py').read_text()).body if isinstance(n,ast.ClassDef) and n.name=='AISettings')
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-AI-settings>','exec'),scope)
    Settings=scope['AISettings']
    with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True):
        owner=QtWidgets.QWidget();owner.store=Store(folder);owner.closed=False;owner.mw=object()
        owner.store.data['model']='gemini-legacy';owner.store.set_key('gemini-fixture');owner.store.save()
        dlg=Settings(owner);dlg.show();app.processEvents()
        assert dlg.provider.currentData()=='gemini' and dlg.model.currentText()=='gemini-legacy'
        dlg.provider.setCurrentIndex(dlg.provider.findData('groq'));app.processEvents()
        assert dlg.model.currentText()=='openai/gpt-oss-20b'
        assert 'Paste your Groq' in dlg.key.placeholderText()
        dlg.key.setText('groq-fixture');dlg.model.setCurrentText('openai/gpt-oss-120b')
        dlg.provider.setCurrentIndex(dlg.provider.findData('gemini'))
        assert dlg.key.text()=='' and dlg.model.currentText()=='gemini-legacy'
        dlg.provider.setCurrentIndex(dlg.provider.findData('groq'))
        assert dlg.key.text()=='groq-fixture' and dlg.model.currentText()=='openai/gpt-oss-120b'
        QTest.mouseClick(dlg.test,Qt.MouseButton.LeftButton);app.processEvents()
        assert dlg.checking and not dlg.provider.isEnabled()
        assert not dlg.buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Save).isEnabled()
        work,done=pending.pop();future=Future();future.set_result(work());done(future)
        assert not dlg.checking and dlg.provider.isEnabled() and 'Connected.' in dlg.status.text()
        assert owner.store.data['model']=='gemini-legacy','Test must not save or change provider'
        app.processEvents();out=root/'qa';out.mkdir(exist_ok=True)
        assert dlg.grab().save(str(out/'ai-settings-groq.png'))
        dlg.save();assert dlg.result()==QtWidgets.QDialog.DialogCode.Accepted
        assert owner.store.data['model']=='groq:openai/gpt-oss-120b'
        assert owner.store.get_key()=='groq-fixture' and owner.store.get_key('gemini')=='gemini-fixture'
        second=Settings(owner);assert second.active=='groq' and 'already available' in second.key.placeholderText()
        second.provider.setCurrentIndex(second.provider.findData('gemini'));second.save()
        assert owner.store.data['model']=='gemini-legacy' and owner.store.get_key()=='gemini-fixture'
        third=Settings(owner);third.provider.setCurrentIndex(third.provider.findData('groq'));third.forget()
        assert not owner.store.get_key('groq') and owner.store.get_key('gemini')=='gemini-fixture'
        third.reject();assert owner.store.data['model']=='gemini-legacy'
        final=Settings(owner);final.provider.setCurrentIndex(final.provider.findData('groq'));final.key.setText('groq-fixture')
        final.network(False);work,done=pending.pop();final.reject()
        future=Future();future.set_result(work());done(future)
        assert final.closed and owner.store.data['model']=='gemini-legacy'
        grok=Settings(owner);grok.provider.setCurrentIndex(grok.provider.findData('grok'));grok.show();app.processEvents()
        assert grok.model.currentText()=='grok-4.7' and 'Cursor' in grok.info.text()
        assert 'console.x.ai' in grok.info.text() and 'XAI_API_KEY' in grok.key_note.text()
        grok.key.setText('xai-fixture');grok.network(False);work,done=pending.pop()
        future=Future();future.set_result(work());done(future);assert 'Connected.' in grok.status.text()
        assert grok.grab().save(str(out/'ai-settings-grok.png'))
        grok.save();assert owner.store.data['model']=='grok:grok-4.7'
        assert owner.store.get_key()=='xai-fixture' and owner.store.get_key('gemini')=='gemini-fixture'
        reopen=Settings(owner);assert reopen.active=='grok' and reopen.model.currentText()=='grok-4.7'
        reopen.provider.setCurrentIndex(reopen.provider.findData('gemini'));assert reopen.model.currentText()=='gemini-legacy'
        reopen.reject()
        for widget in (dlg,second,third,final,grok,reopen,owner):widget.close()
        app.processEvents()
    assert len(calls)==3
    print('Real Qt AI Settings passed: provider/key/model isolation, switching drafts, test-before-save, pending controls, reopen, forget and late callback after Cancel. No live API or user collection.')


if __name__=='__main__':main()
