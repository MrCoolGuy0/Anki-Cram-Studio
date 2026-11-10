"""Real Qt mouse/copy regression: clicks flip and text drags select only."""
from pathlib import Path
import html
import json
import os

ROOT=Path(__file__).resolve().parents[1]

def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl,Qt,QPoint
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtTest import QTest
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    app=QApplication(['flashcard-pointer-qa']);web=ROOT/'cram_studio/web'
    class Page(QWebEnginePage):
        def __init__(self,parent):super().__init__(parent);self.errors=[];self.calls=[];self.callback=lambda *_:None
        def javaScriptConsoleMessage(self,level,message,line,source):
            if message.startswith('BRIDGE:'):
                self.calls.append(message[7:]);QTimer.singleShot(0,lambda:self.callback(message[7:]))
            elif 'Error' in str(level):self.errors.append(message)
    def wait(ms=50):
        loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(page,code):
        loop=QEventLoop();box=[];page.runJavaScript(code,lambda v:(box.append(v),loop.quit()));QTimer.singleShot(3000,loop.quit);loop.exec();assert box
        return box[0]
    scenes=[]
    for mode in ('main','anki'):
        for kind in ('basic','cloze'):
            view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1360,900);view.show();view.activateWindow();view.setFocus()
            answer='A calm explorer tests click and drag.'
            clue='<span>Click this text near its letters.</span>' if kind=='basic' else 'Recall <span class="ct-blank" data-blank="0">_____</span> from this sentence.'
            q={'id':'pointer','kind':kind,'mode':'flash','deck':'Pointer QA','clue':clue,'slots':[{'number':1,'answer':answer,'answer_html':answer}]}
            head=''.join('<link rel="stylesheet" href="'+name+'">' for name in (['app.css'] if mode=='main' else ['live.css'])+['appearance.css'])
            # Animation is covered separately; stable faces isolate mouse hit tests.
            head+='<style>.cl-turn,.flash-turn{transition:none!important}</style><script>window.pycmd=x=>console.log("BRIDGE:"+x);</script>'
            head+=''.join('<script defer src="'+name+'"></script>' for name in ['appearance.js','app.js' if mode=='main' else 'live.js'])
            if mode=='main':
                body='<div id="cram-app"></div><div id="toast"></div>'
                boot={'decks':[{'id':'1','name':'Pointer QA','count':1}],'current':'1','history':[],'settings':{},'dark':False,'media':QUrl.fromLocalFile(str(web)+'/').toString(),'preferences':{'auto_advance':False}}
                init='cram.receive("bootstrap",'+json.dumps(boot)+');cram.receive("session",'+json.dumps({'questions':[q]})+');'
            else:
                packet={'cid':'1','epoch':1,'side':'question','display':'flash','question':q}
                body='<section id="cram-live" data-packet="'+html.escape(json.dumps(packet),quote=True)+'"><div id="cl-stage"><div id="cl-original"></div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>'
                init='cramNative.mount();'
                def route(message):
                    if message=='ans':
                        packet['side']='answer';js(page,'document.querySelector("#cram-live").dataset.packet='+json.dumps(json.dumps(packet))+';cramNative.mount();')
                page.callback=route
            loop=QEventLoop();loaded=[];view.loadFinished.connect(lambda ok:(loaded.append(ok),loop.quit()))
            view.setHtml('<!doctype html><html><head>'+head+'</head><body>'+body+'<script>addEventListener("load",()=>{'+init+'});</script></body></html>',QUrl.fromLocalFile(str(web)+'/'))
            QTimer.singleShot(4000,loop.quit);loop.exec();assert loaded and loaded[0];wait(120)
            card='.flash-card' if mode=='main' else '.cl-flip'
            def flipped():return js(page,'document.querySelector('+json.dumps(card)+').classList.contains("is-flipped")')
            def point(offset=1):
                root=('#answer .face-content' if flipped() else '#clue-face .face-content') if mode=='main' else ('.cl-back .cl-flash-content' if flipped() else '.cl-front .cl-flash-content')
                p=js(page,"""(()=>{const root=document.querySelector(%s),walker=document.createTreeWalker(root,4),nodes=[];let n;while(n=walker.nextNode())if(n.textContent.trim().length>8)nodes.push(n);n=nodes.find(n=>n.textContent.includes('A calm'))||nodes[0];const i=Math.min(%s,n.textContent.length-2),r=document.createRange();r.setStart(n,i);r.setEnd(n,i+1);const b=r.getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2};})()"""%(json.dumps(root),offset))
                return QPoint(round(p['x']),round(p['y']))
            target=view.focusProxy() or view
            QTest.mouseClick(target,Qt.MouseButton.LeftButton,pos=point());wait(120)
            assert flipped(),(mode,kind,'text click did not flip')
            assert js(page,'getSelection().toString()')=='',(mode,kind,'stationary click selected text')
            # A real held mouse drag makes a native range and never flips on release.
            start,end=point(1),point(25);state=flipped()
            QTest.mousePress(target,Qt.MouseButton.LeftButton,pos=start)
            for i in range(1,9):QTest.mouseMove(target,QPoint(start.x()+(end.x()-start.x())*i//8,start.y()+(end.y()-start.y())*i//8));wait(8)
            QTest.mouseRelease(target,Qt.MouseButton.LeftButton,pos=end);wait(70)
            selected=js(page,'getSelection().toString()')
            assert len(selected)>5 and flipped()==state,(mode,kind,selected,flipped())
            app.clipboard().clear();QTest.keyClick(target,Qt.Key.Key_C,Qt.KeyboardModifier.ControlModifier);wait(60)
            assert app.clipboard().text()==selected,(mode,kind,'copy changed or failed',app.clipboard().text(),selected)
            # Rapid clicks on visible letters must clear an old range and flip.
            for i in range(6):
                before=flipped();QTest.mouseClick(target,Qt.MouseButton.LeftButton,pos=point());wait(35)
                assert flipped()!=before and js(page,'getSelection().toString()')=='',(mode,kind,'rapid click selected instead of flipping',i)
            # An actual Qt double-click must not leave a blue word selection.
            QTest.mouseDClick(target,Qt.MouseButton.LeftButton,pos=point());QTest.mouseRelease(target,Qt.MouseButton.LeftButton,pos=point());wait(70)
            assert js(page,'getSelection().toString()')=='',(mode,kind,'double click selected a word')
            assert not page.errors,page.errors
            if mode=='anki':assert page.calls.count('ans')==1 and not any(x.startswith('ease') for x in page.calls),page.calls
            else:assert not any(json.loads(x[5:]).get('action')=='grade' for x in page.calls if x.startswith('cram:')),page.calls
            scenes.append({'mode':mode,'kind':kind,'selected_and_copied':selected})
            view.close();view.deleteLater();wait(20)
    print(json.dumps({'real_mouse_scenes':scenes,'checks':['text clicks flip','real text drags select','Ctrl+C copies','rapid/double clicks do not select','no automatic rating']}))
    app.quit()

if __name__=='__main__':main()
