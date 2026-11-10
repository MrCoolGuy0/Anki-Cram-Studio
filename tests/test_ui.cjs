/* Lightweight DOM interaction checks, no browser download. Does not test pixel layout. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
function makeStyle(css=''){
  const style={},priorities={};const key=name=>name.replace(/-([a-z])/g,(_,c)=>c.toUpperCase());
  Object.defineProperties(style,{
    getPropertyValue:{value:name=>style[key(name)]||''},getPropertyPriority:{value:name=>priorities[name]||''},
    setProperty:{value:(name,value,priority='')=>{style[key(name)]=value;priorities[name]=priority;}},
    removeProperty:{value:name=>{delete style[key(name)];delete priorities[name];}}
  });
  for(const declaration of css.split(';')){const i=declaration.indexOf(':');if(i>0)style.setProperty(declaration.slice(0,i).trim(),declaration.slice(i+1).trim());}
  return style;
}
class Node {
  constructor(tag='div',attrs={},doc=null){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.doc=doc;this.children=[];this.parentElement=null;this.listeners={};this.style=makeStyle(attrs.style||'');this.disabled='disabled' in attrs;this.hidden='hidden' in attrs;this.checked='checked' in attrs;this.value=attrs.value||'';this.dataset={};this.naturalWidth=640;this.naturalHeight=480;this.complete=true;for(const k in attrs)if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=attrs[k];}
  get childNodes(){return this.children;}
  get nodeType(){return this.tagName==='#TEXT'?3:1;}
  get isConnected(){for(let n=this;n;n=n.parentElement)if(n.tagName==='DOCUMENT')return true;return false;}
  get id(){return this.attrs.id||'';}set id(v){this.attrs.id=v;}
  get className(){return this.attrs.class||'';}set className(v){this.attrs.class=v;}
  get classList(){return {contains:v=>this.className.split(/\s+/).includes(v),add:(...v)=>this.className=[...new Set([...this.className.split(/\s+/).filter(Boolean),...v])].join(' '),remove:(...v)=>this.className=this.className.split(/\s+/).filter(x=>!v.includes(x)).join(' '),toggle:(v,force)=>{let add=force??!this.classList.contains(v);add?this.classList.add(v):this.classList.remove(v);return add;}};}
  setAttribute(k,v){this.attrs[k]=String(v);}getAttribute(k){return this.attrs[k]??null;}
  removeAttribute(k){delete this.attrs[k];if(k==='hidden')this.hidden=false;if(k==='disabled')this.disabled=false;}
  get attributes(){return Object.entries(this.attrs).map(([name,value])=>({name,value}));}
  get firstElementChild(){return this.children.find(n=>n.tagName!=='#TEXT')||null;}
  insertBefore(node,ref){node.remove();const i=this.children.indexOf(ref);this.children.splice(i<0?this.children.length:i,0,node);node.parentElement=this;return node;}
  cloneNode(deep=false){const node=new Node(this.tagName,this.attrs,this.doc);node._text=this._text;Object.assign(node.style,this.style);if(deep)for(const child of this.children)node.appendChild(child.cloneNode(true));return node;}
  appendChild(node){node.remove();this.children.push(node);node.parentElement=this;return node;}
  prepend(node){node.remove();this.children.unshift(node);node.parentElement=this;}
  remove(){if(this.parentElement){this.parentElement.children=this.parentElement.children.filter(n=>n!==this);this.parentElement=null;}}
  get innerHTML(){return this._html||'';}
  set innerHTML(value){this._html=value;for(const child of this.children)child.parentElement=null;this.children=[];parse(value,this);}
  get textContent(){return this.tagName==='#TEXT'?this._text:this.children.map(n=>n.textContent).join('');}
  set textContent(value){for(const child of this.children)child.parentElement=null;this.children=[];const t=new Node('#text',{},this.doc);t._text=String(value);this.appendChild(t);}
  get clientWidth(){return this.classList.contains('io-viewport')?850:1000;}
  get clientHeight(){return this.id==='viewer-viewport'?650:this.classList.contains('io-viewport')?340:800;}
  focus(){}
  querySelectorAll(selector){const out=[];function walk(n){for(const child of n.children){if(matches(child,selector))out.push(child);walk(child);}}walk(this);return out;}
  querySelector(s){return this.querySelectorAll(s)[0]||null;}
  closest(s){let n=this;while(n){if(matches(n,s))return n;n=n.parentElement;}return null;}
  addEventListener(name,fn){(this.listeners[name]??=[]).push(fn);}
  dispatch(name,event={}){event.target??=this;event.preventDefault??=()=>{};event.stopPropagation??=()=>{};let n=this;while(n){for(const fn of n.listeners[name]||[])fn(event);n=n.parentElement;}}
  click(){if(!this.disabled)this.dispatch('click');}
}
function decode(s){return s.replace(/&(?:amp|lt|gt|quot|#39);/g,x=>({'&amp;':'&','&lt;':'<','&gt;':'>','&quot;':'"','&#39;':"'"}[x]));}
function parse(value,root){const stack=[root];for(const token of value.match(/<[^>]*>|[^<]+/g)||[]){if(token.startsWith('</')){if(stack.length>1)stack.pop();continue;}if(token.startsWith('<')){const name=token.match(/^<([\w-]+)/);if(!name)continue;const attrs={};for(const m of token.slice(name[0].length).matchAll(/([\w:-]+)(?:="([^"]*)"|='([^']*)')?/g))attrs[m[1]]=decode(m[2]??m[3]??'');const node=new Node(name[1],attrs,root.doc);stack.at(-1).appendChild(node);if(!['INPUT','IMG','BR','HR','META','LINK','BASE'].includes(node.tagName)&&!token.endsWith('/>'))stack.push(node);}else{const node=new Node('#text',{},root.doc);node._text=decode(token);stack.at(-1).appendChild(node);}}}
function simple(n,s){if(n.tagName==='#TEXT')return false;let tag=s.match(/^[\w-]+/);if(tag&&n.tagName!==tag[0].toUpperCase())return false;for(const m of s.matchAll(/#([\w-]+)/g))if(n.id!==m[1])return false;for(const m of s.matchAll(/\.([\w-]+)/g))if(!n.classList.contains(m[1]))return false;for(const m of s.matchAll(/\[([\w-]+)(?:="([^"]*)")?\]/g))if(!(m[1] in n.attrs)||(m[2]!==undefined&&n.attrs[m[1]]!==m[2]))return false;return true;}
function matches(n,s){return s.split(',').some(selector=>{const parts=selector.trim().replace(/\s*>\s*/g,' > ').split(/\s+/);let i=parts.length-1,current=n;if(!simple(current,parts[i--]))return false;while(i>=0){if(parts[i]==='>'){current=current.parentElement;i--;if(!current||!simple(current,parts[i--]))return false;}else{current=current.parentElement;while(current&&!simple(current,parts[i]))current=current.parentElement;if(!current)return false;i--;}}return true;});}
const doc=new Node('document');doc.doc=doc;doc.documentElement=new Node('html',{},doc);doc.appendChild(doc.documentElement);doc.head=new Node('head',{},doc);doc.body=new Node('body',{},doc);doc.documentElement.appendChild(doc.head);doc.documentElement.appendChild(doc.body);doc.createElement=tag=>new Node(tag,{},doc);doc.getElementById=id=>doc.querySelector('#'+id);
doc.body.innerHTML='<div id="cram-app"></div><div id="toast"></div>';
const sent=[],window={addEventListener(){},scrollTo(){}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../cram_studio/web/app.js'),'utf8'),{document:doc,window,pycmd:msg=>sent.push(JSON.parse(msg.slice(5))),setTimeout:()=>1,clearTimeout(){},console});
const app=window.cram,root=doc.getElementById('cram-app');const select=s=>doc.querySelector(s);const click=s=>{const el=select(s);assert.ok(el,'missing '+s);el.click();};const emit=(type,data)=>app.receive(type,data);
assert.equal(sent.at(-1).action,'ready');
const cat={decks:[{id:'1',name:'Biology',count:4},{id:'2',name:'Biology::Tissues',count:8},{id:'3',name:'Design',count:5}],current:'1',history:[],settings:{model:'gemini-test',has_key:true},dark:false,media:'http://127.0.0.1:8765/'};
emit('bootstrap',cat);assert.match(select('#selection-count').textContent,/12 cards/);click('[data-mode="exam"]');click('#start');assert.equal(sent.at(-1).config.mode,'exam');assert.deepEqual(sent.at(-1).config.decks,['1']);
select('#deck-search').value='design';select('#deck-search').dispatch('input');assert.equal(select('#deck-list').querySelectorAll('.deck-row').length,1);
emit('prepare',{questions:2,available:2,skipped:0,missing:2,cached:0,has_key:true,model:'gemini-test'});click('[data-action="generate"]');assert.equal(sent.at(-1).action,'generate');emit('generating',{total:2,single:false});assert.equal(select('#gen-actions').hidden,true);click('[data-action="cancel"]');assert.equal(sent.at(-1).action,'cancel');emit('generationError',{single:false,message:'Quota reached <script>bad</script>'});assert.equal(select('#gen-actions').hidden,false);assert.ok(!select('script'));assert.match(root.textContent,/Quota reached/);
const cloze={id:'cloze:1',kind:'cloze',mode:'exam',deck:'Biology::Tissues',clue:'<b>Fill in the blanks</b><p>A <span class="ct-blank" data-blank="0">(1) ______</span> becomes <span class="ct-blank" data-blank="1">(2) ______</span>.</p>',slots:[{number:1,answer:'Cell',answer_html:'Cell',choices:['Organ','Cell','System','Tissue'],correct:1},{number:2,answer:'Tissue',answer_html:'Tissue',choices:['Organ','Cell','System','Tissue'],correct:3}]};
const io={id:'io:2',kind:'io',mode:'flash',deck:'Biology',clue:'<b>Name these structures</b>',mask_count:2,extra:'Answer explanation',slots:[],picture:'<div class="io-image"><img src="local.png"><svg><rect class="mask target"/><rect class="mask inactive"/></svg></div>'};
emit('session',{questions:[cloze,io],skipped:0});assert.equal(doc.querySelectorAll('.choice').length,8);assert.equal(select('[data-action="submit"]').disabled,true);
click('[data-slot="0"][data-choice="1"]');assert.equal(select('[data-action="submit"]').disabled,true);click('[data-slot="1"][data-choice="2"]');assert.equal(select('[data-action="submit"]').disabled,false);click('[data-action="submit"]');assert.deepEqual(sent.at(-1),{action:'grade',index:0,picks:{choices:[1,2]}});
const r0={earned:1,total:2,correct:[true,false]};emit('graded',{index:0,result:r0});assert.equal(doc.querySelectorAll('.choice.right').length,2);assert.equal(doc.querySelectorAll('.choice.wrong').length,1);click('[data-action="next"]');
const image=select('.io-image'),stage=select('#io-stage'),frame=select('#preview-viewport');assert.equal(select('[data-action="known"]').disabled,true);click('[data-action="reveal"]');assert.equal(select('.io-image'),image);assert.ok(image.classList.contains('revealed'));assert.equal(select('#io-extra').hidden,false);assert.equal(select('[data-action="known"]').disabled,false);
const initial=image.style.width;click('[data-action="zoom-in"]');assert.notEqual(image.style.width,initial);assert.equal(select('#preview-viewport'),frame);assert.equal(frame.style.height,undefined);
click('[data-action="fullscreen"]');assert.equal(stage.parentElement.id,'viewer-viewport');assert.equal(select('.io-image'),image);click('#viewer-reveal');assert.ok(!image.classList.contains('revealed'));click('#viewer-reveal');click('[data-action="close-viewer"]');assert.equal(stage.parentElement.id,'preview-viewport');assert.equal(select('.io-image'),image);
click('[data-action="known"]');assert.equal(sent.at(-1).picks.known,true);const r1={earned:1,total:1,correct:[true]};emit('graded',{index:1,result:r1});assert.equal(select('.io-image'),image);click('[data-action="next"]');assert.equal(sent.at(-1).action,'finish');
emit('finished',{earned:2,total:3,questions:2,seconds:65,history:[]});assert.match(root.textContent,/67%/);assert.match(root.textContent,/2 \/ 3/);click('[data-action="retry-mistakes"]');assert.deepEqual(sent.at(-1),{action:'retry',mistakes:true});
emit('bootstrap',cat);click('[data-action="history"]');assert.match(root.textContent,/No completed sessions/);console.log('UI interaction checks passed: deck scope, preparation/errors, cloze choices, scoring, stable IO reveal/zoom/fullscreen nodes, results, retry, history.');

// Reproduce Anki's real startup order: scripts in head, then body, then the
// asynchronously injected QWebChannel callback. The original build lost ready.
function startupEnvironment(readyState='loading',bridge=false){
  const document=new Node('document');document.doc=document;document.readyState=readyState;
  document.documentElement=new Node('html',{},document);document.appendChild(document.documentElement);
  document.head=new Node('head',{},document);document.body=new Node('body',{},document);
  document.documentElement.appendChild(document.head);document.documentElement.appendChild(document.body);
  document.createElement=tag=>new Node(tag,{},document);document.getElementById=id=>document.querySelector('#'+id);
  const calls=[],timers=new Map();let now=0,sequence=0;
  const context={document,console,addEventListener(){},scrollTo(){},setTimeout(fn,delay){const id=++sequence;timers.set(id,{fn,time:now+delay});return id;},clearTimeout(id){timers.delete(id);}};
  context.window=context;
  function connect(){context.pycmd=message=>calls.push(JSON.parse(message.slice(5)));}
  if(bridge)connect();
  function body(){document.body.innerHTML='<div id="cram-app"><p>Opening Cram Studio…</p></div><div id="toast"></div>';}
  function dom(){document.readyState='interactive';document.dispatch('DOMContentLoaded');}
  function advance(ms){const target=now+ms;let count=0;while(true){const entries=[...timers.entries()].sort((a,b)=>a[1].time-b[1].time);if(!entries.length||entries[0][1].time>target)break;const [id,timer]=entries[0];timers.delete(id);now=timer.time;timer.fn();assert.ok(++count<2000,'unbounded startup retries');}now=target;}
  function run(){vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../cram_studio/web/app.js'),'utf8'),context);}
  return {document,context,calls,connect,body,dom,advance,run};
}
{
  const e=startupEnvironment();e.run();assert.equal(e.context.cram,undefined,'must wait for body');e.body();e.dom();assert.ok(e.context.cram);assert.equal(e.calls.length,0);
  e.advance(100);assert.equal(e.calls.length,0,'must wait for QWebChannel');e.connect();e.advance(25);assert.equal(e.calls.length,1);assert.equal(e.calls[0].action,'ready');
  e.context.cram.receive('bootstrap',cat);e.advance(30000);assert.equal(e.context.cram.state.screen,'home');assert.ok(e.document.getElementById('deck-list'));assert.equal(e.calls.length,1,'only one startup request');
}
{
  const e=startupEnvironment('loading',true);e.run();assert.equal(e.calls.length,0);e.body();e.dom();e.dom();assert.equal(e.calls.length,1,'do not initialize twice');e.context.cram.receive('bootstrap',cat);assert.equal(e.context.cram.state.screen,'home');
}
{
  const e=startupEnvironment('complete',false);e.body();e.run();e.advance(10025);assert.equal(e.context.cram.state.screen,'startup-error');assert.ok(e.document.querySelector('[data-action="startup-retry"]'));
  e.connect();e.document.querySelector('[data-action="startup-retry"]').click();assert.equal(e.calls.length,1);e.context.cram.receive('bootstrap',cat);assert.equal(e.context.cram.state.screen,'home');
}
{
  const e=startupEnvironment('complete',true);e.body();e.run();e.advance(15000);assert.match(e.document.getElementById('cram-app').textContent,/not returned the deck list/);e.context.cram.receive('bootstrap',cat);assert.equal(e.context.cram.state.screen,'home','late collection response recovers');
}
{
  const e=startupEnvironment('complete',true);e.body();e.run();e.context.cram.receive('error','Collection temporarily unavailable <script>bad</script>');assert.equal(e.context.cram.state.screen,'startup-error');assert.ok(!e.document.querySelector('script'));e.document.querySelector('[data-action="startup-retry"]').click();assert.equal(e.calls.length,2);e.context.cram.receive('bootstrap',cat);e.advance(20000);assert.equal(e.context.cram.state.screen,'home');
}
console.log('Startup regression checks passed: head-before-body, delayed bridge, duplicate events, bounded timeout, retry, backend error, and late-response recovery.');

// Card filters, saved repeat preference, and the redesigned study views.
emit('bootstrap',{...cat,note_types:['Basic','Cloze'],preferences:{repeat_mistakes:false}});
assert.equal(select('#repeat-home').checked,false,'repeat defaults off');assert.ok(!select('.sidebar'),'remove dashboard sidebar');
click('[data-query="is:due"]');assert.equal(select('#anki-search').value,'is:due');
select('#filter-tag').value='Biology';select('#filter-tag').dispatch('input');
select('#filter-note').value='Cloze';select('#filter-note').dispatch('change');
select('#filter-flag').value='4';select('#filter-flag').dispatch('change');
click('#check-matches');let request=sent.at(-1);assert.equal(request.action,'preview');
assert.deepEqual(request.config.filters,{search:'is:due',tag:'Biology',flag:'4',note_type:'Cloze'});
emit('matches',{request_id:request.request_id,count:17});assert.match(select('#match-status').textContent,/17 matching cards/);
select('#anki-search').value='is:learn';select('#anki-search').dispatch('input');emit('matches',{request_id:request.request_id,count:99});assert.equal(select('#match-status').textContent,'','stale count must not overwrite changed filter');
click('#check-matches');request=sent.at(-1);emit('matches',{request_id:request.request_id,error:'Invalid Anki search'});assert.ok(select('#match-status').classList.contains('error'));
click('[data-action="clear-filters"]');assert.equal(select('#anki-search').value,'');assert.equal(select('#filter-tag').value,'');assert.ok(app.state.selected.has('1'));
click('[data-action="options"]');assert.ok(select('#options-modal'));select('#repeat-options').checked=true;select('#repeat-options').dispatch('change');assert.deepEqual(sent.at(-1),{action:'preferences',repeat_mistakes:true});emit('preferences',{repeat_mistakes:true});assert.equal(select('#repeat-home').checked,true);click('[data-action="close-options"]');
const flashA={id:'same-c1',origin:'same-c1',kind:'cloze',mode:'flash',deck:'Biology',clue:'A <span class="ct-blank" data-blank="0">(1) _____</span> forms <span class="ct-blank" data-blank="1">(2) _____</span> and <span class="ct-blank" data-blank="2">(3) _____</span>.',slots:[{number:1,answer:'Cells',answer_html:'Cells'},{number:2,answer:'Tissues',answer_html:'Tissues'},{number:3,answer:'Organs',answer_html:'Organs'}]};
const flashB={id:'b',origin:'b',kind:'basic',mode:'flash',deck:'Biology',clue:'A clue',slots:[{number:1,answer:'Answer B',answer_html:'Answer B'}]};
emit('session',{questions:[flashA,flashB],repeat_mistakes:true,original_count:2,skipped:0});
assert.equal(select('#answer').getAttribute('aria-hidden'),'true');assert.equal(select('#clue-face').getAttribute('aria-hidden'),'false');const face=select('.flash-card');
click('[data-action="reveal"]');assert.equal(select('#answer').getAttribute('aria-hidden'),'false');assert.equal(select('#clue-face').getAttribute('aria-hidden'),'true');assert.equal(select('.flash-card'),face);assert.ok(face.classList.contains('is-flipped'));assert.match(select('#answer').textContent,/A Cells forms Tissues and Organs/);assert.equal(select('#answer').querySelectorAll('.revealed-answer').length,3);
click('[data-action="unknown"]');assert.equal(sent.at(-1).picks.known,false);
const retry={...flashA,id:'same-c1/retry-1',is_retry:true};
emit('graded',{index:0,result:{earned:0,total:1,correct:[false]},queued:{position:2,question:retry},total:3});
assert.equal(select('.flash-card'),face,'grading must keep the card/image node stable');assert.equal(select('#question-count').textContent,'1 / 3');assert.match(root.textContent,/return later/);
click('[data-action="next"]');assert.equal(app.state.index,1);click('[data-action="previous"]');assert.equal(app.state.index,0);click('[data-action="next"]');
click('[data-action="reveal"]');click('[data-action="known"]');emit('graded',{index:1,result:{earned:1,total:1,correct:[true]},queued:null});click('[data-action="next"]');assert.match(root.textContent,/Try again/);
click('[data-action="options"]');assert.match(select('#options-modal').textContent,/next session/);select('#repeat-options').checked=false;select('#repeat-options').dispatch('change');emit('preferences',{repeat_mistakes:false});assert.equal(app.state.repeatActive,true,'next-session setting does not silently change the running queue');click('[data-action="close-options"]');
click('[data-action="reveal"]');click('[data-action="known"]');emit('graded',{index:2,result:{earned:1,total:1,correct:[true]},queued:null});click('[data-action="next"]');assert.equal(sent.at(-1).action,'finish');
emit('finished',{earned:1,total:2,questions:2,seconds:91,repeat_attempts:1,mastered:2,history:[]});assert.match(root.textContent,/50%/);assert.match(root.textContent,/1 repeat attempt/);assert.match(root.textContent,/2\/2 questions mastered/);
const three={...cloze,id:'three-c1',slots:[0,1,2].map((n)=>({number:n+1,ordinal:1,answer:['Cells','Tissues','Organs'][n],answer_html:['Cells','Tissues','Organs'][n],choices:['Cells','Tissues','Organs','Systems'],correct:n}))};
emit('session',{questions:[three],repeat_mistakes:false,skipped:0});assert.equal(doc.querySelectorAll('.choice').length,12);for(let i=0;i<3;i++)assert.match(doc.querySelectorAll('.slot-label')[i].textContent,new RegExp('Blank '+(i+1)));
click('[data-action="dont-know"]');assert.equal(sent.at(-1).picks.unknown,true);emit('graded',{index:0,result:{earned:0,total:3,correct:[false,false,false]},queued:null});assert.equal(doc.querySelectorAll('.choice.right').length,3);assert.equal(app.state.questions.length,1,'default off must not add repeats');
console.log('New UI checks passed: native search/refinement payloads, stale count rejection, clear-all, settings toggle, stable flashcard flip, three c1 slots, in-session retries, honest first-pass scores, previous navigation, and Don’t know.');

// 1.2 interaction regressions with a real fake clock (no network or browser download).
{
  const e=startupEnvironment('complete',true);e.body();e.run();const d=e.document,app=e.context.cram;
  const q=s=>d.querySelector(s),tap=s=>{assert.ok(q(s),'missing '+s);q(s).click();};
  const receive=(event,data)=>app.receive(event,JSON.parse(JSON.stringify(data)));
  const key=(value,extra={})=>d.dispatch('keydown',{key:value,code:value===' '?'Space':value,target:d.body,...extra});
  receive('bootstrap',{...cat,preferences:{auto_advance:true}});
  assert.equal(q('#deck-list').querySelectorAll('.deck-row').length,2);
  const parent=q('[data-branch="Biology"]');assert.equal(parent.getAttribute('aria-expanded'),'false');tap('[data-branch="Biology"]');assert.equal(q('#deck-list').querySelectorAll('.deck-row').length,3);assert.equal(q('[data-branch="Biology"]').getAttribute('aria-expanded'),'true');tap('[data-branch="Biology"]');assert.equal(q('#deck-list').querySelectorAll('.deck-row').length,2);tap('[data-branch="Biology"]');
  const rows=q('#deck-list').querySelectorAll('.deck-row');assert.match(rows[1].getAttribute('style'),/padding-left:36px/);
  q('#order').value='created_desc';q('#order').dispatch('change');tap('#start');assert.equal(e.calls.at(-1).config.order,'created_desc');assert.equal(e.calls.at(-1).config.shuffle,false);
  receive('session',{questions:[cloze,flashB],repeat_mistakes:false});
  key('2');assert.equal(q('.exam-card [data-blank="0"]').textContent,'Cell');key('ArrowUp');key('a');assert.equal(q('.exam-card [data-blank="0"]').textContent,'Organ','changed choice replaces the same blank');
  key('4');assert.equal(q('.exam-card [data-blank="1"]').textContent,'Tissue');
  tap('.exam-card [data-blank="0"]');key('b');key(' ');assert.equal(e.calls.at(-1).action,'grade');assert.deepEqual(e.calls.at(-1).picks.choices,[1,3]);
  receive('graded',{index:0,result:{earned:2,total:2,correct:[true,true]},queued:null});
  e.advance(999);assert.equal(app.state.index,0);key(' ');assert.equal(app.state.index,1);e.advance(2000);assert.equal(app.state.index,1,'Space cancels old auto timer; no double advance');
  const face=q('.flash-card'),front=q('#clue-face'),back=q('#answer');assert.equal(q('[data-action="known"]').disabled,true);
  key(' ');assert.ok(face.classList.contains('is-flipped'));assert.equal(q('.flash-card'),face);assert.equal(back.getAttribute('aria-hidden'),'false');assert.equal(front.getAttribute('aria-hidden'),'true');
  const calls=e.calls.length;face.dispatch('wheel',{ctrlKey:true,deltaY:-1});assert.equal(app.state.textZoom,1.1);assert.equal(face.style.height,undefined);assert.equal(q('#answer .face-content').style.fontSize,'32px');assert.equal(e.calls.length,calls,'card wheel does not trigger global zoom');
  q('.session-header').dispatch('wheel',{ctrlKey:true,deltaY:-1});assert.equal(e.calls.at(-1).action,'view_zoom');
  key('2');receive('graded',{index:1,result:{earned:1,total:1,correct:[true]},queued:null});e.advance(180);assert.equal(e.calls.at(-1).action,'finish');
  receive('session',{questions:[flashA,flashB]});key(' ');assert.match(q('#answer').textContent,/A Cells forms Tissues and Organs/);key('1');receive('graded',{index:0,result:{earned:0,total:1,correct:[false]},queued:null});tap('[data-action="options"]');e.advance(5000);assert.equal(app.state.index,0,'settings pauses auto advance');tap('[data-action="close-options"]');
  // Pending future choices must not discard live picks, reload the current card, or block grading.
  receive('session',{questions:[{...cloze,ready:true},{...cloze,id:'future',ready:false,slots:cloze.slots.map(s=>({number:s.number,answer:s.answer,answer_html:s.answer_html}))}]});
  receive('generating',{single:false,total:2});const card=q('.exam-card');tap('[data-slot="0"][data-choice="1"]');tap('[data-slot="1"][data-choice="3"]');
  receive('choicesReady',{questions:[{...cloze,id:'future',ready:true}],done:2,total:2});assert.equal(q('.exam-card'),card);assert.deepEqual(Array.from(app.state.picks[0]),[1,3]);assert.equal(q('[data-action="submit"]').disabled,false);
  key(' ');assert.equal(e.calls.at(-1).action,'grade');receive('generationError',{active:true,single:false,message:'Quota reached'});assert.equal(app.state.screen,'session');assert.deepEqual(Array.from(app.state.picks[0]),[1,3]);
  receive('graded',{index:0,result:{earned:2,total:2,correct:[true,true]},queued:null});e.advance(1000);assert.equal(app.state.index,1);
  receive('session',{questions:[{...cloze,ready:false,slots:cloze.slots.map(s=>({number:s.number,answer:s.answer,answer_html:s.answer_html}))}]});assert.ok(q('.waiting-card'));key('1');assert.ok(!q('.choice'));receive('generating',{single:false,total:2});receive('choicesReady',{questions:[{...cloze,ready:true}],done:2,total:2});assert.equal(d.querySelectorAll('.choice').length,8);receive('generationDone',{});assert.equal(app.state.generating,false);
  key('?');assert.ok(q('#keys-modal'));key('Escape');assert.ok(!q('#keys-modal'));
}
const css=fs.readFileSync(path.join(__dirname,'../cram_studio/web/app.css'),'utf8');assert.match(css,/transform-style:preserve-3d/);assert.match(css,/backface-visibility:hidden/);assert.match(css,/rotateX\(180deg\)/);assert.match(css,/prefers-reduced-motion/);
console.log('1.2 checks passed: live blank replacement, number/letter/Space keys, no double advance, flip faces/context, text-only versus global zoom, collapsible tree, creation order, background choices, quota recovery, and shortcut guide.');

// The scheduled-review skin has its own controller and never sends a rating.
{
  const e=startupEnvironment('complete',true),d=e.document;d.body.innerHTML='<div id="qa"></div><div id="native-bottom"><button data-ease="1">Again 1m</button><button data-ease="2">Hard 6m</button><button data-ease="3">Good 10m</button><button data-ease="4">Easy 4d</button></div>';
  e.context.pycmd=message=>e.calls.push(message.startsWith('cram_live:')?JSON.parse(message.slice(10)):{native:message});
  e.context.requestAnimationFrame=fn=>fn();
  e.context.getComputedStyle=el=>{
    let font='';for(let n=el;n&&!font;n=n.parentElement)font=n.style.fontSize;
    return {fontSize:font||(el.closest('.cl-clue')?'23px':el.closest('.cl-choice-text')?'16px':'27px'),lineHeight:'normal'};
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../cram_studio/web/live.js'),'utf8'),e.context);
  const app=e.context.cramNative,q=s=>d.querySelector(s),tap=s=>{assert.ok(q(s),'missing native '+s);q(s).click();};
  const nativeBottom=q('#native-bottom'),nativeHTML=nativeBottom.innerHTML;
  function show(packet,original='Original native card'){
    const payload=JSON.stringify(packet).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><header class="cl-header"><span class="cl-brand">ANKI CRAM</span><div class="cl-context"><div class="cl-deck">Biology</div><div class="cl-status">Anki reviews</div></div><button data-live-action="exit" aria-label="Exit ANKI CRAM">×</button></header><div id="cl-stage"><div id="cl-original">${original}</div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>`;app.mount();
  }
  const p={cid:'1',epoch:1,side:'question',display:'exam',question:{...cloze,ready:true},generating:false,reason:'',error:''};
  show(p);app.choose(1);assert.equal(q('[data-blank="0"]').textContent,'Cell');app.moveBlank(-1);app.choose(0);assert.equal(q('[data-blank="0"]').textContent,'Organ');
  app.choose(3);assert.equal(q('[data-blank="1"]').textContent,'Tissue');
  assert.ok(e.calls.every(call=>!['grade','ease1','ease2','ease3','ease4','ans'].includes(call.action)),'selecting a choice must never rate or reveal');
  show({...p,side:'answer'},'<b>Original Anki back with extra details</b>');assert.equal(d.querySelectorAll('.cl-choice.correct').length,2);assert.equal(d.querySelectorAll('.cl-choice.incorrect').length,1);assert.match(q('.cl-feedback').textContent,/1 \/ 2/);assert.ok(!q('.cl-details'),'multiple-choice reveal has no Full Anki answer panel');assert.equal(q('#cl-original').hidden,true);assert.match(q('#cl-original').textContent,/extra details/);
  assert.equal(q('#native-bottom'),nativeBottom);assert.equal(nativeBottom.innerHTML,nativeHTML,'native ratings and intervals are preserved');
  const next={...p,cid:'2',epoch:2,display:'native',question:null};show(next,'Native front <input id="typeans">');const frame=q('.cl-flip');assert.ok(frame);tap('.cl-flip');assert.equal(e.calls.at(-1).native,'ans');
  const count=e.calls.length;tap('.cl-flip');assert.equal(e.calls.length,count,'double click must not reveal twice');
  show({...next,side:'answer'},'Native back');assert.ok(q('.cl-flip').classList.contains('is-flipped'));assert.equal(q('#native-bottom'),nativeBottom);assert.equal(d.querySelectorAll('#typeans').length,0,'snapshot front must not duplicate native input IDs');
  const imagePacket={...p,cid:'3',epoch:3,display:'io',question:io};show(imagePacket,'');const image=q('.io-image');tap('[data-live-action="io-plus"]');assert.ok(image.style.width);show({...imagePacket,side:'answer'},'');assert.equal(q('.io-image'),image);assert.ok(image.classList.contains('revealed'));tap('[data-live-action="io-masks"]');assert.ok(!image.classList.contains('revealed'));tap('[data-live-action="io-full"]');assert.ok(q('#cl-custom').classList.contains('cl-full'));d.dispatch('keydown',{key:'Escape',target:d.body});assert.ok(!q('#cl-custom').classList.contains('cl-full'));
  const waiting={...p,cid:'4',epoch:4,question:{...cloze,ready:false}};show(waiting,'');assert.equal(d.querySelectorAll('.cl-choice').length,0);app.receive({...waiting,question:{...cloze,ready:true}});assert.equal(d.querySelectorAll('.cl-choice').length,8);app.receive({...waiting,cid:'stale',question:{...cloze,ready:true}});assert.equal(app.state.packet.cid,'4');
  const switched={...waiting,cid:'5',epoch:5,display:'native'};show(switched,'Original flashcard selected');const chosenFrame=q('.cl-flip');app.receive({...switched,question:{...cloze,ready:true}});assert.equal(q('.cl-flip'),chosenFrame);assert.ok(!q('.cl-exam'),'late choices must not reverse the original-flashcard selection');
  // Text zoom changes nested text once and keeps card/image nodes intact.
  show({...next,cid:'6',epoch:6,text_zoom:1.5},'<p style="font-size:20px">A <b>bold term</b><img src="fixed.png"></p>');
  const zoomFrame=q('.cl-flip'),zoomImage=q('#cl-original img'),paragraph=q('#cl-original p'),bold=q('#cl-original b');
  assert.equal(paragraph.style.fontSize,'30px');assert.equal(bold.style.fontSize,'30px');
  zoomFrame.dispatch('wheel',{ctrlKey:true,deltaY:-1});assert.equal(app.state.textZoom,1.6);assert.equal(paragraph.style.fontSize,'32px');
  assert.equal(q('.cl-flip'),zoomFrame);assert.equal(q('#cl-original img'),zoomImage);assert.equal(zoomImage.style.width,undefined);assert.equal(zoomFrame.style.height,undefined);
  assert.equal(e.calls.at(-1).action,'text_zoom');assert.equal(e.calls.at(-1).value,1.6);
  d.dispatch('keydown',{ctrlKey:true,key:'0',target:zoomFrame});assert.equal(paragraph.style.fontSize,'20px');assert.equal(bold.style.fontSize,undefined);
  q('#cram-live').dispatch('wheel',{ctrlKey:true,deltaY:-1});assert.equal(e.calls.at(-1).action,'view_zoom');
  show({...p,cid:'7',epoch:7,text_zoom:1.5});const examFrame=q('.cl-exam');examFrame.dispatch('wheel',{ctrlKey:true,deltaY:-1});assert.equal(app.state.textZoom,1.6);assert.equal(q('.cl-exam'),examFrame);
  assert.ok(!q('[data-live-action="keys"]'));assert.ok(!q('.cl-display-tools'));assert.ok(!q('#cl-keys'));
  const compiled={...p,cid:'8',epoch:8,display:'flash',question:{...flashA},text_zoom:1};show(compiled,'');
  assert.equal(q('.cl-front').querySelectorAll('.cram-blank-empty').length,3);assert.ok(!q('.cl-front').textContent.includes('(1)'));
  assert.match(q('.cl-back').textContent,/A Cells forms Tissues and Organs/);
  assert.ok(!q('.cl-back').textContent.includes('_____'));
  assert.ok(!q('.cl-flash-heading'));assert.ok(!q('.cl-text-zoom'),'the zoom display is removed while Ctrl+wheel stays functional');
  d.dispatch('keydown',{key:'ArrowDown',target:d.body});assert.equal(e.calls.at(-1).native,'ans');
  show({...compiled,side:'answer'},'Native back with extras');assert.ok(q('.cl-flip').classList.contains('is-flipped'));assert.ok(!q('.cl-details'),'compiled flashcards have no Full Anki answer panel');assert.equal(q('#cl-original').hidden,true);assert.match(q('#cl-original').textContent,/Native back with extras/);
  assert.equal(q('#native-bottom'),nativeBottom);assert.equal(nativeBottom.innerHTML,nativeHTML);
  // A forced replacement is explicit, resets picks, and never touches native ratings.
  const listQuestion={...cloze,ready:true,slots:[{number:1,answer:'1. banana\n2. mango',answer_html:'<ol><li>banana</li><li>mango</li></ol>',choices:['1. banana\n2. mango','1. apple\n2. pear','1. grape\n2. lemon','1. peach\n2. orange'],correct:0}],clue:'Fruits: <span class="ct-blank" data-blank="0">(1) _____</span>'};
  const listPacket={...p,cid:'list',epoch:9,question:listQuestion};show(listPacket,'');
  assert.equal(q('.cl-choice-text').textContent,'1. banana\n2. mango');app.choose(0);assert.equal(q('[data-blank="0"]').textContent,'1. banana\n2. mango');
  tap('[data-live-action="regenerate"]');assert.equal(e.calls.at(-1).action,'regenerate');const beforeRequest=q('.cl-exam');
  app.receive({...listPacket,generating:true});assert.equal(q('.cl-exam'),beforeRequest);assert.equal(q('[data-live-action="regenerate"]').disabled,true);assert.equal(app.state.picks[0],0);
  app.receive({...listPacket,generating:false,error:'Quota reached'});assert.equal(q('.cl-exam'),beforeRequest);assert.equal(app.state.picks[0],0);assert.match(q('#cl-notice').textContent,/Quota reached/);
  const regenerated={...listPacket,choices_revision:1,question:{...listQuestion,slots:[{...listQuestion.slots[0],choices:['1. new apple\n2. pear',...listQuestion.slots[0].choices.slice(0,3)],correct:1}]}};
  app.receive(regenerated);assert.equal(app.state.picks.length,0);assert.notEqual(q('.cl-exam'),beforeRequest);assert.equal(q('.cl-choice-text').textContent,'1. new apple\n2. pear');assert.ok(q('[data-blank="0"]').classList.contains('cram-blank-empty'));
  show({...regenerated,side:'answer'},'Full Anki answer');assert.ok(!q('[data-live-action="regenerate"]'));assert.equal(nativeBottom.innerHTML,nativeHTML);
  const navigation={...p,cid:'navigation',epoch:10,question:{...cloze,ready:true}};show(navigation,'');
  const questionPanel=q('.cl-question-panel'),navigationScene=q('.cl-exam');assert.ok(questionPanel);assert.equal(questionPanel.querySelectorAll('.cl-choice').length,0);
  app.choose(0);app.choose(3);assert.equal(q('[data-blank="0"]').textContent,'Organ');assert.equal(q('[data-blank="1"]').textContent,'Tissue');
  assert.equal(d.querySelectorAll('.cl-clue .ct-blank.cl-active').length,1);assert.equal(q('[data-blank="1"]').getAttribute('aria-current'),'true');
  tap('[data-live-slot="0"][data-live-choice="1"]');assert.equal(app.state.active,1);app.moveBlank(-1);assert.equal(app.state.active,0,'Up returns to the previous blank');app.moveBlank(-1);assert.equal(app.state.active,1,'Up wraps to the previous blank');
  q('[data-live-slot="0"][data-live-choice="2"]').dispatch('focusin');assert.equal(app.state.active,0);app.choose(2);assert.equal(q('[data-blank="0"]').textContent,'System');
  assert.equal(q('.cl-question-panel'),questionPanel);assert.equal(q('.cl-exam'),navigationScene,'navigation does not redraw the question/choices');
  show({...navigation,side:'answer'},'Full answer');const finalPicks=Array.from(app.state.picks);app.moveBlank(1);app.choose(1);assert.deepEqual(Array.from(app.state.picks),finalPicks);assert.equal(d.querySelectorAll('.cl-clue .ct-blank.cl-active').length,0);
  assert.ok(e.calls.every(call=>!call.native?.startsWith('ease')&&call.action!=='grade'),'the skin never sends a rating');
}
assert.ok(!fs.readFileSync(path.join(__dirname,'../cram_studio/web/app.js'),'utf8').includes('Click or press Space to flip'));
assert.ok(css.includes('border-bottom:0!important'),'underscore blanks have no second underline');
console.log('1.3 native UI checks passed: no auto-rating, native reveal delegation, unchanged interval buttons, cleared picks/IDs, MCQ feedback, stable occlusion nodes, viewer exit, and stale-packet rejection.');
console.log('1.4 native text zoom checks passed: rich text, reset, fixed card/image nodes, MCQ zoom, interface zoom delegation, and clean ANKI CRAM controls.');

// The first answer must have a front-paint opportunity before its transform changes.
// Queue real frame boundaries instead of running RAF synchronously as above.
for(const display of ['flash','native']){
  const e=startupEnvironment('complete',true),d=e.document,frames=[];
  d.body.innerHTML='<div id="qa"></div>';
  e.context.requestAnimationFrame=fn=>frames.push(fn);
  e.context.getComputedStyle=()=>({fontSize:'27px',lineHeight:'normal'});
  e.context.pycmd=()=>{};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../cram_studio/web/live.js'),'utf8'),e.context);
  const app=e.context.cramNative;
  function show(side,cid='first',epoch=1){
    const packet={cid,epoch,side,display,text_zoom:1,question:display==='flash'?flashA:null};
    const payload=JSON.stringify(packet).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    d.querySelector('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-stage"><div id="cl-original">Native ${side}</div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>`;app.mount();
    return d.querySelector('.cl-flip');
  }
  const paint=()=>{const callbacks=frames.splice(0);callbacks.forEach(fn=>fn());};
  show('question');const first=show('answer');
  assert.ok(!first.classList.contains('is-flipped'),display+' starts on the front');
  paint();assert.ok(!first.classList.contains('is-flipped'),display+' front survives the first paint');
  paint();assert.ok(first.classList.contains('is-flipped'),display+' flips on the next frame');
  show('question','second',2);const second=show('answer','second',2);paint();paint();assert.ok(second.classList.contains('is-flipped'));
  show('question','stale',3);const stale=show('answer','stale',3);const current=show('question','next',4);paint();paint();
  assert.equal(stale.isConnected,false);assert.ok(!stale.classList.contains('is-flipped'));assert.ok(!current.classList.contains('is-flipped'),'a stale answer callback cannot flip the next question');
  const oldAnswer=show('answer','next',4);paint();show('question','next',5);paint();assert.ok(!oldAnswer.classList.contains('is-flipped'),'same-card redraw invalidates the old animation');
}
console.log('1.4.1 first-flip checks passed: cold first card, later cards, separate paint frames, native fallback, and stale redraw cancellation.');

// Appearance updates retain active card DOM, picks and native controls.
const webScript=name=>fs.readFileSync(path.join(__dirname,'../cram_studio/web',name),'utf8');
const plain=value=>JSON.parse(JSON.stringify(value));
{
  const e=startupEnvironment('complete',true),d=e.document;vm.runInNewContext(webScript('appearance.js'),e.context);e.body();e.run();
  const A=e.context.cramAppearance,app=e.context.cram;app.receive('bootstrap',cat);app.receive('session',{questions:[cloze,io]});
  const card=d.querySelector('.exam-card'),choice=d.querySelector('[data-slot="0"][data-choice="1"]');choice.click();
  const cfg={size:{width:76,height:65},colors:{light:{exam:{card:'#fff0aa',text:'#223344'},flash:{card:'#fff0bb'}},dark:{exam:{card:'#123456'}}}};
  app.receive('appearance',cfg);assert.equal(d.querySelector('.exam-card'),card);assert.equal(d.querySelector('[data-slot="0"][data-choice="1"]'),choice);assert.equal(app.state.picks[0][0],1);
  const session=d.querySelector('.session');assert.equal(session.style.getPropertyValue('--panel'),'#fff0aa');assert.ok(!session.classList.contains('cram-sized-flash'),'MCQ keeps its own size');
  app.receive('theme',true);assert.equal(session.style.getPropertyValue('--panel'),'#123456');
  assert.ok(!d.querySelector('.under-card .shortcuts'));assert.ok(!d.querySelector('.repeat-session-note'));
  app.receive('appearance',{});assert.equal(session.style.getPropertyValue('--panel'),'');assert.equal(d.querySelector('.exam-card'),card);
  for(const mode of ['main','anki'])for(const dark of [false,true]){
    A.apply(session,cfg,mode,'flash',dark);assert.ok(session.classList.contains('cram-custom-width'));assert.equal(session.style.getPropertyValue('--cram-card-width'),'76%');assert.equal(session.style.getPropertyValue('--cram-card-height'),'calc(var(--cram-scene-height,100vh) * 0.65)');
    A.apply(session,cfg,mode,'io',dark);assert.ok(!session.classList.contains('cram-sized-flash'));assert.equal(session.style.getPropertyValue('--cram-card-height'),'');
    A.apply(session,{size:{height:60}},mode,'flash',dark);assert.ok(session.classList.contains('cram-sized-flash'));assert.ok(!session.classList.contains('cram-custom-width'),'height-only leaves renderer width intact');
    A.apply(session,{},mode,'flash',dark);assert.ok(!session.classList.contains('cram-sized-flash'));
  }
  assert.deepEqual(plain(A.normalize({size:{width:true,height:Infinity},colors:{light:{flash:{card:'url(x)',text:'#ABCDEF'}}}})),{version:1,size:{width:null,height:null},examSize:{width:null,height:null},examLayout:{questionHeight:60,choiceTextSize:18},colors:{light:{flash:{text:'#abcdef'},exam:{}},dark:{flash:{},exam:{}}}});
  assert.deepEqual(plain(A.resize({width:70,height:50},65,90,'xy',{width:1300,height:900})),{width:80,height:60});
  assert.deepEqual(plain(A.resize({width:70,height:50},9999,9999,'xy',{width:1300,height:900,maxHeight:76.7})),{width:100,height:76.7});
  assert.deepEqual(plain(A.resize({width:70,height:50},-9999,-9999,'xy',{width:1300,height:900})),{width:35,height:30});
  // Percentage geometry remains close under whole-window zoom; no stored device pixels.
  const physicalWidth=zoom=>(1360/zoom-60)*.76*zoom;
  assert.ok(Math.abs(physicalWidth(1)-physicalWidth(1.25))<12);
  app.receive('theme',false);app.receive('session',{questions:[cloze,cloze]});
  app.receive('graded',{index:0,result:{earned:2,total:2,correct:[true,true]}});assert.notEqual(app.state.autoTimer,null);
  app.receive('customizing',true);e.advance(10000);assert.equal(app.state.index,0);assert.equal(app.state.autoTimer,null);
  app.receive('customizing',false);e.advance(10000);assert.equal(app.state.index,0,'closing editor does not unexpectedly advance');
}

// Real customizer controller: trusted iframe, no write before Save, no iframe churn while dragging.
{
  const e=startupEnvironment('complete'),d=e.document,handlers={},calls=[];d.body.innerHTML='<main id="cram-customize"></main>';
  e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);e.context.pycmd=message=>calls.push(JSON.parse(message.slice('cram_custom:'.length)));
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize.js'),e.context);
  assert.deepEqual(calls,[{action:'ready'}]);const C=e.context.cramCustomize;
  C.receive('load',{config:{},dark:false,assets:'http://127.0.0.1/_addons/cram_studio/web/'});
  const q=s=>d.querySelector(s),tap=s=>{assert.ok(q(s),s);q(s).click();};let frame=q('iframe'),messages=[];
  frame.contentWindow={postMessage:data=>messages.push(data)};
  assert.equal((frame.srcdoc.match(/<\/script>/g)||[]).length,3,'iframe scripts close correctly');assert.ok(!frame.srcdoc.includes('<\\/script>'));
  const receive=(data,source=frame.contentWindow)=>handlers.message.forEach(fn=>fn({source,data}));
  receive({type:'cram-preview-ready'});assert.ok(frame.classList.contains('ready'));
  receive({type:'cram-preview-resize',size:{width:99,height:80}},{});assert.equal(C.state.config.size.width,null,'reject unrelated frame');
  receive({type:'cram-preview-resize',size:{width:82,height:64}});assert.equal(q('#size-width').value,82);assert.equal(q('iframe'),frame);assert.equal(calls.length,1);
  tap('[data-custom="reset-size"]');assert.equal(C.state.config.size.width,null);assert.equal(q('iframe'),frame);
  q('#size-height').value='999';q('#size-height').dispatch('input');tap('[data-custom="save"]');assert.equal(calls.length,1);assert.match(q('#cu-status').textContent,/highlighted/);
  q('#size-height').value='62';q('#size-height').dispatch('input');tap('[data-custom="colors"]');frame=q('iframe');frame.contentWindow={postMessage:data=>messages.push(data)};
  q('#hex-card').value='#f1e2d3';q('#hex-card').dispatch('input');assert.equal(C.state.config.colors.light.flash.card,'#f1e2d3');assert.equal(q('iframe'),frame);
  q('#preview-theme').value='dark';q('#preview-theme').dispatch('change');q('#preview-view').value='exam';q('#preview-view').dispatch('change');q('#hex-accent').value='#aabbcc';q('#hex-accent').dispatch('input');
  assert.equal(C.state.config.colors.dark.exam.accent,'#aabbcc');assert.equal(C.state.config.colors.light.flash.card,'#f1e2d3');assert.deepEqual(plain(C.state.config.colors.light.exam),{});
  q('#preview-mode').value='anki';q('#preview-mode').dispatch('change');assert.equal(messages.at(-1).mode,'anki');assert.equal(q('iframe'),frame);
  tap('[data-custom="reset-colors"]');assert.equal(C.state.config.size.height,62);assert.deepEqual(plain(C.state.config.colors),plain(e.context.cramAppearance.normalize({}).colors));
  tap('[data-custom="save"]');assert.equal(calls.at(-1).action,'save');assert.equal(calls.at(-1).config.size.height,62);
  tap('[data-custom="cancel"]');assert.deepEqual(calls.at(-1),{action:'cancel'});
}

// Preview uses actual presentation CSS/classes; pointer moves keep the card and handle mounted.
{
  const e=startupEnvironment('complete'),d=e.document,handlers={},out=[],parent={postMessage:data=>out.push(data)};
  d.body.innerHTML='';e.context.parent=parent;e.context.innerWidth=1360;e.context.innerHeight=900;e.context.requestAnimationFrame=fn=>fn();e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);
  Node.prototype.getBoundingClientRect=function(){
    const native=!!this.closest('#cram-live'),host=this.closest('#cram-live,.session'),w=1360-(native?56:60);
    const width=w*(parseFloat(host?.style.getPropertyValue('--cram-card-width'))||80)/100,height=900*(parseFloat(host?.style.getPropertyValue('--cram-card-height'))||(native?74:58))/100;
    return {width,height,left:(1360-width)/2,right:(1360+width)/2,top:120,bottom:120+height};
  };
  Node.prototype.setPointerCapture=function(id){this._capture=id;};Node.prototype.hasPointerCapture=function(id){return this._capture===id;};Node.prototype.releasePointerCapture=function(){this._capture=null;};
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize-preview.js'),e.context);
  assert.equal(out.at(-1).type,'cram-preview-ready');const config=(mode='main',view='flash',panel='size')=>handlers.message.forEach(fn=>fn({source:parent,data:{type:'cram-preview-config',mode,view,panel,theme:'light',face:'question',config:{}}}));
  config();const frame=d.querySelector('.flash-card'),handle=d.querySelector('[data-axis="xy"]');
  handle.dispatch('pointerdown',{pointerId:1,clientX:100,clientY:100});handle.dispatch('pointermove',{pointerId:1,clientX:165,clientY:145});
  assert.equal(d.querySelector('.flash-card'),frame);assert.equal(d.querySelector('[data-axis="xy"]'),handle);assert.equal(handle.hasPointerCapture(1),true);
  assert.equal(out.at(-1).type,'cram-preview-resize');assert.ok(out.at(-1).size.width>80);handle.dispatch('pointerup',{pointerId:1});assert.equal(handle.hasPointerCapture(1),false);
  config('anki');assert.ok(d.querySelector('.cl-flip'));assert.equal(d.querySelectorAll('.preview-resize').length,3);
  config('anki','exam','colors');assert.ok(d.querySelector('.cl-exam'));assert.equal(d.querySelectorAll('.preview-resize').length,0);d.querySelector('[data-sample-choice="0"]').click();assert.match(d.querySelector('[data-sample-blank]').textContent,/Tissue/);
  d.querySelector('[data-sample-flip]').click();assert.equal(d.querySelectorAll('.cl-choice.correct').length,1);assert.match(d.querySelector('.sample-footer').textContent,/AgainHardGoodEasy/);
  assert.equal(e.calls.length,0,'preview never calls the Anki bridge');
  delete Node.prototype.getBoundingClientRect;delete Node.prototype.setPointerCapture;delete Node.prototype.hasPointerCapture;delete Node.prototype.releasePointerCapture;
}
console.log('1.5 appearance checks passed: profile palette/size scopes, in-place updates, zoom geometry, cancel/reset/save, iframe security, drag capture, native preview and paused auto-continue.');

{
  const e=startupEnvironment('complete',true);e.body();e.run();const app=e.context.cram,d=e.document;
  app.receive('bootstrap',cat);
  const option='1. banana\n2. mango',question={...cloze,slots:[{number:1,answer:option,answer_html:'1. banana<br>2. mango',choices:[option,'1. apple\n2. pear','1. grape\n2. lemon','1. peach\n2. orange'],correct:0}],clue:'Fruits: <span class="ct-blank" data-blank="0">(1) _____</span>'};
  app.receive('session',{questions:[question]});assert.equal(d.querySelector('.choice-text').textContent,option);d.querySelector('[data-choice="0"]').click();assert.equal(d.querySelector('[data-blank="0"]').textContent,option);
  d.querySelector('[data-action="regenerate"]').click();assert.equal(e.calls.at(-1).action,'regenerate');assert.equal(e.calls.at(-1).index,0);
  app.receive('replace',{index:0,question});assert.deepEqual(Array.from(app.state.picks[0]),[null]);assert.equal(d.querySelector('.choice-text').textContent,option);
  assert.match(webScript('app.css'),/\.choice-text\{[^}]*white-space:pre-wrap/);assert.match(webScript('live.css'),/\.cl-choice-text\{[^}]*white-space:pre-wrap/);
}
console.log('1.5.1 choice checks passed: preserved numbered lines/blank selections, explicit regeneration in both modes, pending/failure stability, revision reset and native ratings intact.');

// Deck totals include home cards in filtered decks, descendants, and union counts.
{
  const e=startupEnvironment('complete',true);e.body();e.run();const app=e.context.cram,d=e.document,q=s=>d.querySelector(s),tap=s=>{assert.ok(q(s),s);q(s).click();};
  const decks=[{id:'1',name:'Course',count:0,total_count:3},{id:'10',name:'Course::Lesson',count:2,total_count:2,borrowed_count:1},{id:'20',name:'Course::Lesson 2',count:1,total_count:1},{id:'90',name:'Filtered',count:1,total_count:1}];
  const groups=[{did:'10',home:'10',count:1},{did:'90',home:'10',count:1},{did:'20',home:'20',count:1}];
  app.receive('bootstrap',{...cat,decks,current:'1',scope_groups:groups});assert.equal(app.state.limit,'0');assert.match(q('#selection-count').textContent,/3 cards/);assert.equal(q('[data-deck="1"]').closest('.deck-row').querySelector('.deck-count').textContent,'3');
  q('#children').checked=false;q('#children').dispatch('change');assert.match(q('#selection-count').textContent,/0 cards/);assert.equal(q('[data-deck="1"]').closest('.deck-row').querySelector('.deck-count').textContent,'0');assert.equal(q('#start').disabled,true);
  tap('[data-action="clear-decks"]');tap('[data-branch="Course"]');for(const id of ['10','90']){q('[data-deck="'+id+'"]').checked=true;q('[data-deck="'+id+'"]').dispatch('change');}
  assert.match(q('#selection-count').textContent,/2 cards/,'borrowed card counted once when both decks selected');
  tap('[data-action="regen-decks"]');assert.equal(e.calls.at(-1).action,'regen_decks');assert.deepEqual(e.calls.at(-1).config.decks,['10','90']);
  tap('[data-action="refresh-decks"]');assert.equal(e.calls.at(-1).action,'ready');tap('#start');assert.equal(e.calls.at(-1).config.limit,0);
}
console.log('1.6 deck checks passed: accurate parent/borrowed totals, overlapping selection union, include-subdeck toggles, all-question default, refresh and deck regeneration entry.');

{
  const e=startupEnvironment('complete',true);e.body();e.run();const d=e.document,app=e.context.cram,q=s=>d.querySelector(s),key=k=>d.dispatch('keydown',{key:k,target:d.body});
  app.receive('bootstrap',cat);app.receive('session',{questions:[cloze]});const panel=q('.question-panel'),scene=q('.exam-card');assert.ok(panel);assert.equal(panel.querySelectorAll('.choice').length,0);
  key('1');key('4');assert.deepEqual(Array.from(app.state.picks[0]),[0,3]);assert.equal(q('[data-blank="1"]').getAttribute('aria-current'),'true');assert.equal(d.querySelectorAll('.ct-blank.active').length,1);
  q('[data-slot="0"][data-choice="1"]').click();key('1');assert.deepEqual(Array.from(app.state.picks[0]),[1,0]);
  q('[data-slot="0"][data-choice="2"]').dispatch('focusin');key('2');assert.deepEqual(Array.from(app.state.picks[0]),[1,0]);assert.equal(app.state.activeSlot,1);
  key('ArrowUp');assert.equal(app.state.activeSlot,0);assert.equal(q('.question-panel'),panel);assert.equal(q('.exam-card'),scene);assert.ok(!e.calls.some(call=>call.action==='grade'));
  app.receive('graded',{index:0,result:{earned:0,total:2,correct:[false,false]}});assert.equal(d.querySelectorAll('.ct-blank.active').length,0);
}
{
  const e=startupEnvironment('complete',true),d=e.document;vm.runInNewContext(webScript('appearance.js'),e.context);const A=e.context.cramAppearance;
  const before=A.palette({},'main','light','exam').question,custom={colors:{light:{exam:{card:'#ffeedd',accent:'#883344'}}}};
  const auto=A.palette(custom,'main','light','exam').question;assert.notEqual(auto,before);assert.match(auto,/^#[a-f0-9]{6}$/);
  custom.colors.light.exam.question='#bbccdd';assert.equal(A.palette(custom,'main','light','exam').question,'#bbccdd');
  const host=d.createElement('div');d.body.appendChild(host);A.apply(host,custom,'main','exam',false);assert.equal(host.style.getPropertyValue('--cram-question-panel'),'#bbccdd');A.apply(host,custom,'main','flash',false);assert.equal(host.style.getPropertyValue('--cram-question-panel'),'');
  const handlers={};d.body.innerHTML='<main id="cram-customize"></main>';e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);e.context.pycmd=()=>{};vm.runInNewContext(webScript('customize.js'),e.context);const C=e.context.cramCustomize;
  C.receive('load',{config:{},dark:false,assets:'http://127.0.0.1/_addons/cram_studio/web/'});d.querySelector('[data-custom="colors"]').click();assert.equal(d.getElementById('color-question'),null,'question panel setting is MCQ only');
  const view=d.getElementById('preview-view');view.value='exam';view.dispatch('change');assert.equal(d.getElementById('question-auto').checked,true);assert.equal(d.getElementById('color-question').disabled,true);
  const initial=d.getElementById('color-question').value;d.getElementById('hex-card').value='#ffeecc';d.getElementById('hex-card').dispatch('input');assert.notEqual(d.getElementById('color-question').value,initial);assert.equal(C.state.config.colors.light.exam.question,undefined);
  d.getElementById('question-auto').checked=false;d.getElementById('question-auto').dispatch('change');assert.equal(d.getElementById('color-question').disabled,false);d.getElementById('hex-question').value='#bbaadd';d.getElementById('hex-question').dispatch('input');assert.equal(C.state.config.colors.light.exam.question,'#bbaadd');
  d.getElementById('hex-card').value='#aaffee';d.getElementById('hex-card').dispatch('input');assert.equal(C.state.config.colors.light.exam.question,'#bbaadd','explicit override stays fixed');
  d.getElementById('question-auto').checked=true;d.getElementById('question-auto').dispatch('change');assert.equal(C.state.config.colors.light.exam.question,undefined);assert.equal(d.getElementById('color-question').disabled,true);
}
console.log('1.6.1 focus/panel checks passed: arrow/number/mouse/focus blank sync, one active highlight, stable question nodes, answer-side guards and automatic/custom question colors.');

// 1.7: Independent surfaces, card-derived palettes, and exact theme defaults.
{
  const e=startupEnvironment('complete',true),d=e.document;vm.runInNewContext(webScript('appearance.js'),e.context);const A=e.context.cramAppearance;
  const base={auto:true,card:'#ffd9da'},config=(theme,view,values)=>({colors:{[theme]:{[view]:values}}});
  for(const mode of ['main','anki'])for(const theme of ['light','dark'])for(const view of ['flash','exam']){
    for(const card of ['#ffffff','#000000','#ffd9da','#1c1830','#777777','#8a438c','#00ff00','#ffff00','#ff0000','#0000ff']){
      const p=A.palette(config(theme,view,{auto:true,card}),mode,theme,view);
      for(const [text,bg] of [['text','card'],['buttonText','buttonBackground'],['revealText','revealBackground'],['correct','correctBackground'],['incorrect','incorrectBackground'],['answerText','answerBackground'],['selectionText','selection'],['primaryText','accent']])assert.ok(A.contrast(p[text],p[bg])>=4.5,`${mode}/${theme}/${card} ${text} contrast`);
    }
    const p=A.palette(config(theme,view,base),mode,theme,view),manual={...base,answerText:'#123456',answerBackground:'#aabbcc',buttonBackground:'#223344',revealBackground:'#ccbbaa',correct:'#654321',correctBackground:'#abcdef'};
    const m=A.palette(config(theme,view,manual),mode,theme,view);
    for(const role of Object.keys(manual).filter(key=>!['auto','card'].includes(key)))assert.equal(m[role],manual[role],role+' is independently pinned');
    const changed=A.palette(config(theme,view,{...base,correct:'#aa0000',correctBackground:'#ffaaaa'}),mode,theme,view);assert.equal(changed.answerText,p.answerText);assert.equal(changed.answerBackground,p.answerBackground,'Correct cannot recolor the revealed answer');
    const recolored=A.palette(config(theme,view,{...base,card:'#243b42'}),mode,theme,view);assert.notEqual(recolored.buttonBackground,p.buttonBackground);assert.notEqual(recolored.revealBackground,p.revealBackground);assert.notEqual(recolored.answerBackground,p.answerBackground);
    const host=d.createElement('div');d.body.appendChild(host);A.apply(host,config(theme,view,manual),mode,view,theme==='dark');assert.equal(host.style.getPropertyValue('--cram-answer-text'),'#123456');assert.equal(host.style.getPropertyValue('--cram-correct-text'),'#654321');assert.ok(host.classList.contains('cram-answer-text-custom'));
    A.apply(host,{},mode,view,theme==='dark');for(const key of ['--cram-answer-text','--cram-answer-bg','--cram-button-bg','--cram-reveal-bg','--cram-correct-bg'])assert.equal(host.style.getPropertyValue(key),'',key+' reset to renderer CSS');assert.ok(!host.classList.contains('cram-answer-text-custom'));
    const defaults=A.palette({},mode,theme,view);assert.equal(defaults.card,A.defaults[mode][theme].card);assert.equal(defaults.background,A.defaults[mode][theme].background);assert.ok(A.contrast(defaults.answerText,defaults.card)>=4.5);
  }
  // Native bottom bar only gets colors: its original nodes, handlers and intervals remain.
  d.body.innerHTML='<div id="middle"><button id="ansbut">Show Answer</button><button data-ease="1">Again<span class="nobold">1m</span></button><button data-ease="4">Easy<span class="nobold">4d</span></button></div>';
  const native=d.getElementById('middle'),nativeHTML=native.innerHTML,answer=d.getElementById('ansbut');let clicks=0;answer.addEventListener('click',()=>clicks++);
  const cfg=config('light','flash',{...base,buttonBackground:'#112233',revealBackground:'#445566',revealText:'#ffffff'});
  A.applyBottom(cfg,'flash',false);assert.equal(d.body.style.getPropertyValue('--cram-button-bg'),'#112233');assert.equal(d.body.style.getPropertyValue('--cram-reveal-bg'),'#445566');assert.equal(d.getElementById('middle'),native);assert.equal(native.innerHTML,nativeHTML);answer.click();assert.equal(clicks,1);
  A.applyBottom({},'flash',false);assert.ok(!d.body.classList.contains('cram-bottom-custom'));assert.equal(d.body.style.getPropertyValue('--cram-button-bg'),'');A.applyBottom(cfg,'io',false);assert.ok(!d.body.classList.contains('cram-bottom-custom'));
}
{
  const e=startupEnvironment('complete',true),d=e.document,handlers={},calls=[];d.body.innerHTML='<main id="cram-customize"></main>';
  e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);e.context.pycmd=msg=>calls.push(JSON.parse(msg.slice('cram_custom:'.length)));
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize.js'),e.context);const C=e.context.cramCustomize,A=e.context.cramAppearance;
  C.receive('load',{config:{size:{width:82,height:60}},dark:false,assets:'http://127.0.0.1/_addons/cram_studio/web/'});const q=s=>d.querySelector(s),edit=(id,value)=>{q('#'+id).value=value;q('#'+id).dispatch('input');},toggle=(role,value)=>{q('#'+role+'-auto').checked=value;q('#'+role+'-auto').dispatch('change');};q('[data-custom="colors"]').click();
  const frame=q('iframe');edit('hex-card','#ffd9da');assert.deepEqual(plain(C.state.config.colors.light.flash),{auto:true,card:'#ffd9da'});assert.equal(q('#scheme').value,'auto');assert.equal(q('#color-answerText').disabled,true);
  q('[data-color-group="revealed-answer"]').setAttribute('open','');q('.cu-sidebar').scrollTop=220;
  toggle('answerText',false);assert.notEqual(q('[data-color-group="revealed-answer"]').getAttribute('open'),null);assert.equal(q('.cu-sidebar').scrollTop,220);edit('hex-answerText','#443366');toggle('buttonBackground',false);edit('hex-buttonBackground','#eeccff');toggle('revealBackground',false);edit('hex-revealBackground','#ddeeff');toggle('correct',false);edit('hex-correct','#007755');
  assert.equal(q('#color-answerText').value,'#443366');edit('hex-card','#ccaacc');assert.equal(C.state.config.colors.light.flash.answerText,'#443366');assert.equal(q('#color-buttonBackground').value,'#eeccff');assert.equal(q('#color-revealBackground').value,'#ddeeff');assert.equal(q('iframe'),frame,'color input cannot rebuild the preview');
  toggle('answerText',true);assert.equal(C.state.config.colors.light.flash.answerText,undefined);assert.notEqual(q('#color-answerText').value,'#443366');assert.equal(C.state.config.colors.light.flash.correct,'#007755');
  q('#scheme').value='auto';q('#scheme').dispatch('change');assert.deepEqual(plain(C.state.config.colors.light.flash),{auto:true,card:'#ccaacc'},'Automatic discards manual pins but keeps the chosen Card');
  q('#preview-theme').value='dark';q('#preview-theme').dispatch('change');edit('hex-card','#213546');q('#preview-view').value='exam';q('#preview-view').dispatch('change');edit('hex-card','#221133');toggle('answerBackground',false);edit('hex-answerBackground','#112211');q('#preview-mode').value='anki';q('#preview-mode').dispatch('change');assert.ok(q('#hex-revealBackground'),'native MCQ Show Answer has its own controls');
  q('[data-custom="reset-colors"]').click();assert.deepEqual(plain(C.state.config.colors),plain(A.normalize({}).colors));assert.deepEqual(plain(C.state.config.size),{width:82,height:60});assert.equal(q('iframe'),frame);assert.equal(q('#color-card').value,A.defaults.anki.dark.card,'reset uses the original dark card, not a custom base');
  q('#preview-theme').value='light';q('#preview-theme').dispatch('change');assert.equal(q('#color-card').value,'#ffffff');q('[data-custom="save"]').click();assert.equal(calls.at(-1).action,'save');assert.deepEqual(calls.at(-1).config.colors,plain(A.normalize({}).colors));
  assert.equal(calls.filter(call=>call.action==='save').length,1,'draft edits never write the profile');
}
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();vm.runInNewContext(webScript('appearance.js'),e.context);e.run();const app=e.context.cram;app.receive('bootstrap',cat);app.receive('session',{questions:[flashB]});
  app.receive('appearance',{colors:{light:{flash:{answerText:'#123456',answerBackground:'#eeeecc',correct:'#990000'}}}});const host=d.querySelector('.flash-card'),answer=d.querySelector('.answer-value');assert.equal(answer.textContent,'Answer B');d.querySelector('[data-action="reveal"]').click();assert.equal(d.querySelector('.flash-card'),host);assert.equal(d.querySelector('.answer-value'),answer);assert.equal(d.querySelector('.session').style.getPropertyValue('--cram-answer-text'),'#123456');assert.ok(host.classList.contains('is-flipped'));
}
console.log('1.7 color checks passed: independent answer/button/feedback surfaces, readable automatic palettes, manual pins, exact all-theme reset, stable preview/cards, Basic answer markup, and unchanged native button nodes/actions/intervals.');

