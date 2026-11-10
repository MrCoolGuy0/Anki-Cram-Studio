"""Independent practice and an opt-in skin for Anki's unchanged native reviewer."""
from aqt import gui_hooks, mw
from aqt.qt import QAction, QKeySequence, Qt
from aqt.utils import showWarning
from pathlib import Path

window=None
live=None
customizer=None
deck_choices=None
overview_bottom_visibility=None
MAIN_SHORTCUTS=('Ctrl+Alt+M','Ctrl+Shift+T')
ANKI_SHORTCUT='Ctrl+Alt+A'

def open_deck_choices(config=None):
    global deck_choices
    if not mw or not mw.col:return
    if deck_choices is not None and not deck_choices.closed:
        deck_choices.raise_();deck_choices.activateWindow();return
    if live is not None and live.busy or window is not None and getattr(window,'generating',False):
        showWarning('Wait for the current AI request to finish, or pause it, before regenerating deck choices.',parent=mw);return
    token=(live.current['cid'],live.current['epoch']) if live is not None and live.current else None
    if window is not None and not window.closed:window.emit('customizing',True)
    try:
        from .deck_choices import DeckChoices
        deck_choices=DeckChoices(mw,config);deck_choices.show();deck_choices.exec()
        if token and live is not None and live.is_review() and live.current:
            packet=live.current
            if (packet['cid'],packet['epoch'])==token and packet['side']=='question' and packet['display']=='exam':
                from .content import cache_key,prepare_choices,attach_choices
                question=packet['question'];model=live.store.data['model'];cache=live.store.cache()
                if any(cache_key(question,slot,model) in deck_choices.changed_keys for slot in question['slots']):
                    missing,_=prepare_choices([question],cache,model)
                    if not missing:
                        attach_choices([question],cache,model,force=True)
                        packet['choices_revision']=packet.get('choices_revision',0)+1;live.emit()
    except Exception as error:showWarning('Deck choices could not open:\n'+str(error),parent=mw)
    finally:
        deck_choices=None
        if window is not None and not window.closed:window.emit('customizing',False)

def appearance_saved(config):
    if window is not None and not window.closed:window.emit('appearance',config)
    if live is not None and live.current is not None:
        live.current['appearance']=config;live.emit()

def open_customize(*args):
    global customizer
    if not mw or not mw.col:return
    if customizer is not None and not customizer.closed:
        customizer.raise_();customizer.activateWindow();return
    if window is not None and not window.closed:window.emit('customizing',True)
    try:
        from .customize import CustomizeCram
        from .storage import profile_store
        customizer=CustomizeCram(mw,profile_store(mw.pm.profileFolder()),appearance_saved)
        customizer.showMaximized();customizer.exec()
    except Exception as error:showWarning('CUSTOMIZE CRAM could not open:\n'+str(error),parent=mw)
    finally:
        customizer=None
        if window is not None and not window.closed:window.emit('customizing',False)

def live_controller():
    global live
    if live is None:
        from .live_review import LiveReviewer
        live=LiveReviewer(mw,mw.addonManager.addonFromModule(__name__))
    return live

def open_live(*args):
    if not mw or not mw.col:return
    if live is not None and live.dialog is not None:
        live.dialog.raise_();live.dialog.activateWindow();return
    if live is not None and live.is_review():
        mw.raise_();mw.activateWindow();return
    if mw.state not in ('deckBrowser','overview'):
        showWarning('Return to the deck list or deck overview, then choose Tools → ANKI CRAM.',parent=mw)
        return
    try:
        # Use the selected deck and the existing setup; do not start/rate a review here.
        if mw.state=='deckBrowser':mw.moveToState('overview')
        live_controller().open()
    except Exception as error:showWarning('ANKI CRAM could not open:\n'+str(error),parent=mw)

def open_cram(deck_id=None):
    global window
    if not mw or not mw.col: return
    try:
        if window is None or window.closed:
            from .dialog import CramDialog
            window=CramDialog(mw,deck_id)
        window.showMaximized(); window.raise_(); window.activateWindow()
    except Exception as error: showWarning('MAIN CRAM could not open:\n'+str(error),parent=mw)

def close_cram(*args):
    global window,customizer,deck_choices
    if deck_choices is not None:deck_choices.reject();deck_choices=None
    if customizer is not None:customizer.reject();customizer=None
    if window is not None: window.close()
    window=None
    if live is not None:live.close()
    from .network_jobs import close_network
    close_network()
    from .storage import clear_profile_stores
    clear_profile_stores()
    restore_overview_bottom()

