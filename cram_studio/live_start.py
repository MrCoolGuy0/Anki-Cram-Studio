"""Mode choice before entering Anki's existing reviewer."""
from aqt.qt import *
from .dialog import AISettings
from .live_review import filtered_status

class LiveStartDialog(QDialog):
    def __init__(self,controller):
        super().__init__(controller.mw);self.controller=controller;self.mw=controller.mw
        self.store=controller.store;self.closed=False
        self.setWindowTitle('ANKI CRAM');self.resize(540,350)
        layout=QVBoxLayout(self);layout.setSpacing(16)
        title=QLabel('<h2>ANKI CRAM</h2>');layout.addWidget(title)
        deck=self.mw.col.decks.current()
        info=QLabel(deck.get('name','')+'\n'+filtered_status(deck)+'\n\nUses the same cards, daily limits, order, intervals and undo as Study Now. Choose your rating after revealing; it also advances to the next card.')
        info.setTextFormat(Qt.TextFormat.PlainText);info.setWordWrap(True);layout.addWidget(info)
        self.flash=QRadioButton('Flashcards · Space to reveal, then Anki ratings')
        self.exam=QRadioButton('Multiple choice · choose, reveal, then Anki ratings')
        self.write=QRadioButton('Writing · Enter to check, then Anki ratings')
        mode=self.store.data['preferences'].get('live_mode','flash')
        self.flash.setChecked(mode not in ('exam','write'));self.exam.setChecked(mode=='exam');self.write.setChecked(mode=='write')
        layout.addWidget(self.flash);layout.addWidget(self.exam);layout.addWidget(self.write)
        self.extra=QCheckBox('Ignore extra text in Writing')
        self.extra.setChecked(self.store.data['preferences'].get('write_ignore_extra',False));layout.addWidget(self.extra)
        self.auto=QCheckBox('Automatically create missing choices with AI')
        preferences=self.store.data['preferences']
        self.auto.setChecked(preferences.get('live_generate',True) if preferences.get('live_generate_configured') else True);layout.addWidget(self.auto)
        note=QLabel('Preparing choices or Writing groups sends the current card’s text to the selected AI provider and uses your API quota. Saved results work offline. Writing also supports full answers without AI. Image occlusion keeps its image recall view.');note.setWordWrap(True);layout.addWidget(note)
        settings=QPushButton('AI settings');settings.clicked.connect(lambda:AISettings(self).exec());layout.addWidget(settings)
        self.exam.toggled.connect(self.update_choices);self.write.toggled.connect(self.update_choices);self.update_choices()
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText('Start ANKI CRAM')
        buttons.accepted.connect(self.save);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def update_choices(self,*args):
        self.auto.setEnabled(self.exam.isChecked() or self.write.isChecked());self.extra.setVisible(self.write.isChecked())
        self.auto.setText('Automatically prepare answer groups with AI' if self.write.isChecked() else 'Automatically create missing choices with AI')
    def save(self):
        c=self.controller;c.mode='write' if self.write.isChecked() else 'exam' if self.exam.isChecked() else 'flash';c.auto_generate=c.mode in ('exam','write') and self.auto.isChecked()
        with self.store.lock:
            self.store.data['preferences'].update(live_mode=c.mode,live_generate=self.auto.isChecked(),live_generate_configured=True,write_ignore_extra=self.extra.isChecked());self.store.save()
        self.accept()
    def closeEvent(self,event):self.closed=True;super().closeEvent(event)