// 1.8: image readability, image drafts, color locators and initially collapsed decks.
const tinyPng='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aNOcAAAAASUVORK5CYII=';
{
  const e=startupEnvironment('complete',true),d=e.document;vm.runInNewContext(webScript('appearance.js'),e.context);const A=e.context.cramAppearance;
  const photo={data:tinyPng,name:'image.png',opacity:90,overlay:0,smart:true};
  for(const base of ['#ffffff','#171e36','#ffd9da','#ffeebb']){
    const text=base==='#171e36'?'#ffffff':'#282e3e',shown=A.imagePresentation(photo,base,[text]);assert.ok(shown.alpha<.9);for(const pixel of ['#000000','#ffffff'])assert.ok(A.contrast(text,A.blend(pixel,base,shown.alpha))>=Math.min(4.5,A.contrast(text,base))-1e-6);
    const manual=A.imagePresentation({...photo,smart:false},base,[text]);assert.equal(manual.alpha,.9);assert.ok(manual.style.includes(tinyPng));assert.equal(A.imagePresentation({...photo,opacity:0},base,[text]).style,'none');
  }
  assert.deepEqual(plain(A.normalizeImages({card:{...photo,data:'https://bad.test/photo.png'}})),{});assert.deepEqual(plain(A.normalizeImages({card:{...photo,data:'data:image/svg+xml;base64,PHN2Zz4='}})),{});
  const cfg={images:{card:{...photo,smart:false},background:{...photo,overlay:50}}},host=d.createElement('main');d.body.appendChild(host);
  for(const mode of ['main','anki']){
    A.apply(host,cfg,mode,'flash',false);assert.ok(host.style.getPropertyValue('--cram-card-image').includes(tinyPng));const first=host.style.getPropertyValue('--cram-card-image');
    A.apply(host,{...cfg,images:{...cfg.images,card:{...photo,smart:false,opacity:15}}},mode,'flash',false);assert.notEqual(host.style.getPropertyValue('--cram-card-image'),first);assert.equal(host.parentElement,d.body);
    A.apply(host,{},mode,'flash',false);assert.equal(host.style.getPropertyValue('--cram-card-image'),'none');A.apply(host,cfg,mode,'io',false);assert.equal(host.style.getPropertyValue('--cram-card-image'),'');if(mode==='anki')assert.equal(d.body.style.getPropertyValue('--cram-page-image'),'');
  }
}
{
  const e=startupEnvironment('complete',true),d=e.document,handlers={},calls=[];d.body.innerHTML='<main id="cram-customize"></main>';e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);e.context.pycmd=msg=>calls.push(JSON.parse(msg.slice('cram_custom:'.length)));
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize.js'),e.context);const C=e.context.cramCustomize,q=s=>d.querySelector(s);
  C.receive('load',{config:{size:{height:60}},dark:false,assets:'http://127.0.0.1/_addons/cram_studio/web/'});q('[data-custom="colors"]').click();let frame=q('iframe'),messages=[];frame.contentWindow={postMessage:m=>messages.push(m)};
  const before=JSON.stringify(C.state.config);q('[data-locate-color="answerText"]').dispatch('dblclick');assert.equal(messages.at(-1).locate.role,'answerText');assert.equal(JSON.stringify(C.state.config),before);assert.equal(q('iframe'),frame);assert.equal(calls.filter(x=>x.action==='save').length,0);
  q('[data-locate-color="card"]').dispatch('keydown',{key:'Enter'});assert.equal(messages.at(-1).locate.role,'card');
  q('[data-custom="images"]').click();frame=q('iframe');frame.contentWindow={postMessage:m=>messages.push(m)};q('[data-image-upload="card"]').click();assert.deepEqual(calls.at(-1),{action:'choose-image',target:'card'});assert.equal(C.state.imagePending,true);
  const image={data:tinyPng,name:'local.png',opacity:35,overlay:35,smart:true};C.receive('image',{target:'card',image});assert.equal(C.state.config.images.card.data,tinyPng);assert.equal(C.state.imagePending,false);assert.equal(q('iframe'),frame);
  const slider=q('#image-opacity-card');slider.value='72';slider.dispatch('input');assert.equal(C.state.config.images.card.opacity,72);assert.equal(q('#image-opacity-card'),slider);assert.equal(q('iframe'),frame);q('[data-image-setting="smart"]').checked=false;q('[data-image-setting="smart"]').dispatch('change');assert.equal(C.state.config.images.card.smart,false);
  q('[data-image-upload="background"]').click();C.receive('image',{target:'background',image:null});assert.equal(C.state.config.images.background,undefined);assert.equal(C.state.config.images.card.opacity,72);
  q('[data-custom="colors"]').click();q('[data-custom="reset-colors"]').click();assert.equal(C.state.config.images.card.opacity,72,'color reset leaves chosen images intact');q('[data-custom="images"]').click();q('[data-custom="save"]').click();assert.equal(calls.at(-1).config.images.card.opacity,72);
  q('[data-custom="reset-images"]').click();assert.equal(C.state.config.images,undefined);assert.equal(C.state.config.size.height,60);q('[data-custom="cancel"]').click();assert.equal(calls.at(-1).action,'cancel');
}
{
  const e=startupEnvironment('complete'),d=e.document,handlers={},out=[],parent={postMessage:data=>out.push(data)};d.body.innerHTML='';e.context.parent=parent;e.context.innerWidth=1360;e.context.innerHeight=900;e.context.requestAnimationFrame=fn=>fn();e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);
  Node.prototype.getBoundingClientRect=function(){return {left:120,top:220,width:360,height:80,right:480,bottom:300};};
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize-preview.js'),e.context);
  let id=0;const show=(mode,view,role)=>handlers.message.forEach(fn=>fn({source:parent,data:{type:'cram-preview-config',mode,view,panel:'colors',theme:'light',face:'question',config:{},locate:role?{role,label:role,id:++id}:null}}));
  for(const mode of ['main','anki'])for(const view of ['flash','exam'])for(const role of e.context.cramAppearance.roles){
    if(view==='flash'&&['question','selection','selectionText'].includes(role)||mode==='anki'&&['primaryText'].includes(role)||mode==='anki'&&view==='flash'&&['correct','correctBackground','incorrect','incorrectBackground'].includes(role)||mode==='main'&&view==='exam'&&role.startsWith('reveal'))continue;
    show(mode,view,role);assert.ok(d.getElementById('preview-locator'),mode+'/'+view+'/'+role+' points to a visible component');assert.equal(d.getElementById('preview-locator').dataset.colorRole,role);
    if(role==='answerText')assert.equal(out.at(-1).face,'answer');
  }
  show('main','exam','selection');assert.ok(d.querySelector('.choice.selected'));const panel=d.querySelector('.question-panel');d.querySelector('[data-close-locator]').click();assert.equal(d.getElementById('preview-locator'),null);assert.equal(d.querySelector('.question-panel'),panel);assert.equal(out.at(-1).type,'cram-preview-locate-done');
  show('anki','flash','answerText');e.advance(7000);assert.equal(d.getElementById('preview-locator'),null);assert.equal(e.calls.length,0,'mockup locator never calls Anki or Gemini');delete Node.prototype.getBoundingClientRect;
}
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();e.run();const app=e.context.cram,q=s=>d.querySelector(s);app.receive('bootstrap',cat);assert.equal(q('[data-branch="Biology"]').getAttribute('aria-expanded'),'false');assert.equal(q('[data-deck="2"]'),null);
  q('#deck-search').value='Biology';q('#deck-search').dispatch('input');assert.ok(q('[data-deck="2"]'),'search finds a child through collapsed parents');q('#deck-search').value='';q('#deck-search').dispatch('input');assert.equal(q('[data-deck="2"]'),null);q('[data-branch="Biology"]').click();app.receive('bootstrap',cat);assert.equal(q('[data-branch="Biology"]').getAttribute('aria-expanded'),'true','refresh preserves a branch the user expanded');
}
console.log('1.8 checks passed: local image drafts/validation/readability, stable image controls, source-checked locators for every visible color role, automatic preview states, locator dismissal and collapsed searchable decks.');

