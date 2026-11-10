"""Private live previews for both Cram modes; appearance saves only on Save."""
import json
from pathlib import Path
from aqt.qt import QDialog,QVBoxLayout,Qt
from aqt.webview import AnkiWebView
from aqt.theme import theme_manager
from .appearance import get_appearance,save_appearance
from .appearance_images import choose_image

class CustomizeCram(QDialog):
    def __init__(self,mw,store,on_saved):
        super().__init__(mw)
        self.mw=mw;self.store=store;self.on_saved=on_saved;self.closed=False
        self.setWindowTitle('CUSTOMIZE CRAM');self.resize(1360,900);self.setMinimumSize(850,580)
        self.setWindowFlags(Qt.WindowType.Window|Qt.WindowType.WindowTitleHint|Qt.WindowType.WindowSystemMenuHint|Qt.WindowType.WindowMinimizeButtonHint|Qt.WindowType.WindowMaximizeButtonHint|Qt.WindowType.WindowCloseButtonHint)
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        self.web=AnkiWebView(parent=self,title='customize_cram');layout.addWidget(self.web)
        self.web.set_bridge_command(self.bridge,self)
        package=mw.addonManager.addonFromModule(__name__)
        self.assets=mw.serverURL().rstrip('/')+f'/_addons/{package}/web/'
        body=(Path(__file__).parent/'web/customize.html').read_text(encoding='utf-8')
        self.web.stdHtml(body,css=[f'/_addons/{package}/web/customize.css'],js=[f'/_addons/{package}/web/appearance.js',f'/_addons/{package}/web/customize.js'],context=self)
    def emit(self,event,data):
        if not self.closed:self.web.eval('window.cramCustomize && window.cramCustomize.receive('+json.dumps(event)+','+json.dumps(data,ensure_ascii=True)+');')
    def bridge(self,message):
        if not message.startswith('cram_custom:') or self.closed:return
        try:
            if len(message)>1000000:raise ValueError('Appearance request too large.')
            data=json.loads(message[len('cram_custom:'):]);action=data.get('action')
            if action=='ready':self.emit('load',{'config':get_appearance(self.store),'dark':bool(theme_manager.night_mode),'assets':self.assets})
            elif action=='choose-image':
                target=data.get('target')
                if target not in ('background','card'):raise ValueError('Choose a page or card image.')
                image=choose_image(self)
                self.emit('image',{'target':target,'image':image})
            elif action=='save':
                config=save_appearance(self.store,data.get('config',{}))
                self.on_saved(config);self.accept()
            elif action=='cancel':self.reject()
        except Exception as error:self.emit('error',str(error))
    def done(self,result):self.closed=True;super().done(result)
