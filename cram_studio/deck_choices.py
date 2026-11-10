"""Full-deck choice regeneration, explicit preview and resumable small batches."""
import copy
import threading
from aqt.qt import QDialog,QVBoxLayout,QHBoxLayout,QTreeWidget,QTreeWidgetItem,QCheckBox,QPushButton,QLabel,QProgressBar,Qt
from aqt.operations import QueryOp
from .bulk_choices import bulk_config,deck_choice_plan
from .content import catalog
from .ai import client as Gemini
from .gemini import generate_batches
from .storage import profile_store
from .network_jobs import run_network

class DeckChoices(QDialog):
    def __init__(self,mw,config=None):
        super().__init__(mw);self.mw=mw;self.store=profile_store(mw.pm.profileFolder());self.closed=False
        self.running=False;self.reading=False;self.jobs=[];self.total=0;self.completed=0;self.model='';self.changed_keys=set();self.cancel=threading.Event();self.run_token=0
        self.initial=config or {'decks':[str(mw.col.decks.get_current_id())],'children':True}
        self.setWindowTitle('Regenerate deck choices · MAIN CRAM + ANKI CRAM');self.resize(820,700);self.setMinimumSize(600,500)
        self.setWindowFlags(Qt.WindowType.Window|Qt.WindowType.WindowTitleHint|Qt.WindowType.WindowSystemMenuHint|Qt.WindowType.WindowMinimizeButtonHint|Qt.WindowType.WindowMaximizeButtonHint|Qt.WindowType.WindowCloseButtonHint)
        layout=QVBoxLayout(self);layout.setContentsMargins(24,22,24,22);layout.setSpacing(14)
        heading=QLabel('Regenerate deck choices');font=heading.font();font.setPointSize(18);font.setBold(True);heading.setFont(font);layout.addWidget(heading)
        scope=QLabel('Entire selected decks · MAIN CRAM + ANKI CRAM\nPractice filters and question limits do not restrict this action.');scope.setWordWrap(True);layout.addWidget(scope)
        self.tree=QTreeWidget();self.tree.setHeaderLabels(['Deck','Cards']);self.tree.setColumnWidth(0,590);layout.addWidget(self.tree)
        self.children=QCheckBox('Include subdecks');self.children.setChecked(self.initial.get('children',True));layout.addWidget(self.children)
        self.stats=QLabel('Loading decks…');self.stats.setWordWrap(True);layout.addWidget(self.stats)
        self.progress=QProgressBar();self.progress.setRange(0,1);self.progress.setValue(0);layout.addWidget(self.progress)
        self.status=QLabel('Replaces saved choices for these decks. Selected provider’s API quota applies.');self.status.setWordWrap(True);self.status.setTextFormat(Qt.TextFormat.PlainText);layout.addWidget(self.status)
        row=QHBoxLayout();layout.addLayout(row)
        self.settings=QPushButton('AI settings');self.preview=QPushButton('Preview');self.generate=QPushButton('Regenerate all choices');self.pause=QPushButton('Pause');close=QPushButton('Close')
        for button in (self.settings,self.preview,self.generate,self.pause,close):row.addWidget(button)
        self.tree.itemChanged.connect(self.invalidate);self.children.toggled.connect(self.invalidate)
        self.settings.clicked.connect(self.ai_settings);self.preview.clicked.connect(self.prepare);self.generate.clicked.connect(self.start);self.pause.clicked.connect(self.stop);close.clicked.connect(self.reject)
        self.reading=True;self.controls()
        QueryOp(parent=self,op=catalog,success=self.loaded).failure(self.failed).run_in_background()
    def controls(self):
        idle=not self.running and not self.reading
        self.tree.setEnabled(idle);self.children.setEnabled(idle);self.settings.setEnabled(idle);self.preview.setEnabled(idle)
        self.generate.setEnabled(idle and bool(self.jobs));self.pause.setEnabled(self.running)
    def loaded(self,cat):
        if self.closed:return
        self.reading=False;self.decks=cat['decks'];self.items={};selected=set(map(str,self.initial.get('decks',[])));nodes={}
        self.tree.blockSignals(True)
        for deck in self.decks:
            parts=deck['name'].split('::');parent=None
            for i,part in enumerate(parts):
                name='::'.join(parts[:i+1])
                if name not in nodes:
                    node=QTreeWidgetItem(parent if parent is not None else self.tree,[part,'']);nodes[name]=node
                parent=nodes[name]
            node=nodes[deck['name']];node.setData(0,Qt.ItemDataRole.UserRole,deck['id'])
            node.setFlags(node.flags()|Qt.ItemFlag.ItemIsUserCheckable)
            node.setCheckState(0,Qt.CheckState.Checked if deck['id'] in selected else Qt.CheckState.Unchecked);self.items[deck['id']]=node
        self.tree.blockSignals(False);self.tree.collapseAll();self.invalidate()
        checked=next((node for did,node in self.items.items() if did in selected),None)
        if checked and checked.parent() is None:self.tree.scrollToItem(checked)
    def invalidate(self,*args):
        if self.running or self.reading:return
        self.jobs=[];self.total=0;self.completed=0;self.generate.setText('Regenerate all choices')
        self.stats.setText('No preview yet.');self.progress.setRange(0,1);self.progress.setValue(0)
        for deck in getattr(self,'decks',[]):
            count=deck['total_count'] if self.children.isChecked() else deck['count'];self.items[deck['id']].setText(1,str(count))
        self.controls()
    def config(self):
        return bulk_config({'decks':[did for did,item in self.items.items() if item.checkState(0)==Qt.CheckState.Checked],'children':self.children.isChecked()})
    def failed(self,error):
        if self.closed:return
        self.reading=False;self.status.setText(str(error));self.controls()
    def prepare(self):
        if self.running or self.reading:return
        try:config=self.config()
        except Exception as error:self.failed(error);return
        self.reading=True;self.jobs=[];self.controls();self.status.setText('Reading the full selected decks…')
        mappings=copy.deepcopy(self.store.data['mappings']);model=self.store.data['model']
        def done(plan):
            if self.closed:return
            self.reading=False;self.jobs=plan['jobs'];self.total=len(self.jobs);self.completed=0;self.model=model
            self.stats.setText(f'{plan["cards"]} cards · {plan["questions"]} practice questions · {self.total} choice sets'+(f' · {plan["skipped"]} unsupported/empty cards skipped' if plan['skipped'] else ''))
            self.progress.setRange(0,max(1,self.total));self.progress.setValue(0);self.generate.setText(f'Regenerate {self.total} choice sets')
            self.status.setText('Ready. Existing cached choices will also be replaced.' if self.jobs else 'No supported multiple-choice answers in this selection. Image-only and long answers use flashcards.')
            self.controls()
        QueryOp(parent=self,op=lambda col:deck_choice_plan(col,config,mappings,model),success=done).failure(self.failed).run_in_background()
    def ai_settings(self):
        if self.running or self.reading:return
        from .dialog import AISettings
        AISettings(self).exec();self.invalidate()
    def start(self):
        if self.running or self.reading or not self.jobs:return
        try:client=Gemini(self.store.get_model_key(self.model),self.model)
        except Exception as error:self.status.setText(str(error));return
        self.running=True;self.cancel=threading.Event();cancel=self.cancel;jobs=list(self.jobs);completed=[0];saved=set();store=self.store;base=self.completed
        self.run_token+=1;token=self.run_token
        self.status.setText('Regenerating choices…');self.controls()
        def progress(done,total):
            completed[0]=done
            def show():
                if not self.closed and self.running and token==self.run_token:self.progress.setValue(base+done);self.status.setText(f'{base+done} / {self.total} choice sets saved')
            self.mw.taskman.run_on_main(show)
        def work():return generate_batches(client,jobs,store,cancel,progress,batch_size=10,
            parallelism=getattr(store,'generation_parallelism',2),batch_complete=saved.update)
        def done(future):
            if self.closed or token!=self.run_token:return
            self.running=False;self.completed=base+len(saved);self.jobs=[job for job in jobs if job['id'] not in saved]
            self.changed_keys.update(saved)
            try:future.result();message='All choices regenerated. Saved for MAIN CRAM and ANKI CRAM.'
            except Exception as error:message=str(error)
            self.progress.setValue(self.completed);self.status.setText(message)
            self.generate.setText(f'Resume {len(self.jobs)} remaining sets' if self.jobs else 'Completed');self.controls()
        run_network(self.mw,work,done)
    def stop(self):
        self.cancel.set();self.pause.setEnabled(False);self.status.setText('Pausing after the current requests. Saved batches are retained.')
    def done(self,result):
        self.closed=True;self.cancel.set();super().done(result)