// 1.9: standard hue relationships, contrast, manual pins, and precise color pointers.
{
  const e=startupEnvironment('complete',true);vm.runInNewContext(webScript('appearance.js'),e.context);const A=e.context.cramAppearance;
  const hue=color=>{const [r,g,b]=[1,3,5].map(i=>parseInt(color.slice(i,i+2),16)/255),hi=Math.max(r,g,b),lo=Math.min(r,g,b),d=hi-lo;return (((hi===r?(g-b)/d:hi===g?(b-r)/d+2:(r-g)/d+4)*60)%360+360)%360;};
  const offsets={monochromatic:[0,0,0],analogous:[30,-30,0],complementary:[180,0,180],split_complementary:[150,210,0],triadic:[120,240,0],tetradic:[180,60,240],square:[180,90,270]},base='#e080a0';
  for(const [id,angles] of Object.entries(offsets)){
    const tones=A.harmonyColors(base,false,'#4255ff',id);for(const [i,key] of ['primary','secondary','tertiary'].entries()){const delta=(hue(tones[key])-hue(base)-angles[i]+720)%360;assert.ok(Math.min(delta,360-delta)<2,id+' '+key+' follows the requested hue relation');}
    for(const mode of ['main','anki'])for(const theme of ['light','dark'])for(const view of ['flash','exam'])for(const card of ['#ffffff','#000000','#ffd9da','#1c1830','#777777','#00ff00','#ffff00','#ff0000','#0000ff']){
      const config={colors:{[theme]:{[view]:{auto:true,card,harmony:id}}}},p=A.palette(config,mode,theme,view);
      assert.equal(p.card,card);for(const [fg,bg] of [['text','card'],['buttonText','buttonBackground'],['revealText','revealBackground'],['answerText','answerBackground'],['selectionText','selection'],['primaryText','accent'],['correct','correctBackground'],['incorrect','incorrectBackground']])assert.ok(A.contrast(p[fg],p[bg])>=4.5,`${id}/${mode}/${theme}/${card} ${fg}`);
      const pinned={...config,colors:{[theme]:{[view]:{...config.colors[theme][view],accent:'#123456',answerText:'#654321',buttonBackground:'#abcdef'}}}},manual=A.palette(pinned,mode,theme,view);assert.equal(manual.accent,'#123456');assert.equal(manual.answerText,'#654321');assert.equal(manual.buttonBackground,'#abcdef');const green=[1,3,5].map(i=>parseInt(p.correct.slice(i,i+2),16)),red=[1,3,5].map(i=>parseInt(p.incorrect.slice(i,i+2),16));assert.ok(green[1]>green[0]&&green[1]>green[2]&&red[0]>red[1]&&red[0]>red[2],'feedback keeps its green/red meaning while tones adapt for contrast');
    }
  }
  const old={colors:{light:{flash:{auto:true,card:base}}}},current={colors:{light:{flash:{auto:true,card:base,harmony:'current'}}}};assert.deepEqual(plain(A.palette(old,'main','light','flash')),plain(A.palette(current,'main','light','flash')));
  const gray=A.harmonyColors('#ffffff',false,'#4255ff','monochromatic').primary;assert.equal(gray.slice(1,3),gray.slice(3,5));assert.equal(gray.slice(3,5),gray.slice(5,7));
  const designs=new Set(Object.keys(offsets).map(id=>JSON.stringify(A.palette({colors:{light:{exam:{auto:true,card:base,harmony:id}}}},'main','light','exam'))));assert.equal(designs.size,7,'schemes produce distinct full palettes');
}
{
  const e=startupEnvironment('complete',true),d=e.document,handlers={},sent=[];d.body.innerHTML='<main id="cram-customize"></main>';e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);e.context.pycmd=msg=>sent.push(JSON.parse(msg.slice('cram_custom:'.length)));
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize.js'),e.context);const C=e.context.cramCustomize,q=s=>d.querySelector(s);
  C.receive('load',{config:{size:{height:64},images:{card:{data:tinyPng,name:'local.png',opacity:30,overlay:20,smart:true}}},dark:false,assets:'http://127.0.0.1/_addons/cram_studio/web/'});q('[data-custom="colors"]').click();const frame=q('iframe');assert.equal(q('#harmony').disabled,true);q('#scheme').value='auto';q('#scheme').dispatch('change');assert.equal(q('#harmony').disabled,false);
  q('#harmony').value='triadic';q('#harmony').dispatch('change');assert.equal(C.state.config.colors.light.flash.harmony,'triadic');assert.equal(q('#scheme option[selected]').value,'auto');assert.equal(q('iframe'),frame);q('#answerText-auto').checked=false;q('#answerText-auto').dispatch('change');q('#hex-answerText').value='#123456';q('#hex-answerText').dispatch('input');q('#harmony').value='square';q('#harmony').dispatch('change');assert.equal(C.state.config.colors.light.flash.answerText,'#123456','harmony preserves manual pins');assert.equal(q('#scheme option[selected]').value,'custom');
  q('#scheme').value='auto';q('#scheme').dispatch('change');assert.equal(C.state.config.colors.light.flash.harmony,'square');assert.equal(C.state.config.colors.light.flash.answerText,undefined);q('[data-custom="save"]').click();assert.equal(sent.at(-1).config.colors.light.flash.harmony,'square');
  q('[data-custom="reset-colors"]').click();assert.equal(q('#harmony').disabled,true);assert.equal(q('#harmony option[selected]').value,'current');assert.equal(C.state.config.colors.light.flash.harmony,undefined);assert.equal(C.state.config.images.card.data,tinyPng);assert.equal(C.state.config.size.height,64);
}
{
  const e=startupEnvironment('complete'),d=e.document,handlers={},out=[],parent={postMessage:m=>out.push(m)};d.body.innerHTML='';e.context.parent=parent;e.context.innerWidth=1360;e.context.innerHeight=900;e.context.requestAnimationFrame=fn=>fn();e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);
  Node.prototype.getBoundingClientRect=function(){return {left:120,top:220,width:360,height:80,right:480,bottom:300};};
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize-preview.js'),e.context);let id=0;const show=(role,mode='main',view='exam')=>handlers.message.forEach(fn=>fn({source:parent,data:{type:'cram-preview-config',mode,view,panel:'colors',theme:'light',face:'question',config:{colors:{light:{exam:{auto:true,harmony:'triadic',card:'#ffd9da'}}}},locate:{role,label:role,id:++id}}}));
  for(const mode of ['main','anki'])for(const [role,property,target] of [['buttonText','color',mode==='main'?'choice-text':'cl-choice-text'],['selectionText','color',mode==='main'?'choice-text':'cl-choice-text'],['correct','color',mode==='main'?'choice-text':'cl-choice-text'],['incorrectBackground','background-color',mode==='main'?'choice':'cl-choice'],['border','border-top-color',mode==='main'?'exam-card':'cl-exam']]){
    show(role,mode);const overlay=d.getElementById('preview-locator');assert.equal(overlay.dataset.colorProperty,property);assert.ok(overlay.dataset.colorTarget.includes(target));assert.ok(!overlay.dataset.colorTarget.includes('choice-key')&&!overlay.dataset.colorTarget.includes('cl-key'),'text colors never point to key circles');assert.match(overlay.textContent,/#[0-9a-f]{6}/);
  }
  show('background','anki');const ring=d.querySelector('.preview-locate-ring');assert.ok(parseFloat(ring.style.top)<740,'background pointer avoids native footer');show('buttonText','main','flash');assert.equal(out.at(-1).mode,'anki');assert.equal(d.querySelector('.preview-color-example'),null,'no invented component is used as a locator target');assert.equal(d.getElementById('preview-locator').dataset.colorProperty,'color');
  e.context.getComputedStyle=()=>({getPropertyValue:()=> 'rgb(1, 2, 3)'});show('buttonText');assert.ok(d.querySelector('.preview-locate-ring'),'a known semantic target remains locatable when default styling differs');assert.equal(d.getElementById('preview-locator').dataset.shownColor,'#010203');assert.match(d.getElementById('preview-locator').textContent,/Shown: #010203/);delete Node.prototype.getBoundingClientRect;
}
console.log('1.9 checks passed: seven hue harmonies, preserved current palette and manual colors, readable automatic pairs, persistence/reset, precise text/background/border targets, footer exclusion and separate shown/setting values.');

// 1.10: use a browser-like NodeList (no Array.find) and semantic color bindings.
function inspectorEnvironment(){
  const e=startupEnvironment('complete'),d=e.document,handlers={},out=[],parent={postMessage:m=>out.push(m)};
  d.body.innerHTML='';e.context.parent=parent;e.context.innerWidth=1360;e.context.innerHeight=900;e.context.requestAnimationFrame=fn=>fn();e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);
  const queryAll=d.querySelectorAll.bind(d);
  d.querySelectorAll=selector=>{const nodes=queryAll(selector);return Object.assign({length:nodes.length,forEach:fn=>nodes.forEach(fn),[Symbol.iterator]:()=>nodes[Symbol.iterator]()},nodes);};
  Node.prototype.getBoundingClientRect=function(){return {left:120,top:220,width:360,height:80,right:480,bottom:300};};
  e.context.getComputedStyle=()=>({getPropertyValue:()=> 'rgb(68, 68, 68)'});
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize-preview.js'),e.context);
  const A=e.context.cramAppearance,labels=Object.fromEntries(A.roles.map(role=>[role,role]));let serial=0;
  let context={mode:'main',view:'exam',theme:'light',face:'question',panel:'colors',inspect:true,config:{colors:{light:{exam:Object.fromEntries(A.roles.map(role=>[role,'#444444']))}}},colorLabels:labels,locate:null};
  const send=(changes={},source=parent)=>{context={...context,...changes};handlers.message.forEach(fn=>fn({source,data:{type:'cram-preview-config',...context}}));};
  const locate=(role,mode='main',view='exam',theme='light')=>send({mode,view,theme,inspect:false,face:'question',locate:{role,label:role,id:++serial}});
  const q=selector=>d.querySelector(selector),roles=()=>Array.from(d.querySelectorAll('[data-inspect-role]')).map(n=>n.dataset.inspectRole);
  send();return {e,d,q,out,send,locate,roles,labels,parent};
}
{
  const t=inspectorEnvironment(),{d,q,locate}=t;
  for(const mode of ['main','anki'])for(const view of ['flash','exam'])for(const theme of ['light','dark'])for(const role of ['buttonText','buttonBackground','correct','correctBackground','incorrect','incorrectBackground','selection','selectionText']){
    if(view==='flash'&&(['selection','selectionText'].includes(role)||mode==='anki'&&role.startsWith('correct')||mode==='anki'&&role.startsWith('incorrect')))continue;
    locate(role,mode,view,theme);assert.ok(q('#preview-locator'),[mode,view,theme,role].join('/')+' handles real NodeList semantics');
    assert.equal(q('#preview-locator').dataset.colorRole,role);assert.ok(q('.preview-locate-ring'));
  }
  delete Node.prototype.getBoundingClientRect;
}
{
  const t=inspectorEnvironment(),{d,q,send,roles,out,e}=t;
  const choice=q('[data-sample-choice="0"]'),text=choice.querySelector('.choice-text');text.click();
  assert.deepEqual(roles(),['buttonText','buttonBackground','border'],'overlapping text/background/border are offered separately even with identical colors');
  assert.ok(q('[data-sample-choice="0"]')===choice,'inspection does not select an answer or rebuild the card');assert.ok(!choice.classList.contains('selected'));
  q('[data-inspect-index="1"]').click();assert.equal(out.at(-1).role,'buttonBackground');assert.equal(out.at(-1).property,'background-color');assert.equal(q('#preview-locator').dataset.colorTarget,'choice ');
  assert.equal(q('#preview-inspect-menu'),null);send({config:{colors:{light:{exam:{buttonBackground:'#123456'}}}}});assert.ok(q('[data-sample-choice="0"]')===choice,'live color edits retain exact component nodes');assert.equal(q('#preview-locator').dataset.settingColor,'#123456');
  text.click();q('[data-inspect-index="0"]').click();assert.equal(out.at(-1).role,'buttonText');assert.ok(q('#preview-locator').dataset.colorTarget.includes('choice-text'));
  text.click();q('[data-inspect-index="2"]').click();assert.equal(out.at(-1).role,'border');assert.equal(q('#preview-locator').dataset.colorProperty,'border-top-color');
  const before=out.length;send({mode:'anki'},{postMessage(){}});assert.equal(q('#cram-live'),null,'foreign windows cannot change inspector context');assert.equal(out.length,before);
  d.dispatch('keydown',{key:'Escape'});assert.equal(out.at(-1).type,'cram-preview-inspect-done');assert.equal(q('#preview-locator'),null);assert.ok(!d.body.classList.contains('cram-inspecting'));assert.equal(e.calls.length,0,'inspector never calls the Anki/Gemini bridge');
  delete Node.prototype.getBoundingClientRect;
}
{
  const t=inspectorEnvironment(),{d,q,send,roles,out}=t;
  send({inspect:false});q('[data-sample-choice="1"]').click();const selected=q('.choice.selected');assert.ok(selected);
  send({inspect:true});selected.querySelector('.choice-key').click();assert.deepEqual(roles(),['accent','card','selectionText','selection','accent'],'selected letter badge and surrounding choice stay distinct');
  q('[data-inspect-index="1"]').click();assert.equal(out.at(-1).role,'card');assert.ok(q('#preview-locator').dataset.colorTarget.includes('choice-key'));
  q('[data-sample-choice="0"] .choice-key').click();assert.match(q('#preview-inspect-menu').textContent,/no separate color setting/);assert.deepEqual(roles(),['buttonText','buttonBackground','border']);
  q('.slot-label').click();assert.deepEqual(roles(),['accent','card','border']);
  send({mode:'anki',face:'answer'});q('.cl-choice.correct .cl-choice-text').click();assert.deepEqual(roles(),['correct','correctBackground','correct']);q('[data-inspect-index="1"]').click();assert.equal(out.at(-1).role,'correctBackground');
  q('.cl-choice.incorrect .cl-choice-text').click();assert.deepEqual(roles(),['incorrect','incorrectBackground','incorrect']);
  q('.cl-revealed-answer').click();assert.deepEqual(roles(),['answerText','answerBackground','question','card','border']);q('[data-inspect-index="2"]').click();assert.equal(out.at(-1).role,'question');assert.equal(q('#preview-locator').dataset.colorTarget,'cl-question-panel');
  q('.cl-revealed-answer').click();q('[data-inspect-index="3"]').click();assert.equal(out.at(-1).role,'card');assert.equal(q('#preview-locator').dataset.colorTarget,'cl-exam');
  send({view:'flash',face:'question'});const card=q('.cl-flip');card.click();assert.ok(!card.classList.contains('is-flipped'),'pick mode prevents card flips');assert.deepEqual(roles(),['card','border']);
  q('#ansbut').click();assert.deepEqual(roles(),['revealText','revealBackground']);assert.ok(q('#ansbut'),'pick mode never reveals an answer');
  send({face:'answer'});assert.ok(!q('.sample-original'),'customizer matches the clean answer layout');q('.sample-footer button[data-ease="2"]').click();assert.deepEqual(roles(),['buttonText','buttonBackground']);
  send({panel:'size',inspect:true});assert.ok(!d.body.classList.contains('cram-inspecting'),'color inspection cannot hijack the size mockup');
  delete Node.prototype.getBoundingClientRect;
}
{
  const e=startupEnvironment('complete',true),d=e.document,handlers={},calls=[];d.body.innerHTML='<main id="cram-customize"></main>';e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);e.context.pycmd=msg=>calls.push(JSON.parse(msg.slice('cram_custom:'.length)));
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize.js'),e.context);const C=e.context.cramCustomize,q=s=>d.querySelector(s);
  C.receive('load',{config:{size:{height:64}},dark:false,assets:'http://127.0.0.1/_addons/cram_studio/web/'});q('[data-custom="colors"]').click();const frame=q('iframe'),messages=[];frame.contentWindow={postMessage:m=>messages.push(m)};
  q('#pick-preview').click();assert.equal(C.state.inspect,true);assert.equal(messages.at(-1).inspect,true);const before=JSON.stringify(C.state.config);
  const pick=(data={},source=frame.contentWindow)=>handlers.message.forEach(fn=>fn({source,data:{type:'cram-preview-picked',role:'answerText',mode:'main',view:'flash',theme:'light',face:'question',...data}}));
  pick({},{});assert.equal(C.state.selectedColor,null,'foreign frames cannot select a category');pick({mode:'anki'});assert.equal(C.state.selectedColor,null,'stale mode packets are ignored');pick();
  assert.equal(C.state.selectedColor,'answerText');assert.ok(q('[data-color-entry="answerText"]').classList.contains('cu-picked-color'));assert.ok(q('[data-color-entry="answerText"]').closest('details').getAttribute('open')!==null,'the selected color group opens');assert.match(q('#picked-color').textContent,/Auto/);
  assert.equal(JSON.stringify(C.state.config),before,'inspecting never pins automatic colors or saves preferences');assert.ok(q('iframe')===frame);
  q('#answerText-auto').checked=false;q('#answerText-auto').dispatch('change');q('#hex-answerText').value='#13579b';q('#hex-answerText').dispatch('input');assert.equal(C.state.config.colors.light.flash.answerText,'#13579b');assert.ok(q('iframe')===frame);
  q('[data-locate-color="card"]').dispatch('dblclick');assert.equal(C.state.inspect,false);assert.equal(messages.at(-1).inspect,false);assert.equal(messages.at(-1).locate.role,'card');
  q('#pick-preview').click();q('[data-custom="images"]').click();assert.equal(C.state.inspect,false);pick();assert.equal(C.state.selectedColor,null);assert.equal(calls.filter(x=>x.action==='save').length,0);
  q('[data-custom="cancel"]').click();assert.equal(calls.at(-1).action,'cancel');
}
console.log('1.10 inspector checks passed: browser NodeLists, semantic overlap choices, badge/choice/layer distinctions, stable draft edits, Auto preservation, source/context guards, no flip/rating/bridge calls, and clean exit.');

