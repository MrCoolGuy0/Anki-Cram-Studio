"""Bounded Qt regression: long filled terms must not displace their bullets."""
from pathlib import Path
import html
import json
import os

ROOT=Path(__file__).resolve().parents[1]

def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    app=QApplication(['mcq-blank-qa']);web=ROOT/'cram_studio/web'
    out=Path(os.environ.get('CRAM_MCQ_OUTPUT',str(ROOT/'../../tmp/cram206-mcq'))).resolve();out.mkdir(parents=True,exist_ok=True)
    class Page(QWebEnginePage):
        def __init__(self,parent):super().__init__(parent);self.errors=[]
        def javaScriptConsoleMessage(self,level,message,line,source):
            if 'Error' in str(level):self.errors.append(message)
    def wait(ms=80):
        loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(page,code):
        loop=QEventLoop();box=[];page.runJavaScript(code,lambda v:(box.append(v),loop.quit()));QTimer.singleShot(3000,loop.quit);loop.exec()
        assert box,'JavaScript timed out'
        return box[0]
    slots=[]
    for index,(answer,markup) in enumerate([
        ('Institute for Electrical and\nElectronic Engineers (IEEE)','Institute for Electrical and\nElectronic Engineers (IEEE)'),
        ('International Telecommunications\nUnion (ITU)','<b>International Telecommunications\nUnion (ITU)</b>'),
        ('First explicit line\nSecond explicit line','First explicit line<br>Second explicit line'),
    ]):
        slots.append({'number':index+1,'answer':answer,'answer_html':markup,'choices':[answer,'Wrong A','Wrong B','Wrong C'],'correct':0})
    clue='<b>Data link layer protocols are defined by engineering organizations:</b>'+''.join('<p><span class="qa-bullet" data-marker="'+str(i)+'">•</span><span class="ct-blank" data-blank="'+str(i)+'">_____</span>.</p>' for i in range(3))
    question={'id':'ieee-itu','kind':'cloze','mode':'exam','ready':True,'deck':'NETC','clue':clue,'slots':slots}
    checks=[]
    for mode in ('main','anki'):
        for width in (1360,540):
            view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(width,900);view.show()
            styles=(['app.css'] if mode=='main' else ['live.css'])+['appearance.css']
            head=''.join('<link rel="stylesheet" href="'+name+'">' for name in styles)
            head+='<script>window.pycmd=()=>{};</script>'+''.join('<script defer src="'+name+'"></script>' for name in ['appearance.js','app.js' if mode=='main' else 'live.js'])
            if mode=='main':
                body='<div id="cram-app"></div><div id="toast"></div>'
                boot={'decks':[{'id':'1','name':'NETC','count':1}],'current':'1','history':[],'settings':{},'dark':False,'media':QUrl.fromLocalFile(str(web)+'/').toString(),'preferences':{'auto_advance':False}}
                session={'questions':[question],'config':{'mode':'exam','decks':['1'],'limit':0,'children':True,'filters':{}}}
                init='cram.receive("bootstrap",'+json.dumps(boot)+');cram.receive("session",'+json.dumps(session)+');'
                choose='for(let i=0;i<3;i++)document.querySelector(`[data-slot="${i}"][data-choice="0"]`).click();'
            else:
                packet={'cid':'1','epoch':1,'side':'question','display':'exam','question':question}
                body='<section id="cram-live" data-packet="'+html.escape(json.dumps(packet),quote=True)+'"><div id="cl-stage"><div id="cl-original"></div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>'
                init='cramNative.mount();';choose='for(let i=0;i<3;i++)cramNative.choose(0);'
            markup='<!doctype html><html><head>'+head+'</head><body>'+body+'<script>addEventListener("load",()=>{'+init+'});</script></body></html>'
            loop=QEventLoop();loaded=[];view.loadFinished.connect(lambda ok:(loaded.append(ok),loop.quit()))
            view.setHtml(markup,QUrl.fromLocalFile(str(web)+'/'));QTimer.singleShot(4000,loop.quit);loop.exec();assert loaded and loaded[0]
            wait();js(page,choose);wait()
            measured=js(page,"""(()=>{const first=n=>{const r=document.createRange();r.setStart(n.firstChild,0);r.setEnd(n.firstChild,1);return r.getBoundingClientRect().top;};return [...document.querySelectorAll('.question-panel [data-blank],.cl-question-panel [data-blank]')].map(n=>{const s=getComputedStyle(n),marker=document.querySelector(`[data-marker="${n.dataset.blank}"]`);return {text:n.textContent,display:s.display,whiteSpace:s.whiteSpace,bulletDifference:Math.abs(first(n)-first(marker)),lines:n.getClientRects().length};});})()""")
            assert len(measured)==3,measured
            for i in (0,1):
                row=measured[i]
                assert row['display']=='inline' and row['whiteSpace']=='normal' and row['bulletDifference']<3,(mode,width,row)
                assert '\n' not in row['text'] and ('IEEE' if i==0 else 'ITU') in row['text'],row
            assert measured[2]['display']=='inline' and measured[2]['whiteSpace']=='pre-wrap' and '\n' in measured[2]['text'],measured[2]
            assert not page.errors,page.errors
            view.grab().save(str(out/(mode+'-'+str(width)+'.png')))
            if mode=='anki':
                packet['side']='answer';js(page,'document.querySelector("#cram-live").dataset.packet='+json.dumps(json.dumps(packet))+';cramNative.mount();');wait()
                assert js(page,"getComputedStyle(document.querySelector('[data-blank=\"0\"]')).display")=='inline'
            checks.append({'mode':mode,'width':width,'blanks':measured})
            view.close();view.deleteLater();wait(20)
    (out/'metrics.json').write_text(json.dumps(checks,indent=2))
    print(json.dumps({'mcq_phrase_layouts':len(checks),'checks':['first-line bullet alignment','soft newline collapse','real BR retention','native answer redraw'],'output':str(out)}))
    app.quit()

if __name__=='__main__':main()
