"""Bounded real-WebEngine render of the reported five-item Writing question."""
from pathlib import Path
import html
import json
import os

def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from test_writing_provider_parity import question,w,TEXT
    app=QApplication(['writing-enumeration-regression']);web=Path(__file__).resolve().parents[1]/'cram_studio/web'
    q=question(True);assert w.attach([q],{})[:2]==([],1)
    empty=w.evaluate(q['writing'],[]);events=[{'text':'SWEET','target':0}];partial=w.evaluate(q['writing'],events)
    class Page(QWebEnginePage):
        def __init__(self,parent):super().__init__(parent);self.errors=[]
        def javaScriptConsoleMessage(self,level,message,line,source):
            if 'Error' in str(level):self.errors.append(message)
    def wait(ms=60):loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(page,code):
        box=[];loop=QEventLoop();page.runJavaScript(code,lambda v:(box.append(v),loop.quit()))
        QTimer.singleShot(3000,loop.quit);loop.exec();assert box,'JS callback timed out';return box[0]
    for mode in ('main','anki'):
        for width,dark in ((1360,False),(620,True)):
            styles=['app.css' if mode=='main' else 'live.css','appearance.css','writing.css']
            head=''.join('<link rel="stylesheet" href="'+f+'">' for f in styles)
            head+='<script>window.pycmd=()=>{};</script>'
            head+=''.join('<script defer src="'+f+'"></script>' for f in ('appearance.js','writing.js','app.js' if mode=='main' else 'live.js'))
            if mode=='main':
                body='<div id="cram-app"></div><div id="toast"></div>'
                boot={'decks':[{'id':'1','name':'Taste','count':1}],'current':'1','history':[],'settings':{},'preferences':{'auto_advance':False},'media':QUrl.fromLocalFile(str(web)+'/').toString(),'dark':dark}
                init='cram.receive("bootstrap",'+json.dumps(boot)+');cram.receive("session",'+json.dumps({'questions':[q],'config':{'mode':'write'}})+');'
                controller='cram.state.writeUI'
            else:
                packet={'cid':'1','epoch':1,'side':'question','display':'write','question':q,'writing_events':[],'writing_state':empty,'appearance':{}}
                body='<section id="cram-live" data-packet="'+html.escape(json.dumps(packet),quote=True)+'"><div id="cl-stage"><div id="cl-original"></div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>'
                init='cramNative.mount();';controller='cramNative.state.writeUI'
            document='<!doctype html><html><head><meta charset="utf-8">'+head+'</head><body class="'+('nightMode' if dark else '')+'">'+body+'<script>addEventListener("load",()=>{'+init+'});</script></body></html>'
            view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(width,850);view.show()
            box=[];loop=QEventLoop();view.loadFinished.connect(lambda ok:(box.append(ok),loop.quit()))
            view.setHtml(document,QUrl.fromLocalFile(str(web)+'/'));QTimer.singleShot(5000,loop.quit);loop.exec();assert box and box[0];wait(120)
            assert js(page,'document.querySelector(".write-progress").textContent')=='0 / 5'
            assert js(page,'document.querySelectorAll("[data-write-item]").length')==5
            js(page,controller+'.receive('+json.dumps({'events':events,'state':partial})+')')
            assert js(page,'document.querySelector(".write-progress").textContent')=='1 / 5'
            assert js(page,'document.querySelectorAll("[data-write-item]")[0].textContent')=='sweet'
            assert js(page,'document.querySelectorAll("[data-write-item]")[1].textContent')=='\u00a0'
            js(page,controller+'.fill(true)');wait()
            assert TEXT in js(page,'document.querySelector(".write-clue").textContent')
            assert js(page,'document.documentElement.scrollWidth<=innerWidth+1')
            assert not page.errors,page.errors
            view.close();view.deleteLater();wait(30)
    print('Writing enumeration: MAIN/ANKI, light/dark and narrow/wide show 0/5 -> 1/5; exact original reveal, no horizontal overflow.')

if __name__=='__main__':main()