// 1.10.1: reproduce the screenshot's page-sized target outside the iframe.
{
  const t=inspectorEnvironment(),{d,q,e}=t;
  Node.prototype.getBoundingClientRect=function(){return {left:-20,top:-10,width:1420,height:1080,right:1400,bottom:1070};};
  d.body.dispatch('pointermove');let ring=q('#preview-inspect-ring');assert.ok(ring);
  const box={left:parseFloat(ring.style.left),top:parseFloat(ring.style.top),width:parseFloat(ring.style.width),height:parseFloat(ring.style.height)};
  assert.ok(box.left>=5&&box.top>=5,'outline starts inside the visible preview');
  assert.ok(box.left+box.width<=e.context.innerWidth-5,'right edge stays visible');
  assert.ok(box.top+box.height<=e.context.innerHeight-5,'bottom edge stays visible');
  const existing=ring;d.body.dispatch('pointermove');assert.ok(q('#preview-inspect-ring')===existing,'hover updates reuse one outline');
  d.body.dispatch('pointerout',{relatedTarget:null});assert.equal(q('#preview-inspect-ring'),null,'leaving the iframe clears the outline');
  d.body.dispatch('pointermove');d.documentElement.dispatch('pointerleave');assert.equal(q('#preview-inspect-ring'),null);
  Node.prototype.getBoundingClientRect=function(){return {left:1600,top:200,width:100,height:80,right:1700,bottom:280};};
  d.body.dispatch('pointermove');assert.equal(q('#preview-inspect-ring'),null,'fully offscreen targets never leave a clipped fragment');
  delete Node.prototype.getBoundingClientRect;
}
console.log('1.10.1 outline checks passed: oversized page bounds, four visible edges, one stable outline, offscreen targets and pointer exit.');

// Nested note highlights must scale their own inline box, not only leaf text.
const nestedHighlight='<span class="zoom-highlight" style="background-color:#fff19b;font-size:20px;line-height:28px"><b class="zoom-bold"><i class="zoom-inner">Important term</i></b></span><img class="zoom-image" src="fixed.png">';
function richTextComputed(el){
  let font='',line='';for(let n=el;n;n=n.parentElement){font||=n.style.fontSize||'';line||=n.style.lineHeight||'';}
  return {fontSize:font||'27px',lineHeight:line||'normal'};
}
{
  const e=startupEnvironment('complete',true);e.context.getComputedStyle=richTextComputed;e.body();e.run();const d=e.document,app=e.context.cram,q=s=>d.querySelector(s);
  app.receive('bootstrap',{...cat,preferences:{auto_advance:false}});
  app.receive('session',{questions:[{...flashA,id:'highlight-main',clue:nestedHighlight,slots:[{number:1,answer:'Important term',answer_html:nestedHighlight}]}],skipped:0});
  const frame=q('.flash-card'),highlight=q('#clue-face .zoom-highlight'),bold=q('#clue-face .zoom-bold'),inner=q('#clue-face .zoom-inner'),image=q('#clue-face .zoom-image');
  for(let n=0;n<5;n++)frame.dispatch('wheel',{ctrlKey:true,deltaY:-1});
  assert.equal(app.state.textZoom,1.5);assert.equal(highlight.style.fontSize,'30px');assert.equal(bold.style.fontSize,'30px');assert.equal(inner.style.fontSize,'30px');assert.equal(highlight.style.lineHeight,'42px');assert.equal(highlight.style.backgroundColor,'#fff19b');
  assert.equal(q('#answer .zoom-highlight').style.fontSize,'30px','back-side highlights scale with the front');
  const added=d.createElement('em');added.textContent=' new';inner.appendChild(added);frame.dispatch('wheel',{ctrlKey:true,deltaY:-1});
  assert.equal(highlight.style.fontSize,'32px');assert.equal(added.style.fontSize,'32px','new descendants use the original baseline, not the already zoomed parent');
  d.dispatch('keydown',{ctrlKey:true,key:'0',target:frame});assert.equal(highlight.style.fontSize,'20px');assert.equal(highlight.style.lineHeight,'28px');assert.equal(bold.style.fontSize,undefined);assert.equal(inner.style.fontSize,undefined);assert.equal(added.style.fontSize,undefined);
  assert.ok(q('.flash-card')===frame);assert.ok(q('#clue-face .zoom-image')===image);assert.equal(image.style.width,undefined);assert.equal(frame.style.height,undefined);assert.equal(frame.style.width,undefined);
}
for(const display of ['native','flash']){
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);d.body.innerHTML='<div id="qa"></div><div id="native-bottom">Again Hard Good Easy</div>';
  e.context.requestAnimationFrame=fn=>fn();e.context.getComputedStyle=richTextComputed;e.context.pycmd=msg=>e.calls.push(msg.startsWith('cram_live:')?JSON.parse(msg.slice(10)):{native:msg});
  vm.runInNewContext(webScript('live.js'),e.context);const app=e.context.cramNative,nativeBottom=q('#native-bottom');
  const packet={cid:'highlight-'+display,epoch:1,side:'question',display,text_zoom:1.5,question:display==='flash'?{...flashA,kind:'basic',clue:nestedHighlight,slots:[{number:1,answer:'Important term',answer_html:nestedHighlight}]}:null};
  const show=p=>{const payload=JSON.stringify(p).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-stage"><div id="cl-original">${nestedHighlight}</div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>`;app.mount();};
  show(packet);const frame=q('.cl-flip'),highlight=q('.cl-front .zoom-highlight'),bold=q('.cl-front .zoom-bold'),inner=q('.cl-front .zoom-inner'),image=q('.cl-front .zoom-image');
  assert.equal(highlight.style.fontSize,'30px',display+' scales a background wrapper without direct text');assert.equal(highlight.style.lineHeight,'42px');assert.equal(bold.style.fontSize,'30px');assert.equal(inner.style.fontSize,'30px');assert.equal(highlight.style.backgroundColor,'#fff19b');
  const added=d.createElement('em');added.textContent=' new';inner.appendChild(added);frame.dispatch('wheel',{ctrlKey:true,deltaY:-1});assert.equal(highlight.style.fontSize,'32px');assert.equal(added.style.fontSize,'32px');
  d.dispatch('keydown',{ctrlKey:true,key:'0',target:frame});assert.equal(highlight.style.fontSize,'20px');assert.equal(highlight.style.lineHeight,'28px');assert.equal(bold.style.fontSize,undefined);assert.equal(inner.style.fontSize,undefined);assert.equal(added.style.fontSize,undefined);
  assert.ok(q('.cl-flip')===frame);assert.ok(q('.cl-front .zoom-image')===image);assert.equal(image.style.width,undefined);assert.equal(frame.style.height,undefined);assert.equal(frame.style.width,undefined);assert.ok(q('#native-bottom')===nativeBottom);
  show({...packet,side:'answer'});assert.equal(q('.cl-back .zoom-highlight').style.fontSize,'30px');assert.ok(!q('.cl-details'));
  assert.ok(e.calls.every(call=>call.action==='ready'||call.action==='text_zoom'),'zooming never reveals or rates a native card');
}
console.log('1.10.3 rich zoom checks passed: nested highlight wrappers/children, fixed authored font sizes, matching line heights, both faces/modes, baseline reset, inserted descendants, unchanged frame/image nodes and native ratings.');

