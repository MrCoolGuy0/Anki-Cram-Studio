"""Bounded WebEngine regression for both overview add-ons together.

Pass --cram path/to/entry.js --study path/to/overview.js. Optional --before
uses the 2.0.11/0.6.15 archives to demonstrate their observer loop. Internal
screenshots are optional (--screenshots DIR); no user collections are opened.
"""
from pathlib import Path
import argparse
import json
import os
from zipfile import ZipFile


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--cram',required=True);args.add_argument('--study',required=True)
    args.add_argument('--before',action='store_true');args.add_argument('--screenshots')
    a=args.parse_args()
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS','--no-sandbox --disable-gpu')
    from PyQt6.QtCore import QEventLoop,QTimer,QUrl,Qt,QPoint
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    app=QApplication(['overview-pair-check']);calls=[];errors=[];results=[]
    class Page(QWebEnginePage):
        def javaScriptConsoleMessage(self,level,message,line,source):
            if message.startswith('BRIDGE:'):calls.append(message[7:])
            elif 'Error' in str(level):errors.append(message)
    view=QWebEngineView();page=Page(view);view.setPage(page);view.resize(1020,760);view.show()
    def wait(ms):
        loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
    def js(code):
        loop=QEventLoop();values=[]
        page.runJavaScript(code,lambda v:(values.append(v),loop.quit()))
        QTimer.singleShot(1500,loop.quit);loop.exec();assert values,'JavaScript timeout'
        return values[0]
    if a.before:
        with ZipFile(a.cram) as z:cram=z.read('web/entry.js').decode()
        with ZipFile(a.study) as z:study=z.read('web/overview.js').decode()
    else:cram=Path(a.cram).read_text();study=Path(a.study).read_text()
    study=study.replace('STUDYLIST_NATIVE_VISIBLE','false')
    css='''body{font:16px Arial;background:#eff3ff;padding:60px 40px}
      #native-controls{display:flex;align-items:stretch;gap:12px;justify-content:center}
      button{font:inherit;padding:12px 20px;border:1px solid #8ca3cc;border-radius:100px;background:#fff;color:#142034;line-height:24px}
      #native-controls>[data-native]{border-radius:9px;background:#c2d1f0}
      button:hover{transform:scale(1.045);transition:all .12s}
      body.dark{background:#142034}body.dark [data-native]{background:#344365!important;color:#fff}
      h1{font-size:24px;text-align:center}.stats{height:220px;width:440px;margin:10px auto 26px;border-radius:20px;background:#c2d1f0}
    '''
    modes=['finished'] if a.before else ['regular','filtered','finished']
    for mode in modes:
        labels=['Options','Rebuild','Empty'] if mode=='filtered' else ['Options','Custom<br>Study','Description']
        body='<h1>'+('No more cards due' if mode=='finished' else mode)+'</h1><div class="stats"></div><div id="native-controls">'+''.join('<button data-native="1" id="n'+str(i)+'">'+s+'</button>' for i,s in enumerate(labels))+'</div>'
        loop=QEventLoop();view.loadFinished.connect(loop.quit)
        view.setHtml('<html><head><style>'+css+'</style><script>window.pycmd=m=>console.log("BRIDGE:"+m)</script></head><body>'+body+'</body></html>',QUrl('http://127.0.0.1/'))
        QTimer.singleShot(2500,loop.quit);loop.exec();view.loadFinished.disconnect(loop.quit);wait(100)
        native=js('[...document.querySelectorAll("[data-native]")].map(n=>({html:n.outerHTML,height:n.getBoundingClientRect().height}))')
        # Different load orders plus repeated Study List refreshes must settle.
        if mode=='filtered':js(study);js(cram+';cramEntryMount()')
        else:js(cram+';cramEntryMount()');js(study)
        wait(550);js(study);wait(450)
        js('window.mutations=0;window.counter=new MutationObserver(r=>mutations+=r.length);counter.observe(document.body,{childList:true,subtree:true,attributes:true})')
        wait(700)
        changes=js('mutations')
        if a.before:
            assert changes>5,changes
            print(json.dumps({'before_observer_loop':'reproduced','mutations_in_700ms':changes}));break
        assert changes==0,(mode,changes)
        assert js('document.querySelectorAll("#cram-anki-overview").length===1&&document.querySelectorAll("#studylist_overview_button").length===1')
        assert js('document.querySelector("#n2").nextElementSibling.id==="studylist_overview_button"&&document.querySelector("#studylist_overview_button").nextElementSibling.id==="cram-anki-overview"')
        assert not js('!!document.querySelector("#cram-entry-buttons,#cram-entry-style")')
        after=js('[...document.querySelectorAll("[data-native]")].map(n=>({html:n.outerHTML,height:n.getBoundingClientRect().height}))')
        assert after==native,(mode,native,after)
        def bounds():
            return js('[...document.querySelectorAll("#native-controls>button")].map(n=>{const r=n.getBoundingClientRect(),s=getComputedStyle(n);return {id:n.id,x:r.x,y:r.y,w:r.width,h:r.height,radius:s.borderTopLeftRadius,transform:s.transform,animation:s.animationName,transition:s.transitionDuration,bg:s.backgroundColor}})')
        initial=bounds();reference=initial[2]
        for b in initial[3:]:assert b['radius']==reference['radius'] and b['h']==reference['h'],initial
        for ident in ('cram-anki-overview','studylist_overview_button'):
            point=js('(()=>{const b=document.getElementById('+json.dumps(ident)+').getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2]})()')
            for offset in (0,2,-2,1):QTest.mouseMove(view.focusProxy() or view,QPoint(round(point[0]+offset),round(point[1])));wait(45)
            wait(180)
            hovered=bounds()
            for b,c in zip(initial,hovered):
                if b['id'] in ('cram-anki-overview','studylist_overview_button'):
                    assert [b[k] for k in ('x','y','w','h','radius')]==[c[k] for k in ('x','y','w','h','radius')],(b,c)
                    assert c['transform']=='none' and c['animation']=='none' and c['transition']=='0s',c
            assert js('mutations')==0,(mode,ident,js('mutations'))
            count=len(calls);js('document.getElementById('+json.dumps(ident)+').click()');wait(40)
            assert calls[count:]==['cram_live_open' if ident.startswith('cram') else 'studylist_open'],calls[count:]
        # Native labels/widths are retained; our labels are not wrapped.
        assert not js('document.documentElement.scrollWidth>innerWidth')
        if a.screenshots:
            out=Path(a.screenshots);out.mkdir(parents=True,exist_ok=True);view.grab().save(str(out/(mode+'.png')))
        js('counter.disconnect();document.body.classList.add("dark")');wait(500)
        assert js('getComputedStyle(document.getElementById("cram-anki-overview")).backgroundColor===getComputedStyle(document.getElementById("n2")).backgroundColor')
        assert js('getComputedStyle(document.getElementById("studylist_overview_button")).backgroundColor===getComputedStyle(document.getElementById("n2")).backgroundColor')
        # Recover a theme's full control-row rerender without duplication.
        js('document.getElementById("native-controls").innerHTML='+json.dumps(''.join('<button data-native="1" id="n'+str(i)+'">'+s+'</button>' for i,s in enumerate(labels))))
        wait(550)
        assert js('document.querySelectorAll("#cram-anki-overview").length===1&&document.querySelectorAll("#studylist_overview_button").length===1')
        results.append({'layout':mode,'settled_mutations':changes,'native_shape_and_height':'matched','hover_geometry':'stable','clicks':'once','theme_rerender':'passed'})
    assert not errors,errors
    if not a.before:print(json.dumps({'overview_pair':'passed','results':results}))
    view.close();app.quit()


if __name__=='__main__':main()
