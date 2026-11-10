/* MAIN CRAM. No API keys, remote scripts, or external assets in this view. */
(() => {
  'use strict';
  function initCram(){
  if(window.cram)return;
  const root=document.getElementById('cram-app');
  if(!root)return;
  window.cramAppearance?.preventStudySelection(root,'.exam-card .ct-blank,.waiting-card .ct-blank,.flash-card .cram-blank-empty,.io-card,#viewer,.flash-card img,.exam-card img');
  const flashPointer=window.cramAppearance?.flashcardPointer(root,'.flash-card');
  const shapes={
    book:'<path d="M4 4h6a3 3 0 0 1 2 1 3 3 0 0 1 2-1h6v15h-6a3 3 0 0 0-2 1 3 3 0 0 0-2-1H4Z"/><path d="M12 5v15"/>',
    cards:'<rect x="7" y="7" width="14" height="14" rx="2" fill="currentColor" opacity=".35" stroke="none"/><rect x="3" y="3" width="14" height="14" rx="2" fill="currentColor" stroke="none"/>',
    bolt:'<path d="m13 3-8 11h7l-1 7 8-11h-7Z"/>',mix:'<path d="m4 5 16 14m-5 0h5v-5M4 19 20 5m-5 0h5v5"/>',
    search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
    settings:'<path d="M4 7h5m4 0h7M4 17h9m4 0h3"/><circle cx="11" cy="7" r="2"/><circle cx="15" cy="17" r="2"/>',
    check:'<path d="m5 12 4 4L19 6"/>',x:'<path d="m6 6 12 12M6 18 18 6"/>',arrow:'<path d="M5 12h14m-6-6 6 6-6 6"/>',back:'<path d="M19 12H5m6-6-6 6 6 6"/>',
    history:'<path d="M3 4v6h6M3.5 10a8.5 8.5 0 1 1 1 7M12 7v5l3 2"/>',
    edit:'<path d="m15 5 4 4M4 20l5-1L20 8a2.8 2.8 0 0 0-4-4L5 15Z"/>',refresh:'<path d="M20 4v6h-6M4 20v-6h6M4 9a8 8 0 0 1 13-4l3 5M4 14l3 5a8 8 0 0 0 13-4"/>',
    plus:'<path d="M12 5v14M5 12h14"/>',minus:'<path d="M5 12h14"/>',expand:'<path d="M4 9V4h5m6 0h5v5M4 15v5h5m11-5v5h-5"/>',
    eye:'<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    spark:'<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5Z"/>',
    sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2"/>'
  };
  const icon=n=>`<svg class="cram-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${shapes[n]||shapes.book}</svg>`;
  const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const text=html=>{const d=document.createElement('div');d.innerHTML=html||'';return d.textContent.trim();};
  const S={screen:'home',cat:null,appearance:{},customizing:false,selected:new Set(),mode:'flash',limit:'0',children:true,shuffle:true,search:'',questions:[],index:0,results:{},picks:{},revealed:new Set(),flashSeen:new Set(),zoom:1,fullscreen:false,busy:false,pending:false,prep:null,error:'',history:[],activeSlot:0,written:{},ioMasks:{},writeUI:null,ignoreExtra:false,filters:{search:'',tag:'',flag:'',note_type:''},repeat:false,repeatActive:false,matchRequest:0,order:'shuffle',orderDesc:false,collapsed:new Set(),treeSeen:new Set(),autoAdvance:true,feedbackMs:1000,textZoom:1,generating:false,genProgress:null,autoTimer:null,savedExpanded:false,savedSearch:''};
  function send(action,data={}){if(['restart','grade','write_submit'].includes(action)&&S.sessionId)data={session_id:S.sessionId,...data};if(typeof pycmd==='function')pycmd('cram:'+JSON.stringify({action,...data}));else if(window.cramDemo)window.cramDemo(action,data);}
  function checkpoint(){
    if(S.screen!=='session'||!S.sessionId)return;
    send('checkpoint',{session_id:S.sessionId,view:{index:S.index,picks:S.picks,written:S.written,ioMasks:S.ioMasks,revealed:[...S.revealed],flashSeen:[...S.flashSeen],activeSlot:S.activeSlot,zoom:S.fullscreen?S.previewZoom:S.zoom,scroll:window.scrollY||0}});
  }
  function toast(message){const el=document.getElementById('toast');el.textContent=message;el.style.display='block';clearTimeout(S.toastTimer);S.toastTimer=setTimeout(()=>el.style.display='none',6500);}
  const brand=()=>`<div class="brand"><span class="brand-icon">${icon('cards')}</span><span class="main-mode-label"><strong>MAIN CRAM</strong><small>Practice only · Schedule unchanged</small></span></div>`;
  const button=(action,label,kind='secondary',ic='',extra='')=>`<button class="btn ${kind}" data-action="${action}" ${extra}>${ic?icon(ic):''}${label}</button>`;
  const ib=(action,label,ic,extra='')=>`<button class="icon-btn" data-action="${action}" title="${label}" aria-label="${label}" ${extra}>${icon(ic)}</button>`;
  let startupTimer=null,startupWait=null,startupAttempts=0,startupDone=false;
  function startupError(message){
    clearTimeout(startupTimer);clearTimeout(startupWait);
    if(S.cat)return;
    S.screen='startup-error';
    root.innerHTML=`<div class="boot"><section class="panel prepare"><div class="brand-mark" style="margin:0 auto 20px">C</div><h2>MAIN CRAM couldn’t finish opening.</h2><p>${esc(message)}</p>${button('startup-retry','Try opening again','primary','refresh')}<p class="microcopy">If this continues, close this window and restart Anki.</p></section></div>`;
  }
  function connectToAnki(){
    if(startupDone)return;
    if(typeof pycmd==='function'||typeof window.cramDemo==='function'){
      // QWebChannel can become ready after DOMContentLoaded. Never discard ready.
      startupWait=setTimeout(()=>startupError('Anki has not returned the deck list yet. Another operation may still be using the collection. You can retry below.'),15000);
      send('ready');
    }else if(startupAttempts++<400){
      startupTimer=setTimeout(connectToAnki,25);
    }else startupError('The connection to Anki did not become ready. No AI request was made.');
  }
  function retryStartup(){
    clearTimeout(startupTimer);clearTimeout(startupWait);startupAttempts=0;startupDone=false;
    root.innerHTML='<div class="boot"><div class="brand-mark">C</div><p>Connecting to Anki…</p></div>';
    connectToAnki();
  }
  function theme(dark){document.documentElement.classList.toggle('cram-dark',dark);S.dark=dark;applyAppearance();}
  function applyAppearance(){const card=root.querySelector('.session'),q=current();if(card&&q)window.cramAppearance?.apply(card,S.appearance,'main',q.kind==='io'?'io':q.mode==='flash'?'flash':q.mode==='write'?'write':'exam',S.dark);}
  function shell(content,active='study'){
    return `<div class="shell"><header class="site-header"><div class="row">${brand()}<nav class="site-nav"><button class="nav-btn ${active==='study'?'active':''}" data-action="home">Study</button><button class="nav-btn ${active==='history'?'active':''}" data-action="history">History</button></nav></div><div class="row">${button('options','Settings','ghost','settings')}</div></header><main class="workspace">${content}</main></div>`;
  }
  function sessionConfig(){return {decks:[...S.selected],mode:S.mode,limit:Number(S.limit),children:S.children,shuffle:S.order==='shuffle',order:S.order,order_desc:S.orderDesc,filters:{...S.filters},...(S.mode==='write'?{write_ignore_extra:S.ignoreExtra}:{})};}
  function invalidateMatches(){S.matchRequest++;const el=document.getElementById('match-status');if(el){el.textContent='';el.classList.remove('error');}const b=document.getElementById('check-matches');if(b)b.disabled=false;}
  function filterControls(){
    const flags=[['','Any flag'],['any','Flagged'],['0','No flag'],['1','Red'],['2','Orange'],['3','Green'],['4','Blue'],['5','Pink'],['6','Turquoise'],['7','Purple']];
    return `<section class="panel filters"><div class="row spread"><h3>Filter cards</h3><button class="link-btn" data-action="clear-filters">Clear all</button></div><label class="label search-label" for="anki-search">Anki search · accepts every search supported by your Anki version</label><input id="anki-search" class="filter-input" type="search" placeholder="Any Anki search · is:due, prop:lapses&gt;2, rated:1…" aria-label="Anki card search" value="${esc(S.filters.search)}"><div class="filter-pills">${[['','All'],['is:due','Due'],['is:new','New'],['is:learn','Learning'],['is:review','Review'],['is:due -rated:1','Due · not answered today'],['is:due prop:due=0','Due today only'],['rated:1','Answered today'],['is:suspended','Suspended'],['tag:leech','Leeches']].map(([query,label])=>`<button class="filter-pill ${S.filters.search===query?'active':''}" data-query="${query}">${label}</button>`).join('')}</div><div class="refine"><label class="wide"><span class="label">Tag</span><input id="filter-tag" placeholder="Any tag" value="${esc(S.filters.tag)}"></label><label><span class="label">Note type</span><select id="filter-note" class="filter-select"><option value="">Any note type</option>${(S.cat.note_types||[]).map(name=>`<option value="${esc(name)}" ${S.filters.note_type===name?'selected':''}>${esc(name)}</option>`).join('')}</select></label><label><span class="label">Flag</span><select id="filter-flag" class="filter-select">${flags.map(([value,label])=>`<option value="${value}" ${S.filters.flag===value?'selected':''}>${label}</option>`).join('')}</select></label></div><details class="filter-help"><summary>Search help</summary><div>Blank search = all cards in the selected decks, including cards temporarily in a filtered deck from their selected home deck. The buttons are shortcuts; you can type any Anki query. Filters combine with AND. <code>is:due -rated:1</code> = due and not answered today. <code>rated:1</code> = answered today.<br>Due uses Anki search results, including overdue cards; daily review limits are not applied.</div></details><div class="search-tools"><span id="match-status" class="match-status" aria-live="polite"></span><button id="check-matches" class="link-btn" data-action="check-matches">Check matches</button></div></section>`;
  }
  function repeatControl(id){return `<div class="repeat-option"><div><strong>Repeat missed questions</strong><p>Bring mistakes back later in the same session until correct. Off lets you finish with mistakes.${S.screen==='session'?'<br>Changes apply to your next session.':''}</p></div><label class="switch" title="Repeat missed questions"><input id="${id}" type="checkbox" aria-label="Repeat missed questions" ${S.repeat?'checked':''}><span></span></label></div>`;}
  function options(){
    document.getElementById('options-modal')?.remove();const overlay=document.createElement('div');overlay.className='modal-shade';overlay.id='options-modal';
    overlay.innerHTML=`<section class="panel modal-box" role="dialog" aria-modal="true" aria-label="Study settings"><div class="row spread modal-title"><h2>Settings</h2>${ib('close-options','Close settings','x')}</div>${S.screen==='session'?`<div class="option-row"><span>Restart this practice</span>${button('restart-practice','Start over','secondary','refresh')}</div>`:''}${repeatControl('repeat-options')}${advanceControl()}<div class="option-row"><span>Card text size</span><div class="row">${ib('text-smaller','Smaller card text','minus')}<span class="text-zoom-value">${Math.round(S.textZoom*100)}%</span>${ib('text-larger','Larger card text','plus')}${button('text-reset','Reset','ghost')}</div></div><div class="option-row"><span>Shortcuts</span>${button('shortcuts','Show keys','secondary')}</div><div class="option-row"><span>Customize Cram</span>${button('customize','Open','secondary','settings')}</div><div class="option-row"><span>Appearance</span>${button('theme',S.dark?'Use light mode':'Use dark mode','secondary','sun')}</div>${S.screen!=='session'?`<div class="option-row"><span>Answer / clue fields</span>${button('mapping','Field mapping','secondary','edit')}</div><div class="option-row"><div>AI choices<div class="muted" style="font-size:11px">${S.cat.settings.has_key?esc(S.cat.settings.provider_name||'AI')+' key added':'No AI key added'}</div></div>${button('settings','AI settings','secondary','settings')}</div>`:''}<div class="option-row"><span class="muted" style="font-size:11px">MAIN CRAM 2.0.26<br>Practice does not change your Anki schedule.</span>${button('close-options','Done','primary')}</div></section>`;
    root.appendChild(overlay);overlay.querySelector('button').focus();
  }
  function advanceControl(){return `<div class="repeat-option"><div><strong>Automatically continue</strong><p>Continue after correct answers or Got it. Missed answers wait for Continue.</p></div><label class="switch"><input id="auto-advance" type="checkbox" aria-label="Automatically continue" ${S.autoAdvance?'checked':''}><span></span></label></div><label class="option-row"><span>Answer feedback</span><select id="feedback-delay">${[[600,'Brief · 0.6 seconds'],[1000,'Normal · 1 second'],[2000,'Longer · 2 seconds'],[4000,'Read feedback · 4 seconds']].map(([v,l])=>`<option value="${v}" ${S.feedbackMs===v?'selected':''}>${l}</option>`).join('')}</select></label>`;}
  function cancelAdvance(){clearTimeout(S.autoTimer);S.autoTimer=null;}
  function scheduleAdvance(){
    cancelAdvance();if(!S.autoAdvance||S.screen!=='session'||S.fullscreen||S.customizing||document.getElementById('options-modal')||document.getElementById('leave-modal')||document.getElementById('keys-modal')||document.getElementById('restart-modal'))return;
    const index=S.index,result=S.results[index];if(!result||result.earned<result.total)return;
    S.autoTimer=setTimeout(()=>{S.autoTimer=null;if(S.screen==='session'&&S.index===index&&S.results[index])click('next');},current().mode==='flash'?180:S.feedbackMs);
  }
  function shortcuts(){
    cancelAdvance();document.getElementById('keys-modal')?.remove();const el=document.createElement('div');el.className='modal-shade';el.id='keys-modal';el.innerHTML=`<section class="panel modal-box" role="dialog" aria-modal="true" aria-label="Keyboard shortcuts"><div class="row spread"><h2>Keyboard shortcuts</h2>${ib('close-keys','Close shortcuts','x')}</div><table class="keys-table"><tr><th>Flashcards</th><th>Key</th></tr><tr><td>Flip card</td><td>Space / Up / Down</td></tr><tr><td>Previous / next answered card</td><td>Left / Right</td></tr><tr><td>Still learning / Got it (after reveal)</td><td>1 / 2</td></tr><tr><th>Learn</th><th>Key</th></tr><tr><td>Choose A / B / C / D</td><td>1 / 2 / 3 / 4 or A / B / C / D</td></tr><tr><td>Check / continue</td><td>Space / Enter</td></tr><tr><td>Previous / next blank</td><td>Up / Down</td></tr><tr><td>Pick a blank to change</td><td>Click the blank or its choices</td></tr><tr><th>Writing</th><th>Key</th></tr><tr><td>Check typed items</td><td>Enter</td></tr><tr><td>New line in the answer box</td><td>Shift + Enter</td></tr><tr><td>Previous / next remaining blank</td><td>Up / Down</td></tr><tr><td>Leave the answer box</td><td>Esc</td></tr><tr><td>Reveal remaining (outside the box)</td><td>Space</td></tr><tr><th>Every mode</th><th>Key</th></tr><tr><td>Show this guide</td><td>?</td></tr><tr><td>Close dialog / image viewer</td><td>Esc</td></tr><tr><td>Resize card text only</td><td>Ctrl + wheel over card</td></tr><tr><td>Reset card text</td><td>Ctrl + 0 over card</td></tr></table><p class="microcopy">Quizlet-style Space to flip and arrows to navigate, with practice-specific choice and grading keys. Unanswered cards require a rating before advancing.</p>${button('close-keys','Done','primary')}</section>`;root.appendChild(el);el.querySelector('button').focus();
  }
  const textFontBases=new WeakMap();
  function zoomContent(root,size){
    if(typeof getComputedStyle!=='function'){root.style.fontSize=Math.round(size*S.textZoom)+'px';return;}
    const nodes=[root,...root.querySelectorAll('*')].filter(el=>!el.closest('script,style,svg,math,canvas')&&el.textContent.trim());
    // Restore the original rich text before reading any new element's metrics.
    nodes.forEach(el=>{
      const base=textFontBases.get(el);if(!base)return;
      if(base.font)el.style.setProperty('font-size',base.font,base.fontPriority);else el.style.removeProperty('font-size');
      if(base.lineStyle)el.style.setProperty('line-height',base.lineStyle,base.linePriority);else el.style.removeProperty('line-height');
    });
    root.style.fontSize=size+'px';
    nodes.forEach(el=>{
      if(textFontBases.has(el))return;
      const computed=getComputedStyle(el);
      textFontBases.set(el,{size:parseFloat(computed.fontSize)||size,line:parseFloat(computed.lineHeight),
        font:el.style.getPropertyValue('font-size'),fontPriority:el.style.getPropertyPriority('font-size'),
        lineStyle:el.style.getPropertyValue('line-height'),linePriority:el.style.getPropertyPriority('line-height')});
    });
    if(S.textZoom===1)return;
    // Include highlight wrappers with no direct text, and avoid nested scaling.
    nodes.forEach(el=>{
      const base=textFontBases.get(el);
      el.style.setProperty('font-size',Math.round(base.size*S.textZoom*100)/100+'px','important');
      if(Number.isFinite(base.line))el.style.setProperty('line-height',base.line*S.textZoom+'px','important');
    });
  }
  function setTextZoom(value){
    S.textZoom=Math.max(.6,Math.min(2.5,Math.round(value*100)/100));
    document.querySelectorAll('.flash-face .face-content').forEach(el=>zoomContent(el,el.closest('.long')?22:29));
    document.querySelectorAll('.exam-card .question-panel>.clue,.waiting-card>.clue').forEach(el=>zoomContent(el,21));
    // Choices have an independent readable size in Customize Cram.
    document.querySelectorAll('.text-zoom-value').forEach(el=>el.textContent=Math.round(S.textZoom*100)+'%');
    clearTimeout(S.zoomSave);S.zoomSave=setTimeout(()=>send('preferences',{text_zoom:S.textZoom}),350);
  }
  function scopeCount(){
    const names=S.cat.decks.filter(d=>S.selected.has(d.id)).map(d=>d.name),decks=S.cat.decks.filter(d=>names.includes(d.name)||(S.children&&names.some(n=>d.name.startsWith(n+'::')))),ids=new Set(decks.map(d=>d.id));
    return S.cat.scope_groups?S.cat.scope_groups.reduce((sum,g)=>sum+(ids.has(g.did)||ids.has(g.home)?g.count:0),0):decks.reduce((sum,d)=>sum+d.count,0);
  }
  function renderDecks(){
    const list=document.getElementById('deck-list');if(!list)return;
    const search=S.search.toLocaleLowerCase(),all=[...S.cat.decks].sort((a,b)=>{const x=a.name.split('::'),y=b.name.split('::');for(let i=0;i<Math.min(x.length,y.length);i++){const d=x[i].localeCompare(y[i]);if(d)return d;}return x.length-y.length;});
    const decks=all.filter(d=>d.name.toLocaleLowerCase().includes(search)).filter(d=>search||!d.name.split('::').slice(0,-1).some((_,i)=>S.collapsed.has(d.name.split('::').slice(0,i+1).join('::'))));
    const standalone=new Set(all.filter(d=>d.filtered&&!d.name.includes('::')).map(d=>d.id));
    const row=d=>{
      const parts=d.name.split('::'),name=parts.at(-1),branch=all.some(child=>child.name.startsWith(d.name+'::')),count=S.children?(d.total_count??d.count):d.count;
      return `<div class="deck-row ${parts.length===1?'deck-root ':''}${S.selected.has(d.id)?'selected':''}" style="padding-left:${12+(parts.length-1)*24}px">${branch?`<button class="tree-toggle" data-branch="${esc(d.name)}" aria-expanded="${!S.collapsed.has(d.name)}" aria-label="${S.collapsed.has(d.name)?'Expand':'Collapse'} ${esc(name)}"><svg class="tree-chevron ${S.collapsed.has(d.name)?'closed':''}" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 4.5 3 3 3-3"/></svg></button>`:'<span class="tree-spacer"></span>'}<label class="deck-select"><input type="checkbox" data-deck="${esc(d.id)}" ${S.selected.has(d.id)?'checked':''}><span class="deck-icon">${icon('book')}</span><span class="grow"><span class="deck-name">${esc(name)}</span>${search&&parts.length>1?`<div class="deck-path">${esc(parts.slice(0,-1).join(' / '))}</div>`:''}</span>${d.filtered?'<span class="deck-type">Filtered</span>':''}<span class="deck-count" title="${count.toLocaleString()} cards" aria-label="${count.toLocaleString()} cards">${count.toLocaleString()}</span></label></div>`;
    };
    const families=new Map();for(const d of decks.filter(d=>!standalone.has(d.id))){const name=d.name.split('::')[0];if(!families.has(name))families.set(name,[]);families.get(name).push(d);}
    const normal=[...families].map(([name,items])=>`<section class="deck-family" data-family="${esc(name)}">${items.map(row).join('')}</section>`).join('');
    const filtered=decks.filter(d=>standalone.has(d.id));
    list.innerHTML=decks.length?normal+(filtered.length?`<section class="filtered-family"><div class="deck-section-title"><span>Filtered decks</span><span>${filtered.length}</span></div><div class="filtered-list">${filtered.map(row).join('')}</div></section>`:''):'<div class="empty">No decks match your search.</div>';
    updateCount();
  }
  function savedLabel(item){const full=[...new Set(item.decks||[])],names=[...new Set(full.map(name=>name.split('::').at(-1)))].slice(0,2),extra=full.length-names.length;return names.join(' · ')+(extra>0?' +'+extra:'');}
  function renderSaved(){
    const host=document.getElementById('saved-list');if(!host)return;
    const all=S.cat.saved_sessions||[],query=S.savedSearch.trim().toLocaleLowerCase(),filtered=all.filter(item=>(item.decks||[]).join(' ').toLocaleLowerCase().includes(query));
    const shown=S.savedExpanded||query?filtered:filtered.slice(0,2),modeNames={flash:'Flashcards',exam:'Learn',mixed:'Mixed',write:'Writing'},modeIcons={flash:'cards',exam:'bolt',mixed:'mix',write:'edit'};
    host.innerHTML=shown.length?shown.map(item=>{
      const total=Math.max(0,Number(item.total)||0),answered=Math.max(0,Number(item.answered)||0),progress=total?Math.min(100,answered/total*100):0,label=savedLabel(item),same=all.filter(other=>savedLabel(other)===label),parents=[...new Set(item.decks.map(name=>name.split('::').slice(-2,-1)[0]).filter(Boolean))];
      const context=same.length>1&&new Set(same.flatMap(other=>other.decks.map(name=>name.split('::').slice(-2,-1)[0]))).size>1?parents.join(' · '):'';
      return `<article class="saved-row"><div class="saved-heading"><span class="saved-mode">${icon(modeIcons[item.config.mode]||'cards')}</span><div class="grow"><strong title="${esc(item.decks.join(' / '))}">${esc(label||'Practice')}</strong>${context?`<span class="saved-context">${esc(context)}</span>`:''}<small>${esc(modeNames[item.config.mode]||'Practice')} · ${answered} / ${total} answered</small></div></div><div class="saved-track" role="progressbar" aria-label="Answered questions" aria-valuenow="${Math.min(answered,total)}" aria-valuemax="${total}" aria-valuemin="0"><span style="width:${progress}%"></span></div>${item.error?'<div class="saved-warning">Saved position needs attention</div>':''}<div class="saved-actions"><button class="btn primary" data-resume="${esc(item.id)}">Resume</button><button class="link-btn" data-reset-progress="${esc(item.id)}">Reset</button></div></article>`;
    }).join(''):'<div class="saved-empty">No saved practice matches.</div>';
    const more=document.getElementById('saved-more');if(more)more.textContent=S.savedExpanded?'Show less':`View all (${all.length})`;
    const search=document.getElementById('saved-search-wrap');if(search)search.hidden=!S.savedExpanded;
  }
  function updateCount(){const count=document.getElementById('selection-count');if(count)count.textContent=`${S.selected.size} selected · ${scopeCount().toLocaleString()} cards before filters`;for(const id of ['start','regen-decks']){const b=document.getElementById(id);if(b)b.disabled=!S.selected.size||!scopeCount();}}
  let orderActive='',orderTyped='',orderTypeTimer=null;
  const orderItems=()=>Array.from(document.querySelectorAll('#order option')).map(el=>({value:el.value,label:el.textContent,disabled:el.disabled,group:el.parentElement.tagName==='OPTGROUP'?el.parentElement.getAttribute('label'):''}));
  function syncOrder(){
    const value=document.getElementById('order-value'),item=orderItems().find(el=>el.value===S.order);
    if(value)value.textContent=item?.label||'Choose order';
    const direction=document.getElementById('order-direction');if(direction)direction.hidden=!S.order.startsWith('anki:');
  }
  function closeOrder(focus=false){
    document.getElementById('order-menu')?.remove();const trigger=document.getElementById('order-trigger');
    trigger?.setAttribute('aria-expanded','false');trigger?.removeAttribute('aria-activedescendant');
    clearTimeout(orderTypeTimer);orderTyped='';if(focus)trigger?.focus();
  }
  function activateOrder(value){
    orderActive=value;
    document.querySelectorAll('#order-menu [data-order-value]').forEach(el=>{
      const active=el.dataset.orderValue===value;el.classList.toggle('active',active);
      if(active){document.getElementById('order-trigger')?.setAttribute('aria-activedescendant',el.id);el.scrollIntoView?.({block:'nearest'});}
    });
  }
  function openOrder(){
    const trigger=document.getElementById('order-trigger');if(!trigger)return;
    closeOrder();const items=orderItems(),menu=document.createElement('div');menu.id='order-menu';menu.className='order-menu';menu.setAttribute('role','listbox');menu.setAttribute('aria-labelledby','order-label');
    let group='';menu.innerHTML=items.map((item,index)=>{
      const heading=item.group&&item.group!==group?`<div class="order-group" role="presentation">${esc(item.group)}</div>`:'';group=item.group;
      return heading+`<div id="order-item-${index}" class="order-option ${item.value===S.order?'selected':''}" role="option" aria-selected="${item.value===S.order}" aria-disabled="${item.disabled}" data-order-value="${esc(item.value)}"><span>${esc(item.label)}</span><span class="order-check" aria-hidden="true">${item.value===S.order?'✓':''}</span></div>`;
    }).join('');root.appendChild(menu);
    const r=trigger.getBoundingClientRect(),w=window.innerWidth||1360,h=window.innerHeight||900,below=h-r.bottom-12,above=r.top-12,up=below<180&&above>below;
    const height=Math.max(60,Math.min(360,(up?above:below)-8)),width=Math.min(Math.max(260,r.width),w-24);
    menu.style.width=width+'px';menu.style.maxHeight=height+'px';menu.style.left=Math.max(12,Math.min(w-width-12,r.left))+'px';
    if(up)menu.style.bottom=Math.max(12,h-r.top+6)+'px';else menu.style.top=Math.max(12,r.bottom+6)+'px';
    trigger.setAttribute('aria-expanded','true');trigger.focus();activateOrder(items.find(item=>item.value===S.order&&!item.disabled)?.value||items.find(item=>!item.disabled)?.value||'');
  }
  function chooseOrder(value,focus=true){
    const item=orderItems().find(el=>el.value===value&&!el.disabled);if(!item)return;
    S.order=value;S.shuffle=value==='shuffle';const select=document.getElementById('order');if(select)select.value=value;syncOrder();closeOrder(focus);
  }
  function orderKeys(e){
    const open=!!document.getElementById('order-menu'),control=e.target.closest?.('#order-trigger,#order-menu');
    if(!control&&!(open&&e.key==='Escape')||e.ctrlKey||e.metaKey)return false;
    if(e.key==='Tab'){if(open)chooseOrder(orderActive,false);return false;}
    if(e.key==='Escape'){if(!open)return false;e.preventDefault();e.stopPropagation();closeOrder(true);return true;}
    if(e.altKey&&!['ArrowDown','ArrowUp'].includes(e.key))return false;
    const printable=e.key.length===1&&e.key!==' ',navigation=['ArrowDown','ArrowUp','Home','End','PageDown','PageUp'].includes(e.key);
    if(!printable&&!navigation&&!['Enter',' '].includes(e.key))return false;
    e.preventDefault();e.stopPropagation();
    if(e.repeat&&['Enter',' '].includes(e.key))return true;
    if(open&&(['Enter',' '].includes(e.key)||e.altKey&&e.key==='ArrowUp')){chooseOrder(orderActive);return true;}
    if(!open)openOrder();const items=orderItems().filter(item=>!item.disabled);if(!items.length)return true;
    let index=Math.max(0,items.findIndex(item=>item.value===orderActive));
    if(printable){
      clearTimeout(orderTypeTimer);orderTyped+=e.key.toLowerCase();orderTypeTimer=setTimeout(()=>{orderTyped='';},700);
      const prefix=[...orderTyped].every(char=>char===orderTyped[0])?orderTyped[0]:orderTyped;
      const candidates=prefix.length===1?[...items.slice(index+1),...items.slice(0,index+1)]:items;
      const match=candidates.find(item=>item.label.toLowerCase().startsWith(prefix));if(match)activateOrder(match.value);
    }else if(e.key==='Home')activateOrder(items[0].value);
    else if(e.key==='End')activateOrder(items.at(-1).value);
    else if(open&&navigation&&!e.altKey){index=Math.max(0,Math.min(items.length-1,index+(['ArrowUp','PageUp'].includes(e.key)?-1:1)*(e.key.startsWith('Page')?10:1)));activateOrder(items[index].value);}
    return true;
  }
  function home(){
    cancelAdvance();S.screen='home';S.sessionId=null;S.error='';S.busy=false;S.generating=false;S.fullscreen=false;
    const modes=[['flash','cards','Flashcards','Reveal & recall'],['exam','bolt','Learn','Multiple choice'],['mixed','mix','Mixed','Both styles'],['write','edit','Writing','Type & recall']];
    root.innerHTML=shell(`<header class="page-title"><div class="breadcrumb">Your Anki decks</div><h1>Choose a study set</h1><p>Select decks, filter your cards, then start practicing.</p></header><div class="home-grid"><div class="stack home-library"><section class="panel library-panel"><div class="panel-head row spread"><h3>Decks & subjects</h3><div class="row"><button class="link-btn" data-action="refresh-decks">Refresh</button><button class="link-btn" data-action="clear-decks">Clear</button></div></div><div class="search">${icon('search')}<input id="deck-search" type="search" placeholder="Find a deck or lesson" aria-label="Search decks" value="${esc(S.search)}"></div><div class="deck-list" id="deck-list"></div><div class="panel-bottom row spread wrap"><span id="selection-count"></span><label class="check"><input id="children" type="checkbox" ${S.children?'checked':''}> Include subdecks</label></div></section>${filterControls()}</div><section class="panel practice-panel"><div class="panel-head"><h3>Practice options</h3></div><div class="panel-body"><div class="study-modes">${modes.map(([id,ic,title,desc])=>`<button class="mode ${S.mode===id?'selected':''}" data-mode="${id}" aria-pressed="${S.mode===id}">${icon(ic)}<strong>${title}</strong><small>${desc}</small></button>`).join('')}</div><div class="controls"><label class="control"><span class="label">Practice questions</span><select id="limit">${[['10','10'],['20','20'],['30','30'],['50','50'],['100','100'],['0','All questions']].map(([v,l])=>`<option value="${v}" ${S.limit===v?'selected':''}>${l}</option>`).join('')}</select></label><div class="control order-control"><span id="order-label" class="label">Question order</span><button type="button" id="order-trigger" class="order-trigger" role="combobox" aria-labelledby="order-label order-value" aria-haspopup="listbox" aria-controls="order-menu" aria-expanded="false"><span id="order-value"></span><span class="order-chevron" aria-hidden="true"></span></button><select id="order" hidden aria-hidden="true" tabindex="-1">${[['shuffle','Random cards'],['random_notes','Random note, then card type'],['card_type','Card type, then order gathered'],['card_type_random','Card type, then random'],['deck_random_notes','Deck, then random notes'],['created_asc','Created · oldest first'],['created_desc','Created · newest first'],['due_random','Due date, then random'],['due_deck','Due date, then deck'],['deck_due','Deck, then due date'],['retrievability_asc','Retrievability · low to high'],['retrievability_desc','Retrievability · high to low']].map(([v,l])=>`<option value="${v}" ${S.order===v?'selected':''} ${v.startsWith('retrievability')&&S.cat.retrievability_order===false?'disabled':''}>${l}</option>`).join('')}${S.cat.sort_columns?.length?`<optgroup label="Anki card columns">${S.cat.sort_columns.map(c=>`<option value="anki:${esc(c.key)}" ${S.order==='anki:'+c.key?'selected':''}>${esc(c.label)}</option>`).join('')}</optgroup>`:''}</select></div></div><label id="order-direction" class="check order-direction" ${S.order.startsWith('anki:')?'':'hidden'}><input id="order-desc" type="checkbox" ${S.orderDesc?'checked':''}> Descending (Anki column orders)</label><button class="link-btn" data-action="mapping">Choose answer / clue fields</button><label class="check writing-extra" ${S.mode==='write'?'':'hidden'}><input id="write-ignore-extra" type="checkbox" ${S.ignoreExtra?'checked':''}> Ignore extra text</label>${repeatControl('repeat-home')}<button id="start" class="btn primary start-btn" data-action="start">Start studying</button><button id="regen-decks" class="btn secondary start-btn" data-action="regen-decks">Regenerate deck choices</button><p class="microcopy">Flashcards and image recall work offline. Learn reuses saved choices. Writing can prepare text answer groups with your selected AI provider and save them for offline use.</p></div></section></div><div class="home-caption">MAIN CRAM · Practice only, including filtered decks. For Anki’s queue and ratings, open Tools → ANKI CRAM.</div><div id="home-error"></div>`);
    root.querySelector('.workspace').classList.add('home-page');
    const saved=S.cat.saved_sessions||[];
    if(saved.length<=2){S.savedSearch='';S.savedExpanded=false;}
    if(saved.length){
      const panel=document.createElement('section');panel.className='panel saved-practice';panel.id='saved-practice';
      panel.innerHTML=`<div class="panel-head row spread"><h3>Resume practice <span class="saved-count">${saved.length}</span></h3>${saved.length>2?'<button class="link-btn" id="saved-more" data-action="saved-more">View all</button>':''}</div>${saved.length>2?`<div class="search saved-search" id="saved-search-wrap" ${S.savedExpanded?'':'hidden'}>${icon('search')}<input id="saved-search" type="search" placeholder="Find saved practice" aria-label="Search saved practice" value="${esc(S.savedSearch)}"></div>`:''}<div class="saved-list" id="saved-list"></div>`;
      root.querySelector('.workspace').insertBefore(panel,root.querySelector('.home-grid'));renderSaved();
    }
    renderDecks();syncOrder();
  }
  function history(){S.screen='history';root.innerHTML=shell(`<header class="page-title"><h1>Practice history</h1><p>These results belong to MAIN CRAM. Anki’s review history stays unchanged.</p></header><section class="panel">${S.history.length?S.history.map(h=>`<div class="history-row"><div class="history-score">${Math.round(h.earned/h.total*100)}%</div><div class="grow"><strong>${esc(h.decks.map(d=>d.split('::').pop()).slice(0,3).join(', '))}</strong><div class="muted" style="font-size:12px">${esc(h.date)} · ${h.questions} questions · ${h.earned}/${h.total} points</div></div><span class="badge">${duration(h.seconds)}</span></div>`).join(''):`<div class="empty">${icon('history')}No completed sessions yet.<br>Your practice results will appear here.</div>`}</section><div style="margin-top:20px">${button('home','Start practicing','primary','arrow')}</div>`,'history');}
  function duration(seconds){const min=Math.floor(seconds/60);return min?`${min}m ${seconds%60}s`:`${seconds}s`;}
  function preparation(){
    S.screen='prepare';const p=S.prep;
    root.innerHTML=shell(`<section class="panel prepare"><h2>Prepare multiple-choice answers</h2><p>${esc(S.cat?.settings?.provider_name||'Your selected AI provider')} creates three matching wrong choices for each answer. Your original correct answers stay locked.</p><div class="prepare-stats"><div><strong>${p.questions}</strong><small>questions</small></div><div><strong>${p.cached}</strong><small>cached blanks</small></div><div><strong>${p.missing}</strong><small>new choice sets</small></div></div><div class="notice">Only this set’s text clues and answers are sent to ${esc(S.cat?.settings?.provider_name||'your selected AI provider')} when you click Generate. Images stay in Anki. Choices are saved locally for offline reuse. Review AI choices for accuracy.<br><br>Model: <strong>${esc(p.model)}</strong>${p.skipped?`<br>${p.skipped} unsupported or empty cards skipped.`:''}</div><div id="gen-status">${S.error?`<div class="notice error" role="alert">${esc(S.error)}</div>`:''}</div><div id="gen-actions" class="stack" style="gap:8px">${p.has_key?button('generate',S.error?'Retry generation':'Generate choices','primary'):button('settings','Set up AI','primary','settings')}${button('flash','Use flashcards instead','secondary','cards')}${button('home','Back to decks','ghost')}</div><p class="microcopy">No automatic billing. Your project’s API quota applies.</p></section>`);
  }
  function loading(message){S.screen='loading';root.innerHTML=shell(`<div class="panel prepare"><div class="spinner"></div><h2>${esc(message)}</h2><p>Reading your selected decks. Anki scheduling stays untouched.</p></div>`);}
  function current(){return S.questions[S.index];}
  function answerSeen(q=current()){return S.revealed.has(S.index)||(q?.kind==='io'&&S.ioMasks[S.index]?.seen)||(q?.mode==='flash'&&q.kind!=='io'&&S.flashSeen.has(S.index));}
  function getPicks(){return S.picks[S.index]||(S.picks[S.index]=Array(current().slots.length).fill(null));}
  function zoomTools(){return `<div class="io-tools">${button('reveal',S.revealed.has(S.index)?'Show masks':'Hide masks','secondary')}${ib('zoom-out','Zoom out','minus')}<span class="zoom-value">${Math.round(S.zoom*100)}%</span>${ib('zoom-in','Zoom in','plus')}${ib('zoom-reset','Fit image','refresh')}${ib('fullscreen','Open full-screen image viewer','expand')}</div>`;}
  function progressDots(){return S.questions.length<=100?`<nav class="q-nav" aria-label="Question progress">${S.questions.map((_,i)=>`<button class="q-dot ${i===S.index?'current':''} ${S.results[i]?(S.results[i].earned===S.results[i].total?'correct':'incorrect'):''}" data-question="${i}" title="Question ${i+1}" aria-label="Question ${i+1}" ${i>Object.keys(S.results).length?'disabled':''}></button>`).join('')}</nav>`:'';}
  function footer(q){
    const result=S.results[S.index],reveal=S.revealed.has(S.index);
    if(q.mode==='write'){
      if(q.ready===false)return '<span class="muted">Preparing answer groups…</span>';
      if(result)return `<div class="feedback ${result.earned===result.total?'right':'wrong'}">${result.earned} / ${result.total} correct</div>${button('next',S.index===S.questions.length-1?'See results':'Continue','primary','arrow')}`;
      return `${button('write-reveal','Reveal answer','secondary','',S.pending?'disabled':'')}`;
    }
    if(q.mode==='exam'&&q.ready===false)return `<span class="muted">Choices are being prepared.</span>${button('flash','Use this as a flashcard','secondary')}`;
    const flip=q.kind==='io'?'':button('reveal',reveal?'Show clue':'Reveal answer','secondary');
    if(result){
      const good=result.earned===result.total;
      const feedback=`<div class="feedback ${good?'right':'wrong'}">${icon(good?'check':'x')}<div>${good?'Correct':q.mode==='exam'?`${result.earned} / ${result.total} correct`:'Still learning'}${S.repeatActive&&!good?'<small>This question will return later.</small>':''}</div></div>`;
      return q.mode==='flash'?`${feedback}<div class="flash-nav">${flip}</div>${button('next',S.index===S.questions.length-1?'Results':'Continue','primary','arrow')}`:`${feedback}${button('next',S.index===S.questions.length-1?'See results':'Continue','primary','arrow')}`;
    }
    if(q.mode==='exam')return `<button class="link-btn" data-action="dont-know" ${S.pending?'disabled':''}>Don’t know?</button>${button('submit',S.pending?'Checking…':'Check answer','primary','',S.pending||getPicks().some(v=>v===null)?'disabled':'')}`;
    return `${button('unknown','Still learning','bad','',!answerSeen(q)?'disabled':'')}<div class="flash-nav">${flip}</div>${button('known','Got it','good','',!answerSeen(q)?'disabled':'')}`;
  }
  function question(restore={}){
    cancelAdvance();closeViewer();S.screen='session';S.pending=false;S.zoom=restore.zoom||1;S.activeSlot=restore.activeSlot||0;
    const q=current(),result=S.results[S.index],revealed=S.revealed.has(S.index),picks=getPicks(),flash=q.mode==='flash'&&q.kind!=='io';
    const modeName=S.mode==='mixed'?'Mixed practice':q.mode==='write'?'Writing':q.mode==='exam'?'Learn':'Flashcards';
    const header=`<header class="session-header"><div class="study-mode">${ib('previous','Previous question','back',S.index===0?'disabled':'')}${icon(q.mode==='exam'?'bolt':'cards')}<span class="main-mode-label"><strong>MAIN CRAM</strong><small>${modeName}</small><small>Practice only · Schedule unchanged</small></span></div><div class="session-progress"><strong id="question-count">${S.index+1} / ${S.questions.length}</strong><div class="session-deck">${esc(q.deck.split('::').at(-1))}</div></div><div class="header-actions">${button('options','Settings','ghost','settings')}${ib('leave','Pause practice','x')}</div></header>`;
    let body='';
    if(flash){
      const back=q.kind==='cloze'?q.clue:q.slots.map(slot=>`<div class="answer-item">${q.slots.length>1?`<span class="answer-number">${slot.number}</span>`:''}<div class="answer-value">${slot.answer_html}</div></div>`).join('');
      body=`<section class="panel study-card flash-card ${revealed?'is-flipped':''}" data-flip="yes" tabindex="0" role="button" aria-label="Flip flashcard"><div class="card-heading"><span id="face-label">${revealed?'Answer':'Clue'}</span><span class="text-zoom-value">${Math.round(S.textZoom*100)}%</span>${q.is_retry?'<span class="badge">Try again</span>':''}</div><div class="flash-turn"><div id="clue-face" class="flash-face ${text(q.clue).length>150?'long':''}" aria-hidden="${revealed}"><div class="face-content clue">${q.clue}</div></div><div id="answer" class="flash-face flash-back answer ${q.kind==='cloze'&&text(back).length>150?'long':''}" aria-hidden="${!revealed}"><div class="face-content clue">${back}</div></div></div></section><div id="card-footer" class="flash-controls">${footer(q)}</div>`;
    }else if(q.kind==='io'){
      body=`<section class="panel study-card io-card"><div class="card-heading"><span class="question-label">Image recall${q.is_retry?' · Try again':''}</span>${zoomTools()}</div>${q.clue?`<div class="clue io-caption">${q.clue}</div>`:''}<div id="preview-viewport" class="io-viewport"><div id="io-stage" class="io-stage">${q.picture}</div></div>${q.extra?`<div id="io-extra" class="io-extra ${revealed?'':'concealed'}" aria-hidden="${!revealed}">${q.extra}</div>`:''}</section><div id="card-footer" class="flash-controls">${footer(q)}</div>`;
    }else if(q.mode==='write'&&q.ready!==false){
      body=`<section class="panel study-card exam-card write-card"><div class="card-heading"><span class="question-label">Writing</span></div><div class="question-panel"><div class="clue write-clue">${window.cramWriting.question(q)}</div></div><div class="choice-section write-response-host"></div><div id="card-footer" class="card-footer">${footer(q)}</div></section>`;
    }else if(q.ready===false){
      body=`<section class="panel study-card waiting-card"><div class="question-label">${q.mode==='write'?'Preparing answer groups':'Preparing this question'}</div><div class="clue">${q.clue}</div><div id="waiting-message"><div class="spinner"></div><p>${S.error?esc(S.error):(q.mode==='write'?'Preparing the original answer items.':'Creating choices for this question first. Upcoming choices prepare in the background.')}</p></div><div class="row wait-actions">${q.mode==='write'?button('write-whole','Use full answer','primary'):button('generate','Retry / resume','secondary')+button('flash','Use this as a flashcard','primary')}</div></section>`;
    }else{
      body=`<section class="panel study-card exam-card"><div class="card-heading"><span class="question-label">${q.kind==='cloze'?'Complete the blanks':'Clue'}</span>${q.is_retry?'<span class="badge">Try again</span>':''}</div><div class="question-panel"><div class="clue">${q.clue}</div></div><div class="choice-section">${q.slots.map((slot,i)=>`<section class="slot-group"><div class="slot-label">${q.kind==='cloze'?`Blank ${slot.number}${q.slots.length>1?` / ${q.slots.length}`:''}`:'Choose an answer'}</div><div class="choices">${slot.choices.map((option,j)=>`<button class="choice ${picks[i]===j?'selected':''} ${result&&j===slot.correct?'right':''} ${result&&picks[i]===j&&!result.correct[i]?'wrong':''}" data-slot="${i}" data-choice="${j}" ${result?'disabled':''}><span class="choice-key">${result&&j===slot.correct?icon('check'):'ABCD'[j]}</span><span class="grow choice-text">${esc(window.cramAppearance?.choiceText(slot.answer,option)??option)}</span></button>`).join('')}</div></section>`).join('')}</div><div id="card-footer" class="card-footer">${footer(q)}</div></section>`;
    }
    root.innerHTML=`<main class="session">${header}<div class="session-main"><div class="progress-track"><div class="progress-fill" style="width:${Object.keys(S.results).length/S.questions.length*100}%"></div></div>${body}${q.mode==='exam'&&q.ready!==false?`<div class="under-card"><button class="link-btn" data-action="edit" ${result?'disabled':''}>Edit choices</button><button class="link-btn" data-action="regenerate" ${result?'disabled':''}>Regenerate choices</button></div>`:''}<div id="single-generation"></div><div id="background-generation"></div><div id="question-dots">${progressDots()}</div><div id="session-error"></div></div></main>`;
    S.writeUI=null;
    if(q.mode==='write'&&q.ready!==false){
      const view=S.written[S.index]||(S.written[S.index]={events:[],draft:'',target:0});
      if(result?.writing_state)view.state=result.writing_state;
      S.writeUI=window.cramWriting.mount(root.querySelector('.write-response-host'),root.querySelector('.write-clue'),q,view,{
        revealed:!!result||revealed,autofocus:!result&&!revealed,practice:true,
        submit:data=>send('write_submit',{...data,index:S.index}),
        changed:()=>{clearTimeout(S.writeSave);S.writeSave=setTimeout(checkpoint,300);},
        finish:finishWriting
      });
    }
    fillBlanks();if(flash)fillBack();setTextZoom(S.textZoom);applyAppearance();
    generationStatus();
    if(q.kind==='io'){
      setupIOMasks();
      const image=document.querySelector('.io-image>img');if(image){image.onload=fitImage;if(image.complete)fitImage();}
    }
    if(restore.scroll)window.scrollTo(0,restore.scroll);
    checkpoint();
  }
  function fillBack(){
    const q=current();if(q.kind!=='cloze')return;
    document.querySelectorAll('#answer [data-blank]').forEach(el=>{const i=Number(el.dataset.blank);el.innerHTML=q.slots[i]?.answer_html||'';el.classList.add('filled','revealed-answer');});
  }
  function fillBlanks(){
    const q=current();if(!q)return;
    // Existing snapshots keep their original clue/slot IDs. Only the displayed
    // placeholder changes, so the Gemini cache and resume data stay compatible.
    document.querySelectorAll('#clue-face [data-blank],.waiting-card [data-blank]').forEach((el,n)=>{
      const i=Number(el.dataset.blank??n);el.textContent='\u00a0';el.classList.add('cram-blank-empty');el.setAttribute('aria-label',`Blank ${i+1}`);
    });
    if(q.mode!=='exam'||q.ready===false)return;
    S.activeSlot=Math.max(0,Math.min(q.slots.length-1,S.activeSlot));
    document.querySelectorAll('.exam-card .ct-blank').forEach((el,n)=>{
      const i=el.dataset.blank===undefined?n:Number(el.dataset.blank),slot=q.slots[i],pick=getPicks()[i],answer=!!S.results[S.index];if(!slot)return;
      el.setAttribute('data-blank',i);el.dataset.blank=String(i);const empty=!answer&&(pick===null||pick<0);
      if(empty){el.textContent='\u00a0';el.classList.remove('cram-blank-lines');}
      else if(window.cramAppearance?.fillBlank)window.cramAppearance.fillBlank(el,slot,answer?slot.answer:slot.choices[pick]);
      else el.textContent=answer?slot.answer:slot.choices[pick];
      el.classList.toggle('cram-blank-empty',empty);el.setAttribute('aria-label',`Blank ${slot.number}`);el.classList.toggle('filled',!empty);el.classList.toggle('revealed-answer',answer);
      const active=!S.results[S.index]&&i===S.activeSlot;el.classList.toggle('active',active);if(active)el.setAttribute('aria-current','true');else el.removeAttribute('aria-current');
    });
    document.querySelectorAll('.slot-group').forEach((el,i)=>{el.hidden=i!==S.activeSlot;el.classList.toggle('active-slot',i===S.activeSlot);});
  }
  function selectBlank(index,scroll=false){
    const q=current();if(!q||q.mode!=='exam'||q.ready===false||S.busy||S.pending||!Number.isInteger(index)||!q.slots.length)return;
    const next=(index+q.slots.length)%q.slots.length;
    if(next===S.activeSlot){
      if(scroll)window.cramAppearance?.showInPane(document.querySelector(`.question-panel [data-blank="${next}"]`),document.querySelector('.question-panel'));
      return;
    }
    S.activeSlot=next;fillBlanks();
    const answers=document.querySelector('.choice-section');if(answers)answers.scrollTop=0;
    if(scroll)window.cramAppearance?.showInPane(document.querySelector(`.question-panel [data-blank="${S.activeSlot}"]`),document.querySelector('.question-panel'));
    checkpoint();
  }
  function generationStatus(){
    const el=document.getElementById('background-generation');if(!el)return;
    el.innerHTML=S.generating?`<div class="background-status"><span class="tiny-spinner"></span><span>Preparing upcoming ${S.mode==='write'?'answer groups':'choices'} ${S.genProgress?`· ${S.genProgress.done} / ${S.genProgress.total}`:''}</span>${button('cancel','Pause','ghost')}</div>`:S.error?`<div class="background-status error"><span>${esc(S.error)}</span>${button('generate','Resume','ghost')}</div>`:'';
    document.querySelectorAll('[data-action="generate"]').forEach(b=>b.disabled=S.generating);
    document.querySelectorAll('[data-action="regenerate"],[data-action="edit"]').forEach(b=>b.disabled=S.generating||!!S.results[S.index]);
    const wait=document.getElementById('waiting-message');if(wait&&!S.generating&&S.error)wait.innerHTML=`<p class="error">${esc(S.error)}</p>`;
  }
  function updateFooter(){const el=document.getElementById('card-footer');if(el)el.innerHTML=footer(current());}
  function finishWriting(){
    const q=current();if(!q||q.mode!=='write'||q.ready===false||S.results[S.index]||S.pending)return;
    const view=S.writeUI?.view||S.written[S.index]||{},unknown=!view.state?.complete;
    S.pending=true;S.revealed.add(S.index);S.writeUI?.fill(true);updateFooter();
    send('grade',{index:S.index,picks:{writing:view.events||[],unknown}});
  }
  function reveal(){
    const q=current();if(!q||q.mode!=='flash')return;
    if(S.results[S.index])cancelAdvance();
    const yes=!S.revealed.has(S.index);yes?S.revealed.add(S.index):S.revealed.delete(S.index);
    if(yes&&q.kind!=='io')S.flashSeen.add(S.index);
    if(q.kind==='io'){
      const state=S.ioMasks[S.index]||(S.ioMasks[S.index]={open:[],closed:[],seen:false});state.open=[];state.closed=[];if(yes)state.seen=true;setupIOMasks();
      const extra=document.getElementById('io-extra');if(extra){extra.classList.toggle('concealed',!yes);extra.setAttribute('aria-hidden',!yes);}
      const b=document.getElementById('viewer-reveal');if(b)b.innerHTML=icon('eye')+(yes?'Show masks':'Hide masks');
    }else{document.querySelector('.flash-card').classList.toggle('is-flipped',yes);document.getElementById('answer').setAttribute('aria-hidden',!yes);document.getElementById('clue-face').setAttribute('aria-hidden',yes);document.getElementById('face-label').textContent=yes?'Answer':'Clue';}
    updateFooter();
    checkpoint();
  }
  function setupIOMasks(){
    const image=document.querySelector('.io-image');if(!image)return;
    const state=S.ioMasks[S.index]||(S.ioMasks[S.index]={open:[],closed:[],seen:S.revealed.has(S.index)});
    image.classList.toggle('revealed',S.revealed.has(S.index));image.querySelector('svg')?.removeAttribute('aria-hidden');
    const masks=[...image.querySelectorAll('.mask.target')];
    masks.forEach((mask,i)=>{
      mask.dataset.mainMask=String(i);mask.setAttribute('role','button');mask.setAttribute('tabindex','0');
      mask.classList.toggle('io-mask-open',state.open.includes(i));mask.classList.toggle('io-mask-closed',state.closed.includes(i));
      const open=maskOpen(mask);mask.setAttribute('aria-label',`${open?'Hide':'Reveal'} mask ${i+1}`);mask.setAttribute('aria-pressed',String(open));
    });
    if(masks.length&&masks.every(maskOpen))state.seen=true;
    document.querySelectorAll('.io-tools [data-action="reveal"]').forEach(b=>{b.textContent=S.revealed.has(S.index)?'Show masks':'Hide masks';});
  }
  function maskOpen(mask){return !!(S.revealed.has(S.index)?!mask.classList.contains('io-mask-closed'):mask.classList.contains('io-mask-open'));}
  function toggleMask(mask){
    if(current()?.kind!=='io'||S.pending)return;
    const i=Number(mask.dataset.mainMask),state=S.ioMasks[S.index],all=S.revealed.has(S.index),open=maskOpen(mask);
    if(!state||!Number.isInteger(i))return;
    const key=all?'closed':'open',values=new Set(state[key]);values.has(i)?values.delete(i):values.add(i);state[key]=[...values];
    setupIOMasks();updateFooter();checkpoint();
  }
  function fitImage(){
    const image=document.querySelector('.io-image>img');if(!image||!image.naturalWidth)return;
    const viewport=document.getElementById(S.fullscreen?'viewer-viewport':'preview-viewport');if(!viewport)return;
    const width=Math.max(100,Math.min(viewport.clientWidth-30,(viewport.clientHeight-30)*image.naturalWidth/image.naturalHeight));
    image.parentElement.style.width=Math.round(width*S.zoom)+'px';
    document.querySelectorAll('.zoom-value').forEach(e=>e.textContent=Math.round(S.zoom*100)+'%');
  }
  function openViewer(){
    cancelAdvance();
    if(S.fullscreen||!document.getElementById('io-stage'))return;S.fullscreen=true;S.previewZoom=S.zoom;S.zoom=1;
    const overlay=document.createElement('div');overlay.className='overlay';overlay.id='viewer';overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');overlay.setAttribute('aria-label','Image occlusion viewer');
    overlay.innerHTML=`<div class="overlay-header"><h3>MAIN CRAM · Image recall <span class="muted">· ${current().mask_count} target masks</span></h3><div class="row"><div class="io-tools">${ib('zoom-out','Zoom out','minus')}<span class="zoom-value">100%</span>${ib('zoom-in','Zoom in','plus')}${ib('zoom-reset','Fit image','refresh')}</div>${ib('close-viewer','Close full-screen viewer (Esc)','x')}</div></div>${current().clue?`<div class="viewer-caption">${current().clue}</div>`:''}<div id="viewer-viewport" class="io-viewport"></div><div class="overlay-footer"><button class="btn primary" id="viewer-reveal" data-action="reveal">${icon('eye')}${S.revealed.has(S.index)?'Show masks':'Hide masks'}</button><span class="muted" style="font-size:12px">Esc to close</span></div>`;
    root.appendChild(overlay);document.getElementById('viewer-viewport').appendChild(document.getElementById('io-stage'));fitImage();overlay.querySelector('[data-action="close-viewer"]').focus();
  }
  function closeViewer(){if(!S.fullscreen)return;const stage=document.getElementById('io-stage'),preview=document.getElementById('preview-viewport');if(stage&&preview)preview.appendChild(stage);document.getElementById('viewer')?.remove();S.fullscreen=false;S.zoom=S.previewZoom||1;fitImage();}
  function results(data){
    cancelAdvance();closeViewer();S.screen='results';S.sessionId=null;S.finished=data;S.history=data.history;
    const pct=Math.round(data.earned/data.total*100),originals=S.questions.map((q,i)=>({q,i})).filter(v=>!v.q.is_retry),mistakes=originals.filter(v=>S.results[v.i].earned<S.results[v.i].total).length;
    root.innerHTML=shell(`<section class="result-hero"><div class="result-percent">${pct}%</div><h1>Session complete</h1><p>First-attempt score${data.repeat_attempts?` · ${data.repeat_attempts} repeat attempt${data.repeat_attempts===1?'':'s'} · ${data.mastered}/${data.questions} questions mastered`:''}</p><div class="row result-actions">${mistakes?button('retry-mistakes','Review missed questions','primary','refresh'):''}${button('retry-all','Repeat set','secondary')}${button('home','Choose another set','ghost')}</div></section><div class="result-grid"><div class="result-stat"><strong>${data.earned} / ${data.total}</strong><small>First-attempt points</small></div><div class="result-stat"><strong>${data.questions}</strong><small>Original questions</small></div><div class="result-stat"><strong>${duration(data.seconds)}</strong><small>Session time</small></div></div><section class="panel review-list"><div class="panel-head"><h3>Question review</h3><p class="muted" style="font-size:12px;margin-top:6px">First attempts below. Cloze points are awarded per blank; recall is self-marked.</p></div>${originals.map(({q,i},n)=>{const r=S.results[i],good=r.earned===r.total;return `<div class="review-row"><span style="color:var(--${good?'green':'red'})">${icon(good?'check':'x')}</span><div class="grow"><strong>${n+1}. ${esc(q.deck.split('::').pop())}</strong><div class="clue-snippet">${esc(text(q.clue).slice(0,230)||'Image occlusion recall')}</div>${q.kind!=='io'?`<div class="review-answer">${q.slots.map(slot=>`(${slot.number}) ${esc(slot.answer)}`).join(' · ')}</div>`:''}</div><span class="badge">${r.earned}/${r.total}</span></div>`;}).join('')}</section>`);
  }
  function leave(){cancelAdvance();checkpoint();const shade=document.createElement('div');shade.className='modal-shade';shade.id='leave-modal';shade.innerHTML=`<div class="panel modal-box" role="dialog" aria-modal="true"><h2>Pause this practice?</h2><p>Your progress is saved. Use Resume practice on the MAIN CRAM home screen to continue here.</p><div class="row spread">${button('stay','Keep practicing','secondary')}${button('confirm-leave','Save & exit','primary')}</div></div>`;root.appendChild(shade);shade.querySelector('button').focus();}
  function restartPrompt(){
    cancelAdvance();if(!S.sessionId||S.screen!=='session')return;
    document.getElementById('restart-modal')?.remove();
    const shade=document.createElement('div');shade.className='modal-shade';shade.id='restart-modal';
    shade.innerHTML=`<div class="panel modal-box" role="dialog" aria-modal="true" aria-label="Restart practice"><h2>Start this practice over?</h2><p>Your answers and position in this practice will reset.${S.order==='shuffle'?' The cards will be reshuffled.':''}</p><div class="row spread">${button('restart-cancel','Cancel','secondary')}${button('restart-confirm','Start over','primary')}</div></div>`;
    root.appendChild(shade);shade.querySelector('button').focus();
  }
  function click(action){
    if(action==='startup-retry'){retryStartup();return;}
    if(S.busy&&!['cancel','theme','zoom-in','zoom-out','zoom-reset','close-viewer'].includes(action)){toast('Wait for generation to finish, or pause it first.');return;}
    switch(action){
      case 'shortcuts':shortcuts();break;
      case 'close-keys':document.getElementById('keys-modal')?.remove();break;
      case 'text-larger':setTextZoom(S.textZoom+.1);break;
      case 'text-smaller':setTextZoom(S.textZoom-.1);break;
      case 'text-reset':setTextZoom(1);break;
      case 'theme':theme(!S.dark);if(document.getElementById('options-modal'))options();break;
      case 'options':cancelAdvance();options();break;
      case 'restart-practice':restartPrompt();break;
      case 'restart-cancel':document.getElementById('restart-modal')?.remove();break;
      case 'restart-confirm':checkpoint();document.getElementById('restart-modal')?.remove();document.getElementById('options-modal')?.remove();S.pending=true;send('restart');break;
      case 'close-options':document.getElementById('options-modal')?.remove();break;
      case 'settings':send('settings');break;
      case 'mapping':send('mapping');break;
      case 'customize':cancelAdvance();send('customize');break;
      case 'home':if(S.busy){toast('Pause generation before returning to decks.');break;}send('home');break;
      case 'history':if(!S.busy)history();break;
      case 'saved-more':S.savedExpanded=!S.savedExpanded;if(!S.savedExpanded){S.savedSearch='';const input=document.getElementById('saved-search');if(input)input.value='';}renderSaved();break;
      case 'clear-decks':S.selected.clear();invalidateMatches();renderDecks();break;
      case 'clear-filters':S.filters={search:'',tag:'',flag:'',note_type:''};invalidateMatches();home();break;
      case 'check-matches':{const request_id=++S.matchRequest;document.getElementById('match-status').textContent='Checking…';document.getElementById('check-matches').disabled=true;send('preview',{config:sessionConfig(),request_id});break;}
      case 'start':send('start',{config:sessionConfig()});break;
      case 'regen-decks':send('regen_decks',{config:sessionConfig()});break;
      case 'refresh-decks':send('ready');break;
      case 'generate':S.error='';send('generate');break;
      case 'flash':send('flash',S.screen==='session'?{index:S.index}:{});break;
      case 'cancel':send('cancel');break;
      case 'write-whole':send('write_whole');break;
      case 'write-finish':case 'write-reveal':finishWriting();break;
      case 'submit':if(current().ready!==false&&!S.results[S.index]&&!S.pending&&!getPicks().some(p=>p===null)){S.pending=true;updateFooter();send('grade',{index:S.index,picks:{choices:getPicks()}});}break;
      case 'dont-know':if(current().ready!==false&&!S.results[S.index]&&!S.pending){S.pending=true;S.picks[S.index]=Array(current().slots.length).fill(-1);updateFooter();send('grade',{index:S.index,picks:{unknown:true}});}break;
      case 'known':case 'unknown':if(answerSeen()&&!S.results[S.index]&&!S.pending){S.pending=true;send('grade',{index:S.index,picks:{known:action==='known'}});}break;
      case 'reveal':reveal();break;
      case 'next':cancelAdvance();if(S.results[S.index]){if(S.index===S.questions.length-1)send('finish');else{S.index++;question();window.scrollTo(0,0);}}break;
      case 'previous':cancelAdvance();if(S.index>0&&!S.pending){S.index--;question();window.scrollTo(0,0);}break;
      case 'leave':leave();break;
      case 'stay':document.getElementById('leave-modal')?.remove();break;
      case 'confirm-leave':send('home');break;
      case 'reset-cancel':document.getElementById('reset-modal')?.remove();S.resetId=null;break;
      case 'reset-confirm':{const id=S.resetId;document.getElementById('reset-modal')?.remove();S.resetId=null;if(id)send('reset_progress',{session_id:id});break;}
      case 'zoom-in':S.zoom=Math.min(6,S.zoom+.25);fitImage();checkpoint();break;
      case 'zoom-out':S.zoom=Math.max(.5,S.zoom-.25);fitImage();checkpoint();break;
      case 'zoom-reset':S.zoom=1;fitImage();checkpoint();break;
      case 'fullscreen':openViewer();break;
      case 'close-viewer':closeViewer();break;
      case 'retry-mistakes':send('retry',{mistakes:true});break;
      case 'retry-all':send('retry',{mistakes:false});break;
      case 'edit':if(!S.results[S.index]&&!S.busy)send('edit',{index:S.index});break;
      case 'regenerate':if(!S.results[S.index]&&!S.busy)send('regenerate',{index:S.index});break;
    }
  }
  root.addEventListener('click',event=>{
    const mask=event.target.closest('[data-main-mask]');if(mask){event.preventDefault();toggleMask(mask);return;}
    if(event.target.closest('#order-trigger')){document.getElementById('order-menu')?closeOrder(true):openOrder();return;}
    const orderOption=event.target.closest('[data-order-value]');if(orderOption){chooseOrder(orderOption.dataset.orderValue);return;}
    const resume=event.target.closest('[data-resume]');if(resume){send('resume',{session_id:resume.dataset.resume});return;}
    const reset=event.target.closest('[data-reset-progress]');if(reset){S.resetId=reset.dataset.resetProgress;const shade=document.createElement('div');shade.className='modal-shade';shade.id='reset-modal';shade.innerHTML=`<div class="panel modal-box" role="dialog" aria-modal="true"><h2>Reset this practice?</h2><p>This deletes its unfinished practice progress. Your Anki schedule and saved choices stay intact.</p><div class="row spread">${button('reset-cancel','Cancel','secondary')}${button('reset-confirm','Reset progress','primary')}</div></div>`;root.appendChild(shade);shade.querySelector('button').focus();return;}
    const branch=event.target.closest('[data-branch]');if(branch){const name=branch.dataset.branch;S.collapsed.has(name)?S.collapsed.delete(name):S.collapsed.add(name);renderDecks();return;}
    const blank=event.target.closest('.exam-card [data-blank]');if(blank&&!S.pending){selectBlank(Number(blank.dataset.blank));return;}
    const action=event.target.closest('[data-action]');if(action&&!action.disabled){click(action.dataset.action);return;}
    const preset=event.target.closest('[data-query]');if(preset){if(!preset.dataset.query){S.filters={search:'',tag:'',flag:'',note_type:''};home();}else{S.filters.search=preset.dataset.query;document.getElementById('anki-search').value=S.filters.search;root.querySelectorAll('[data-query]').forEach(b=>b.classList.toggle('active',b===preset));}invalidateMatches();return;}
    const mode=event.target.closest('[data-mode]');if(mode){S.mode=mode.dataset.mode;const extra=root.querySelector('.writing-extra');if(extra)extra.hidden=S.mode!=='write';root.querySelectorAll('[data-mode]').forEach(el=>{el.classList.toggle('selected',el===mode);el.setAttribute('aria-pressed',el===mode);});return;}
    const choice=event.target.closest('[data-choice]');if(choice&&!choice.disabled&&!S.results[S.index]&&!S.busy&&!S.pending){const i=+choice.dataset.slot;selectBlank(i);getPicks()[i]=+choice.dataset.choice;choice.closest('.choices').querySelectorAll('.choice').forEach(el=>el.classList.toggle('selected',el===choice));fillBlanks();if(i<current().slots.length-1)selectBlank(i+1,true);updateFooter();checkpoint();return;}
    const flip=event.target.closest('[data-flip]');if(flip&&!S.pending&&(!flashPointer||flashPointer.canFlip(event,flip))){reveal();return;}
    const dot=event.target.closest('[data-question]');if(dot&&!dot.disabled&&!S.busy&&!S.pending){S.index=+dot.dataset.question;question();}
  });
  root.addEventListener('focusin',e=>{const choice=e.target.closest('.exam-card [data-choice]');if(choice)selectBlank(Number(choice.dataset.slot));});
  root.addEventListener('input',event=>{if(event.target.id==='saved-search'){S.savedSearch=event.target.value;renderSaved();}});
  root.addEventListener('input',e=>{
    const t=e.target;
    if(t.id==='deck-search'){S.search=t.value;renderDecks();}
    if(t.id==='anki-search'){S.filters.search=t.value;root.querySelectorAll('[data-query]').forEach(b=>b.classList.toggle('active',b.dataset.query===t.value));invalidateMatches();}
    if(t.id==='filter-tag'){S.filters.tag=t.value;invalidateMatches();}
  });
  root.addEventListener('change',e=>{
    if(e.target.id==='write-ignore-extra'){S.ignoreExtra=e.target.checked;send('preferences',{write_ignore_extra:S.ignoreExtra});return;}
    const t=e.target;
    if(t.dataset.deck){t.checked?S.selected.add(t.dataset.deck):S.selected.delete(t.dataset.deck);t.closest('.deck-row').classList.toggle('selected',t.checked);invalidateMatches();updateCount();}
    if(t.id==='children'){S.children=t.checked;invalidateMatches();renderDecks();}
    if(t.id==='order'){chooseOrder(t.value,false);}if(t.id==='order-desc')S.orderDesc=t.checked;if(t.id==='limit')S.limit=t.value;
    if(t.id==='auto-advance'){S.autoAdvance=t.checked;send('preferences',{auto_advance:S.autoAdvance});S.autoAdvance?scheduleAdvance():cancelAdvance();}
    if(t.id==='feedback-delay'){S.feedbackMs=Number(t.value);send('preferences',{feedback_ms:S.feedbackMs});}

    if(t.id==='filter-note'){S.filters.note_type=t.value;invalidateMatches();}
    if(t.id==='filter-flag'){S.filters.flag=t.value;invalidateMatches();}
    if(t.id==='repeat-home'||t.id==='repeat-options'){S.repeat=t.checked;send('preferences',{repeat_mistakes:S.repeat});document.querySelectorAll('#repeat-home,#repeat-options').forEach(input=>input.checked=S.repeat);}
  });
  root.addEventListener('wheel',e=>{
    if(!(e.ctrlKey||e.metaKey))return;
    e.preventDefault();e.stopPropagation?.();
    if(e.target.closest('.flash-card,.exam-card,.waiting-card'))setTextZoom(S.textZoom+(e.deltaY<0?.1:-.1));
    else send('view_zoom',{delta:e.deltaY<0?.1:-.1});
  },{passive:false});
  document.addEventListener('keydown',e=>{
    if(orderKeys(e))return;
    if(e.key==='Escape'){if(S.fullscreen)closeViewer();else{document.getElementById('leave-modal')?.remove();document.getElementById('options-modal')?.remove();document.getElementById('keys-modal')?.remove();document.getElementById('reset-modal')?.remove();document.getElementById('restart-modal')?.remove();S.resetId=null;}return;}
    if((e.ctrlKey||e.metaKey)&&e.key==='0'){e.preventDefault();if(e.target.closest?.('.flash-card,.exam-card,.waiting-card'))setTextZoom(1);else send('view_zoom',{reset:true});return;}
    if(S.screen!=='session'||S.busy||S.pending||e.ctrlKey||e.metaKey||e.altKey||/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||document.getElementById('leave-modal')||document.getElementById('options-modal')||document.getElementById('keys-modal')||document.getElementById('restart-modal'))return;
    const mask=e.target.closest?.('[data-main-mask]');
    if(mask&&(e.key==='Enter'||e.code==='Space'||e.key===' ')){e.preventDefault();e.stopPropagation();if(!e.repeat)toggleMask(mask);return;}
    if(e.repeat){e.preventDefault();return;}
    const q=current(),key=e.key.toLowerCase(),space=e.code==='Space'||e.key===' ';
    if(key==='?'){e.preventDefault();shortcuts();return;}
    if(key==='arrowleft'){e.preventDefault();click('previous');return;}
    if(key==='arrowright'){e.preventDefault();if(S.results[S.index])click('next');else toast('Reveal and mark your recall before continuing.');return;}
    if(space&&q.mode==='flash'&&q.kind!=='io'){e.preventDefault();reveal();return;}
    if((space||key==='enter')&&S.results[S.index]){e.preventDefault();click('next');return;}
    if(q.mode==='write'){
      if(key==='arrowup'||key==='arrowdown'){e.preventDefault();S.writeUI?.move(key==='arrowup'?-1:1);}
      else if(key==='enter'){e.preventDefault();S.writeUI?.submit();}
      else if(space){e.preventDefault();click('write-reveal');}
      return;
    }
    if(q.mode==='flash'){
      if(space||key==='arrowup'||key==='arrowdown'){e.preventDefault();reveal();}
      if(answerSeen(q)&&!S.fullscreen&&!S.results[S.index]&&['1','2'].includes(key)){e.preventDefault();click(key==='1'?'unknown':'known');}
    }else if(q.ready!==false&&['arrowup','arrowdown'].includes(key)){
      e.preventDefault();e.stopPropagation();selectBlank(S.activeSlot+(key==='arrowdown'?1:-1),true);
    }else if(!S.results[S.index]&&q.ready!==false){
      const number='1234'.indexOf(key),letter='abcd'.indexOf(key),choice=number>=0?number:letter;
      if(choice>=0&&key.length===1){e.preventDefault();document.querySelector(`[data-slot="${S.activeSlot}"][data-choice="${choice}"]`)?.click();}
      else if(space||key==='enter'){e.preventDefault();const missing=getPicks().findIndex(p=>p===null);if(missing>=0){selectBlank(missing,true);toast('Choose an answer for each numbered blank.');}else click('submit');}
    }
  });
  window.addEventListener('resize',()=>{fitImage();window.cramAppearance?.fitImages(root);});
  window.addEventListener('blur',checkpoint);window.addEventListener('pagehide',checkpoint);
  document.addEventListener('pointerdown',e=>{if(!e.target.closest?.('#order-trigger,#order-menu'))closeOrder();});
  root.addEventListener('pointermove',e=>{const option=e.target.closest('#order-menu [data-order-value]');if(option&&option.getAttribute('aria-disabled')!=='true'&&option.dataset.orderValue!==orderActive)activateOrder(option.dataset.orderValue);});
  window.addEventListener('resize',()=>closeOrder());window.addEventListener('blur',()=>closeOrder());
  window.addEventListener('scroll',e=>{if(!e.target?.closest?.('#order-menu'))closeOrder();},true);
  window.cram={receive(event,data){
    switch(event){
      case 'bootstrap':for(const deck of data.decks){const parts=deck.name.split('::');for(let i=1;i<parts.length;i++){const name=parts.slice(0,i).join('::');if(!S.treeSeen.has(name)){S.treeSeen.add(name);S.collapsed.add(name);}}}startupDone=true;clearTimeout(startupTimer);clearTimeout(startupWait);S.cat=data;S.ignoreExtra=!!data.preferences?.write_ignore_extra;S.appearance=data.preferences?.appearance||{};S.history=data.history;S.repeat=!!data.preferences?.repeat_mistakes;S.autoAdvance=data.preferences?.auto_advance!==false;S.feedbackMs=data.preferences?.feedback_ms||1000;S.textZoom=data.preferences?.text_zoom||1;theme(data.dark);if(!S.selected.size&&data.decks.some(d=>d.id===data.current))S.selected.add(data.current);let base=document.getElementById('cram-media-base');if(!base){base=document.createElement('base');base.id='cram-media-base';document.head.prepend(base);}base.href=data.media;home();break;
      case 'theme':theme(data);break;
      case 'appearance':S.appearance=data;applyAppearance();break;
      case 'customizing':S.customizing=!!data;cancelAdvance();break;
      case 'preferences':if(data.write_ignore_extra!==undefined)S.ignoreExtra=data.write_ignore_extra;if(data.repeat_mistakes!==undefined)S.repeat=!!data.repeat_mistakes;if(data.auto_advance!==undefined)S.autoAdvance=data.auto_advance;if(data.feedback_ms)S.feedbackMs=data.feedback_ms;if(data.text_zoom)S.textZoom=data.text_zoom;break;
      case 'writeFeedback':if(data.index===S.index&&current()?.mode==='write'){S.writeUI?.receive(data);}break;
      case 'matches':if(S.screen==='home'&&data.request_id===S.matchRequest){const el=document.getElementById('match-status');el.classList.toggle('error',!!data.error);el.textContent=data.error||`${data.count} matching cards`;document.getElementById('check-matches').disabled=false;}break;
      case 'settings':S.cat.settings=data;if(S.screen==='home')home();break;
      case 'loading':loading(data);break;
      case 'prepare':S.prep=data;S.busy=false;preparation();break;
      case 'generating':{
        S.singleGeneration=data.single;S.error='';S.genProgress={done:0,total:data.total};
        if(S.screen==='session'&&!data.single){S.generating=true;generationStatus();break;}
        S.busy=true;const el=document.getElementById(data.single?'single-generation':'gen-status');
        if(el)el.innerHTML=`<div class="notice"><div class="row spread"><strong>Creating choices…</strong><span id="gen-count">0 / ${data.total}</span></div>${button('cancel','Pause generation','secondary')}</div>`;
        const actions=document.getElementById('gen-actions');if(actions)actions.hidden=true;
        document.querySelectorAll('.choice,#card-footer button,[data-action="edit"],[data-action="regenerate"]').forEach(b=>b.disabled=true);break;
      }
      case 'generationProgress':{const count=document.getElementById('gen-count');if(count)count.textContent=`${data.done} / ${data.total}`;break;}
      case 'choicesReady':{
        const waiting=current()?.ready===false;
        for(const q of data.questions){const i=S.questions.findIndex(item=>item.id===q.id);if(i>=0&&!S.results[i])S.questions[i]=q;}
        S.genProgress={done:data.done,total:data.total};if(waiting&&current()?.ready!==false)question();else generationStatus();break;
      }
      case 'generationDone':S.busy=false;S.generating=false;S.error='';generationStatus();break;
      case 'generationError':S.busy=false;S.generating=false;S.error=data.message;if(data.active&&S.screen==='session'){generationStatus();if(data.single){question();toast(data.message);}}else{if(data.prepared)S.prep=data.prepared;preparation();}break;
      case 'session':{
        cancelAdvance();S.busy=false;S.generating=false;S.error='';S.repeatActive=!!data.repeat_mistakes;S.sessionId=data.session_id||null;S.questions=data.questions;S.results=data.results||{};S.picks={};
        const view=data.view||{};S.written=view.written||{};S.ioMasks=view.ioMasks||{};
        for(const [i,result] of Object.entries(S.results)){if(result.picks?.choices)S.picks[i]=result.picks.choices;else if(result.picks?.unknown)S.picks[i]=Array(S.questions[i].slots.length).fill(-1);}
        Object.assign(S.picks,view.picks||{});S.index=Math.max(0,Math.min(view.index??Object.keys(S.results).length,S.questions.length-1));S.revealed=new Set(view.revealed||[]);S.flashSeen=new Set(view.flashSeen||view.revealed||[]);
        if(data.config){S.mode=data.config.mode;S.selected=new Set(data.config.decks);S.limit=String(data.config.limit);S.children=data.config.children;S.order=data.config.order||'shuffle';S.orderDesc=!!data.config.order_desc;S.filters=data.config.filters||{search:'',tag:'',flag:'',note_type:''};}
        if(S.results[S.index]&&!Array.isArray(view.revealed))S.revealed.add(S.index);
        if(data.restored&&S.questions.some(q=>q.mode==='exam'&&q.ready===false))S.error='Choice generation is paused. Resume it when you’re ready.';
        question(view);if(data.skipped&&!data.restored)toast(`${data.skipped} unsupported or empty cards skipped.`);break;
      }
      case 'replace':S.busy=false;S.questions[data.index]=data.question;delete S.picks[data.index];if(S.index===data.index)question();break;
      case 'graded':S.pending=false;S.results[data.index]=data.result;S.revealed.add(data.index);if(data.queued){S.questions.splice(data.queued.position,0,data.queued.question);}if(S.index===data.index){
        if(current().mode==='write')S.writeUI?.fill(true);
        // Update controls in place: grading must not reload clue/answer images.
        if(current().mode==='exam')current().slots.forEach((slot,i)=>{
          document.querySelectorAll(`[data-slot="${i}"]`).forEach(choice=>{
            const j=Number(choice.dataset.choice);choice.disabled=true;
            choice.classList.toggle('right',j===slot.correct);
            choice.classList.toggle('wrong',getPicks()[i]===j&&!data.result.correct[i]);
            if(j===slot.correct)choice.querySelector('.choice-key').innerHTML=icon('check');
          });
        });
        fillBlanks();updateFooter();
        const counter=document.getElementById('question-count');if(counter)counter.textContent=`${S.index+1} / ${S.questions.length}`;
        const dots=document.getElementById('question-dots');if(dots)dots.innerHTML=progressDots();
        document.querySelectorAll('[data-action="edit"],[data-action="regenerate"]').forEach(b=>b.disabled=true);
        const dot=document.querySelector(`[data-question="${S.index}"]`);if(dot)dot.classList.add(data.result.earned===data.result.total?'correct':'incorrect');
        const bar=document.querySelector('.progress-fill');if(bar)bar.style.width=Object.keys(S.results).length/S.questions.length*100+'%';
        checkpoint();scheduleAdvance();
      }break;
      case 'finished':results(data);break;
      case 'notice':toast(data);break;
      case 'error':S.busy=false;S.pending=false;S.error=data;if(!S.cat)startupError(data);else if(S.screen==='prepare')preparation();else if(S.screen==='loading'){home();document.getElementById('home-error').innerHTML=`<div class="notice error" role="alert">${esc(data)}</div>`;}else{toast(data);if(S.screen==='session'){S.writeUI?.failure(data);updateFooter();}}break;
    }
  },state:S};
  connectToAnki();
  }
  // Anki's stdHtml can load this file from the head, before body elements exist.
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initCram,{once:true});
  else initCram();
})();