// The order list is drawn in-page; no OS/Qt native select popup is opened.
{
  const e=startupEnvironment('complete',true),events={};e.context.addEventListener=(name,fn)=>(events[name]??=[]).push(fn);e.context.innerWidth=900;e.context.innerHeight=700;e.body();e.run();
  const d=e.document,app=e.context.cram,q=s=>d.querySelector(s),tap=s=>{assert.ok(q(s),'missing '+s);q(s).click();};
  const key=(value,extra={})=>d.dispatch('keydown',{key:value,target:q('#order-trigger'),...extra});
  const active=()=>q('#'+q('#order-trigger').getAttribute('aria-activedescendant'))?.dataset.orderValue;
  const open=(rect={left:620,top:100,bottom:142,width:250})=>{q('#order-trigger').getBoundingClientRect=()=>rect;tap('#order-trigger');assert.ok(q('#order-menu'));};
  const columns=[{key:'cardLapses',label:'Lapses'},{key:'cardEase',label:'Ease'}];
  app.receive('bootstrap',{...cat,retrievability_order:false,sort_columns:columns});
  assert.equal(q('#order').hidden,true);assert.equal(q('#order-trigger').getAttribute('role'),'combobox');assert.equal(q('#order-value').textContent,'Random cards');
  const before=e.calls.length;open();assert.equal(e.calls.length,before,'opening a menu performs no bridge action');
  assert.equal(q('#order-trigger').getAttribute('aria-expanded'),'true');assert.equal(d.querySelectorAll('#order-menu [role="option"]').length,14);assert.equal(q('.order-group').textContent,'Anki card columns');
  assert.equal(q('#order-menu').style.left,'620px');assert.equal(q('#order-menu').style.maxHeight,'360px');assert.equal(q('#order-menu').style.top,'148px');
  key('ArrowDown');assert.equal(active(),'random_notes');assert.equal(app.state.order,'shuffle','navigation does not commit');
  key('Escape');assert.ok(!q('#order-menu'));assert.equal(app.state.order,'shuffle');assert.equal(q('#order-trigger').getAttribute('aria-activedescendant'),null);
  open();key('End');assert.equal(active(),'anki:cardEase');key('Enter');assert.equal(app.state.order,'anki:cardEase');assert.equal(q('#order').value,'anki:cardEase');assert.equal(q('#order-value').textContent,'Ease');assert.equal(q('#order-direction').hidden,false);assert.ok(!q('#order-menu'));
  open();key('ArrowUp');assert.equal(active(),'anki:cardLapses');key('ArrowUp');assert.equal(active(),'deck_due','disabled retrievability orders are skipped');key('Tab');assert.equal(app.state.order,'deck_due');assert.equal(q('#order-direction').hidden,true);
  open();const disabled=q('[data-order-value="retrievability_asc"]');disabled.click();assert.equal(app.state.order,'deck_due');assert.ok(q('#order-menu'));
  q('[data-order-value="created_asc"] span').click();assert.equal(app.state.order,'created_asc');assert.equal(app.state.shuffle,false);assert.ok(!q('#order-menu'));
  open();key('r');assert.equal(active(),'shuffle');key('a');assert.equal(active(),'shuffle');key('n');assert.equal(active(),'shuffle');key('Enter');assert.equal(app.state.order,'shuffle');assert.equal(app.state.shuffle,true);
  key('Enter',{repeat:true});assert.ok(!q('#order-menu'),'held confirm key cannot reopen a menu');
  open();key('Home');key('PageDown');assert.equal(active(),'anki:cardLapses');key('PageUp');assert.equal(active(),'shuffle');key(' ');assert.ok(!q('#order-menu'));
  open({left:850,top:600,bottom:642,width:250});assert.equal(q('#order-menu').style.left,'628px');assert.equal(q('#order-menu').style.bottom,'106px');assert.equal(q('#order-menu').style.maxHeight,'360px');
  for(const fn of events.scroll||[])fn({target:q('#order-menu')});assert.ok(q('#order-menu'),'scrolling the menu keeps it open');
  for(const fn of events.scroll||[])fn({target:d});assert.ok(!q('#order-menu'),'page scroll dismisses a fixed menu');
  open();q('#order-trigger').dispatch('pointerdown');assert.ok(q('#order-menu'));q('#deck-search').dispatch('pointerdown');assert.ok(!q('#order-menu'));
  for(const event of ['resize','blur']){open();for(const fn of events[event]||[])fn({});assert.ok(!q('#order-menu'),event+' dismisses menu');}
  app.receive('theme',true);open();assert.ok(d.documentElement.classList.contains('cram-dark'));tap('[data-order-value="anki:cardLapses"]');q('#order-desc').checked=true;q('#order-desc').dispatch('change');tap('#start');assert.equal(e.calls.at(-1).config.order,'anki:cardLapses');assert.equal(e.calls.at(-1).config.order_desc,true);
  assert.match(css,/\.order-menu\{[^}]*background:var\(--panel\);color:var\(--ink\)/,'menu surface and text follow the page theme');
}
console.log('1.10.3 order menu checks passed: complete options, disabled choices, pointer/keyboard/typeahead, cancel/commit, held keys, both themes, viewport placement/dismissal and unchanged start payload.');

// Resume restores the saved view without submitting answers or auto-continuing.
{
  const e=startupEnvironment('complete',true);e.body();e.run();const d=e.document,app=e.context.cram,q=s=>d.querySelector(s),tap=s=>{assert.ok(q(s),'missing '+s);q(s).click();};
  const sid='a'.repeat(32),other='b'.repeat(32),saved={id:sid,decks:['Biology::Tissues'],config:{mode:'exam'},answered:1,total:3};
  app.receive('bootstrap',{...cat,saved_sessions:[saved,{...saved,id:other,decks:['Design'],config:{mode:'flash'}}]});
  assert.equal(d.querySelectorAll('.saved-row').length,2);assert.match(q('#saved-practice').textContent,/1 \/ 3 answered/);tap('[data-resume="'+sid+'"]');assert.deepEqual(e.calls.at(-1),{action:'resume',session_id:sid});
  tap('[data-reset-progress="'+other+'"]');assert.ok(q('#reset-modal'));const count=e.calls.length;tap('[data-action="reset-cancel"]');assert.equal(e.calls.length,count,'opening/canceling reset does not delete progress');
  tap('[data-reset-progress="'+other+'"]');d.dispatch('keydown',{key:'Escape',target:d.body});assert.ok(!q('#reset-modal'));assert.equal(e.calls.length,count);
  tap('[data-reset-progress="'+other+'"]');tap('[data-action="reset-confirm"]');assert.deepEqual(e.calls.at(-1),{action:'reset_progress',session_id:other});
  const options={mode:'exam',decks:['1'],limit:0,children:true,order:'created_asc',order_desc:false,filters:{search:'is:due',tag:'',flag:'',note_type:''}};
  app.receive('session',{session_id:sid,restored:true,questions:[cloze,io,flashA],results:{},config:options,view:{index:0,picks:{0:[1,null]},revealed:[],activeSlot:1,zoom:1}});
  assert.equal(app.state.activeSlot,1);assert.deepEqual(Array.from(app.state.picks[0]),[1,null]);assert.equal(q('.exam-card [data-blank="0"]').textContent,'Cell');assert.ok(q('.slot-group.active-slot'));assert.equal(q('[data-action="submit"]').disabled,true);assert.equal(e.calls.at(-1).action,'checkpoint');
  const card=q('.exam-card'),choice=q('[data-slot="1"][data-choice="3"]'),before=e.calls.length,view=JSON.stringify(app.state.picks);
  for(let i=0;i<12;i++)choice.dispatch('pointermove');assert.equal(q('.exam-card'),card);assert.equal(e.calls.length,before);assert.equal(JSON.stringify(app.state.picks),view,'hover never selects or redraws choices');
  choice.click();assert.equal(q('.exam-card'),card);assert.deepEqual(e.calls.at(-1).view.picks[0],[1,3]);assert.equal(e.calls.at(-1).view.activeSlot,1);assert.equal(q('[data-action="submit"]').disabled,false);
  app.receive('session',{session_id:sid,restored:true,questions:[cloze,io,flashA],results:{0:{earned:2,total:2,correct:[true,true],picks:{choices:[1,3]}}},view:{index:1,picks:{},revealed:[1],zoom:2}});
  assert.equal(app.state.index,1);assert.equal(app.state.zoom,2);assert.ok(q('.io-image').classList.contains('revealed'));assert.equal(q('[data-action="known"]').disabled,false);assert.equal(q('#question-count').textContent,'2 / 3');
  tap('[data-action="leave"]');assert.match(q('#leave-modal').textContent,/progress is saved/);tap('[data-action="confirm-leave"]');assert.equal(e.calls.at(-1).action,'home');
  app.receive('session',{session_id:sid,restored:true,questions:[flashA],results:{0:{earned:1,total:1,correct:[true],picks:{known:true}}},view:{index:0}});
  assert.ok(q('.flash-card').classList.contains('is-flipped'));const after=e.calls.length;e.advance(5000);assert.ok(q('.flash-card'));assert.ok(!e.calls.slice(after).some(c=>c.action==='finish'||c.action==='grade'),'reopening an answered card never auto-finishes/grades');
  app.receive('session',{session_id:sid,restored:true,questions:[flashA],results:{0:{earned:1,total:1,correct:[true],picks:{known:true}}},view:{index:0,revealed:[]}});assert.ok(!q('.flash-card').classList.contains('is-flipped'),'an explicitly saved clue side stays hidden even after grading');
  app.receive('finished',{earned:1,total:1,questions:1,seconds:10,history:[]});assert.equal(app.state.sessionId,null);
  assert.match(css,/\.session button\.choice:hover[^}]*transform:none!important/);assert.match(css,/\.session button\.choice:hover[^}]*transition:none!important/);
}
console.log('1.10.4 resume checks passed: saved-set list/reset confirmation, partial cloze picks/active blank, stable hover nodes, revealed IO zoom, saved cursor and no automatic grading/finish.');

// Scheduling boundary: the skin may request reveal, never a rating or advance.
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();d.body.innerHTML='<div id="qa"></div><div id="native-ratings"><button data-ease="1">Again 1m</button><button data-ease="2">Hard 6m</button><button data-ease="3">Good 10m</button><button data-ease="4">Easy 4d</button></div>';
  e.context.pycmd=message=>e.calls.push(message.startsWith('cram_live:')?JSON.parse(message.slice(10)):{native:message});e.context.requestAnimationFrame=fn=>fn();e.context.getComputedStyle=()=>({fontSize:'20px',lineHeight:'28px'});
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../cram_studio/web/live.js'),'utf8'),e.context);
  const app=e.context.cramNative,q=s=>d.querySelector(s),ratings=q('#native-ratings'),buttons=Array.from(ratings.querySelectorAll('button')),labels=buttons.map(b=>b.textContent);
  const show=packet=>{const payload=JSON.stringify(packet).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-stage"><div id="cl-original">Original native card</div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>`;app.mount();};
  let epoch=100;
  for(const display of ['flash','native','exam','io']){
    const packet={cid:'card-'+display,epoch:epoch++,side:'question',display,question:display==='io'?io:display==='native'?null:display==='exam'?{...cloze,ready:true}:flashA,text_zoom:1};show(packet);const start=e.calls.length;
    if(display==='exam'){
      app.choose(1);app.choose(3);assert.equal(e.calls.length,start,'choosing all blanks does not reveal or rate');
    }else if(display==='io'){
      q('[data-live-action="io-masks"]').click();q('[data-live-action="io-masks"]').click();
      assert.equal(e.calls.length,start,'mask controls are visual only, even before native reveal');
      assert.equal(q('.cl-io-controls'),null,'no extra reveal row takes image space');
      const mask=q('.mask.target');mask.click();assert.equal(mask.getAttribute('aria-pressed'),'true');mask.click();assert.equal(mask.getAttribute('aria-pressed'),'false');
      assert.equal(e.calls.length,start,'individual masks never reveal or rate in Anki');
    }else{
      q('.cl-flip').click();q('.cl-flip').click();
      assert.deepEqual(e.calls.slice(start),[{native:'ans'}],'repeated reveal requests send ans exactly once');
    }
    const beforeAnswer=e.calls.length;show({...packet,side:'answer'});e.advance(60000);
    if(display==='io'){q('[data-live-action="io-masks"]').click();q('[data-live-action="io-full"]').click();}
    else if(display==='flash'||display==='native'){q('.cl-flip').click();q('.cl-flip').click();}
    else app.choose(0);
    for(const key of ['1','2','3','4',' ','e','b']){
      let prevented=false;d.dispatch('keydown',{key,target:d.body,preventDefault:()=>prevented=true});assert.equal(prevented,key===' '&&['flash','native'].includes(display),'only Flashcard Space is presentation-only: '+key);
    }
    assert.ok(!e.calls.slice(beforeAnswer).some(call=>call.native),'answer feedback/timers/flips never submit or advance');
    assert.ok(!e.calls.some(call=>/^(ease[1-4]|grade|finish|reschedule|set_due_date)$/.test(call.native||call.action||'')));
    assert.equal(q('#native-ratings'),ratings);assert.deepEqual(Array.from(ratings.querySelectorAll('button')),buttons);assert.deepEqual(buttons.map(b=>b.textContent),labels,'native button nodes, callbacks and displayed intervals remain mounted');
  }
}
console.log('Scheduling UI boundary passed: flash/native/cloze-MCQ/occlusion reveal once; Flashcard Space only flips, original ratings and interval buttons preserved.');