def restore_overview_bottom():
    global overview_bottom_visibility
    bottom=getattr(mw,'bottomWeb',None)
    if overview_bottom_visibility is True and bottom is not None:bottom.show()
    overview_bottom_visibility=None

def overview_controls(duplicated):
    global overview_bottom_visibility
    bottom=getattr(mw,'bottomWeb',None)
    if mw.state!='overview' or bottom is None:return
    if duplicated:
        if overview_bottom_visibility is None:overview_bottom_visibility=bottom.isVisible()
        bottom.hide()
    else:restore_overview_bottom()

def overview(handler,links):
    # The requested entry is one button in the overview body, not more bottom links.
    links[:]=[link for link in links if len(link)<2 or link[1] not in ('cram_studio_open','cram_live_open')]
    return handler

def message(handled,value,context):
    if not handled[0] and value in ('cram_overview_controls:0','cram_overview_controls:1') and mw.state=='overview':
        overview_controls(value.endswith(':1'));return True,None
    if not handled[0] and value=='cram_live_open' and mw.state in ('overview','deckBrowser'):
        open_live();return True,None
    if live is not None:
        handled=live.message(handled,value,context)
    if not handled[0] and value=='cram_studio_open' and mw.state in ('overview','deckBrowser'):
        open_cram(mw.col.decks.get_current_id()); return True,None
    return handled

def deck_menu(menu,did):
    action=menu.addAction('Practice in MAIN CRAM')
    action.triggered.connect(lambda checked=False:open_cram(did))

def open_live_deck(did):
    if not mw or not mw.col or mw.state not in ('deckBrowser','overview'):return
    mw.col.decks.select(did)
    mw.moveToState('overview')
    open_live()

def entry_buttons(surface):
    if not mw or not mw.col or mw.state!='overview':return
    web=getattr(surface,'web',surface)
    if web is not getattr(mw,'web',None):return
    script=(Path(__file__).parent/'web/entry.js').read_text(encoding='utf-8')
    web.eval(script+'\nwindow.cramEntryMount();')

def theme(*args):
    if window is not None and not window.closed: window.apply_theme()

def live_card(text,card,kind):return live.card_html(text,card,kind) if live is not None else text
def live_web(content,context):live_controller().web_content(content,context)
def live_shortcuts(state,keys):
    if live is not None:live.shortcuts(state,keys)
def live_state(new,old):
    if new!='overview':restore_overview_bottom()
    if live is not None:live.state_change(new,old)

if mw is not None:
    mw.addonManager.setWebExports(__name__,r'web/.*\.(css|js)$')
    action=QAction('MAIN CRAM',mw)
    action.setObjectName('cram_studio_tools')
    action.setShortcuts([QKeySequence(key) for key in MAIN_SHORTCUTS])
    action.setShortcutContext(Qt.ShortcutContext.WindowShortcut);action.setAutoRepeat(False)
    action.triggered.connect(lambda checked=False:open_cram(mw.col.decks.get_current_id() if mw.col and mw.state=='overview' else None))
    mw.form.menuTools.addAction(action)
    live_action=QAction('ANKI CRAM',mw)
    live_action.setObjectName('cram_studio_native_reviews')
    live_action.setShortcut(QKeySequence(ANKI_SHORTCUT))
    live_action.setShortcutContext(Qt.ShortcutContext.WindowShortcut);live_action.setAutoRepeat(False)
    live_action.triggered.connect(open_live)
    mw.form.menuTools.addAction(live_action)
    customize_action=QAction('CUSTOMIZE CRAM',mw)
    customize_action.setObjectName('cram_studio_customize')
    customize_action.triggered.connect(open_customize)
    mw.form.menuTools.addAction(customize_action)
    deck_choices_action=QAction('Regenerate deck choices',mw)
    deck_choices_action.setObjectName('cram_studio_deck_choices')
    deck_choices_action.triggered.connect(lambda checked=False:open_deck_choices())
    mw.form.menuTools.addAction(deck_choices_action)
    for name,fn in [('profile_will_close',close_cram),('overview_will_render_bottom',overview),('overview_did_refresh',entry_buttons),('webview_did_inject_style_into_page',entry_buttons),('webview_did_receive_js_message',message),('deck_browser_will_show_options_menu',deck_menu),('theme_did_change',theme),('card_will_show',live_card),('webview_will_set_content',live_web),('state_shortcuts_will_change',live_shortcuts),('state_will_change',live_state)]:
        hook=getattr(gui_hooks,name,None)
        if hook is not None: hook.append(fn)
