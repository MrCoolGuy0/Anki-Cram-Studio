"""Optional bounded Qt WebEngine smoke test. Synthetic notes; no Anki collection.

Run directly with PyQt6-WebEngine available. Not a substitute for Windows/Anki QA.
"""
from pathlib import Path
import importlib
import json
import os
import sys
import types

ROOT=Path(__file__).resolve().parents[1]

def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl,Qt,QEvent,QObject
    from PyQt6.QtGui import QShortcut,QKeySequence
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage,QWebEngineSettings
    from PyQt6.QtTest import QTest
    pkg=types.ModuleType('cram_studio');pkg.__path__=[str(ROOT/'cram_studio')];sys.modules['cram_studio']=pkg
    w=importlib.import_module('cram_studio.writing')
    from test_writing import basic,mapped
    from cram_studio.content import cloze_question
    app=QApplication(['cram-writing-qa']);web=ROOT/'cram_studio/web';out=Path(os.environ.get('CRAM_LAYOUT_OUTPUT',str(ROOT/'../../tmp/cram2-layout'))).resolve();out.mkdir(parents=True,exist_ok=True)
    question=mapped(basic('<b>The fruits are</b> banana, mango, and lemon.','<b>Name the fruits.</b>'),['banana','mango','lemon'])
    empty={'accepted':[],'remaining':[0,1,2],'target':0,'complete':False,'missed':[],'last':{'status':'idle'}}
    appearance={'examSize':{'width':82,'height':70},'examLayout':{'questionHeight':60,'choiceTextSize':18},'colors':{'dark':{'exam':{'auto':True,'card':'#1c2844'}}}}
    application=[]
    class Page(QWebEnginePage):
        def __init__(self,parent):super().__init__(parent);self.messages=[];self.errors=[];self.callback=lambda *_:None
        def javaScriptConsoleMessage(self,level,message,line,source):
            if message.startswith('BRIDGE:'):
                self.messages.append(message[7:]);QTimer.singleShot(0,lambda:self.callback(message[7:]))
            elif 'Error' in str(level):self.errors.append(message)
    def wait(ms=100):
        loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(page,code):
        loop=QEventLoop();box=[]
        page.runJavaScript(code,lambda value:(box.append(value),loop.quit()))
        QTimer.singleShot(4000,loop.quit);loop.exec()
        if not box:raise AssertionError('JavaScript callback timed out')
        return box[0]
    def load(view,html):
        loop=QEventLoop();box=[]
        callback=lambda value:(box.append(value),loop.quit());view.loadFinished.connect(callback)
        view.setHtml(html,QUrl.fromLocalFile(str(web)+'/'))
        QTimer.singleShot(5000,loop.quit);loop.exec();view.loadFinished.disconnect(callback)
        assert box and box[0],'HTML did not load';wait(150)
    def html(mode,dark=False,config=None):
        styles=['app.css'] if mode=='main' else ['live.css']
        styles+=['appearance.css','writing.css']
        head=''.join('<link rel="stylesheet" href="'+name+'">' for name in styles)
        head+='<script>window.pycmd=message=>console.log("BRIDGE:"+message);</script>'
        head+=''.join('<script defer src="'+name+'"></script>' for name in ['appearance.js','writing.js','app.js' if mode=='main' else 'live.js'])
        config=config or {}
        if mode=='main':
            body='<div id="cram-app"></div><div id="toast"></div>'
            boot={'decks':[{'id':'1','name':'Fruit','count':1}],'current':'1','history':[],'settings':{'model':'test','has_key':False},'media':QUrl.fromLocalFile(str(web)+'/').toString(),'dark':dark,'preferences':{'auto_advance':False,'appearance':config}}
            session={'session_id':'a'*32,'questions':[question],'config':{'mode':'write','decks':['1'],'limit':0,'children':True,'filters':{}}}
            init='cram.receive("bootstrap",'+json.dumps(boot)+');cram.receive("session",'+json.dumps(session)+');'
        else:
            packet={'cid':'1','epoch':1,'side':'question','display':'write','question':question,'writing_events':[],'writing_state':empty,'appearance':config}
            import html as esc
            body='<section id="cram-live" data-packet="'+esc.escape(json.dumps(packet),quote=True)+'"><header class="cl-header"><span class="cl-brand">ANKI CRAM</span><div class="cl-context"><div class="cl-deck">Fruit</div></div></header><div id="cl-stage"><div id="cl-original"></div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>'
            init='cramNative.mount();'
        return '<!doctype html><html><head><meta charset="utf-8">'+head+'</head><body class="'+('nightMode' if dark and mode=='anki' else '')+'">'+body+'<script>window.addEventListener("load",()=>{'+init+'});</script></body></html>'
    metrics=[]
    for mode in ('main','anki'):
        for dark,width,height,config in [(False,1360,900,{}),(True,1360,900,appearance),(False,900,680,appearance),(True,540,520,{})]:
            view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(width,height);view.show()
            page.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls,True)
            load(view,html(mode,dark,config))
            data=js(page,"""(()=>{const r=s=>{const x=document.querySelector(s).getBoundingClientRect();return {x:x.x,y:x.y,w:x.width,h:x.height,right:x.right,bottom:x.bottom};};return {card:r('.write-card'),input:r('.write-input'),panel:r('.question-panel,.cl-question-panel'),host:r('.write-response-host'),width:innerWidth,scroll:document.documentElement.scrollWidth,inputColor:getComputedStyle(document.querySelector('.write-input')).color};})()""")
            assert not page.errors,page.errors
            assert data['scroll']<=width+1,data
            assert data['card']['right']<=width+1 and data['card']['x']>=-1,data
            assert data['input']['right']<=data['card']['right']+1,data
            assert data['input']['w']>100 and data['panel']['h']>30,data
            view.grab().save(str(out/(f'{mode}-{width}-{height}-'+('dark.png' if dark else 'light.png'))))
            metrics.append({'mode':mode,'dark':dark,'width':width,'height':height,**data})
            view.close();view.deleteLater();wait(20)
    # The customization mockup runs the same Writing component and size palette.
    for mode in ('main','anki'):
        for dark in (False,True):
            head=''.join('<link rel="stylesheet" href="'+name+'">' for name in ['app.css','live.css','live-bottom.css','appearance.css','writing.css'])
            head+=''.join('<script defer src="'+name+'"></script>' for name in ['appearance.js','writing.js','customize-preview.js'])
            data={'type':'cram-preview-config','mode':mode,'view':'write','panel':'size','face':'question','theme':'dark' if dark else 'light','config':appearance}
            markup='<!doctype html><html><head>'+head+'</head><body><script>window.addEventListener("load",()=>window.postMessage('+json.dumps(data)+',"*"));</script></body></html>'
            view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1360,900);view.show();load(view,markup)
            measured=js(page,"(()=>{const input=document.querySelector('.write-input'),card=document.querySelector('.write-card');return {input:!!input,card:!!card,scroll:document.documentElement.scrollWidth,width:innerWidth};})()")
            assert measured['input'] and measured['card'] and measured['scroll']<=1361,measured
            assert not page.errors,page.errors
            view.grab().save(str(out/(f'customize-{mode}-'+('dark.png' if dark else 'light.png'))))
            view.close();view.deleteLater();wait(20)
    # Raw HTML whitespace must collapse inside inline clozes; explicit <br> stays.
    original_question=question
    for mode in ('main','anki'):
        for label,answer_html in [('existing','existing\nlogic'),('official','official\nproceedings'),('explicit-break','existing<br>logic')]:
            clue,slots=cloze_question('<b>Heading</b><br>Programs reuse {{c1::'+answer_html+'}}.',{1})
            question={'kind':'cloze','mode':'write','id':'format-'+label,'clue':clue,'slots':slots,'ready':True,'deck':'Format'}
            question['writing']=w.build_plan(question)
            view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1360,900);view.show();load(view,html(mode))
            js(page,('cram.state' if mode=='main' else 'cramNative.state')+'.writeUI.fill(true)')
            measured=js(page,"""(()=>{const nodes=[...document.querySelectorAll('[data-write-item="0"]')],n=nodes[0],r=document.createRange();r.setStartBefore(n);r.setEndAfter(nodes.at(-1));const rects=[...r.getClientRects()].filter(r=>r.width>0);return {text:nodes.map(n=>n.textContent).join(' '),display:getComputedStyle(n).display,space:getComputedStyle(n).whiteSpace,lines:new Set(rects.map(r=>Math.round(r.top))).size,breaks:r.cloneContents().querySelectorAll('br').length,bold:!!document.querySelector('.write-cloze b')};})()""")
            assert measured['display']=='inline' and measured['space']=='normal' and measured['bold'],measured
            expected=('official','proceedings') if label=='official' else ('existing','logic')
            assert all(term in measured['text'] for term in expected),measured
            if label=='explicit-break':assert measured['breaks']==1 and measured['lines']>=2,measured
            else:assert measured['lines']==1,measured
            wait(80);view.grab().save(str(out/f'format-{mode}-{label}.png'));view.close();view.deleteLater();wait(20)
    question=original_question
    # One original cloze can now contain several typed targets and rich joiners.
    for mode in ('main','anki'):
        clue,slots=cloze_question('<b>Fruit</b><br>Name {{c1::<strong>mango</strong>, banana, with the final spotlight going to apple}} and {{c1::orange}}; {{c2::pear}}.',{1})
        question={'kind':'cloze','mode':'write','id':'combined','clue':clue,'slots':slots,'ready':False,'deck':'Format'}
        jobs,_,_=w.attach([question],{});assert len(jobs)==1
        text=jobs[0]['text'];spans=[[text.index(v),text.index(v)+len(v)] for v in ['mango','banana','apple']]
        w.attach([question],{jobs[0]['id']:{'kind':'list','spans':spans,'connectors':['with the final spotlight going to']}})
        empty={'accepted':[],'remaining':[0,1,2,3],'target':0,'complete':False,'missed':[],'last':{'status':'idle'}}
        view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1360,900);view.show();load(view,html(mode))
        measured=js(page,"(()=>{const c=document.querySelector('.write-clue'),nodes=[...c.querySelectorAll('[data-write-item]')];return {count:nodes.length,ids:nodes.map(n=>n.dataset.writeItem),text:c.textContent};})()")
        assert measured['count']==4 and measured['ids']==['0','1','2','3'],measured
        assert 'with the final spotlight going to' in measured['text'] and 'pear' in measured['text'] and 'apple' not in measured['text'],measured
        state=w.evaluate(question['writing'],[{'text':'banana','target':0}])
        controller='cram.state.writeUI' if mode=='main' else 'cramNative.state.writeUI'
        js(page,controller+'.receive('+json.dumps({'events':[{'text':'banana','target':0}],'state':state})+')')
        assert js(page,"document.querySelector('[data-write-item=\"1\"]').textContent")=='banana'
        assert js(page,"document.querySelector('[data-write-item=\"2\"]').textContent")== '\u00a0'
        js(page,controller+'.fill(true)');wait(80)
        final=js(page,"(()=>{const c=document.querySelector('.write-clue');return {text:c.textContent,bold:c.querySelector('strong').textContent};})()")
        assert 'mango, banana, with the final spotlight going to apple' in final['text'] and final['bold']=='mango',final
        assert not page.errors,page.errors
        view.grab().save(str(out/f'combined-{mode}.png'));view.close();view.deleteLater();wait(20)
    question=original_question
    empty={'accepted':[],'remaining':[0,1,2],'target':0,'complete':False,'missed':[],'last':{'status':'idle'}}
    # Verify real Qt shortcut behavior, rather than assuming a JS key handler wins.
    view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1360,828);view.show();view.activateWindow();view.setFocus();load(view,html('anki'))
    aq=types.ModuleType('aqt');qt=types.ModuleType('aqt.qt');qt.QObject=QObject;qt.QEvent=QEvent;qt.Qt=Qt;aq.qt=qt
    sys.modules['aqt']=aq;sys.modules['aqt.qt']=qt
    Live=importlib.import_module('cram_studio.live_review').LiveReviewer
    owner=Live.__new__(Live);owner.active=True;owner.writing_filter=None;owner.writing_focus=True;owner.current={'display':'write','side':'question'}
    owner.mw=types.SimpleNamespace(state='review',col=object(),reviewer=types.SimpleNamespace(web=view));owner.install_writing_filter()
    events=[];shortcut=QShortcut(QKeySequence('e'),view);shortcut.activated.connect(lambda:events.append('edit'))
    js(page,"document.querySelector('.write-input').focus()")
    QTest.keyClicks(view.focusProxy() or view,'banana mango lemon e');wait()
    typed=js(page,"document.querySelector('.write-input').value")
    assert typed=='banana mango lemon e',(typed,events)
    assert events==[],events
    js(page,"document.querySelector('.write-input').blur()")
    owner.writing_focus=False;view.activateWindow();view.setFocus();wait();QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_E);wait()
    assert events==['edit'],events
    # Exercise Enter -> Python matching -> native reveal -> original rating key.
    rating_events=[];reveal_events=[];callback_errors=[]
    rating=QShortcut(QKeySequence('1'),view);rating.activated.connect(lambda:rating_events.append('Again'))
    packet={};attempts=[]
    def route(message):
        nonlocal packet,attempts
        try:
            if message=='ans':
                reveal_events.append('ans');packet['side']='answer';owner.current=packet;owner.writing_focus=False
                script="document.querySelector('#cram-live').dataset.packet="+json.dumps(json.dumps(packet))+";cramNative.mount();"
                js(page,script);return
            if not message.startswith('cram_live:'):return
            data=json.loads(message[10:])
            if data['action']=='writing_focus':owner.writing_focus=data['focused']
            elif data['action']=='write_submit':
                attempts,state=w.attempt(question,attempts,data['text'],data['target'])
                packet.update(writing_events=attempts,writing_state=state)
                js(page,'cramNative.receive('+json.dumps(packet)+')')
        except Exception as error:callback_errors.append(str(error))
    page.callback=route
    for case in ('correct','wrong-reveal','wrong-revise','partial','empty'):
        packet={'cid':'1','epoch':1,'side':'question','display':'write','question':question,'writing_events':[],'writing_state':empty,'appearance':{}}
        owner.current=packet;owner.writing_focus=True;attempts=[];reveal_events.clear();rating_events.clear()
        load(view,html('anki'));view.activateWindow();view.setFocus();js(page,"document.querySelector('.write-input').focus()")
        text='banana mango lemon' if case=='correct' else 'banana' if case=='partial' else '' if case=='empty' else 'potato'
        QTest.keyClicks(view.focusProxy() or view,text);QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Return);wait(100)
        if case.startswith('wrong'):
            assert reveal_events==[],(case,reveal_events)
            assert js(page,"document.activeElement.classList.contains('write-input')"),case
            if case=='wrong-revise':
                js(page,"document.querySelector('.write-input').select()")
                QTest.keyClicks(view.focusProxy() or view,'banana mango lemon')
            QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Return);wait(100)
        assert not callback_errors,callback_errors
        assert len(reveal_events)==(0 if case=='partial' else 1),(case,reveal_events)
        assert rating_events==[],(case,rating_events)
        if case!='partial':
            QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_1);wait(80)
            assert rating_events==['Again'],(case,rating_events)
        assert not page.errors,page.errors
    # Current-card mode switching uses the real controller + actual WebEngine DOM.
    # Qt shortcuts are real, while collection/native rating callbacks are spies.
    import tempfile
    from test_live_review import Environment
    view.removeEventFilter(owner.writing_filter);shortcut.deleteLater();rating.deleteLater();wait(20)
    temporary=tempfile.TemporaryDirectory()
    fixture=Environment(temporary.name);view.eval=lambda code:js(page,code);fixture.mw.reviewer.web=view
    (out/'photo-qa.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500"><rect width="800" height="500" fill="#cddcf6"/></svg>')
    fixture.col.media=types.SimpleNamespace(escape_media_filenames=lambda value:value.replace('photo-qa.svg',QUrl.fromLocalFile(str(out/'photo-qa.svg')).toString()))
    fixture.mw.reviewer.card.fields[:]=['<b>Identify the fruit</b><br><img src="photo-qa.svg">','<ul><li>banana</li><li>mango</li></ul>']
    fixture.live.begin('flash');markup=fixture.packet();card=fixture.mw.reviewer.card;bridge_errors=[];ratings=[];arrows=[]
    def controls_route(message):
        try:
            if message.startswith('cram_live:'):fixture.live.message((False,None),message,fixture.mw.reviewer)
            elif message=='ans':bridge_errors.append('Unexpected native reveal')
        except Exception as error:bridge_errors.append(str(error))
    page.callback=controls_route
    head=''.join('<link rel="stylesheet" href="'+name+'">' for name in ['live.css','appearance.css','writing.css'])
    head+='<script>window.pycmd=message=>console.log("BRIDGE:"+message);</script>'
    head+=''.join('<script defer src="'+name+'"></script>' for name in ['appearance.js','writing.js','live.js'])
    load(view,'<!doctype html><html><head>'+head+'</head><body><div id="qa">'+markup+'</div><script>addEventListener("load",()=>cramNative.mount());</script></body></html>')
    one=QShortcut(QKeySequence('1'),view);one.activated.connect(lambda:ratings.append('Again'))
    up=QShortcut(QKeySequence('Up'),view);up.activated.connect(lambda:arrows.append('Up'))
    down=QShortcut(QKeySequence('Down'),view);down.activated.connect(lambda:arrows.append('Down'))
    view.activateWindow();view.setFocus()
    js(page,'document.querySelector("[data-live-action=settings]").click()');wait()
    assert fixture.live.overlay_focus
    QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_1);wait(30);assert ratings==[],ratings
    view.grab().save(str(out/'anki-mode-menu.png'))
    js(page,'document.querySelector("[data-live-mode=write]").click()');wait(120)
    assert fixture.live.current['display']=='write' and fixture.mw.reviewer.card is card
    short=js(page,'document.querySelector(".write-input").getBoundingClientRect().height')
    assert 40<=short<=65,short
    js(page,'document.querySelector(".write-input").focus()')
    QTest.keyClicks(view.focusProxy() or view,'first');QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Return,Qt.KeyboardModifier.ShiftModifier);QTest.keyClicks(view.focusProxy() or view,'second')
    assert js(page,'document.querySelector(".write-input").value')=='first\nsecond'
    multiline='\n'.join('line '+str(i) for i in range(40))
    js(page,'(()=>{const i=document.querySelector(".write-input");i.value='+json.dumps(multiline)+';i.dispatchEvent(new Event("input",{bubbles:true}));i.focus();i.setSelectionRange(i.value.length,i.value.length);i.scrollTop=i.scrollHeight;})()')
    before=js(page,'(()=>{const i=document.querySelector(".write-input");return {cursor:i.selectionStart,scroll:i.scrollTop};})()')
    for _ in range(12):QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Up)
    wait(40)
    after=js(page,'(()=>{const i=document.querySelector(".write-input");return {cursor:i.selectionStart,scroll:i.scrollTop};})()')
    assert after['cursor']<before['cursor'] and after['scroll']<before['scroll'] and arrows==[],(before,after,arrows)
    QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Down);wait(30)
    assert js(page,'document.querySelector(".write-input").selectionStart')>after['cursor']
    draft=js(page,'document.querySelector(".write-input").value')
    def select_mode(mode):
        js(page,'document.querySelector("[data-live-action=settings]").click();document.querySelector("[data-live-mode='+mode+']").click()');wait(100)
    select_mode('exam')
    controller_module=importlib.import_module('cram_studio.live_review')
    jobs,_=controller_module.prepare_choices([fixture.live.current['question']],{},fixture.live.store.data['model'])
    fixture.live.store.put({job['id']:['Carrot','Potato','Onion'] for job in jobs})
    controller_module.attach_choices([fixture.live.current['question']],fixture.live.store.cache(),fixture.live.store.data['model'],partial=True);fixture.live.emit();wait()
    js(page,'cramNative.choose(1)');picks=js(page,'cramNative.state.picks.slice()')
    select_mode('flash');select_mode('write');assert js(page,'document.querySelector(".write-input").value')==draft
    select_mode('exam');assert js(page,'cramNative.state.picks.slice()')==picks
    js(page,'document.querySelector(".cl-clue img").dispatchEvent(new MouseEvent("dblclick",{bubbles:true}))');wait(120)
    assert fixture.live.overlay_focus and js(page,'!!document.querySelector("#cl-photo-viewer")')
    bounds=js(page,'(()=>{const i=document.querySelector("#cl-photo-image"),b=i.getBoundingClientRect();return {w:b.width,h:b.height,width:innerWidth,height:innerHeight,naturalWidth:i.naturalWidth};})()')
    assert bounds['w']>500 and bounds['w']<=bounds['width'] and bounds['h']<=bounds['height'] and abs(bounds['w']/bounds['h']-1.6)<.01,bounds
    QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_1);wait(30)
    assert ratings==[] and js(page,'cramNative.state.picks.slice()')==picks
    view.grab().save(str(out/'anki-photo-viewer.png'))
    QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_Escape);wait(60)
    assert not fixture.live.overlay_focus and js(page,'!document.querySelector("#cl-photo-viewer")')
    markup=fixture.packet('reviewAnswer');js(page,'document.querySelector("#qa").innerHTML='+json.dumps(markup)+';cramNative.mount()');wait(100)
    view.activateWindow();view.setFocus();QTest.keyClick(view.focusProxy() or view,Qt.Key.Key_1);wait(40)
    assert ratings==['Again'] and fixture.calls==['study'] and not bridge_errors,(ratings,fixture.calls,bridge_errors)
    assert not page.errors,page.errors
    fixture.live.close();temporary.cleanup();view.close();view.deleteLater()
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps({'rendered_scenes':len(metrics),'customization_scenes':4,'format_scenes':6,'combined_cloze_scenes':2,'qt_input_shortcut_check':'passed','qt_writing_flow_cases':5,'native_mode_photo_caret_checks':'passed','output':str(out)}))
    app.quit()

if __name__=='__main__':main()