// 1.10.5: identical preview/live geometry, independent MCQ sizes and larger photos.
{
  const e=startupEnvironment('complete'),d=e.document;vm.runInNewContext(webScript('appearance.js'),e.context);const A=e.context.cramAppearance;
  for(const mode of ['main','anki'])for(const view of ['flash','exam'])for(const size of [{width:76,height:65},{width:95,height:40},{height:60},{width:60}]){
    const g=A.sizeGeometry(size,mode,view),preview=A.projectSize(size,mode,view,g.areaWidth,g.sceneHeight);
    for(const [width,height] of [[1850,810],[1000,700],[620,450]]){
      const live=A.projectSize(size,mode,view,width,height);
      assert.ok(Math.abs(live.width/live.height-preview.width/preview.height)<1e-10,'saved aspect ratio agrees with preview');
      assert.ok(live.width<=width&&live.height<=Math.max(180,height-g.reserve)+1e-7,'card stays within scene bounds');
    }
  }
  d.body.innerHTML='<main class="session"><section class="flash-card"><div class="flash-face"><div class="face-content"><img src="photo.png"></div></div></section></main>';
  const host=d.querySelector('.session'),image=d.querySelector('img'),face=d.querySelector('.flash-face');image.naturalWidth=200;image.naturalHeight=100;
  e.context.getComputedStyle=()=>({paddingLeft:'30px',paddingRight:'30px',paddingTop:'24px',paddingBottom:'24px'});
  const config={size:{width:74,height:60},examSize:{width:88,height:70}};
  A.apply(host,config,'main','flash',false);const frame=d.querySelector('.flash-card');
  assert.ok(parseFloat(image.style.getPropertyValue('width'))>image.naturalWidth,'small photo grows into available space');assert.equal(image.style.getPropertyValue('height'),'auto');assert.equal(d.querySelector('.flash-card'),frame);
  const width=image.style.getPropertyValue('width');A.fitImages(host);assert.equal(image.style.getPropertyValue('width'),width,'repeat fitting is stable');
  A.apply(host,config,'main','exam',false);assert.ok(host.classList.contains('cram-sized-exam'));assert.ok(!host.classList.contains('cram-sized-flash'));assert.equal(host.style.getPropertyValue('--cram-card-width'),'88%');
  A.apply(host,config,'main','io',false);assert.equal(host.style.getPropertyValue('--cram-card-width'),'');assert.ok(!host.classList.contains('cram-sized-exam'));
  for(const mode of ['main','anki'])for(const view of ['flash','exam'])for(const dark of [false,true]){
    A.apply(host,{colors:{[dark?'dark':'light']:{[view]:{auto:true,card:dark?'#192039':'#ffffff'}}}},mode,view,dark);
    assert.equal(host.style.getPropertyValue('--cram-answer-bg'),'','automatic palettes add no cloze highlight');assert.ok(!host.classList.contains('cram-answer-bg-custom'));
    assert.ok(A.contrast(host.style.getPropertyValue('--cram-answer-text'),dark?'#192039':'#ffffff')>=4.5);
    A.apply(host,{colors:{[dark?'dark':'light']:{[view]:{answerBackground:'#abcdef'}}}},mode,view,dark);assert.equal(host.style.getPropertyValue('--cram-answer-bg'),'#abcdef','existing explicit highlight preference remains available');
  }
}
{
  const e=startupEnvironment('complete'),d=e.document,handlers={},messages=[];d.body.innerHTML='<main id="cram-customize"></main>';
  e.context.addEventListener=(n,f)=>(handlers[n]??=[]).push(f);e.context.pycmd=()=>{};
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize.js'),e.context);
  const C=e.context.cramCustomize,q=s=>d.querySelector(s);C.receive('load',{config:{size:{width:74,height:60}},dark:false,assets:'local/'});
  const frame=q('iframe');frame.contentWindow={postMessage:p=>messages.push(p)};
  q('#preview-view').value='exam';q('#preview-view').dispatch('change');assert.equal(messages.at(-1).view,'exam');
  q('#size-width').value='88';q('#size-width').dispatch('input');q('#size-height').value='70';q('#size-height').dispatch('input');
  assert.deepEqual(plain(C.state.config.examSize),{width:88,height:70});assert.deepEqual(plain(C.state.config.size),{width:74,height:60});assert.equal(q('iframe'),frame);
  const message=p=>handlers.message.forEach(fn=>fn({source:frame.contentWindow,data:p}));
  message({type:'cram-preview-resize',view:'flash',size:{width:95,height:80}});assert.equal(C.state.config.examSize.width,88,'ignore stale drag from other view');
  message({type:'cram-preview-resize',view:'exam',size:{width:84,height:68}});assert.equal(q('#size-width').value,84);
  q('[data-custom="reset-size"]').click();assert.deepEqual(plain(C.state.config.examSize),{width:null,height:null});assert.deepEqual(plain(C.state.config.size),{width:74,height:60});
}
{
  const e=startupEnvironment('complete'),d=e.document,handlers={},out=[],parent={postMessage:p=>out.push(p)};
  e.context.parent=parent;e.context.innerWidth=1360;e.context.innerHeight=900;e.context.requestAnimationFrame=f=>f();e.context.addEventListener=(n,f)=>(handlers[n]??=[]).push(f);
  Node.prototype.getBoundingClientRect=function(){return {left:100,top:120,right:1260,bottom:750,width:1160,height:630};};
  Node.prototype.setPointerCapture=function(id){this._capture=id;};Node.prototype.hasPointerCapture=function(id){return this._capture===id;};Node.prototype.releasePointerCapture=function(){this._capture=null;};
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize-preview.js'),e.context);
  for(const mode of ['main','anki']){
    handlers.message.forEach(f=>f({source:parent,data:{type:'cram-preview-config',panel:'size',view:'exam',mode,config:{size:{width:74,height:60}}}}));
    const card=d.querySelector(mode==='anki'?'.cl-exam':'.exam-card'),handle=d.querySelector('[data-axis="xy"]');assert.ok(card);assert.equal(d.querySelectorAll('.preview-resize').length,3);
    handle.dispatch('pointerdown',{pointerId:1,clientX:100,clientY:100});handle.dispatch('pointermove',{pointerId:1,clientX:130,clientY:130});handle.dispatch('pointerup',{pointerId:1});
    assert.equal(out.at(-1).view,'exam');assert.ok(out.at(-1).size.width);assert.equal(d.querySelector(mode==='anki'?'.cl-exam':'.exam-card'),card);
  }
  delete Node.prototype.getBoundingClientRect;delete Node.prototype.setPointerCapture;delete Node.prototype.hasPointerCapture;delete Node.prototype.releasePointerCapture;
}
// Multiple targets can be opened independently, including while zoomed/fullscreen.
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();d.body.innerHTML='<div id="qa"></div>';
  e.context.pycmd=p=>e.calls.push(p);e.context.requestAnimationFrame=f=>f();e.context.getComputedStyle=()=>({fontSize:'20px',lineHeight:'28px'});
  vm.runInNewContext(webScript('live.js'),e.context);const app=e.context.cramNative,q=s=>d.querySelector(s);
  const packet={cid:'io-many',epoch:900,side:'question',display:'io',question:{...io,picture:'<div class="io-image"><img src="local.png"><svg aria-hidden="true"><rect class="mask target"/><rect class="mask target"/><rect class="mask inactive"/></svg></div>'}};
  const show=p=>{q('#qa').innerHTML=`<section id="cram-live" data-packet="${JSON.stringify(p).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;app.mount();};
  show(packet);const image=q('.io-image'),masks=Array.from(image.querySelectorAll('.mask.target')),before=e.calls.length;
  masks[0].click();assert.equal(masks[0].getAttribute('aria-pressed'),'true');assert.equal(masks[1].getAttribute('aria-pressed'),'false');assert.equal(app.state.packet.side,'question');
  q('[data-live-action="io-plus"]').click();q('[data-live-action="io-full"]').click();const zoom=image.style.width;masks[1].click();assert.equal(masks[1].getAttribute('aria-pressed'),'true');assert.equal(image.style.width,zoom);
  assert.equal(q('.cl-io-controls'),null);assert.equal(e.calls.length,before,'mask taps/zoom/fullscreen send no native or scheduling action');
  show({...packet,side:'answer'});assert.equal(q('.io-image'),image);assert.ok(image.classList.contains('revealed'));assert.equal(masks[0].getAttribute('aria-pressed'),'true');
  masks[0].click();assert.equal(masks[0].getAttribute('aria-pressed'),'false');assert.equal(masks[1].getAttribute('aria-pressed'),'true');
  q('[data-live-action="io-masks"]').click();assert.equal(masks[1].getAttribute('aria-pressed'),'false');assert.equal(app.state.packet.side,'answer');assert.equal(image.style.width,zoom);
  show({...packet,epoch:901});assert.notEqual(q('.io-image'),image);assert.equal(q('.mask.target').getAttribute('aria-pressed'),'false','undo/new question resets visual masks');
}
console.log('1.10.5 presentation checks passed: consistent aspect ratios/bounds, separate MCQ resize/save/reset/drag, enlarged stable photos, default unhighlighted clozes, independent tappable masks, native reveal/rating separation and fullscreen state.');

// 1.10.6: sentence-only display change, including old saved cloze markup.
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();e.run();const app=e.context.cram,q=s=>d.querySelector(s);
  app.receive('bootstrap',cat);const original=JSON.stringify(flashA);app.receive('session',{questions:[flashA]});
  const front=q('#clue-face'),back=q('#answer'),blanks=Array.from(front.querySelectorAll('[data-blank]'));
  assert.equal(blanks.length,3);for(const [i,blank] of blanks.entries()){assert.equal(blank.textContent,'\u00a0');assert.ok(blank.classList.contains('cram-blank-empty'));assert.equal(blank.getAttribute('aria-label'),'Blank '+(i+1));}
  assert.ok(!front.textContent.includes('(1)'));assert.match(back.textContent,/A Cells forms Tissues and Organs/);assert.equal(back.querySelectorAll('.cram-blank-empty').length,0);
  q('[data-action="reveal"]').click();assert.equal(q('#clue-face'),front);assert.equal(q('#answer'),back);assert.equal(JSON.stringify(flashA),original,'display does not modify clues, slot IDs or cache inputs');
  const list={...cloze,slots:[{number:1,answer:'1. banana\n2. mango',answer_html:'<ol><li>banana</li><li>mango</li></ol>',choices:['1. banana\n2. mango','Other A','Other B','Other C'],correct:0}],clue:'Fruit: <span class="ct-blank" data-blank="0">(1) _____________</span>'};
  app.receive('session',{questions:[list]});const blank=q('[data-blank="0"]'),card=q('.exam-card');assert.ok(blank.classList.contains('cram-blank-empty'));assert.ok(blank.classList.contains('active'));
  q('[data-choice="0"]').click();assert.equal(blank.textContent,'1. banana\n2. mango');assert.ok(!blank.classList.contains('cram-blank-empty'));assert.equal(q('.exam-card'),card);assert.equal(q('[data-blank="0"]'),blank);
  app.receive('session',{questions:[{...cloze,ready:false}]});assert.equal(d.querySelectorAll('.waiting-card .cram-blank-empty').length,2);assert.ok(!q('.waiting-card').textContent.includes('(1)'));
  app.receive('session',{questions:[cloze]});const sentence=q('.question-panel'),first=q('[data-blank="0"]'),second=q('[data-blank="1"]');
  d.getElementById('cram-app').dispatch('keydown',{key:'ArrowDown'});assert.ok(second.classList.contains('active'));assert.ok(!first.classList.contains('active'));assert.equal(q('.question-panel'),sentence);
}
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();d.body.innerHTML='<div id="qa"></div>';
  e.context.pycmd=p=>e.calls.push(p);e.context.requestAnimationFrame=f=>f();e.context.getComputedStyle=()=>({fontSize:'20px',lineHeight:'28px'});
  vm.runInNewContext(webScript('live.js'),e.context);const app=e.context.cramNative,q=s=>d.querySelector(s);
  const show=packet=>{const payload=JSON.stringify(packet).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;app.mount();};
  const packet={cid:'clean',epoch:1001,side:'question',display:'flash',question:flashA};show(packet);
  assert.equal(q('.cl-front').querySelectorAll('.cram-blank-empty').length,3);assert.ok(!q('.cl-front').textContent.includes('(1)'));assert.match(q('.cl-back').textContent,/Cells.*Tissues.*Organs/);
  const exam={...packet,epoch:1002,display:'exam',question:{...cloze,ready:true}};show(exam);const first=q('[data-blank="0"]'),second=q('[data-blank="1"]'),frame=q('.cl-exam'),before=e.calls.length;
  app.choose(1);assert.equal(first.textContent,'Cell');assert.ok(second.classList.contains('cl-active'));app.choose(3);assert.equal(second.textContent,'Tissue');assert.equal(q('.cl-exam'),frame);assert.equal(e.calls.length,before,'focus and choices do not reveal/rate');
  show({...exam,side:'answer'});assert.equal(q('[data-blank="0"]').textContent,'Cell');assert.equal(q('[data-blank="1"]').textContent,'Tissue');assert.equal(d.querySelectorAll('.cram-blank-empty').length,0);assert.equal(d.querySelectorAll('.cl-revealed-answer').length,2);assert.ok(!q('.cl-clue').textContent.includes('(1)'));
}
{
  const e=startupEnvironment('complete'),d=e.document,handlers={},parent={postMessage(){}};e.context.parent=parent;e.context.requestAnimationFrame=f=>f();e.context.addEventListener=(n,f)=>(handlers[n]??=[]).push(f);
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize-preview.js'),e.context);
  for(const mode of ['main','anki'])for(const view of ['flash','exam']){
    handlers.message.forEach(f=>f({source:parent,data:{type:'cram-preview-config',panel:'colors',view,mode,face:'question',config:{}}}));
    const blank=d.querySelector('[data-sample-blank]'),keptPick=mode==='anki'&&view==='exam';assert.equal(blank.textContent,keptPick?'Tissue':'\u00a0');assert.equal(blank.classList.contains('cram-blank-empty'),!keptPick);assert.ok(!blank.textContent.includes('(1)'));
    if(view==='exam'){d.querySelector('[data-sample-choice="0"]').click();assert.equal(d.querySelector('[data-sample-blank]').textContent,'Tissue');assert.ok(!d.querySelector('[data-sample-blank]').classList.contains('cram-blank-empty'));}
  }
  const rules=webScript('appearance.css');assert.match(rules,/cram-blank-empty::after/);assert.match(rules,/outline:1px solid var\(--cram-blank-ink/);
}
console.log('1.10.6 blank checks passed: clean flash/MCQ/preview sentences, stable active-blank navigation, real numbered answers retained, old saved clue compatibility, and no added native reveal/rating.');

// 1.10.7: repeated clicks act on controls, never start browser selection/drag.
{
  const e=startupEnvironment('complete'),d=e.document;vm.runInNewContext(webScript('appearance.js'),e.context);
  d.body.innerHTML='<div id="test-scope"><p id="copy-text">Ordinary clue text</p><span class="ct-blank"><b id="inside-blank">Answer</b></span><div class="io-image"><img id="photo"><svg><rect class="mask target" tabindex="0"/></svg></div><div class="scroll-frame"></div><input id="field"><div contenteditable="true"><span class="ct-blank" id="editable">Editable answer</span></div></div><img id="outside-photo">';
  const q=s=>d.querySelector(s),scope=q('#test-scope'),mask=q('.mask'),image=q('#photo'),blank=q('.ct-blank');let clears=0,focus=0,range=null;
  const selection={rangeCount:1,getRangeAt:()=>({intersectsNode:node=>node===range}),removeAllRanges(){clears++;this.rangeCount=0;}};
  e.context.getSelection=()=>selection;mask.focus=()=>focus++;
  e.context.cramAppearance.preventStudySelection(scope,'.ct-blank,.io-image,.mask.target');
  const fire=(node,type,extra={})=>{let prevented=false;node.dispatch(type,{type,button:0,preventDefault:()=>prevented=true,...extra});return prevented;};
  range=mask;assert.equal(fire(mask,'mousedown'),true);assert.equal(clears,1);assert.equal(focus,1,'SVG mask keeps keyboard focus');
  selection.rangeCount=1;range=q('#copy-text');assert.equal(fire(image,'mousedown'),true);assert.equal(clears,1,'do not clear a range outside the clicked image');
  for(const node of [image,mask,q('#inside-blank'),q('.io-image')])for(const type of ['mousedown','selectstart','dragstart'])assert.equal(fire(node,type),true,type+' '+node.tagName);
  assert.equal(fire(image,'mousedown',{button:2}),false,'right-click stays available');assert.equal(fire(image,'mousedown',{button:1}),false);
  for(const node of [q('#copy-text'),q('#field'),q('#editable'),q('.scroll-frame'),q('#outside-photo')])assert.equal(fire(node,'mousedown'),false,'unrelated text/inputs/scrollbars/outside images retain normal behavior');
  assert.equal(fire(blank,'wheel'),false);assert.equal(fire(blank,'touchmove'),false,'scroll gestures are not intercepted');
}
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();vm.runInNewContext(webScript('appearance.js'),e.context);e.run();const app=e.context.cram,q=s=>d.querySelector(s);
  app.receive('bootstrap',cat);app.receive('session',{questions:[cloze]});const second=q('[data-blank="1"]'),card=q('.exam-card');
  for(let i=0;i<4;i++){let stopped=false;second.dispatch('mousedown',{type:'mousedown',button:0,preventDefault:()=>stopped=true});assert.ok(stopped);second.click();}
  assert.equal(app.state.activeSlot,1);assert.equal(q('.exam-card'),card);assert.equal(app.state.pending,false);assert.deepEqual(Array.from(app.state.picks[0]),[null,null]);
  app.receive('session',{questions:[io]});q('[data-action="fullscreen"]').click();const image=q('.io-image'),photo=image.querySelector('img');let prevented=false;
  photo.dispatch('dragstart',{type:'dragstart',preventDefault:()=>prevented=true});assert.ok(prevented,'MAIN viewer reparenting retains selection guard');assert.equal(q('.io-image'),image);
}
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();d.body.innerHTML='<div id="qa"></div><div id="native-ratings"><button data-ease="1">Again 1m</button><button data-ease="4">Easy 4d</button></div>';
  e.context.pycmd=p=>e.calls.push(p);e.context.requestAnimationFrame=f=>f();e.context.getComputedStyle=()=>({fontSize:'20px',lineHeight:'28px'});
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('live.js'),e.context);const app=e.context.cramNative,q=s=>d.querySelector(s);
  const p={cid:'selection',epoch:1007,side:'question',display:'io',question:io};
  const payload=JSON.stringify(p).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;app.mount();
  const mask=q('.mask.target'),image=q('.io-image'),ratings=q('#native-ratings'),before=e.calls.length;let clears=0;
  e.context.getSelection=()=>({rangeCount:1,getRangeAt:()=>({intersectsNode:()=>true}),removeAllRanges:()=>clears++});
  for(let i=0;i<6;i++){
    let prevented=false;mask.dispatch('mousedown',{type:'mousedown',button:0,preventDefault:()=>prevented=true});assert.ok(prevented);mask.click();
    assert.equal(mask.getAttribute('aria-pressed'),String(i%2===0));assert.equal(q('.io-image'),image);
  }
  assert.equal(clears,6);assert.equal(app.state.packet.side,'question');assert.equal(e.calls.length,before,'repeated mask clicks never reveal/rate/advance');
  q('[data-live-action="io-plus"]').click();const zoom=app.state.zoom;q('[data-live-action="io-full"]').click();const width=image.style.width;assert.equal(app.state.zoom,zoom);let prevented=false;
  image.querySelector('img').dispatch('dragstart',{type:'dragstart',preventDefault:()=>prevented=true});assert.ok(prevented);assert.equal(image.style.width,width);assert.equal(q('#native-ratings'),ratings);
  for(const key of [' ','1','2','3','4','e','b']){let stopped=false;d.dispatch('keydown',{key,target:d.body,preventDefault:()=>stopped=true});assert.equal(stopped,false,'native shortcut '+key);}
  const css=webScript('appearance.css');assert.match(css,/user-select:none!important/);assert.match(css,/-webkit-user-drag:none!important/);
}
console.log('1.10.7 selection checks passed: repeated blank/mask clicks, stale intersecting ranges only, image drag suppression, right-click/copy/inputs/scroll gestures, viewer/zoom stability and unchanged native review shortcuts.');

// 1.10.9: one blank's choices, automatic next blank, manual check, independent type.
const pagedQuestion={...cloze,id:'four-blanks',ready:true,clue:Array.from({length:4},(_,i)=>`Part ${i+1}: <span class="ct-blank" data-blank="${i}">(old blank)</span>`).join('<br>'),slots:Array.from({length:4},(_,i)=>({...cloze.slots[0],number:i+1}))};
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();vm.runInNewContext(webScript('appearance.js'),e.context);e.run();
  const app=e.context.cram,q=s=>d.querySelector(s),key=k=>d.dispatch('keydown',{key:k,target:d.body});
  app.receive('bootstrap',{...cat,preferences:{text_zoom:.6,appearance:{examLayout:{questionHeight:66,choiceTextSize:20}}}});
  app.receive('session',{session_id:'a'.repeat(32),questions:[pagedQuestion]});
  const card=q('.exam-card'),panel=q('.question-panel'),groups=Array.from(d.querySelectorAll('.slot-group')),choice=q('.choice-text');
  const visible=()=>groups.map((g,i)=>g.hidden?null:i).filter(i=>i!==null);
  assert.deepEqual(visible(),[0]);assert.equal(choice.style.fontSize,undefined,'question zoom never writes inline choice sizes');
  assert.equal(q('.session').style.getPropertyValue('--cram-choice-font'),'20px');
  assert.equal(q('.session').style.getPropertyValue('--cram-question-track'),'66fr');
  for(let i=0;i<4;i++){
    key('2');assert.equal(q(`[data-blank="${i}"]`).textContent,'Cell');
    assert.equal(app.state.activeSlot,Math.min(i+1,3));assert.deepEqual(visible(),[Math.min(i+1,3)]);
    assert.equal(q('.exam-card'),card);assert.equal(q('.question-panel'),panel);
  }
  e.advance(10000);assert.equal(app.state.pending,false);assert.equal(app.state.index,0);
  assert.ok(!e.calls.some(x=>['grade','finish','next'].includes(x.action)),'last pick never checks/continues');
  key('ArrowUp');assert.deepEqual(visible(),[2]);key('1');assert.deepEqual(Array.from(app.state.picks[0]),[1,1,0,1]);assert.deepEqual(visible(),[3]);
  q('[data-blank="0"]').click();assert.deepEqual(visible(),[0]);key('ArrowUp');assert.deepEqual(visible(),[3]);key('ArrowDown');assert.deepEqual(visible(),[0]);
  assert.equal(e.calls.at(-1).view.activeSlot,0,'resume checkpoint retains pager position');
  const font=choice.style.fontSize;panel.dispatch('wheel',{ctrlKey:true,deltaY:-1});assert.equal(choice.style.fontSize,font);assert.equal(q('.session').style.getPropertyValue('--cram-choice-font'),'20px');
  key(' ');assert.equal(e.calls.at(-1).action,'grade');assert.deepEqual(e.calls.at(-1).picks.choices,[1,1,0,1]);
}
{
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);d.body.innerHTML='<div id="qa"></div><div id="ratings"><button>Again 1m</button><button>Hard 6m</button><button>Good 10m</button><button>Easy 4d</button></div>';
  e.context.getComputedStyle=el=>({fontSize:el.closest('.cl-choice-text')?'20px':'23px',lineHeight:'normal'});
  e.context.pycmd=msg=>e.calls.push(msg.startsWith('cram_live:')?JSON.parse(msg.slice(10)):{native:msg});
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('live.js'),e.context);const app=e.context.cramNative;
  const packet={cid:'pager',epoch:55,side:'question',display:'exam',question:pagedQuestion,text_zoom:.6,appearance:{examLayout:{questionHeight:66,choiceTextSize:20}}};
  const show=p=>{const payload=JSON.stringify(p).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;app.mount();};
  show(packet);const card=q('.cl-exam'),panel=q('.cl-question-panel'),ratings=q('#ratings'),groups=Array.from(d.querySelectorAll('.cl-slot'));
  const visible=()=>groups.map((g,i)=>g.hidden?null:i).filter(i=>i!==null);
  for(let i=0;i<4;i++){assert.deepEqual(visible(),[i]);app.choose(1);assert.equal(q(`[data-blank="${i}"]`).textContent,'Cell');}
  assert.deepEqual(visible(),[3]);assert.equal(app.state.pending,false);e.advance(10000);assert.ok(e.calls.every(x=>x.action==='ready'));
  app.moveBlank(-1);assert.deepEqual(visible(),[2]);app.choose(0);assert.deepEqual(Array.from(app.state.picks),[1,1,0,1]);
  q('[data-blank="0"]').click();assert.deepEqual(visible(),[0]);
  const font=q('.cl-choice-text').style.fontSize;panel.dispatch('wheel',{ctrlKey:true,deltaY:-1});assert.equal(q('.cl-choice-text').style.fontSize,font);
  assert.equal(q('#cram-live').style.getPropertyValue('--cram-choice-font'),'20px');assert.equal(q('.cl-exam'),card);assert.equal(q('.cl-question-panel'),panel);assert.equal(q('#ratings'),ratings);
  show({...packet,side:'answer'});const picks=Array.from(app.state.picks);app.moveBlank(1);app.choose(3);assert.deepEqual(Array.from(app.state.picks),picks,'answer-side paging cannot edit a committed selection');
  for(const key of ['1','2','3','4',' ','e','b']){let prevented=false;d.dispatch('keydown',{key,target:d.body,preventDefault:()=>prevented=true});assert.equal(prevented,false,'native rating/reveal/edit/browse key is untouched');}
  assert.ok(!e.calls.some(x=>x.native),'pager never reveals or rates in Anki');assert.equal(q('#ratings'),ratings);
}
{
  const e=startupEnvironment('complete',true),d=e.document,handlers={},messages=[],calls=[];d.body.innerHTML='<main id="cram-customize"></main>';
  e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);e.context.pycmd=msg=>calls.push(JSON.parse(msg.slice(12)));
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('customize.js'),e.context);
  const C=e.context.cramCustomize,q=s=>d.querySelector(s);C.receive('load',{config:{size:{width:74,height:60}},dark:false,assets:'local/'});
  const iframe=q('iframe');iframe.contentWindow={postMessage:msg=>messages.push(msg)};
  q('#preview-view').value='exam';q('#preview-view').dispatch('change');
  q('#exam-question-height').value='68';q('#exam-question-height').dispatch('input');q('#exam-choice-size').value='22';q('#exam-choice-size').dispatch('input');
  assert.deepEqual(plain(C.state.config.examLayout),{questionHeight:68,choiceTextSize:22});assert.equal(messages.at(-1).config.examLayout.choiceTextSize,22);assert.equal(q('iframe'),iframe,'layout changes preserve live preview iframe');
  q('#exam-choice-size').value='99';q('#exam-choice-size').dispatch('input');q('[data-custom="save"]').click();assert.ok(!calls.some(x=>x.action==='save'),'invalid font size cannot save');
  q('#exam-choice-size').value='21';q('#exam-choice-size').dispatch('input');q('[data-custom="save"]').click();assert.equal(calls.at(-1).config.examLayout.choiceTextSize,21);
  q('[data-custom="reset-size"]').click();assert.deepEqual(plain(C.state.config.examLayout),{questionHeight:60,choiceTextSize:18});assert.deepEqual(plain(C.state.config.size),{width:74,height:60});
}
console.log('1.10.9 checks passed: four-blank pager, auto-next without auto-check/rating, stable question/choice nodes, keyboard/mouse revisits, independent choice type, profile layout preview/save/reset, and original native controls.');

// Pointer hit-testing lets text drags select; current behavior flips on text clicks.
function installTextGeometry(e){
  let active=null;
  e.document.caretPositionFromPoint=(x,y)=>({offsetNode:active,offset:Math.max(0,Math.min(active?.textContent.length||0,Math.round((x-100)/8)))});
  e.document.createRange=()=>{
    let start=0,end=0,node=null;
    return {setStart(n,i){node=n;start=i;},setEnd(n,i){node=n;end=i;},selectNodeContents(n){node=n;start=0;end=n.textContent.length;},
      getClientRects(){return node?[{left:100+8*start,right:100+8*end,top:100,bottom:120,width:8*(end-start),height:20}]:[];}};
  };
  return node=>{active=node?.nodeType===3?node:node?.children.find(n=>n.nodeType===3);};
}
{
  const e=startupEnvironment('complete'),d=e.document;d.body.innerHTML='<main id="test"><section class="flash-card"><div class="face-content"><b id="words">Words to copy</b><span id="answer-word" class="ct-blank revealed-answer">Cells</span><input id="edit-field"><a id="link">Link</a></div></section><p id="other">Other text</p></main>';
  const q=s=>d.querySelector(s),root=q('#test'),card=q('.flash-card'),words=q('#words'),content=q('.face-content'),point=installTextGeometry(e);point(words);
  vm.runInNewContext(webScript('appearance.js'),e.context);const guard=e.context.cramAppearance.flashcardPointer(root,'.flash-card');
  const event=(target,x=110,y=110,extra={})=>({target,clientX:x,clientY:y,button:0,detail:1,...extra});
  function down(target,x,y,extra={}){let prevented=false;target.dispatch('mousedown',{type:'mousedown',...event(target,x,y,extra),preventDefault:()=>prevented=true});return prevented;}
  assert.equal(down(words,110,110),false,'first text press allows native drag selection');assert.equal(guard.canFlip(event(words),card),true,'a stationary text click flips');
  root.dispatch('mousemove',event(card,450,220));assert.equal(guard.canFlip(event(card,450,220),card),false,'selection drag released on background cannot flip');
  assert.equal(down(content,450,220),true,'empty space in a text container is not treated as a letter');
  let prevented=false;words.dispatch('selectstart',{type:'selectstart',preventDefault:()=>prevented=true});assert.ok(prevented,'background double/triple clicks cannot start paragraph selection');
  assert.equal(guard.canFlip(event(content,450,220),card),true);
  assert.equal(down(words,110,110,{detail:2}),true,'repeated clicks do not select whole words');
  prevented=false;words.dispatch('selectstart',{type:'selectstart',preventDefault:()=>prevented=true});assert.ok(prevented);
  assert.equal(guard.canFlip(event(words,110,110,{detail:2}),card),true,'a repeated stationary text click still flips');
  assert.equal(down(card,450,220),true);root.dispatch('mousemove',event(card,650,220));assert.equal(guard.canFlip(event(card,650,220),card),false,'dragging the surface does not flip on release');
  assert.equal(down(words,110,110,{button:2}),false);assert.equal(guard.canFlip(event(words,110,110,{button:2}),card),false);
  for(const node of [q('#edit-field'),q('#link')]){assert.equal(down(node,110,110),false);assert.equal(guard.canFlip(event(node),card),false);}
  point(q('#answer-word'));assert.equal(down(q('#answer-word'),110,110),false,'revealed cloze words remain copyable');
  let clears=0,selectedNode=card;const selection={isCollapsed:false,rangeCount:1,getRangeAt:()=>({intersectsNode:n=>n===selectedNode}),removeAllRanges(){this.isCollapsed=true;this.rangeCount=0;clears++;}};
  e.context.getSelection=()=>selection;assert.equal(guard.canFlip(event(card,450,220,{detail:0}),card),false,'a programmatic click does not discard a copied selection');
  down(card,450,220);assert.equal(clears,1);assert.equal(guard.canFlip(event(card,450,220),card),true);
  selection.isCollapsed=false;selection.rangeCount=1;selectedNode=q('#other');down(card,450,220);assert.equal(clears,1,'unrelated copied text is retained');
  // Older Chromium exposes caretRangeFromPoint instead of caretPositionFromPoint.
  const position=d.caretPositionFromPoint;delete d.caretPositionFromPoint;d.caretRangeFromPoint=(x,y)=>{const p=position(x,y);return {startContainer:p.offsetNode,startOffset:p.offset};};point(words);
  assert.equal(down(words,110,110),false);assert.equal(down(content,450,220),true);
  delete d.caretRangeFromPoint;d.createTreeWalker=()=>{let used=false;return {nextNode(){if(used)return null;used=true;return words.children[0];}};};
  assert.equal(down(words,110,110),false);assert.equal(down(content,450,220),true,'text-line fallback also rejects empty padding');
  content.getBoundingClientRect=()=>({left:0,top:0,right:1016,bottom:800});content.offsetWidth=1016;content.scrollHeight=1200;
  assert.equal(down(content,1008,100),false,'flashcard scrollbar drag keeps its native default');assert.equal(guard.canFlip(event(content,1008,100),card),false,'scrollbar click never flips');
  assert.ok(!d.listeners.copy&&!root.listeners.copy,'clipboard behavior is not replaced');
}
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();const point=installTextGeometry(e);vm.runInNewContext(webScript('appearance.js'),e.context);e.run();
  const app=e.context.cram,q=s=>d.querySelector(s);app.receive('bootstrap',cat);app.receive('session',{questions:[flashA]});
  const card=q('.flash-card'),front=q('#clue-face .face-content');point(front);
  function click(target,x,y){let prevented=false;const event={target,clientX:x,clientY:y,button:0,detail:1};target.dispatch('mousedown',{type:'mousedown',...event,preventDefault:()=>prevented=true});target.dispatch('click',event);return prevented;}
  assert.equal(click(front,104,110),false);assert.ok(card.classList.contains('is-flipped'),'a stationary click on question text reveals');
  for(let i=0;i<8;i++){assert.equal(click(card,450,220),true);assert.equal(card.classList.contains('is-flipped'),i%2!==0);assert.equal(q('.flash-card'),card);}
  const answer=q('#answer .revealed-answer');point(answer);assert.equal(click(answer,110,110),false);assert.ok(!card.classList.contains('is-flipped'),'a stationary click on revealed text flips back');
  assert.ok(!e.calls.some(call=>call.action==='grade'),'copy/flip never grades');
  app.receive('session',{questions:[io]});const caption=q('.io-caption');let prevented=false;
  caption.dispatch('mousedown',{type:'mousedown',button:0,preventDefault:()=>prevented=true});assert.ok(prevented,'IO captions are also protected');
  q('[data-action="fullscreen"]').click();const viewerCaption=q('.viewer-caption');prevented=false;viewerCaption.dispatch('mousedown',{type:'mousedown',button:0,preventDefault:()=>prevented=true});assert.ok(prevented,'IO viewer text cannot be selected');
  const viewport=q('#viewer-viewport');viewport.getBoundingClientRect=()=>({left:0,top:0,right:866,bottom:650});viewport.offsetWidth=866;viewport.scrollHeight=1200;prevented=false;
  viewport.dispatch('mousedown',{type:'mousedown',button:0,clientX:858,clientY:100,preventDefault:()=>prevented=true});assert.equal(prevented,false,'IO scrollbar drag remains available');

}
for(const display of ['flash','native']){
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s),point=installTextGeometry(e);d.body.innerHTML='<div id="qa"></div><div id="native-ratings"><button>Again 1m</button><button>Easy 4d</button></div>';
  e.context.requestAnimationFrame=fn=>fn();e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});
  e.context.pycmd=msg=>e.calls.push(msg.startsWith('cram_live:')?JSON.parse(msg.slice(10)):{native:msg});
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('live.js'),e.context);const app=e.context.cramNative,ratings=q('#native-ratings');
  const packet={cid:'pointer-'+display,epoch:1111,side:'question',display,question:display==='flash'?flashA:null};
  function show(p){const payload=JSON.stringify(p).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-original">Native text to copy</div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;app.mount();}
  function click(target,x,y){let prevented=false;const event={target,clientX:x,clientY:y,button:0,detail:1};target.dispatch('mousedown',{type:'mousedown',...event,preventDefault:()=>prevented=true});target.dispatch('click',event);return prevented;}
  show(packet);const front=q(display==='flash'?'.cl-front .cl-flash-content':'.cl-front .cl-original-content');point(front);const before=e.calls.length;
  assert.equal(click(front,104,110),false);assert.equal(e.calls.length,before+1,'native question text click delegates reveal once');assert.deepEqual(e.calls.at(-1),{native:'ans'});
  assert.equal(click(q('.cl-flip'),450,220),true);assert.deepEqual(e.calls.at(-1),{native:'ans'});click(q('.cl-flip'),450,220);assert.equal(e.calls.filter(x=>x.native==='ans').length,1);
  show({...packet,side:'answer'});const card=q('.cl-flip'),back=q(display==='flash'?'.cl-back .cl-flash-content':'.cl-back .cl-original-content');point(back);const nativeCalls=e.calls.filter(x=>x.native).length;
  assert.equal(click(back,104,110),false);assert.ok(!card.classList.contains('is-flipped'));
  click(card,450,220);assert.ok(card.classList.contains('is-flipped'));assert.equal(e.calls.filter(x=>x.native).length,nativeCalls,'answer-side text/surface flips are visual only');
  if(display==='flash'){
    const term=q('.cl-back .cl-revealed-answer');point(term);click(term,110,110);
    assert.ok(!card.classList.contains('is-flipped'),'a revealed cloze word is not swallowed by the MCQ blank handler');
    assert.equal(e.calls.filter(x=>x.native).length,nativeCalls);
  }
  for(const key of ['c',' ','1','2','3','4','e','b']){let prevented=false;d.dispatch('keydown',{key,ctrlKey:key==='c',target:d.body,preventDefault:()=>prevented=true});assert.equal(prevented,key===' ','only Space changes to a visual flip; copy/rating/edit/browse keys remain native');}
  assert.equal(q('#native-ratings'),ratings);
}
console.log('Flashcard pointer checks passed: text/padding clicks flip, drag release does not flip, repeated clicks suppress word selection, copied ranges stay native, old-engine fallbacks, protected IO and untouched rating keys.');

// Display capitalization must not reveal which option is the authored answer.
{
  const e=startupEnvironment('complete',true);vm.runInNewContext(webScript('appearance.js'),e.context);
  const f=e.context.cramAppearance.choiceText;
  for(const [answer,option,want] of [
    ['OBJECT CLASS TESTING','Integration testing','INTEGRATION TESTING'],
    ['object class testing','Integration Testing','integration testing'],
    ['Object Class Testing','integration testing','Integration Testing'],
    ['Object class testing','Integration Testing','Integration testing'],
    ['DNA Repair','RNA processing','RNA Processing'],
    ['pH','NaCl','NaCl'],['42','3.14','3.14'],
    ['1. BANANA\n2. MANGO','1. apple\n2. pear','1. APPLE\n2. PEAR'],
    ['OBJECT CLASS TESTING','<img src=x>','<IMG SRC=X>'],
  ])assert.equal(f(answer,option),want);
}
const caseQuestion={...cloze,id:'case-match',ready:true,slots:[{number:1,answer:'OBJECT CLASS TESTING',answer_html:'<b>OBJECT CLASS TESTING</b>',choices:['Integration testing','OBJECT CLASS TESTING','System testing','Unit testing'],correct:1}]};
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();vm.runInNewContext(webScript('appearance.js'),e.context);e.run();
  const app=e.context.cram,q=s=>d.querySelector(s),original=JSON.stringify(caseQuestion);
  app.receive('bootstrap',cat);app.receive('session',{session_id:'case-saved',restored:true,questions:[caseQuestion],view:{index:0,picks:{0:[0]}}});
  assert.deepEqual(d.querySelectorAll('.choice-text').map(x=>x.textContent),['INTEGRATION TESTING','OBJECT CLASS TESTING','SYSTEM TESTING','UNIT TESTING']);
  q('[data-choice="0"]').click();assert.equal(q('.ct-blank').textContent,'INTEGRATION TESTING');
  assert.equal(app.state.picks[0][0],0);assert.equal(app.state.questions[0].slots[0].correct,1);
  assert.equal(JSON.stringify(caseQuestion),original,'cached/resumed questions and answer indices stay unchanged');
}
{
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);d.body.innerHTML='<div id="qa"></div><div id="native-ratings"><button>Good 2d</button></div>';
  e.context.requestAnimationFrame=fn=>fn();e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});e.context.pycmd=x=>e.calls.push(x);
  vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('live.js'),e.context);
  const app=e.context.cramNative,packet={cid:'caps',epoch:14,side:'question',display:'exam',question:caseQuestion},original=JSON.stringify(packet),ratings=q('#native-ratings');
  const payload=JSON.stringify(packet).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;app.mount();
  assert.deepEqual(d.querySelectorAll('.cl-choice-text').map(x=>x.textContent),['INTEGRATION TESTING','OBJECT CLASS TESTING','SYSTEM TESTING','UNIT TESTING']);
  q('[data-live-choice="0"]').click();assert.equal(q('.ct-blank').textContent,'INTEGRATION TESTING');
  assert.equal(JSON.stringify(packet),original);assert.equal(app.state.picks[0],0);assert.equal(q('#native-ratings'),ratings);
  assert.equal(e.calls.filter(x=>x==='ans'||/^ease/.test(x)).length,0,'case display does not reveal or rate');
}
console.log('Capitalization checks passed: uppercase/lowercase/title/sentence/list display, cached/resumed sets, filled blanks, original option strings/indices and native ratings unchanged.');

const writingQuestion={id:'write:1',kind:'basic',mode:'write',ready:true,deck:'Fruit',clue:'<b>Name the fruit</b>',slots:[{number:1,answer:'banana, mango, and lemon.',answer_html:'banana, mango, and lemon.'}],writing:{kind:'list',ordered:false,template:'The fruits are <span class="ct-blank" data-write-item="0" data-write-piece="0">\u00a0</span>, <span class="ct-blank" data-write-item="1" data-write-piece="0">\u00a0</span>, and <span class="ct-blank" data-write-item="2" data-write-piece="0">\u00a0</span>.',items:['banana','mango','lemon'].map(answer=>({answer,parts:[answer]}))}};
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();vm.runInNewContext(webScript('appearance.js'),e.context);vm.runInNewContext(webScript('writing.js'),e.context);e.run();
  const app=e.context.cram,q=s=>d.querySelector(s);app.receive('bootstrap',cat);
  d.querySelector('[data-mode="write"]').click();assert.ok(q('#write-ignore-extra'));
  app.receive('session',{session_id:'a'.repeat(32),questions:[writingQuestion],config:{mode:'write',decks:['1'],limit:0,children:true,filters:{}}});
  const input=q('.write-input'),panel=q('.question-panel'),card=q('.write-card');assert.ok(input);assert.ok(card);assert.equal(q('[data-action="write-reveal"]').disabled,false);
  input.value='BANANA';input.dispatch('input');input.dispatch('keydown',{key:'Enter'});
  assert.equal(e.calls.at(-1).action,'write_submit');assert.equal(e.calls.at(-1).text,'BANANA');assert.equal(e.calls.filter(x=>x.action==='grade').length,0);
  app.receive('error','Temporary save failure');assert.equal(input.disabled,false);assert.equal(input.value,'BANANA');
  input.dispatch('keydown',{key:'Enter'});assert.equal(e.calls.at(-1).action,'write_submit','a failed request can be retried');
  const events=[{text:'BANANA',target:0}],state={accepted:[0],remaining:[1,2],target:1,missed:[],complete:false,last:{status:'correct'}};
  app.receive('writeFeedback',{index:0,events,state});assert.equal(q('[data-write-item="0"]').textContent,'banana');assert.equal(q('[data-write-item="1"]').textContent,'\u00a0');assert.equal(q('.question-panel'),panel);assert.equal(q('.write-card'),card);assert.ok(q('.write-clue').textContent.includes(', and '));assert.equal(q('.write-feedback').textContent,'','a partial match has no success banner');
  input.value='man';input.dispatch('input');e.advance(350);const checkpoint=e.calls.filter(x=>x.action==='checkpoint').at(-1);assert.equal(checkpoint.view.written[0].draft,'man');
  q('[data-action="write-reveal"]').click();assert.equal(e.calls.filter(x=>x.action==='grade').length,1,'explicit reveal completes this practice attempt without requiring a correct answer');
  assert.equal(q('[data-write-item="2"]').textContent,'lemon');assert.equal(input.readOnly,true);assert.equal(e.calls.at(-1).action,'grade');assert.equal(e.calls.at(-1).picks.unknown,true);
}
{
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);d.body.innerHTML='<div id="qa"></div><div id="native-ratings"><button data-ease="1">Again 1m</button><button data-ease="3">Good 2d</button></div>';
  e.context.pycmd=msg=>e.calls.push(msg);e.context.requestAnimationFrame=f=>f();e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});
  for(const file of ['appearance.js','writing.js','live.js'])vm.runInNewContext(webScript(file),e.context);
  const app=e.context.cramNative,p={cid:'write:1',epoch:200,side:'question',display:'write',question:writingQuestion,writing_events:[],writing_state:{accepted:[],remaining:[0,1,2],target:0,complete:false,missed:[],last:{status:'idle'}}};
  function show(packet){const payload=JSON.stringify(packet).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;app.mount();}
  show(p);const input=q('.write-input'),ratings=q('#native-ratings'),panel=q('.cl-question-panel');input.value='banana, mango, lemon';input.dispatch('input');input.dispatch('keydown',{key:'Enter'});
  assert.equal(e.calls.filter(x=>x==='ans'||/^ease/.test(x)).length,0);assert.ok(e.calls.some(x=>x.includes('write_submit')));
  app.receive({...p,error:'Temporary failure'});assert.equal(input.disabled,false);assert.equal(input.value,'banana, mango, lemon');input.dispatch('keydown',{key:'Enter'});
  const events=[{text:'banana, mango, lemon',target:0}],state={accepted:[0,1,2],remaining:[],target:0,complete:true,missed:[],last:{status:'correct'}};
  app.receive({...p,writing_events:events,writing_state:state});assert.equal(q('.write-input'),input);assert.equal(q('.cl-question-panel'),panel);assert.equal(input.readOnly,true);assert.equal(q('#native-ratings'),ratings);
  assert.equal(e.calls.filter(x=>x==='ans').length,1,'the checked final answer opens native ratings without a second Enter');
  assert.equal(e.calls.filter(x=>/^ease/.test(x)).length,0,'Writing never chooses a native rating');
  show({...p,side:'answer',writing_events:events,writing_state:state});assert.equal(q('[data-write-item="0"]').textContent,'banana');assert.equal(q('#native-ratings'),ratings);
}
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();vm.runInNewContext(webScript('appearance.js'),e.context);const A=e.context.cramAppearance;
  const cfg={examSize:{width:71,height:64},colors:{dark:{exam:{card:'#152740',buttonBackground:'#24374f',buttonText:'#f0f7ff',question:'#123047'}}}};
  assert.deepEqual(plain(A.palette(cfg,'main','dark','write')),plain(A.palette(cfg,'main','dark','exam')));
  assert.deepEqual(plain(A.sizeGeometry(cfg.examSize,'anki','write')),plain(A.sizeGeometry(cfg.examSize,'anki','exam')));
}
console.log('2.0 Writing checks passed: stable input/card nodes, Enter/paste, partial reveal and draft checkpoints, explicit grading only, passive native review and inherited size/color geometry.');

{
  const e=startupEnvironment('complete',true),d=e.document,handlers={},messages=[],calls=[];d.body.innerHTML='<main id="cram-customize"></main>';
  e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);e.context.pycmd=msg=>calls.push(JSON.parse(msg.slice(12)));
  for(const file of ['appearance.js','customize.js'])vm.runInNewContext(webScript(file),e.context);
  const C=e.context.cramCustomize,q=s=>d.querySelector(s);C.receive('load',{config:{size:{width:72,height:61}},dark:false,assets:'local/'});
  const iframe=q('iframe');iframe.contentWindow={postMessage:msg=>messages.push(msg)};
  q('#preview-view').value='write';q('#preview-view').dispatch('change');assert.match(q('#cu-status').textContent,/shares/);
  q('#size-width').value='81';q('#size-width').dispatch('input');q('#exam-question-height').value='64';q('#exam-question-height').dispatch('input');
  assert.equal(C.state.config.examSize.width,81);assert.equal(C.state.config.examLayout.questionHeight,64);assert.equal(C.state.config.size.width,72);
  q('[data-custom="colors"]').click();q('#hex-card').value='#143047';q('#hex-card').dispatch('input');
  assert.equal(C.state.config.colors.light.exam.card,'#143047');assert.equal(C.state.config.colors.light.flash.card,undefined);assert.equal(q('[data-locate-color="buttonText"]').textContent,'Input / button text');assert.equal(q('[data-locate-color="correct"]'),null);assert.ok(q('[data-locate-color="incorrect"]'));
  q('[data-custom="cancel"]').click();assert.equal(calls.at(-1).action,'cancel');q('[data-custom="save"]').click();assert.equal(calls.at(-1).config.examSize.width,81);
}
{
  const e=startupEnvironment('complete',true),d=e.document,handlers={},out=[],parent={postMessage:data=>out.push(data)};
  e.context.parent=parent;e.context.innerWidth=1360;e.context.innerHeight=900;e.context.requestAnimationFrame=fn=>fn();e.context.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);
  Node.prototype.getBoundingClientRect=function(){return {left:100,right:1200,top:150,bottom:760,width:1100,height:610};};
  for(const file of ['appearance.js','writing.js','customize-preview.js'])vm.runInNewContext(webScript(file),e.context);
  let id=0;const show=(mode,face='question',role=null)=>handlers.message.forEach(fn=>fn({source:parent,data:{type:'cram-preview-config',mode,view:'write',panel:'colors',theme:'dark',face,config:{examSize:{width:81,height:70}},locate:role?{role,label:role,id:++id}:null}}));
  for(const mode of ['main','anki']){
    show(mode);const input=d.querySelector('.write-input');assert.ok(input);input.value='banana';input.dispatch('input');input.dispatch('keydown',{key:'Enter'});
    assert.equal(d.querySelector('[data-write-item="0"]').textContent,'banana');assert.equal(d.querySelector('[data-write-item="1"]').textContent,'\u00a0');
    show(mode,'answer');assert.equal(d.querySelector('[data-write-item="2"]').textContent,'lemon');assert.equal(d.querySelector('.write-input').readOnly,true);
    for(const role of ['buttonBackground','buttonText','incorrect','incorrectBackground','answerText','question','revealText']){
      show(mode,'question',role);const locator=d.querySelector('#preview-locator');assert.ok(locator);assert.ok(d.querySelector('.preview-locate-ring'),mode+'/'+role+' points to a real Writing component');
    }
  }
  assert.equal(e.calls.length,0,'Writing previews cannot call the native or practice bridge');delete Node.prototype.getBoundingClientRect;
}
console.log('2.0 Writing customization and error recovery passed: size/color save/cancel, shared geometry, both live mockups, original-format reveal, real color targets, and retryable input errors.');

// 2.0.1: native Writing check -> reveal -> manual native rating, including misses.
for(const outcome of ['partial','wrong','incomplete','complete','empty','revise']){
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);d.body.innerHTML='<div id="qa"></div><div id="native-ratings"><button data-ease="1">Again 1m</button><button data-ease="4">Easy 4d</button></div>';
  e.context.pycmd=msg=>e.calls.push(msg);e.context.requestAnimationFrame=f=>f();e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});
  for(const file of ['appearance.js','writing.js','live.js'])vm.runInNewContext(webScript(file),e.context);
  const app=e.context.cramNative,p={cid:'enter-'+outcome,epoch:600,side:'question',display:'write',question:writingQuestion,writing_events:[],writing_state:{accepted:[],remaining:[0,1,2],target:0,complete:false,missed:[],last:{status:'idle'}}};
  const show=packet=>{const payload=JSON.stringify(packet).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;app.mount();};
  show(p);const input=q('.write-input'),panel=q('.cl-question-panel'),ratings=q('#native-ratings');
  let prevented=false;input.dispatch('keydown',{key:' ',preventDefault:()=>prevented=true});assert.equal(prevented,false,'Space remains a typing character');
  input.value=outcome==='empty'?'':outcome==='complete'?'banana, mango, lemon':['wrong','revise'].includes(outcome)?'potato':outcome==='incomplete'?'research':'banana';input.dispatch('input');
  input.dispatch('keydown',{key:'Enter',repeat:true});assert.equal(e.calls.filter(x=>x.includes('write_submit')||x==='ans').length,0,'held Enter cannot submit a second action');
  input.dispatch('keydown',{key:'Enter'});
  if(outcome!=='empty'){
    assert.equal(e.calls.filter(x=>x==='ans').length,0,'wait for the checked result before native reveal');
    const status=outcome==='partial'||outcome==='complete'?'correct':outcome==='revise'?'wrong':outcome,accepted=outcome==='complete'?[0,1,2]:outcome==='partial'?[0]:[],remaining=[0,1,2].filter(i=>!accepted.includes(i));
    const packet={...p,writing_events:[{text:input.value,target:0}],writing_state:{accepted,remaining,target:remaining[0]||0,complete:!remaining.length,missed:outcome==='wrong'?[0]:[],last:{status}}};
    app.receive(packet);app.receive(packet);
    if(['wrong','incomplete','revise'].includes(outcome)){
      assert.equal(e.calls.filter(x=>x==='ans').length,0,'a miss never automatically reveals the answer');assert.equal(input.readOnly,false);
      assert.equal(q('.write-enter').textContent,'Reveal answer');if(outcome!=='incomplete'){assert.match(q('.write-feedback').textContent,/Not a match/);assert.ok(q('.write-root').classList.contains('write-error'));}
      if(outcome==='revise'){
        input.value='banana, mango, lemon';input.dispatch('input');assert.equal(q('.write-enter').textContent,'Check answer');input.dispatch('keydown',{key:'Enter'});
        assert.equal(e.calls.filter(x=>x==='ans').length,0,'a revised typo is checked again');
        assert.equal(e.calls.filter(x=>x.includes('write_submit')).length,2);
        app.receive({...packet,writing_events:[...packet.writing_events,{text:input.value,target:0}],writing_state:{accepted:[0,1,2],remaining:[],target:0,complete:true,missed:[0],last:{status:'correct'}}});
      }else input.dispatch('keydown',{key:'Enter'});
    }
  }
  assert.equal(q('.cl-question-panel'),panel);assert.equal(q('#native-ratings'),ratings);
  assert.equal(e.calls.filter(x=>x==='ans').length,outcome==='partial'?0:1,'only a correct partial answer stays in the input');
  assert.equal(e.calls.filter(x=>/^ease/.test(x)).length,0,'no rating or queue advancement is generated');
  if(outcome!=='partial'){
    assert.ok(e.calls.some(x=>x.includes('writing_focus')&&x.includes('false')),'release the input shortcut guard');
    show({...p,side:'answer'});
    for(const key of ['1','2','3','4',' ','e','b']){let blocked=false;d.dispatch('keydown',{key,target:d.body,preventDefault:()=>blocked=true});assert.equal(blocked,false,'native answer-side shortcuts remain available');}
  }
}
console.log('2.0.1 Writing flow passed: one Enter for a final match, editable misses, second-Enter reveal, revision recheck, empty-answer reveal, partial enumeration, Space typing and no automatic ratings.');

// 2.0.5: switch only this scheduled card's view; retain native rating nodes.
{
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);
  d.body.innerHTML='<div id="qa"></div><div id="native-ratings"><button>Again 1m</button><button>Easy 4d</button></div>';
  e.context.pycmd=x=>e.calls.push(x);e.context.requestAnimationFrame=f=>f();e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});
  for(const file of ['appearance.js','writing.js','live.js'])vm.runInNewContext(webScript(file),e.context);
  const app=e.context.cramNative,menu='<div class="cl-settings"><button data-live-action="settings" aria-expanded="false">Settings</button><div id="cl-mode-menu" hidden><button data-live-mode="flash">Flashcards</button><button data-live-mode="write">Writing</button><button data-live-mode="exam">Multiple Choice</button></div></div>';
  const examQ={...cloze,ready:true},writeQ={...writingQuestion,kind:'cloze'};
  const base={cid:'mode-card',card_epoch:10,epoch:10,side:'question',mode:'exam',display:'exam',question:examQ};
  const show=p=>{const payload=JSON.stringify(p).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><header>${menu}</header><div id="cl-stage"><div id="cl-original">Original</div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>`;app.mount();};
  show(base);const ratings=q('#native-ratings');app.choose(1);const picks=plain(app.state.picks);
  q('[data-live-action="settings"]').click();assert.equal(q('#cl-mode-menu').hidden,false);q('[data-live-mode="write"]').click();
  assert.ok(e.calls.some(x=>x.includes('switch_mode')&&x.includes('write')));
  app.switchMode({...base,epoch:11,mode:'write',display:'write',question:writeQ});
  const input=q('.write-input');input.value='first\nsecond\nthird';input.dispatch('input');
  let blocked=false;input.dispatch('keydown',{key:'ArrowUp',preventDefault:()=>blocked=true});assert.equal(blocked,false,'Up moves the textarea caret');
  input.dispatch('keydown',{key:'ArrowDown',preventDefault:()=>blocked=true});assert.equal(blocked,false,'Down moves the textarea caret');
  assert.equal(app.state.writeView.target,0);input.dispatch('keydown',{key:'ArrowDown',altKey:true});assert.equal(app.state.writeView.target,1,'Alt+Down still selects another blank');
  assert.equal(input.getAttribute('rows'),'1');
  app.switchMode({...base,epoch:12,mode:'flash',display:'flash'});assert.ok(q('.cl-compiled-flash'));
  app.switchMode({...base,epoch:13});assert.deepEqual(plain(app.state.picks),picks);
  app.switchMode({...base,epoch:14,mode:'write',display:'write',question:writeQ});assert.equal(q('.write-input').value,'first\nsecond\nthird');assert.equal(app.state.writeView.target,1);
  app.state.writeUI.receive({events:[{text:'first',target:1}],state:{accepted:[],remaining:[0,1,2],target:0,complete:false,last:{status:'incomplete'}}});
  assert.match(q('.write-feedback').textContent,/incomplete/i);assert.ok(q('.write-root').classList.contains('write-error'));
  const stable=q('.write-card');app.switchMode({...base,epoch:13});assert.equal(q('.write-card'),stable,'stale switches are ignored');
  app.switchMode({...base,cid:'wrong-card',epoch:15});assert.equal(q('.write-card'),stable);
  app.switchMode({...base,card_epoch:99,epoch:15});assert.equal(q('.write-card'),stable);
  assert.equal(q('#native-ratings'),ratings);assert.equal(e.calls.filter(x=>x==='ans'||/^ease/.test(x)).length,0);
  show({...base,side:'answer',epoch:15});app.switchMode({...base,side:'answer',epoch:16,mode:'write',display:'write',question:writeQ});
  assert.equal(q('.write-input').readOnly,true);assert.equal(q('#native-ratings'),ratings);
  const image=d.createElement('img');image.src='figure.png';image.setAttribute('src','figure.png');q('.write-clue').appendChild(image);
  image.dispatch('click');image.dispatch('click');assert.equal(e.calls.filter(x=>x==='ans').length,0);
  image.dispatch('dblclick');assert.ok(q('#cl-photo-viewer'));assert.equal(q('#cl-photo-image').src,'figure.png');
  q('[data-live-action="photo-plus"]').click();assert.equal(app.state.photo.zoom,1.25);
  q('[data-live-action="photo-close"]').click();assert.ok(!q('#cl-photo-viewer'));assert.equal(image.isConnected,true);
  image.dispatch('dblclick');let escape=false;d.dispatch('keydown',{key:'Escape',target:d.body,preventDefault:()=>escape=true});assert.equal(escape,true);assert.ok(!q('#cl-photo-viewer'));
  image.dispatch('dblclick');show({...base,epoch:16,side:'answer',mode:'write',display:'write',question:writeQ});assert.equal(app.state.photo,null,'a native redraw clears a detached viewer');
  assert.equal(q('#native-ratings'),ratings);assert.equal(e.calls.filter(x=>x==='ans'||/^ease/.test(x)).length,0,'mode/image controls never reveal or rate');
}
console.log('2.0.5 controls passed: same-card mode menu, preserved choices/draft, stale-packet guards, unchanged ratings, image viewer/X/Escape, one-line input, caret arrows, separate blank navigation and incomplete feedback.');

