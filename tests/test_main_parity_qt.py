"""Short real WebEngine check of MAIN flow, IO masks, bounds and native entry UI.

Synthetic notes + real MAIN controller methods; no collection/network access.
Run directly with PyQt6-WebEngine available. Screenshots stay in scratch.
"""
from pathlib import Path
import base64
import copy
import json
import os
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl,Qt,QPoint
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from test_progress import Controller,card,config
    from cram_studio import writing
    from cram_studio.content import cloze_question
    app=QApplication(['main-parity-qa']);web=ROOT/'cram_studio/web'
    out=(ROOT/'../../tmp/cram210-ui').resolve();out.mkdir(parents=True,exist_ok=True)
    temp=tempfile.TemporaryDirectory();fixture=Controller(temp.name);owner=fixture.owner
    errors=[];calls=[];metrics=[]
    class Page(QWebEnginePage):
        def javaScriptConsoleMessage(self,level,message,line,source):
            if message.startswith('BRIDGE:'):
                payload=message[7:];calls.append(payload)
                if payload.startswith('cram:'):QTimer.singleShot(0,lambda:owner.bridge(payload))
            else:errors.append((str(level),message,line,source))
    view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1360,900);view.show()
    def wait(ms=60):loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(code):
        loop=QEventLoop();box=[];page.runJavaScript(code,lambda v:(box.append(v),loop.quit()));QTimer.singleShot(2500,loop.quit);loop.exec();assert box,'JS timed out';return box[0]
    def until(check,label):
        import time
        end=time.monotonic()+4
        while time.monotonic()<end:
            if check():return
            wait(35)
        raise AssertionError(label+'; JS errors: '+repr(errors))
    def load(body,head=''):
        loop=QEventLoop();loaded=[]
        def done(ok):loaded.append(ok);loop.quit()
        view.loadFinished.connect(done);view.setHtml('<!doctype html><html><head>'+head+'</head><body>'+body+'</body></html>',QUrl.fromLocalFile(str(web)+'/'));QTimer.singleShot(4000,loop.quit);loop.exec();view.loadFinished.disconnect(done);assert loaded and loaded[0];wait(80)
    def emit(event,data):page.runJavaScript('cram.receive('+json.dumps(event)+','+json.dumps(data)+')')
    owner.emit=emit
    bridge='<script>window.onerror=(m,s,l,c,e)=>window.maskError=String(m);window.pycmd=m=>console.log("BRIDGE:"+m);</script>'
    head='<style>button:disabled{border-bottom-color:transparent!important}</style>'+''.join('<link rel="stylesheet" href="'+f+'">' for f in ['app.css','appearance.css','writing.css'])+bridge+''.join('<script defer src="'+f+'"></script>' for f in ['appearance.js','writing.js','app.js'])
    load('<div id="cram-app"></div><div id="toast"></div>',head)
    boot={'decks':[{'id':'1','name':'Science','count':5}],'current':'1','history':[],'settings':{},'preferences':{'auto_advance':True,'feedback_ms':600},'dark':False,'media':QUrl.fromLocalFile(str(web)+'/').toString()}
    emit('bootstrap',boot);until(lambda:js('!!document.querySelector("#limit")'),'home')
    for width in (1360,740):
        view.resize(width,900);until(lambda:js("innerWidth")==width,"viewport resize");wait(100)
        m=js('(()=>{const a=document.querySelector("#limit").getBoundingClientRect(),b=document.querySelector("#order-trigger").getBoundingClientRect();return {width:innerWidth,a:a.top,b:b.top,ah:a.height,bh:b.height,overflow:document.documentElement.scrollWidth>innerWidth};})()')
        assert abs(m['a']-m['b'])<1 and abs(m['ah']-m['bh'])<1 and not m['overflow'],m
        metrics.append({'controls':m});js('document.querySelector(".controls").scrollIntoView({block:"center"})');wait(240);view.grab().save(str(out/('setup-'+str(width)+'.png')))
    view.resize(1360,900);until(lambda:js('innerWidth')==1360,'wide viewport')
    # Wrong MCQ: correct text in the sentence, stable feedback until Continue.
    q=card('mcq',mode='exam',kind='cloze');q['clue']='The heart pumps <span class="ct-blank" data-blank="0">_____</span>.'
    q['slots'][0].update(answer='blood',answer_html='blood',wrong=['air','water','lymph'])
    fixture.launch([q,card('second')],config(mode='exam'));until(lambda:js('!!document.querySelector(".choice")'),'MCQ')
    js('document.querySelectorAll(".choice")[cram.state.questions[0].slots[0].correct===0?1:0].click();document.querySelector("[data-action=submit]").click()')
    until(lambda:len(owner.results)==1,'wrong MCQ grading');wait(850)
    assert js('cram.state.index===0&&cram.state.autoTimer===null')
    assert js('document.querySelector(".question-panel [data-blank]").textContent')=='blood'
    assert js('document.querySelectorAll(".choice.wrong").length===1&&document.querySelectorAll(".choice.right").length===1')
    assert js('[...document.querySelectorAll(".choice")].every(n=>{const s=getComputedStyle(n);return s.borderBottomStyle==="solid"&&s.borderBottomWidth==="2px"&&s.borderBottomColor===s.borderTopColor})')
    m=js('(()=>{const p=document.querySelector(".choice-section"),g=p.querySelector(".choices"),b=p.getBoundingClientRect(),r=g.getBoundingClientRect();return {pane:b.height,content:p.scrollHeight,top:r.top-b.top,bottom:b.bottom-r.bottom,overflow:getComputedStyle(p).overflowY};})()');metrics.append({'feedback_bounds':m})
    wait(240);view.grab().save(str(out/'mcq-wrong.png'))
    # Restart from in-session Settings replaces this checkpoint and reshuffles.
    old=owner.session_id;ids=[q['id'] for q in owner.questions]
    js('document.querySelector("[data-action=options]").click();document.querySelector("[data-action=restart-practice]").click();document.querySelector("[data-action=restart-confirm]").click()')
    until(lambda:owner.session_id!=old and not owner.results,'restart')
    assert [q['id'] for q in owner.questions]!=ids
    assert js('cram.state.index===0&&Object.keys(cram.state.results).length===0')
    # Real Writing checks: editable miss, revised correct -> one automatic check;
    # later Enter cannot append a new wrong attempt to the accepted answer.
    q=card('write',mode='write');q['slots'][0].update(answer='banana',answer_html='banana')
    writing.attach([q],{},whole=True);fixture.launch([q,card('next')],config(mode='write'));until(lambda:js('!!document.querySelector(".write-input")'),'writing')
    def type_answer(answer):
        js('cram.state.writeUI.input.value='+json.dumps(answer)+';cram.state.writeUI.input.dispatchEvent(new Event("input"));cram.state.writeUI.input.focus()')
        QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Return)
    type_answer('stone');until(lambda:js('document.querySelector(".write-feedback").textContent.includes("Not a match")'),'wrong warning')
    assert not owner.results and not js('cram.state.writeUI.input.readOnly')
    assert js('(()=>{const s=getComputedStyle(document.querySelector(".write-enter"));return s.borderTopStyle==="solid"&&s.borderBottomStyle==="solid"&&s.borderTopColor===s.borderBottomColor;})()')
    # An unchanged second Enter reveals and permits continuing with the miss.
    QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Return)
    until(lambda:len(owner.results)==1,'second Enter reveal');assert owner.results['0']['earned']==0
    wait(750);assert js('cram.state.index===0&&!!document.querySelector("[data-action=next]")')
    view.grab().save(str(out/'writing-revealed-miss.png'))
    fixture.launch([q,card('next')],config(mode='write'));until(lambda:js('!!document.querySelector(".write-input")&&!cram.state.results[0]'),'new writing')
    type_answer('BANANA');until(lambda:len(owner.results)==1,'one Enter final match')
    assert owner.results['0']['earned']==1 and len(owner.view['written']['0']['events'])==1
    # Clicking the question and pressing Enter explicitly continues; never rechecks.
    js('document.querySelector(".question-panel").click();document.activeElement.blur()');QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Return);wait(80)
    assert len(owner.view['written']['0']['events'])==1 and owner.results['0']['earned']==1
    # MAIN IO has independently tappable masks; the same image survives viewer moves.
    picture=base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="480"><rect width="800" height="480" fill="#dce8f2"/><text x="160" y="140" font-size="36">A</text><text x="450" y="320" font-size="36">B</text></svg>').decode()
    q=card('io',kind='io');q.update(mask_count=2,slots=[],clue='<b>Identify the structures</b>',extra='Answer caption',picture='<div class="io-image"><img src="data:image/svg+xml;base64,'+picture+'"><svg viewBox="0 0 800 480" aria-hidden="true"><rect class="mask target" x="120" y="80" width="150" height="100"/><rect class="mask target" x="400" y="260" width="150" height="100"/><rect class="mask inactive" x="650" y="50" width="80" height="80"/></svg></div>')
    fixture.launch([q],config());until(lambda:js('!!document.querySelector("[data-main-mask]")'),'IO')
    js('window.keptImage=document.querySelector(".io-image>img")');wait(240)
    def click_mask(index):
        pos=js('(()=>{const r=document.querySelectorAll("[data-main-mask]")['+str(index)+'].getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];})()')
        QTest.mouseClick(view.focusProxy() or view,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,QPoint(round(pos[0]),round(pos[1])));wait(100)
    click_mask(0)
    assert js('document.querySelectorAll("[data-main-mask]")[0].classList.contains("io-mask-open")&&!document.querySelectorAll("[data-main-mask]")[1].classList.contains("io-mask-open")')
    assert not owner.results
    js('document.querySelector("[data-action=fullscreen]").click()');wait(200);click_mask(1)
    assert js('document.querySelector(".io-image>img")===keptImage&&cram.state.ioMasks[0].seen')
    js('document.querySelector("[data-action=close-viewer]").click();document.querySelectorAll("[data-main-mask]")[0].focus()');QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Return);wait(100)
    assert js('!document.querySelectorAll("[data-main-mask]")[0].classList.contains("io-mask-open")&&document.querySelector(".io-image>img")===keptImage')
    assert not owner.results;wait(240);view.grab().save(str(out/'io-masks.png'))
    # Exactly one button, no wrapper/bar and no styling changes to native controls.
    entry=(web/'entry.js').read_text()
    for mode in ('regular','filtered','finished'):
        labels=['Options','Rebuild','Empty'] if mode=='filtered' else ['Options','Custom Study','Description']
        body='<main><h1>'+mode+'</h1><div id="native-controls" style="display:flex;align-items:stretch;gap:12px;justify-content:center">'+''.join('<button class="native" id="native'+str(i)+'">'+label+'</button>' for i,label in enumerate(labels))+'</div></main>'
        native_style='<style>.native{height:44px;padding:8px 15px;border:1px solid #8ca3cc;border-radius:9px;background:#c2d1f0;min-width:100px}</style>'
        load(body,bridge+native_style)
        before=js('[...document.querySelectorAll(".native")].map(n=>({html:n.outerHTML,height:n.getBoundingClientRect().height}))')
        js(entry+';cramEntryMount();cramEntryMount()')
        assert js('document.querySelectorAll("#cram-anki-overview").length===1&&!document.querySelector("#cram-entry-buttons")&&!document.querySelector("#cram-entry-style")')
        after=js('[...document.querySelectorAll("#native-controls>.native")].filter(n=>n.id!=="cram-anki-overview").map(n=>({html:n.outerHTML,height:n.getBoundingClientRect().height}))')
        assert before==after,(before,after)
        assert js('document.querySelector("#cram-anki-overview").parentElement.id==="native-controls"')
        count=len(calls);js('document.querySelector("#cram-anki-overview").click()');wait();assert calls[count:]==['cram_live_open']
        js('document.querySelector("#cram-anki-overview").remove()');until(lambda:js('!!document.querySelector("#cram-anki-overview")'),'theme rerender recovery')
        wait(200);view.grab().save(str(out/('entry-'+mode+'.png')))
    assert not errors,errors
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps({'main_flow':'passed','wrong_feedback_waits':'passed','writing_enter_and_retry':'passed','restart_and_shuffle':'passed','individual_IO_and_stable_image':'passed','entry_buttons':'passed','metrics':metrics,'output':str(out)}))
    view.close();temp.cleanup();app.quit()

if __name__=='__main__':main()
