"""Bounded real Chromium mouse/focus/remount regression; synthetic cards only."""
from pathlib import Path
import json
import os
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu --disable-dev-shm-usage')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl,Qt,QPoint
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    observe='--observe-baseline' in sys.argv
    app=QApplication(['choice-stability-qa']);web=ROOT/'cram_studio/web';results=[]
    class Page(QWebEnginePage):
        def __init__(self,parent):super().__init__(parent);self.errors=[];self.calls=[]
        def javaScriptConsoleMessage(self,level,message,line,source):
            if message.startswith('BRIDGE:'):self.calls.append(message[7:])
            elif 'Error' in str(level):self.errors.append(message)
    def wait(ms=35):loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(page,code):
        box=[];loop=QEventLoop();page.runJavaScript(code,lambda value:(box.append(value),loop.quit()))
        QTimer.singleShot(2500,loop.quit);loop.exec();assert box,'JavaScript timed out';return box[0]
    for mode in ('main','anki'):
        view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1100,850);view.show()
        question={'id':'stable','kind':'cloze','mode':'exam','deck':'Synthetic', 'ready':True,
            'clue':'Which option completes <span class="ct-blank" data-blank="0">_____</span>?',
            'slots':[{'number':1,'answer':'Correct','answer_html':'Correct','correct':3,
                'choices':['Option '+str(i+1)+': '+('Long answer content to exercise the choices scroll pane. '*5) for i in range(4)]}]}
        prefix='cl-' if mode=='anki' else ''
        head=''.join('<link rel="stylesheet" href="'+name+'">' for name in (['app.css'] if mode=='main' else ['live.css'])+['appearance.css'])
        # Model a generic theme/add-on hover animation: Cram choices must opt out.
        head+='<style>@keyframes theme-fade{0%,70%{opacity:0}100%{opacity:1}}button:hover{animation:theme-fade 1.5s!important;transform:scale(.97)!important;transition:all 1.5s!important}.choices:hover,.cl-choices:hover{animation:theme-fade 1.5s!important}button:hover .cl-choice-text,button:hover .choice-text{opacity:0!important;animation:theme-fade 1.5s!important}button:hover::before{content:""!important;position:absolute;inset:0;background:white;animation:theme-fade 1.5s!important}.choices,.cl-choices{grid-template-columns:1fr!important}</style>'
        head+='<script>window.pycmd=x=>console.log("BRIDGE:"+x);</script>'
        head+=''.join('<script defer src="'+name+'"></script>' for name in ['appearance.js','app.js' if mode=='main' else 'live.js'])
        body='<div id="cram-app"></div><div id="toast"></div>' if mode=='main' else '<div id="qa"></div><div id="native-ratings">Again Hard Good Easy</div>'
        loaded=[];loop=QEventLoop();view.loadFinished.connect(lambda ok:(loaded.append(ok),loop.quit()))
        view.setHtml('<!doctype html><html><head>'+head+'</head><body>'+body+'</body></html>',QUrl.fromLocalFile(str(web)+'/'));QTimer.singleShot(3500,loop.quit);loop.exec();assert loaded and loaded[0];wait()
        if mode=='main':
            cat={'decks':[{'id':'1','name':'Synthetic','count':1}],'current':'1','history':[],'settings':{},'preferences':{},'media':'','dark':False}
            js(page,'cram.receive("bootstrap",'+json.dumps(cat)+');cram.receive("session",'+json.dumps({'questions':[question]})+');')
            choice='.choice';pane='.choice-section';packet=None
        else:
            packet={'cid':'1','epoch':1,'card_epoch':1,'side':'question','mode':'exam','display':'exam','question':{**question,'ready':False},'text_zoom':1}
            raw=json.dumps(packet).replace('&','&amp;').replace('"','&quot;').replace('<','&lt;')
            markup='<section id="cram-live" data-packet="'+raw+'"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>'
            js(page,'document.querySelector("#qa").innerHTML='+json.dumps(markup)+';cramNative.mount();')
            js(page,'cramNative.receive('+json.dumps({**packet,'question':question})+');')
            choice='.cl-choice';pane='.cl-answers'
        wait();js(page,'window.stableNodes=Array.from(document.querySelectorAll('+json.dumps(choice)+'));window.stablePane=document.querySelector('+json.dumps(pane)+');stablePane.scrollTop=stablePane.scrollHeight;')
        before=js(page,'stablePane.scrollTop');assert before>20,'Fixture must overflow choices'
        point=js(page,'(()=>{const r=stableNodes[3].getBoundingClientRect(),p=stablePane.getBoundingClientRect();return {x:(r.left+r.right)/2,y:(Math.max(r.top,p.top)+Math.min(r.bottom,p.bottom))/2};})()')
        target=QPoint(round(point['x']),round(point['y']));surface=view.focusProxy() or view
        for offset in (0,1,-1,0):QTest.mouseMove(surface,target+QPoint(offset,0));wait(20)
        hover=js(page,'(()=>{const c=getComputedStyle(stableNodes[3]);return {animation:c.animationName,opacity:c.opacity,transform:c.transform};})()')
        layers=js(page,'(()=>{const n=stableNodes[3],text=n.querySelector(".cl-choice-text,.choice-text");return {textOpacity:getComputedStyle(text).opacity,textAnimation:getComputedStyle(text).animationName,panelAnimation:getComputedStyle(n.parentElement).animationName,overlay:getComputedStyle(n,"::before").content};})()')
        QTest.mousePress(surface,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,target);wait()
        after=js(page,'stablePane.scrollTop');QTest.mouseRelease(surface,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,target);wait()
        picks=js(page,'cram.state.picks[0]' if mode=='main' else 'cramNative.state.picks')
        metrics={'mode':mode,'scroll_before':before,'scroll_after_focus':after,'picked':picks,'hover':hover,'hover_layers':layers}
        if not observe:
            assert abs(before-after)<1,metrics
            assert picks==[3],metrics
            assert hover=={'animation':'none','opacity':'1','transform':'none'},metrics
            assert layers=={'textOpacity':'1','textAnimation':'none','panelAnimation':'none','overlay':'none'},metrics
        if mode=='anki':
            js(page,'window.appearanceCalls=0;window.originalAppearance=cramAppearance.apply;cramAppearance.apply=(...args)=>{appearanceCalls++;return originalAppearance(...args);};')
            for i in range(8):
                js(page,'document.body.classList.toggle("other-addon-hover");');wait(5)
            mutations=js(page,'appearanceCalls');metrics['unrelated_class_repaints']=mutations
            if not observe:assert mutations==0,metrics
            # A genuine light/dark switch still reapplies the current palette.
            js(page,'document.body.classList.add("nightMode");');wait()
            theme_calls=js(page,'appearanceCalls');metrics['theme_repaints']=theme_calls
            if not observe:assert theme_calls==1,metrics
            js(page,'document.body.classList.remove("nightMode");');wait()
            changed={**packet,'question':question,'appearance':{'colors':{'light':{'exam':{'card':'#eeddee'}}}}}
            js(page,'cramNative.receive('+json.dumps(changed)+');');wait()
            customized=js(page,'appearanceCalls');metrics['customization_repaints']=customized-theme_calls-1
            if not observe:assert customized==theme_calls+2,metrics
            js(page,'cramNative.receive('+json.dumps(changed)+');');wait()
            if not observe:assert js(page,'appearanceCalls')==customized,'Same status/config must not repaint'
            count=len(page.calls);js(page,'cramNative.mount();cramNative.mount();');wait()
            remount=js(page,'({count:document.querySelectorAll(".cl-choice").length,same:stableNodes.every((n,i)=>n===document.querySelectorAll(".cl-choice")[i]),picks:cramNative.state.picks,ready:cramNative.state.packet.question.ready})')
            metrics['repeat_mount']=remount;metrics['extra_bridge_calls']=len(page.calls)-count
            if not observe:
                assert remount=={'count':4,'same':True,'picks':[3],'ready':True},metrics
                assert len(page.calls)==count,'Repeat mount must not request choices again'
            # Explicit regeneration still replaces options once and clears picks.
            fresh={**packet,'question':question,'choices_revision':1}
            js(page,'cramNative.receive('+json.dumps(fresh)+');')
            if not observe:assert js(page,'stableNodes[0]!==document.querySelector(".cl-choice")&&cramNative.state.picks.length===0')
        assert not page.errors,page.errors;results.append(metrics);view.close();view.deleteLater();wait()
    print(json.dumps(results,indent=2))
    if not observe:print('Real Qt choice stability passed: native mouse/focus, scroll preservation, hover isolation, stable ready remount, picks and explicit regeneration.')


if __name__=='__main__':main()