// Filled MCQ phrases follow normal inline flow; only intentional source lines stay.
{
  const e=startupEnvironment('complete',true);e.body();vm.runInNewContext(webScript('appearance.js'),e.context);const A=e.context.cramAppearance;
  const ieee={answer:'Institute for Electrical and\nElectronic Engineers (IEEE)',answer_html:'Institute for Electrical and\nElectronic Engineers (IEEE)'};
  assert.equal(A.blankText(ieee,ieee.answer),'Institute for Electrical and Electronic Engineers (IEEE)');
  const itu={answer:'International Telecommunications\nUnion (ITU)',answer_html:'<b>International Telecommunications\nUnion (ITU)</b>'};
  assert.equal(A.blankText(itu,itu.answer),'International Telecommunications Union (ITU)');
  assert.equal(A.blankText(itu,'Internet Engineering\nTask Force (IETF)'),'Internet Engineering Task Force (IETF)');
  const explicit={answer:'first\nsecond',answer_html:'first<br>second'};
  assert.equal(A.blankText(explicit,explicit.answer),'first\nsecond');
  const list={answer:'3. banana\n4. mango',answer_html:'<ol start="3"><li>banana</li><li>mango</li></ol>'};
  assert.match(A.blankText(list,list.answer),/^3\. banana\n4\. mango$/);
  assert.equal(A.blankText(list,'1. orange\n2. lemon'),'1. orange\n2. lemon');
  assert.equal(A.blankText({answer:'a',answer_html:'a'},'<img src=x>'),'<img src=x>','an option is still rendered as text');
  const span=e.document.createElement('span');A.fillBlank(span,explicit,explicit.answer);assert.ok(span.classList.contains('cram-blank-lines'));
  A.fillBlank(span,itu,itu.answer);assert.ok(!span.classList.contains('cram-blank-lines'));
  assert.equal(ieee.answer,'Institute for Electrical and\nElectronic Engineers (IEEE)','source/cache text is not rewritten');
}
console.log('2.0.6 blank text passed: soft pasted newlines, inline markup, explicit BRs, numbered source/generated lists, safe option text and unchanged cached answers.');

