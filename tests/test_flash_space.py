"""Real Qt Space/ratings regression with separate card and bottom WebViews.

Synthetic cards and native callback spies; no Anki collection or scheduler.
"""
from pathlib import Path
import json
import os
import sys
import tempfile
import types

ROOT=Path(__file__).resolve().parents[1]

def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl,Qt,QObject,QEvent
    from PyQt6.QtGui import QKeySequence,QShortcut
    from PyQt6.QtWidgets import QApplication,QWidget,QVBoxLayout
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtTest import QTest
    from test_live_review import Environment,Card
    app=QApplication(['flash-space-qa']);web=ROOT/'cram_studio/web'
    aq=types.ModuleType('aqt');qt=types.ModuleType('aqt.qt');qt.QObject=QObject;qt.QEvent=QEvent;qt.Qt=Qt;aq.qt=qt
    sys.modules['aqt']=aq;sys.modules['aqt.qt']=qt
    class Page(QWebEnginePage):
        def __init__(self,parent):super().__init__(parent);self.errors=[];self.callback=lambda *_:None
        def javaScriptConsoleMessage(self,level,message,line,source):
            if message.startswith('BRIDGE:'):QTimer.singleShot(0,lambda:self.callback(message[7:]))
            elif 'Error' in str(level):self.errors.append(message)
    def wait(ms=85):
        loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(page,code):
        loop=QEventLoop();box=[];page.runJavaScript(code,lambda value:(box.append(value),loop.quit()));QTimer.singleShot(3000,loop.quit);loop.exec();assert box,'JavaScript timeout';return box[0]
    def load(view,markup):
        loop=QEventLoop();done=[]
        def finished(ok):done.append(ok);loop.quit()
        view.loadFinished.connect(finished);view.setHtml(markup,QUrl.fromLocalFile(str(web)+'/'));QTimer.singleShot(4000,loop.quit);loop.exec();view.loadFinished.disconnect(finished)
        assert done and done[0];wait()
    temporary=tempfile.TemporaryDirectory();fixture=Environment(temporary.name,True,False)
    window=QWidget();layout=QVBoxLayout(window);top=QWebEngineView();bottom=QWebEngineView();bottom.setFixedHeight(90);layout.addWidget(top);layout.addWidget(bottom);window.resize(1360,900);window.show()
    page=Page(top);top.setPage(page);bottom_page=Page(bottom);bottom.setPage(bottom_page)
    top.eval=lambda code:js(page,code);bottom.eval=lambda code:js(bottom_page,code)
    fixture.mw.reviewer.web=top;fixture.mw.bottomWeb=bottom
    fixture.mw.reviewer.card=Card(kind='Cloze');fixture.mw.reviewer.card.fields[:]=['A {{c1::cell}} forms {{c1::tissue}}.','']
    reveals=[];ratings=[];original_space=[];errors=[]
    def remount(kind):
        markup=fixture.packet(kind);js(page,'document.querySelector("#qa").innerHTML='+json.dumps(markup)+';cramNative.mount();')
    def native_space():
        original_space.append(fixture.mw.reviewer.state)
        if fixture.mw.reviewer.state=='question':reveals.append('native');remount('reviewAnswer')
        else:ratings.append('native Space')
    def route(message):
        try:
            if message.startswith('cram_live:'):fixture.live.message((False,None),message,fixture.mw.reviewer)
            elif message=='ans':reveals.append('ans');remount('reviewAnswer')
            elif message.startswith('ease'):ratings.append(message)
            else:errors.append(message)
        except Exception as error:errors.append(str(error))
    page.callback=route;bottom_page.callback=route
    fixture.live.begin('flash');markup=fixture.packet();card=fixture.mw.reviewer.card;deck=dict(fixture.col.deck)
    head=''.join('<link rel="stylesheet" href="'+name+'">' for name in ['live.css','appearance.css','writing.css'])
    head+='<script>window.pycmd=m=>console.log("BRIDGE:"+m);</script>'+''.join('<script defer src="'+name+'"></script>' for name in ['appearance.js','writing.js','live.js'])
    load(top,'<!doctype html><html><head>'+head+'</head><body><div id="qa">'+markup+'</div><script>addEventListener("load",()=>cramNative.mount());</script></body></html>')
    load(bottom,'<html><body><script>window.pycmd=m=>console.log("BRIDGE:"+m);</script><div id="ratings">'+''.join('<button id="rate'+str(i)+'" onclick="pycmd(\'ease'+str(i)+'\')">'+text+'</button>' for i,text in enumerate(['Again 1m','Hard 6m','Good 10m','Easy 4d'],1))+'</div></body></html>')
    callbacks=[(' ',native_space)]+[(str(i),lambda i=i:ratings.append(str(i))) for i in range(1,5)]
    fixture.live.shortcuts('review',callbacks);shortcuts=[]
    for key,callback in callbacks:
        shortcut=QShortcut(QKeySequence(key),window);shortcut.setAutoRepeat(False);shortcut.activated.connect(callback);shortcuts.append(shortcut)
    def focus(view):window.activateWindow();view.setFocus();wait(35)
    def press(view,key=Qt.Key.Key_Space):QTest.keyClick(view.focusProxy() or view,key);wait(95)
    def flipped():return js(page,'document.querySelector(".cl-flip").classList.contains("is-flipped")')
    focus(top);press(top);assert reveals==['ans'] and fixture.live.current['side']=='answer',(reveals,original_space,errors)
    wait(90);assert flipped()
    js(bottom_page,'window.originalRatings=document.querySelector("#ratings");')
    for _ in range(6):
        before=flipped();press(top);assert flipped()!=before
        assert ratings==[] and original_space==[] and fixture.live.current['side']=='answer'
    # Focus a native rating button in the other WebView: Space still flips.
    focus(bottom);js(bottom_page,'document.querySelector("#rate3").focus()')
    for _ in range(3):
        before=flipped();press(bottom);assert flipped()!=before
        assert ratings==[] and original_space==[],(ratings,original_space)
    assert js(bottom_page,'originalRatings===document.querySelector("#ratings")&&originalRatings.querySelectorAll("button").length===4')
    assert fixture.mw.reviewer.card is card and fixture.col.deck==deck and fixture.calls==['study']
    # Explicit ratings remain native, even while the clue side is showing.
    if flipped():press(bottom)
    for key in (Qt.Key.Key_1,Qt.Key.Key_2,Qt.Key.Key_3,Qt.Key.Key_4):press(bottom,key)
    assert ratings==['1','2','3','4'];ratings.clear()
    def mode(name):
        js(page,'document.querySelector("[data-live-action=settings]").click();document.querySelector("[data-live-mode='+name+']").click()');wait()
    mode('exam');focus(top);press(top);assert ratings==['native Space'] and original_space==['answer']
    # Writing keeps literal spaces in its focused input.
    mode('write');fixture.mw.reviewer.card.id=2;remount('reviewQuestion');wait();focus(top)
    js(page,'document.querySelector(".write-input").focus()');QTest.keyClicks(top.focusProxy() or top,'two words');wait()
    assert js(page,'document.querySelector(".write-input").value')=='two words'
    assert original_space==['answer']
    # Leaving the add-on restores the original native shortcut path.
    fixture.state('overview');fixture.mw.state='review';fixture.mw.reviewer.state='answer'
    load(top,'<html><body>Ordinary Anki review</body></html>');focus(top);press(top)
    assert original_space==['answer','answer'] and ratings==['native Space','native Space']
    assert not errors and not page.errors and not bottom_page.errors,(errors,page.errors,bottom_page.errors)
    fixture.live.close();temporary.cleanup();window.close();window.deleteLater();wait(20)
    print(json.dumps({'qt_space_checks':'passed','card_and_rating_webviews':'passed','explicit_1_to_4_ratings':'passed','mcq_and_writing_unchanged':'passed','ordinary_anki_restored':'passed'}))
    app.quit()

if __name__=='__main__':main()
