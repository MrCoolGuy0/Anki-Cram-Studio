"""Bounded Qt keyboard/mouse/native reveal regression; synthetic cards only."""
from pathlib import Path
import json
import os
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu --disable-dev-shm-usage')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl,Qt,QPoint
    from PyQt6.QtGui import QKeySequence,QShortcut
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from test_live_review import Environment,Card
    from test_core import c,s
    app=QApplication(['mcq-space-qa']);web=ROOT/'cram_studio/web'
    class Page(QWebEnginePage):
        def __init__(self,parent):super().__init__(parent);self.errors=[];self.callback=lambda *_:None
        def javaScriptConsoleMessage(self,level,message,line,source):
            if message.startswith('BRIDGE:'):QTimer.singleShot(0,lambda:self.callback(message[7:]))
            elif 'Error' in str(level):self.errors.append(message)
    def wait(ms=45):loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(code):
        box=[];loop=QEventLoop();page.runJavaScript(code,lambda value:(box.append(value),loop.quit()))
        QTimer.singleShot(2500,loop.quit);loop.exec();assert box,'JavaScript timeout';return box[0]
    with tempfile.TemporaryDirectory() as folder:
        env=Environment(folder,True,False);view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1320,900);view.show()
        view.eval=js;env.mw.reviewer.web=view;card=Card(kind='Cloze');env.mw.reviewer.card=card
        card.fields[:]=['<b>The IPv4 network header characteristics:</b><ul><li>It is in {{c1::binary}}.</li><li>Contains several fields of {{c1::information}}.</li><li>Diagram is read from {{c1::left to right}}, 4 bytes per line.</li></ul>','']
        question=c.cloze_question(card.fields[0],{1});q={'id':'space','mode':'exam','kind':'cloze','clue':question[0],'slots':question[1]}
        jobs,_=c.prepare_choices([q],{},env.live.store.data['model'])
        env.live.store.put({job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs})
        env.live.begin('exam',False);markup=env.packet();assert env.live.current['question']['ready']
        reveals=[];ratings=[];native_space=[];errors=[];pending=[]
        def remount(kind):
            html=env.packet(kind);js('document.querySelector("#qa").innerHTML='+json.dumps(html)+';cramNative.mount();')
        def original_space():
            native_space.append(env.mw.reviewer.state)
            if env.mw.reviewer.state=='question':reveals.append('native');remount('reviewAnswer')
            else:ratings.append('Space')
        def route(message):
            try:
                if message.startswith('cram_live:'):env.live.message((False,None),message,env.mw.reviewer)
                elif message=='ans':pending.append(message)
                else:errors.append(message)
            except Exception as error:errors.append(str(error))
        page.callback=route
        head=''.join('<link rel="stylesheet" href="'+name+'">' for name in ['live.css','appearance.css','writing.css'])
        head+='<script>window.pycmd=x=>console.log("BRIDGE:"+x);</script>'
        head+=''.join('<script defer src="'+name+'"></script>' for name in ['appearance.js','writing.js','live.js'])
        loaded=[];loop=QEventLoop();view.loadFinished.connect(lambda ok:(loaded.append(ok),loop.quit()))
        view.setHtml('<!doctype html><html><head>'+head+'</head><body><div id="qa">'+markup+'</div><script>addEventListener("load",()=>cramNative.mount());</script></body></html>',QUrl.fromLocalFile(str(web)+'/'))
        QTimer.singleShot(3500,loop.quit);loop.exec();assert loaded and loaded[0];wait()
        shortcuts=[];keys=[(' ',original_space)]+[(str(i),lambda i=i:ratings.append(str(i))) for i in range(1,5)]
        env.live.shortcuts('review',keys)
        for key,callback in keys:
            shortcut=QShortcut(QKeySequence(key),view);shortcut.setAutoRepeat(False);shortcut.activated.connect(callback);shortcuts.append(shortcut)
        view.activateWindow();view.setFocus();wait()
        for i in range(3):
            box=js('(()=>{const s=cramNative.state.packet.question.slots['+str(i)+'];const b=document.querySelector(`[data-live-slot="'+str(i)+'"][data-live-choice="${s.correct}"]`);const r=b.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()')
            QTest.mouseClick(view.focusProxy() or view,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,QPoint(round(box['x']),round(box['y'])));wait()
        expected=['binary','information','left to right']
        read='[...document.querySelectorAll(".cl-clue [data-blank]")].map(n=>n.textContent)'
        assert js(read)==expected,(js(read),errors)
        js('window.keptFrame=document.querySelector(".cl-exam");window.keptBlanks=[...document.querySelectorAll(".cl-clue [data-blank]")];window.keptChoices=[...document.querySelectorAll(".cl-choice")];window.keptPicks=[...cramNative.state.picks];')
        QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Space);wait()
        assert pending==['ans'] and native_space==[] and ratings==[],(pending,native_space,ratings,errors)
        assert js(read)==expected and js('cramNative.state.pending')
        # Simulate a late Space-triggered activation before the native reply.
        js('(()=>{const wrong=(cramNative.state.packet.question.slots[2].correct+1)%4;document.querySelector(`[data-live-slot="2"][data-live-choice="${wrong}"]`).click();cramNative.reveal();})()')
        wait();assert pending==['ans'];assert js('JSON.stringify(keptPicks)===JSON.stringify(cramNative.state.picks)')
        reveals.append(pending.pop());remount('reviewAnswer');wait()
        assert js(read)==expected
        assert js('keptFrame===document.querySelector(".cl-exam")&&keptBlanks.every((n,i)=>n===document.querySelectorAll(".cl-clue [data-blank]")[i])&&keptChoices.every((n,i)=>n===document.querySelectorAll(".cl-choice")[i])')
        assert js('[...document.querySelectorAll(".cl-choice")].every(n=>n.disabled)')
        assert js('document.querySelectorAll(".cl-clue .cram-blank-empty").length')==0
        assert js('document.querySelector(".cl-feedback").textContent')=='3 / 3 correct'
        js('cramNative.mount();cramNative.mount();');assert js(read)==expected
        assert reveals==['ans'] and not ratings and not errors and not page.errors,(reveals,ratings,errors,page.errors)
        QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_1);wait();assert ratings==['1']
        assert env.calls==['study'] and not env.background and env.live.store.data['history']==[]
        env.live.close();view.close();view.deleteLater();wait();s.clear_profile_stores()
    print(json.dumps({'three_mouse_selected_blanks':expected,'space_reveal_requests':len(reveals),'pending_button_activation':'ignored','question_and_choice_nodes':'preserved','native_rating':'explicit 1 only','scheduler_access':'none','live_api_requests':0}))
    app.quit()


if __name__=='__main__':main()
