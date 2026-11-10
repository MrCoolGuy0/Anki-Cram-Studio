"""Bounded real-renderer regression for image-first Writing questions.

Run directly with PyQt6-WebEngine; synthetic notes only, no collection/network.
"""
from pathlib import Path
import base64
import html
import importlib
import json
import os
import sys
import types

ROOT = Path(__file__).resolve().parents[1]


def main():
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS', '--no-sandbox --disable-gpu')
    from PyQt6.QtCore import QEventLoop, QTimer, QUrl
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    pkg = types.ModuleType('cram_studio')
    pkg.__path__ = [str(ROOT / 'cram_studio')]
    sys.modules['cram_studio'] = pkg
    writing = importlib.import_module('cram_studio.writing')
    from cram_studio.content import cloze_question
    app = QApplication(['writing-scroll-qa'])
    web = ROOT / 'cram_studio/web'
    out = Path(os.environ.get('CRAM_SCROLL_OUTPUT', str(ROOT / '../../tmp/cram204-scroll'))).resolve()
    out.mkdir(parents=True, exist_ok=True)

    class Page(QWebEnginePage):
        def __init__(self, parent):
            super().__init__(parent)
            self.errors = []
        def javaScriptConsoleMessage(self, level, message, line, source):
            if 'Error' in str(level):
                self.errors.append(message)

    def wait(ms=80):
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()

    def js(page, code):
        loop, result = QEventLoop(), []
        page.runJavaScript(code, lambda value: (result.append(value), loop.quit()))
        QTimer.singleShot(3000, loop.quit)
        loop.exec()
        assert result, 'JavaScript timed out'
        return result[0]

    figure = base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="700"><rect width="800" height="700" fill="#ccd9ec"/><text x="40" y="100" font-size="32">Reference image above the answers</text></svg>').decode()
    context = '<p>' + 'Read this context before recalling the fruit. ' * 12 + '</p>'
    clue, slots = cloze_question('<img src="data:image/svg+xml;base64,' + figure + '">' + context + '<p>The first fruit is {{c1::banana}}.</p>' + context + '<p>The next fruit is {{c1::mango}}.</p>' + context + '<p>The last fruit is {{c1::lemon}}.</p>', {1})
    question = {'id': 'scroll', 'kind': 'cloze', 'mode': 'write', 'deck': 'Scroll QA', 'clue': clue, 'slots': slots}
    writing.attach([question], {}, whole=True)
    metrics = []
    for mode in ('main', 'anki'):
        for width, height, zoom in ((1360, 900, 1), (900, 680, 1.5)):
            view = QWebEngineView()
            page = Page(view)
            view.setPage(page)
            view.resize(width, height)
            view.show()
            styles = (['app.css'] if mode == 'main' else ['live.css']) + ['appearance.css', 'writing.css']
            scripts = ['appearance.js', 'writing.js', 'app.js' if mode == 'main' else 'live.js']
            head = ''.join('<link rel="stylesheet" href="' + name + '">' for name in styles)
            head += '<script>window.calls=[];window.pycmd=x=>calls.push(x);</script>'
            head += ''.join('<script defer src="' + name + '"></script>' for name in scripts)
            state = writing.evaluate(question['writing'], [])
            packet = {'cid': 'scroll', 'epoch': 1, 'side': 'question', 'display': 'write', 'question': question, 'writing_events': [], 'writing_state': state, 'text_zoom': zoom}
            if mode == 'main':
                boot = {'decks': [{'id': '1', 'name': 'Scroll QA', 'count': 1}], 'current': '1', 'history': [], 'settings': {}, 'media': QUrl.fromLocalFile(str(web) + '/').toString(), 'dark': False, 'preferences': {'text_zoom': zoom, 'auto_advance': False}}
                session = {'session_id': 'a' * 32, 'questions': [question], 'config': {'mode': 'write', 'decks': ['1'], 'limit': 0, 'children': True, 'filters': {}}}
                body = '<div id="cram-app"></div><div id="toast"></div>'
                init = 'cram.receive("bootstrap",' + json.dumps(boot) + ');cram.receive("session",' + json.dumps(session) + ');'
            else:
                body = '<div id="qa"><section id="cram-live" data-packet="' + html.escape(json.dumps(packet), quote=True) + '"><div id="cl-stage"><div id="cl-original"></div><div id="cl-custom"></div></div><div id="cl-notice"></div></section></div>'
                init = 'cramNative.mount();'
            markup = '<!doctype html><html><head>' + head + '</head><body>' + body + '<script>addEventListener("load",()=>{' + init + '});</script></body></html>'
            loop, loaded = QEventLoop(), []
            view.loadFinished.connect(lambda ok: (loaded.append(ok), loop.quit()))
            view.setHtml(markup, QUrl.fromLocalFile(str(web) + '/'))
            QTimer.singleShot(4000, loop.quit)
            loop.exec()
            assert loaded and loaded[0], 'Page did not load'
            wait(150)
            controller = 'cram.state.writeUI' if mode == 'main' else 'cramNative.state.writeUI'

            def measured(item):
                return js(page, '''(()=>{const p=document.querySelector('.question-panel,.cl-question-panel'),n=p.querySelector('[data-write-item="%s"]'),r=n.getBoundingClientRect(),b=p.getBoundingClientRect();return {visible:r.top>=b.top+6&&r.bottom<=b.bottom-6,top:p.scrollTop,page:scrollY,focused:document.activeElement.classList.contains('write-input'),anchor:%s.view.anchor,text:n.textContent};})()''' % (item, controller))

            initial = measured(0)
            assert not initial['visible'] and initial['top'] == 0, initial
            events = []
            for index, answer in enumerate(('banana', 'mango', 'lemon')):
                js(page, controller + '.input.value=' + json.dumps(answer) + ';' + controller + '.submit();')
                events, state = writing.attempt(question, events, answer, index)
                if mode == 'main':
                    js(page, 'cram.receive("writeFeedback",' + json.dumps({'index': 0, 'events': events, 'state': state}) + ')')
                else:
                    packet.update(writing_events=events, writing_state=state)
                    js(page, 'cramNative.receive(' + json.dumps(packet) + ')')
                wait()
                result = measured(index)
                assert result['visible'] and result['top'] > 0 and result['text'] == answer, (mode, index, result)
                assert result['anchor'] == index and abs(result['page'] - initial['page']) < 1, result
                assert result['focused'] == (index < 2), result
            if mode == 'anki':
                assert js(page, 'calls.filter(x=>x==="ans").length') == 1
                packet['side'] = 'answer'
                new_body = '<section id="cram-live" data-packet="' + html.escape(json.dumps(packet), quote=True) + '"><div id="cl-stage"><div id="cl-original"></div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>'
                js(page, 'document.querySelector("#qa").innerHTML=' + json.dumps(new_body) + ';cramNative.mount();')
            else:
                js(page, controller + '.fill(true)')
            wait(120)
            revealed = measured(2)
            assert revealed['visible'] and revealed['anchor'] == 2, (mode, revealed)
            assert not page.errors, page.errors
            view.grab().save(str(out / (mode + '-' + str(width) + '.png')))
            metrics.append({'mode': mode, 'width': width, 'zoom': zoom, 'revealed': revealed})
            view.close()
            view.deleteLater()
            wait(20)
    (out / 'metrics.json').write_text(json.dumps(metrics, indent=2))
    print(json.dumps({'image_first_scroll_scenes': len(metrics), 'checks_per_scene': ['partial matches', 'final match', 'reveal/remount', 'typing focus', 'no page jump'], 'output': str(out)}))
    app.quit()


if __name__ == '__main__':
    main()
