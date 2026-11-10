"""Bounded real WebEngine/controller regression for revealed mode transitions.

Synthetic cards, fake Gemini responses and native reveal/rating spies only.
"""
from concurrent.futures import Future
from pathlib import Path
import importlib
import json
import os
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl,Qt,QPoint
    from PyQt6.QtGui import QKeySequence,QShortcut
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtTest import QTest
    from test_live_review import Environment,Card
    controller=importlib.import_module('cram_studio.live_review')
    app=QApplication(['cram-mode-transition-qa']);web=ROOT/'cram_studio/web'
    out=Path(os.environ.get('CRAM_MODES_OUTPUT',str(ROOT/'../../tmp/cram208-modes'))).resolve();out.mkdir(parents=True,exist_ok=True)
    class Page(QWebEnginePage):
        def __init__(self,parent):super().__init__(parent);self.errors=[];self.callback=lambda *_:None
        def javaScriptConsoleMessage(self,level,message,line,source):
            if message.startswith('BRIDGE:'):QTimer.singleShot(0,lambda:self.callback(message[7:]))
            elif 'Error' in str(level):self.errors.append(message)
    def wait(ms=70):
        loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(code):
        loop=QEventLoop();box=[];page.runJavaScript(code,lambda value:(box.append(value),loop.quit()));QTimer.singleShot(3000,loop.quit);loop.exec()
        assert box,'JavaScript timed out'
        return box[0]
    temporary=tempfile.TemporaryDirectory();fixture=Environment(temporary.name,True,False)
    view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1360,900);view.show()
    view.eval=lambda code:js(code);fixture.mw.reviewer.web=view
    fixture.mw.reviewer.card=Card(kind='Cloze')
    fixture.mw.reviewer.card.fields[:]=['<b>ETHERNET MAC ADDRESS</b><br>A MAC address is {{c1::48 bits}} long, expressed as {{c1::12 hexadecimal digits}} or {{c1::6 bytes}}.','']
    fixture.live.store.set_key('test-key');fixture.live.store.data['preferences'].update(live_generate=True,live_generate_configured=True)
    class Client:
        def __init__(self,*args):pass
        def generate(self,jobs):
            wrong={'48 bits':['32 bits','64 bits','128 bits'],'12 hexadecimal digits':['8 hexadecimal digits','16 hexadecimal digits','24 hexadecimal digits'],'6 bytes':['4 bytes','8 bytes','16 bytes']}
            return {job['id']:wrong[job['answer']] for job in jobs}
    original=controller.Gemini;controller.Gemini=Client
    fixture.live.begin('flash');markup=fixture.packet();card=fixture.mw.reviewer.card;deck=dict(fixture.col.deck)
    reveals=[];ratings=[];bridge_errors=[]
    def remount(kind):
        markup=fixture.packet(kind);js('document.querySelector("#qa").innerHTML='+json.dumps(markup)+';cramNative.mount();')
    def route(message):
        try:
            if message.startswith('cram_live:'):fixture.live.message((False,None),message,fixture.mw.reviewer)
            elif message=='ans':reveals.append(card.id);remount('reviewAnswer')
            else:bridge_errors.append(message)
        except Exception as error:bridge_errors.append(str(error))
    page.callback=route
    head=''.join('<link rel="stylesheet" href="'+name+'">' for name in ['live.css','appearance.css','writing.css'])
    head+='<script>window.pycmd=message=>console.log("BRIDGE:"+message);</script>'
    head+=''.join('<script defer src="'+name+'"></script>' for name in ['appearance.js','writing.js','live.js'])
    markup='<!doctype html><html><head>'+head+'</head><body><div id="qa">'+markup+'</div><script>addEventListener("load",()=>cramNative.mount());</script></body></html>'
    loop=QEventLoop();loaded=[];view.loadFinished.connect(lambda ok:(loaded.append(ok),loop.quit()));view.setHtml(markup,QUrl.fromLocalFile(str(web)+'/'));QTimer.singleShot(4000,loop.quit);loop.exec()
    assert loaded and loaded[0];wait()
    rating=QShortcut(QKeySequence('1'),view);rating.activated.connect(lambda:ratings.append('Again'))
    def mode(name):
        js('document.querySelector("[data-live-action=settings]").click();document.querySelector("[data-live-mode='+name+']").click()');wait()
    def click_card():
        box=js('(()=>{const r=document.querySelector(".cl-flip").getBoundingClientRect();return {x:r.x+30,y:r.y+30};})()')
        QTest.mouseClick(view.focusProxy() or view,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,QPoint(round(box['x']),round(box['y'])));wait(110)
    click_card();assert reveals==[card.id] and fixture.live.current['side']=='answer',(reveals,bridge_errors)
    mode('exam');assert fixture.live.current['display']=='exam' and len(fixture.background)==1
    assert js('!!document.querySelector(".cl-exam")&&!document.querySelector(".cl-flip")')
    assert js('document.querySelector("#cl-notice").textContent').startswith('Preparing choices')
    js('document.querySelector(".cl-clue").click();document.querySelector(".cl-clue").click()');wait()
    assert reveals==[card.id] and not ratings
    wait(200);view.grab().save(str(out/'anki-revealed-choices-loading.png'))
    work,done=fixture.background[0];future=Future();future.set_result(work());done(future);wait()
    assert js('document.querySelectorAll(".cl-choice").length')==12
    assert js('[...document.querySelectorAll(".cl-choice")].every(n=>n.disabled)')
    assert js('document.querySelectorAll(".cl-choice.correct").length')==3
    assert not js('!!document.querySelector(".cl-flip,.cl-feedback")')
    js('cramNative.moveBlank(1)');assert js('document.querySelector(".cl-slot:not([hidden]) .cl-slot-label").textContent')=='Blank 2 / 3'
    wait(200);view.grab().save(str(out/'anki-revealed-choices-ready.png'))
    mode('write');assert js('document.querySelector(".write-progress").textContent')=='3 / 3 revealed'
    assert fixture.live.current['writing_state']['accepted']==[]
    assert js('document.querySelector(".write-input").readOnly')
    wait(200);view.grab().save(str(out/'anki-revealed-writing.png'))
    for name in ('flash','exam','write','exam'):
        mode(name);assert fixture.live.current['side']=='answer'
        assert fixture.mw.reviewer.card is card and fixture.col.deck==deck
        if name=='exam':assert js('document.querySelectorAll(".cl-choice").length')==12 and not js('!!document.querySelector(".cl-flip")')
    assert len(fixture.background)==1 and reveals==[card.id] and ratings==[]
    # A partial Writing attempt stays partial in stored history, even though a
    # subsequent Flashcards reveal makes all three answers visible in every view.
    fixture.mw.reviewer.card.id=2;fixture.live.mode='write';fixture.live.auto_generate=False;remount('reviewQuestion');wait()
    js('(()=>{const i=document.querySelector(".write-input");i.value="48 bits";i.dispatchEvent(new Event("input",{bubbles:true}));i.dispatchEvent(new KeyboardEvent("keydown",{key:"Enter",bubbles:true,cancelable:true}));})()');wait()
    assert fixture.live.current['writing_state']['accepted']==[0] and fixture.live.current['side']=='question'
    mode('flash');click_card();mode('exam');assert js('document.querySelectorAll(".cl-choice").length')==12
    mode('write');assert js('document.querySelector(".write-progress").textContent')=='3 / 3 revealed'
    assert fixture.live.current['writing_state']['accepted']==[0]
    assert fixture.live.current['writing_events']==[{'text':'48 bits','target':0}]
    assert fixture.calls==['study'] and fixture.live.store.data['history']==[] and ratings==[]
    view.activateWindow();view.setFocus();QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_1);wait()
    assert ratings==['Again'],'native ratings still require an explicit rating key'
    assert not bridge_errors and not page.errors,(bridge_errors,page.errors)
    controller.Gemini=original;fixture.live.close();temporary.cleanup();view.close();view.deleteLater()
    print(json.dumps({'revealed_transitions':'passed','uncached_and_cached_choices':'passed','late_background_choices':'passed','partial_writing_history':'passed','explicit_rating_only':'passed','output':str(out)}))
    app.quit()

if __name__=='__main__':main()