// Revealed mode transitions must keep the requested mode and visible-answer count.
{
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);
  d.body.innerHTML='<div id="qa"></div><div id="native-ratings"><button>Again 1m</button><button>Easy 4d</button></div>';
  e.context.pycmd=x=>e.calls.push(x);e.context.requestAnimationFrame=f=>f();e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});
  for(const file of ['appearance.js','writing.js','live.js'])vm.runInNewContext(webScript(file),e.context);
  const app=e.context.cramNative;
  const slots=['48 bits','12 hexadecimal digits','6 bytes'].map((answer,i)=>({number:i+1,answer,answer_html:answer,choices:[answer,'Wrong A','Wrong B','Wrong C'],correct:0}));
  const ready={id:'mac',kind:'cloze',mode:'exam',ready:true,clue:'A MAC address is <span data-blank="0"></span> long, expressed as <span data-blank="1"></span> or <span data-blank="2"></span>.',slots};
  const missing={...ready,ready:false,slots:slots.map(({choices,correct,...slot})=>slot)};
  const base={cid:'reveal-mode-card',card_epoch:20,epoch:20,side:'answer',mode:'flash',display:'flash',question:ready};
  const show=p=>{const payload=JSON.stringify(p).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-stage"><div id="cl-original">Native answer</div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>`;app.mount();};
  show(base);const ratings=q('#native-ratings');assert.ok(q('.cl-flip'));
  const pending={...base,epoch:21,mode:'exam',display:'exam',question:missing};app.switchMode(pending);
  assert.ok(q('.cl-exam'),'uncached revealed Multiple Choice remains a Multiple Choice panel');assert.equal(q('.cl-flip'),null);
  assert.equal(q('#cl-original').hidden,true);assert.match(q('.cl-clue').textContent,/48 bits.*12 hexadecimal digits.*6 bytes/);
  assert.ok(q('[data-live-action="generate"]'),'missing choices can be prepared after reveal');
  q('.cl-clue').click();q('.cl-clue').click();assert.equal(q('.cl-flip'),null);
  app.receive({...pending,generating:true});assert.match(q('#cl-notice').textContent,/Preparing choices/);assert.equal(q('[data-live-action="generate"]').disabled,true);
  app.receive({...pending,generating:false,question:ready});
  assert.equal(d.querySelectorAll('.cl-choice').length,12);assert.equal(d.querySelectorAll('.cl-choice.correct').length,3);
  assert.ok([...d.querySelectorAll('.cl-choice')].every(el=>el.disabled));assert.equal(q('.cl-feedback'),null,'viewing a revealed answer is not a failed MCQ attempt');
  app.state.active=2;app.moveBlank(-1);assert.equal(app.state.active,1,'revealed choices for every blank remain inspectable');
  const writeQ={...writingQuestion,kind:'cloze'};
  app.switchMode({...base,epoch:22,mode:'write',display:'write',question:writeQ});
  assert.equal(q('.write-progress').textContent,'3 / 3 revealed');assert.equal(q('.write-input').readOnly,true);
  assert.deepEqual(plain(app.state.writeView.state.accepted),[],'revealed counts do not invent correct typed answers');
  app.switchMode({...base,epoch:23,mode:'exam',display:'exam',question:ready});assert.equal(d.querySelectorAll('.cl-choice').length,12);
  app.switchMode({...base,epoch:24});assert.ok(q('.cl-flip'));
  app.switchMode({...base,epoch:25,mode:'exam',display:'exam',question:ready});assert.equal(q('.cl-flip'),null);assert.equal(d.querySelectorAll('.cl-choice').length,12);
  assert.equal(q('#native-ratings'),ratings);assert.equal(e.calls.filter(x=>x==='ans'||/^ease/.test(x)).length,0);
}
console.log('2.0.8 revealed transitions passed: no flippable MCQ fallback, late choices, all blank choices inspectable, revealed Writing count, no invented correctness or native reveal/rating.');

// Flashcard Space always flips, retains recall controls, and cannot submit/advance.
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();e.run();const app=e.context.cram,q=s=>d.querySelector(s);
  const key=(value,extra={})=>d.dispatch('keydown',{key:value,code:value===' '?'Space':value,target:d.body,...extra});
  app.receive('bootstrap',{...cat,preferences:{auto_advance:false}});
  app.receive('session',{session_id:'b'.repeat(32),questions:[flashA,flashB]});
  key(' ');assert.ok(q('.flash-card').classList.contains('is-flipped'));
  key(' ');assert.ok(!q('.flash-card').classList.contains('is-flipped'));assert.equal(q('[data-action="known"]').disabled,false,'a revealed answer can still be rated while showing its clue');
  for(let i=0;i<5;i++)key(' ');assert.equal(app.state.index,0);assert.equal(e.calls.filter(x=>x.action==='grade').length,0);
  const saved=e.calls.filter(x=>x.action==='checkpoint').at(-1).view;assert.deepEqual(plain(saved.flashSeen),[0]);
  key(' ');key('2');assert.equal(e.calls.at(-1).action,'grade');
  app.receive('graded',{index:0,result:{earned:1,total:1,correct:[true],picks:{known:true}},queued:null});
  key(' ');key(' ');assert.equal(app.state.index,0,'Space does not mean Continue in Flashcards, even after grading');
  key('Enter');assert.equal(app.state.index,1,'explicit existing Continue shortcut remains available');
  app.receive('session',{session_id:'b'.repeat(32),restored:true,questions:[flashA,flashB],view:{index:0,revealed:[],flashSeen:[0]}});
  assert.ok(!q('.flash-card').classList.contains('is-flipped'));assert.equal(q('[data-action="unknown"]').disabled,false);
  key('1');assert.equal(e.calls.at(-1).picks.known,false);
}
{
  const e=startupEnvironment('complete',true),d=e.document;e.context.pycmd=x=>e.calls.push(x);e.context.requestAnimationFrame=f=>f();e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});
  for(const file of ['appearance.js','live.js'])vm.runInNewContext(webScript(file),e.context);
  const app=e.context.cramNative,q=s=>d.querySelector(s);
  const show=p=>{const payload=JSON.stringify(p).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');d.body.innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-original">Native</div><div id="cl-custom"></div><div id="cl-notice"></div></section><div id="native-ratings"><button>Again 1m</button><button>Good 4d</button></div>`;app.mount();};
  const p={cid:'space-card',card_epoch:50,epoch:50,mode:'flash',display:'flash',side:'question',question:flashA};
  show(p);const press=(extra={})=>{let blocked=false;d.dispatch('keydown',{key:' ',code:'Space',target:d.body,preventDefault:()=>blocked=true,...extra});return blocked;};
  assert.equal(press(),true);assert.equal(press(),true);assert.equal(e.calls.filter(x=>x==='ans').length,1);
  show({...p,side:'answer'});const ratings=q('#native-ratings'),face=q('.cl-flip');
  for(let i=0;i<6;i++){const before=face.classList.contains('is-flipped');assert.equal(press(),true);assert.equal(face.classList.contains('is-flipped'),!before);assert.equal(q('#native-ratings'),ratings);}
  const before=face.classList.contains('is-flipped');assert.equal(press({repeat:true}),true);assert.equal(face.classList.contains('is-flipped'),before);
  assert.equal(press({ctrlKey:true}),false);assert.equal(e.calls.filter(x=>x==='ans').length,1);assert.ok(!e.calls.some(x=>/^ease/.test(x)));
  app.state.packet={...p,display:'exam',mode:'exam',question:{ready:false}};assert.equal(press(),true,'MCQ question Space uses the guarded native ans reveal');
  for(const display of ['io','write']){app.state.packet={...p,display,mode:display,question:{ready:false}};assert.equal(press(),false,'Space stays native in '+display);}
  app.state.packet={...p,display:'native',mode:'exam'};assert.equal(press(),false,'original-card fallback inside MCQ stays native');
  d.body.innerHTML='<p>Ordinary Anki</p>';assert.equal(press(),false);
}
console.log('2.0.9 Flashcard Space passed: repeated visual flips, reveal once, persistent recall controls, no grading/advance, explicit ratings, and other modes/ordinary Anki unchanged.');

{
  const e=startupEnvironment('complete',true),d=e.document;e.body();
  for(const file of ['appearance.js','writing.js'])vm.runInNewContext(webScript(file),e.context);e.run();
  const app=e.context.cram,q=s=>d.querySelector(s),key=(key,target=d.body)=>d.dispatch('keydown',{key,code:key===' '?'Space':key,target,preventDefault(){}});
  app.receive('bootstrap',{...cat,preferences:{auto_advance:true,feedback_ms:600}});
  app.receive('session',{session_id:'c'.repeat(32),questions:[cloze,cloze],config:{mode:'exam',decks:['1'],order:'shuffle'}});
  app.state.picks[0]=[0,0];app.receive('graded',{index:0,result:{earned:0,total:2,correct:[false,false]}});
  assert.equal(q('[data-blank="0"]').textContent,cloze.slots[0].answer,'the revealed clue shows the correct answer');
  assert.equal(q('[data-blank="1"]').textContent,cloze.slots[1].answer);
  assert.equal(app.state.autoTimer,null);e.advance(20000);assert.equal(app.state.index,0,'misses never advance on a timer');
  q('[data-action="options"]').click();q('[data-action="restart-practice"]').click();
  key(' ');assert.equal(app.state.index,0,'restart confirmation owns keyboard focus');
  q('[data-action="restart-confirm"]').click();assert.deepEqual(plain(e.calls.at(-1)),{action:'restart',session_id:'c'.repeat(32)});
  assert.equal(q('#restart-modal'),null);
  const session=()=>app.receive('session',{session_id:'d'.repeat(32),questions:[writingQuestion,writingQuestion],config:{mode:'write',decks:['1']}});
  session();let input=q('.write-input');input.value='stone';input.dispatch('input');input.dispatch('keydown',{key:'Enter'});
  const wrongEvents=[{text:'stone',target:0}],wrongState={accepted:[],remaining:[0,1,2],target:0,complete:false,missed:[0],last:{status:'wrong'}};
  app.receive('writeFeedback',{index:0,events:wrongEvents,state:wrongState});assert.equal(q('.write-enter').textContent,'Reveal answer');assert.equal(input.readOnly,false);
  input.value='banana';input.dispatch('input');assert.equal(q('.write-enter').textContent,'Check answer');input.dispatch('keydown',{key:'Enter'});assert.equal(e.calls.at(-1).action,'write_submit','editing a miss checks the revision');
  app.receive('writeFeedback',{index:0,events:wrongEvents,state:wrongState});input.dispatch('keydown',{key:'Enter'});assert.equal(e.calls.at(-1).action,'grade');assert.equal(e.calls.at(-1).picks.unknown,true,'an unchanged second Enter can finish a miss');
  assert.equal(q('.write-progress').textContent,'3 / 3 revealed');
  app.receive('graded',{index:0,result:{earned:0,total:3,correct:[false,false,false]}});e.advance(10000);assert.equal(app.state.index,0);
  session();input=q('.write-input');input.value='banana mango lemon';input.dispatch('input');input.dispatch('keydown',{key:'Enter'});
  app.receive('writeFeedback',{index:0,events:[{text:'banana mango lemon',target:0}],state:{accepted:[0,1,2],remaining:[],target:0,complete:true,missed:[],last:{status:'correct'}}});
  assert.equal(e.calls.at(-1).action,'grade');assert.equal(e.calls.at(-1).picks.unknown,false,'a final correct Enter finishes once');
  const count=e.calls.filter(x=>x.action==='write_submit'||x.action==='grade').length;input.dispatch('keydown',{key:'Enter'});
  assert.equal(e.calls.filter(x=>x.action==='write_submit'||x.action==='grade').length,count,'accepted/revealed input cannot add an accidental wrong attempt');
}
console.log('2.0.10 MAIN parity passed: correct revealed clue, unlimited miss feedback, in-session restart, shared editable-miss/final-match Writing flow and duplicate Enter guard.');

// 2.0.13: automatic image-answer cards use the real flashcard UI in either entry.
const imageAnswer={id:'formula-photo',kind:'basic',mode:'flash',image_answer:true,deck:'Math',clue:'Which formula applies?',slots:[{number:1,answer:'',answer_html:'<img src="formula.png" alt="Formula">'}]};
{
  const e=startupEnvironment('complete',true),d=e.document;e.body();e.run();const app=e.context.cram,q=s=>d.querySelector(s);
  app.receive('bootstrap',cat);app.receive('session',{questions:[imageAnswer,cloze]});
  assert.ok(q('.flash-card'));assert.equal(q('.choice'),null);assert.equal(q('.write-input'),null);
  assert.equal(q('#answer img').getAttribute('src'),'formula.png');
  for(let i=0;i<4;i++)d.dispatch('keydown',{key:' ',code:'Space',target:d.body});
  assert.equal(app.state.index,0);assert.equal(e.calls.filter(x=>x.action==='grade').length,0);
  q('[data-action="known"]').click();assert.equal(e.calls.at(-1).picks.known,true);
}
for(const mode of ['exam','write']){
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);
  d.body.innerHTML='<div id="qa"></div><div id="native-ratings"><button>Again</button><button>Good</button></div>';
  e.context.pycmd=x=>e.calls.push(x);e.context.requestAnimationFrame=f=>f();
  e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});
  for(const file of ['appearance.js','writing.js','live.js'])vm.runInNewContext(webScript(file),e.context);
  const app=e.context.cramNative,p={cid:'image-answer',epoch:1,card_epoch:1,side:'question',mode,display:'flash',question:imageAnswer};
  const show=packet=>{const payload=JSON.stringify(packet).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-stage"><div id="cl-original">Native</div><div id="cl-custom"></div></div><div id="cl-notice"></div></section>`;app.mount();};
  show(p);const ratings=q('#native-ratings');assert.ok(q('.cl-compiled-flash'));assert.equal(q('.cl-choice'),null);assert.equal(q('.write-input'),null);
  assert.equal(q('.cl-back img').getAttribute('src'),'formula.png');
  let prevented=false;d.dispatch('keydown',{key:' ',code:'Space',target:d.body,preventDefault:()=>prevented=true});
  assert.ok(prevented);assert.equal(e.calls.filter(x=>x==='ans').length,1);
  show({...p,side:'answer'});const card=q('.cl-flip');
  for(let i=0;i<6;i++){
    const before=card.classList.contains('is-flipped');app.flip();assert.notEqual(card.classList.contains('is-flipped'),before);
  }
  assert.equal(e.calls.filter(x=>x==='ans').length,1);assert.ok(!e.calls.some(x=>/^ease/.test(x)));
  assert.equal(q('#native-ratings'),ratings);assert.equal(app.state.packet.mode,mode);
}
console.log('2.0.13 image answers passed: original image, automatic flashcard UI, no writing/MCQ controls, repeated Space flips and explicit recall/native ratings only.');


// Library layout retains the deck tree, selection, all saved sets and exact IDs.
{
 const e=startupEnvironment('complete',true);e.body();e.run();const d=e.document,app=e.context.cram,q=s=>d.querySelector(s),tap=s=>{assert.ok(q(s),s);q(s).click();};
 const decks=[{id:'1',name:'MIDTERMS',count:0,total_count:9},{id:'2',name:'MIDTERMS::SEPC',count:0,total_count:9},{id:'3',name:'MIDTERMS::SEPC::Lesson 1',count:9,total_count:9},{id:'4',name:'FINAL',count:2,total_count:2},{id:'90',name:'Today only',filtered:true,count:3,total_count:3},{id:'91',name:'Practice mistakes',filtered:true,count:2,total_count:2}];
 const saved=Array.from({length:9},(_,i)=>({id:String(i+1).padStart(32,'a'),decks:['MIDTERMS::SEPC::Lesson '+(i+1)],config:{mode:i%2?'exam':'flash'},answered:i,total:20}));
 app.receive('bootstrap',{...cat,decks,saved_sessions:saved});assert.equal(d.querySelectorAll('.deck-family').length,2);assert.equal(q('.filtered-family').querySelectorAll('.deck-row').length,2);assert.equal(q('[data-deck="90"]').closest('.deck-family'),null,'standalone filtered decks stay outside normal families');
 assert.equal(q('[data-branch="MIDTERMS"]').getAttribute('aria-expanded'),'false');tap('[data-branch="MIDTERMS"]');tap('[data-branch="MIDTERMS::SEPC"]');assert.ok(q('[data-deck="3"]'));assert.equal(q('[data-deck="3"]').closest('[data-family]').dataset.family,'MIDTERMS');
 q('[data-deck="90"]').checked=true;q('[data-deck="90"]').dispatch('change');tap('#start');assert.ok(e.calls.at(-1).config.decks.includes('90'));assert.equal(e.calls.at(-1).config.filters.search,'');
 assert.equal(d.querySelectorAll('.saved-row').length,2);assert.equal(q('.saved-row strong').textContent,'Lesson 1');assert.ok(!q('.saved-row strong').textContent.includes('MIDTERMS'));assert.ok(q('.saved-row strong').getAttribute('title').includes('MIDTERMS::SEPC'));
 tap('[data-action="saved-more"]');assert.equal(d.querySelectorAll('.saved-row').length,9);q('#saved-search').value='Lesson 8';q('#saved-search').dispatch('input');assert.equal(d.querySelectorAll('.saved-row').length,1);tap('[data-resume="'+saved[7].id+'"]');assert.deepEqual(e.calls.at(-1),{action:'resume',session_id:saved[7].id});
 q('#saved-search').value='';q('#saved-search').dispatch('input');tap('[data-action="saved-more"]');assert.equal(d.querySelectorAll('.saved-row').length,2);assert.equal(q('#saved-search').value,'');
 q('#deck-search').value='Lesson 1';q('#deck-search').dispatch('input');assert.equal(d.querySelectorAll('.deck-row').length,1);assert.match(q('.deck-path').textContent,/MIDTERMS/,'search retains hierarchy context');
 assert.ok(q('details.filter-help summary'));app.receive('theme',true);assert.ok(d.documentElement.classList.contains('cram-dark'));assert.ok(q('[data-action="regen-decks"]'));
 const css=webScript('app.css');assert.match(css,/\.home-page \.saved-list/);assert.match(css,/\.home-page \.filtered-family/);
}
console.log('2.0.14 library checks passed: separate filtered roots, intact nested tree and payloads, concise saved names, latest two/all/search/Resume/Reset, dark theme and retained controls.');

{
 const e=startupEnvironment('complete',true);e.body();e.run();const d=e.document,app=e.context.cram,q=s=>d.querySelector(s);
 const make=(id,decks)=>({id:id.repeat(32),decks,config:{mode:'flash'},answered:1,total:5});
 app.receive('bootstrap',{...cat,saved_sessions:[make('a',['MIDTERMS::SEPC::Lesson 1']),make('b',['MIDTERMS::Anatomy::Lesson 1']),make('c',['Other::Lesson 3'])]});
 q('[data-action="saved-more"]').click();q('#saved-search').value='Lesson 3';q('#saved-search').dispatch('input');
 app.receive('bootstrap',{...cat,saved_sessions:[make('a',['MIDTERMS::SEPC::Lesson 1']),make('b',['MIDTERMS::Anatomy::Lesson 1'])]});
 assert.equal(d.querySelectorAll('.saved-row').length,2,'after reset shrinks the list, a hidden stale search cannot hide other progress');assert.equal(app.state.savedSearch,'');
 const context=d.querySelectorAll('.saved-context').map(el=>el.textContent);assert.deepEqual(context,['SEPC','Anatomy']);assert.equal(q('.saved-row strong').textContent,'Lesson 1');
 app.receive('bootstrap',{...cat,saved_sessions:[make('c',['MIDTERMS::SEPC::Lesson 1','MIDTERMS::Anatomy::Lesson 1'])]});assert.equal(q('.saved-row strong').textContent,'Lesson 1 +1');
}
console.log('Saved-name edge cases passed: duplicate lessons, combined deck count and no hidden stale search after reset.');

// Provider-neutral settings and preparation copy use the active provider.
select('#options-modal')?.remove();
emit('bootstrap',{...cat,settings:{model:'groq:openai/gpt-oss-20b',has_key:true,provider_name:'Groq'}});
click('[data-action="options"]');
assert.match(select('#options-modal').textContent,/Groq key added/);
assert.match(select('#options-modal').textContent,/AI settings/);
click('[data-action="close-options"]');
emit('prepare',{questions:1,cached:0,missing:1,has_key:true,model:'groq:openai/gpt-oss-20b'});
assert.match(root.textContent,/Groq creates three/);
assert.match(root.textContent,/sent to Groq/);
assert.doesNotMatch(root.textContent,/sent to Google Gemini/);
console.log('AI provider UI passed: selected-provider key status and preparation recipient, neutral AI Settings entry.');

// Ready answer choices survive pointer focus, duplicate shown hooks and status packets.
for(const mode of ['main','anki']){
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);
  let app,packet;
  if(mode==='main'){
    e.body();e.run();app=e.context.cram;app.receive('bootstrap',cat);
    app.receive('session',{questions:[{...pagedQuestion,slots:pagedQuestion.slots.slice(0,1)}]});
  }else{
    d.body.innerHTML='<div id="qa"></div><div id="ratings">Again Hard Good Easy</div>';
    e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});
    e.context.pycmd=msg=>e.calls.push(msg.startsWith('cram_live:')?JSON.parse(msg.slice(10)):{native:msg});
    vm.runInNewContext(webScript('live.js'),e.context);app=e.context.cramNative;
    packet={cid:'stable',epoch:901,side:'question',display:'exam',question:{...pagedQuestion,slots:pagedQuestion.slots.slice(0,1),ready:false}};
    const payload=JSON.stringify(packet).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    q('#qa').innerHTML=`<section id="cram-live" data-packet="${payload}"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;
    app.mount();packet={...packet,question:{...packet.question,ready:true}};app.receive(packet);
  }
  const selector=mode==='main'?'.choice':'.cl-choice',pane=q(mode==='main'?'.choice-section':'.cl-answers');
  const button=q(selector),before=Array.from(d.querySelectorAll(selector));pane.scrollTop=146;
  for(let i=0;i<15;i++){button.dispatch('pointermove');button.dispatch('focusin');}
  assert.equal(pane.scrollTop,146,mode+' same-blank focus must retain scroll');
  button.click();const picks=mode==='main'?Array.from(app.state.picks[0]):Array.from(app.state.picks);
  assert.deepEqual(picks,[0]);const count=e.calls.length;
  if(mode==='anki'){
    for(let i=0;i<10;i++){app.mount();app.receive({...packet,generating:false});}
    assert.equal(e.calls.length,count,'duplicate mount/status must not request generation');
    assert.equal(app.state.packet.question.ready,true);
    assert.deepEqual(Array.from(app.state.picks),[0]);
  }
  assert.ok(before.every((node,i)=>node===d.querySelectorAll(selector)[i]),mode+' keeps option DOM nodes');
}
assert.match(webScript('live.css'),/#cram-live button\.cl-choice:hover[^}]*animation:none!important/);
console.log('2.0.22 choice stability passed: focus/scroll, hover, ready packets, duplicate native mount, picks and stable option nodes.');

// Space requests native reveal once. Keep filled blanks and the same option
// nodes when Anki replaces the whole #qa; late button activation cannot edit.
{
  const e=startupEnvironment('complete',true),d=e.document,q=s=>d.querySelector(s);
  d.body.innerHTML='<div id="qa"></div><div id="ratings">Again Hard Good Easy</div>';
  e.context.getComputedStyle=()=>({fontSize:'23px',lineHeight:'normal'});
  e.context.pycmd=msg=>e.calls.push(msg.startsWith('cram_live:')?JSON.parse(msg.slice(10)):{native:msg});
  vm.runInNewContext(webScript('appearance.js'),e.context);
  vm.runInNewContext(webScript('live.js'),e.context);const app=e.context.cramNative;
  const question={...pagedQuestion,clue:[0,1,2].map(i=>`Part ${i+1}: <span class="ct-blank" data-blank="${i}">_____</span>`).join('<br>'),slots:pagedQuestion.slots.slice(0,3),ready:true};
  const packet={cid:'space-three',epoch:950,card_epoch:950,side:'question',mode:'exam',display:'exam',question};
  const mount=p=>{
    const raw=JSON.stringify(p).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    q('#qa').innerHTML=`<section id="cram-live" data-packet="${raw}"><div id="cl-original"></div><div id="cl-custom"></div><div id="cl-notice"></div></section>`;
    app.mount();
  };
  mount(packet);for(let i=0;i<3;i++)app.choose(1);
  const frame=q('.cl-exam'),blanks=Array.from(d.querySelectorAll('.cl-clue [data-blank]')),choices=Array.from(d.querySelectorAll('.cl-choice'));
  assert.deepEqual(blanks.map(n=>n.textContent),['Cell','Cell','Cell']);
  let prevented=0;const space={key:' ',code:'Space',preventDefault:()=>prevented++};
  choices[9].dispatch('keydown',space);assert.equal(prevented,1);assert.equal(app.state.pending,true);
  // Key repeat, a second shortcut and a delayed browser click are all harmless.
  choices[9].dispatch('keydown',{...space,repeat:true});app.reveal();choices[8].click();app.choose(0);
  assert.equal(e.calls.filter(call=>call.native==='ans').length,1);
  assert.deepEqual(Array.from(app.state.picks),[1,1,1]);
  assert.deepEqual(blanks.map(n=>n.textContent),['Cell','Cell','Cell']);
  mount({...packet,side:'answer'});
  assert.equal(q('.cl-exam'),frame);assert.ok(blanks.every((n,i)=>n===d.querySelectorAll('.cl-clue [data-blank]')[i]));
  assert.ok(choices.every((n,i)=>n===d.querySelectorAll('.cl-choice')[i]));
  assert.deepEqual(blanks.map(n=>n.textContent),['Cell','Cell','Cell']);
  assert.ok(blanks.every(n=>!n.classList.contains('cram-blank-empty')));
  assert.ok(choices.every(n=>n.disabled));assert.equal(d.querySelectorAll('.cl-feedback').length,1);
  app.mount();assert.equal(d.querySelectorAll('.cl-feedback').length,1);
  assert.ok(!e.calls.some(call=>/ease/.test(call.native||'')));
  mount({...packet,cid:'next-card',epoch:951,card_epoch:951});
  assert.notEqual(q('.cl-exam'),frame);assert.deepEqual(Array.from(app.state.picks),[]);
  assert.ok(Array.from(d.querySelectorAll('.cl-clue [data-blank]')).every(n=>n.classList.contains('cram-blank-empty')));
  // Revealing a wrong or incomplete attempt still fills every correct answer.
  const next={...packet,cid:'next-card',epoch:951,card_epoch:951};app.choose(0);app.reveal();mount({...next,side:'answer'});
  assert.deepEqual(Array.from(d.querySelectorAll('.cl-clue [data-blank]')).map(n=>n.textContent),['Cell','Cell','Cell']);
  assert.equal(q('.cl-feedback').textContent,'0 / 3 correct');assert.equal(d.querySelectorAll('.cl-choice.incorrect').length,1);
}
console.log('2.0.23 Space reveal passed: selected cloze text, pending-click/repeat guard, stable question/options across native answer replacement, feedback and new-card reset.');
