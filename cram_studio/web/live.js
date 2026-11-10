/* Presentation only. Anki owns every reveal, rating, interval and undo operation. */
(()=>{
  'use strict';if(window.cramNative)return;
  window.cramAppearance?.preventStudySelection(document,'#cram-live .cl-clue .ct-blank,#cram-live .cl-flip .cram-blank-empty,#cram-live .cl-io,#cram-live .cl-flip img,#cram-live .cl-exam img');
  const flashPointer=window.cramAppearance?.flashcardPointer(document,'#cram-live .cl-flip');
  const S={packet:null,mountedRoot:null,picks:[],active:0,front:null,exam:null,io:null,ioSide:null,zoom:1,textZoom:1,full:false,pending:false,writeUI:null,writeView:null,modeViews:{},photo:null};
  const fontBases=new WeakMap();
  const $=s=>document.querySelector(s),all=s=>document.querySelectorAll(s);
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const button=(action,text)=>`<button type="button" data-live-action="${action}">${text}</button>`;
  const send=(action,data={})=>{const p=S.packet;if(p&&typeof pycmd==='function')pycmd('cram_live:'+JSON.stringify({...data,action,cid:p.cid,epoch:p.epoch}));};
  function modeMenu(open=false){
    const menu=$('#cl-mode-menu'),toggle=$('[data-live-action="settings"]');if(!menu||!toggle)return;
    menu.hidden=!open;toggle.setAttribute('aria-expanded',String(open));
    all('[data-live-mode]').forEach(el=>{const selected=el.dataset.liveMode===(S.packet.mode||S.packet.display);el.setAttribute('aria-pressed',String(selected));el.disabled=selected;});
    send('overlay_focus',{open});
    if(open)menu.querySelector('[aria-pressed="true"]')?.focus({preventScroll:true});
  }
  function closePhoto(){
    if(!S.photo)return;
    const previous=S.photo.previous;$('#cl-photo-viewer')?.remove();S.photo=null;
    send('overlay_focus',{open:false});if(previous?.isConnected)previous.focus?.({preventScroll:true});
  }
  function fitPhoto(){
    if(!S.photo)return;
    const image=$('#cl-photo-image'),pane=$('.cl-photo-viewport');if(!image||!pane||!image.naturalWidth)return;
    const scale=Math.max(.01,Math.min((pane.clientWidth-32)/image.naturalWidth,(pane.clientHeight-32)/image.naturalHeight));
    image.style.width=Math.max(1,Math.round(image.naturalWidth*scale*S.photo.zoom))+'px';
    $('#cl-photo-zoom').textContent=Math.round(S.photo.zoom*100)+'%';
  }
  function openPhoto(source){
    const url=source.currentSrc||source.getAttribute('src');if(!url)return;
    closePhoto();modeMenu(false);
    const root=$('#cram-live'),viewer=document.createElement('div');
    viewer.id='cl-photo-viewer';viewer.className='cl-photo-viewer';viewer.setAttribute('role','dialog');viewer.setAttribute('aria-modal','true');viewer.setAttribute('aria-label','Enlarged image');
    viewer.innerHTML='<div class="cl-photo-tools">'+button('photo-minus','−')+'<span id="cl-photo-zoom">100%</span>'+button('photo-plus','+')+button('photo-fit','Fit')+'<button type="button" data-live-action="photo-close" aria-label="Close enlarged image">×</button></div><div class="cl-photo-viewport"><div class="cl-photo-stage"><img id="cl-photo-image" alt=""></div></div>';
    S.photo={zoom:1,previous:document.activeElement};root.appendChild(viewer);
    const image=$('#cl-photo-image');image.onload=fitPhoto;image.src=url;image.alt=source.alt||'';
    if(image.complete)fitPhoto();send('overlay_focus',{open:true});$('[data-live-action="photo-close"]').focus({preventScroll:true});
  }
  function appearance(){
    const root=$('#cram-live'),p=S.packet;if(!root||!p)return;
    const dark=document.body.classList.contains('nightMode')||document.body.classList.contains('night_mode');
    // Other add-ons toggle body classes on hover/focus. Reapplying every color,
    // image and size for those mutations can repaint the whole choices panel.
    const raw=p.appearance||null;
    if(S.appearanceRoot===root&&S.appearanceSource===raw&&S.appearanceDisplay===p.display&&S.appearanceDark===dark)return;
    S.appearanceSource=raw;S.appearanceDisplay=p.display;S.appearanceDark=dark;
    const key=JSON.stringify([dark,p.display,raw||{}]);
    if(S.appearanceRoot===root&&S.appearanceKey===key)return;
    S.appearanceRoot=root;S.appearanceKey=key;
    root.classList.toggle('cram-live-exam',p.display==='exam');
    window.cramAppearance?.apply(root,p.appearance||{},'anki',p.display==='io'?'io':['exam','write'].includes(p.display)?p.display:'flash',dark);
  }
  function applyTextZoom(){
    const hosts=new Set();
    all('.cl-original-content,.cl-flash-content,.cl-clue').forEach(root=>{
      [root,...root.querySelectorAll('*')].forEach(el=>{
        if(el.closest('script,style,svg,math,canvas'))return;
        // A highlight can wrap only <b>/<span> children. Its own font metrics
        // must grow too, or its painted background stays shorter than the text.
        if(el.textContent.trim())hosts.add(el);
      });
    });
    // Restore the baseline before measuring newly inserted descendants, which
    // may otherwise inherit an already zoomed parent's size.
    hosts.forEach(el=>{
      const base=fontBases.get(el);if(!base)return;
      if(base.font)el.style.setProperty('font-size',base.font,base.fontPriority);else el.style.removeProperty('font-size');
      if(base.lineStyle)el.style.setProperty('line-height',base.lineStyle,base.linePriority);else el.style.removeProperty('line-height');
    });
    // Measure every wrapper/child before changing any parent; scale only once.
    hosts.forEach(el=>{
      if(fontBases.has(el))return;
      const computed=getComputedStyle(el);
      fontBases.set(el,{size:parseFloat(computed.fontSize)||27,line:parseFloat(computed.lineHeight),
        font:el.style.getPropertyValue('font-size'),fontPriority:el.style.getPropertyPriority('font-size'),
        lineStyle:el.style.getPropertyValue('line-height'),linePriority:el.style.getPropertyPriority('line-height')});
    });
    hosts.forEach(el=>{
      const base=fontBases.get(el),reset=S.textZoom===1;
      if(reset){
        if(base.font)el.style.setProperty('font-size',base.font,base.fontPriority);else el.style.removeProperty('font-size');
        if(base.lineStyle)el.style.setProperty('line-height',base.lineStyle,base.linePriority);else el.style.removeProperty('line-height');
      }else{
        el.style.setProperty('font-size',base.size*S.textZoom+'px','important');
        if(Number.isFinite(base.line))el.style.setProperty('line-height',base.line*S.textZoom+'px','important');
      }
    });
  }
  function setTextZoom(value){
    S.textZoom=Math.max(.6,Math.min(2.5,Math.round(value*100)/100));
    S.packet.text_zoom=S.textZoom;applyTextZoom();send('text_zoom',{value:S.textZoom});
  }
  function reveal(){if(S.packet.side==='question'&&!S.pending){S.pending=true;pycmd('ans');}}
  function isFlashcard(){
    const p=S.packet;
    return !!(p&&['flash','native'].includes(p.display)&&((p.mode||'flash')==='flash'||(p.display==='flash'&&p.question?.image_answer)));
  }
  function flip(){
    const p=S.packet;
    if(!$('#cram-live')||!isFlashcard()||S.photo||$('#cl-mode-menu')?.hidden===false)return;
    if(p.side==='question')reveal();else if(p.side==='answer')$('.cl-flip')?.classList.toggle('is-flipped');
  }
  function cloneFront(node){
    const copy=node.cloneNode(true),ids=new Map(),elements=[copy,...copy.querySelectorAll('*')];
    elements.forEach((el,i)=>{const id=el.getAttribute('id');if(id){const replacement=`cl-snapshot-${S.packet.epoch}-${i}`;ids.set(id,replacement);el.setAttribute('id',replacement);}});
    // Preserve SVG masks/clip paths inside the snapshot without duplicate native IDs.
    elements.forEach(el=>{for(const attr of [...el.attributes]){let value=attr.value;for(const [old,id] of ids){value=value.split(`url(#${old})`).join(`url(#${id})`);if(['href','xlink:href','for'].includes(attr.name)&&value==='#'+old)value='#'+id;}if(value!==attr.value)el.setAttribute(attr.name,value);}});
    copy.querySelectorAll('script,style').forEach(el=>el.remove());
    copy.querySelectorAll('input,button,a,textarea,select').forEach(el=>{el.setAttribute('tabindex','-1');el.setAttribute('disabled','');});
    return copy;
  }
  function flipToAnswer(scene){
    const turn=scene.querySelector('.cl-turn'),packet=S.packet;
    if(!turn)return;
    // A newly inserted first card needs a committed front before its transform changes.
    // One RAF can run before that initial paint, collapsing the flip into a jump.
    void turn.offsetWidth;
    requestAnimationFrame(()=>requestAnimationFrame(()=>{
      if(!scene.isConnected||S.packet?.cid!==packet.cid||S.packet?.epoch!==packet.epoch||S.packet?.side!=='answer')return;
      scene.classList.add('is-flipped');
    }));
  }
  function nativeCard(){
    const original=$('#cl-original');if(!original)return;
    original.classList.add('cl-original-content');
    const scene=document.createElement('div');scene.className='cl-flip cl-native-scene';
    scene.innerHTML='<div class="cl-turn"><div class="cl-face cl-front"></div><div class="cl-face cl-back"></div></div>';
    original.parentElement.insertBefore(scene,original);
    if(S.packet.side==='question'){
      scene.querySelector('.cl-front').appendChild(original);S.front=cloneFront(original);
      scene.querySelector('.cl-back').setAttribute('aria-hidden','true');
    }else{
      scene.querySelector('.cl-back').appendChild(original);scene.querySelector('.cl-front').setAttribute('aria-hidden','true');
      if(S.front){scene.querySelector('.cl-front').appendChild(S.front);flipToAnswer(scene);}
      else scene.classList.add('is-flipped');
    }
  }
  function flashCard(){
    const p=S.packet,q=p.question,host=$('#cl-custom'),original=$('#cl-original');
    original.hidden=true;
    const back=q.kind==='cloze'?q.clue:q.slots.map(slot=>`<div class="cl-answer-item">${slot.answer_html}</div>`).join('');
    host.innerHTML=`<section class="cl-flip cl-compiled-flash" tabindex="0" role="button" aria-label="Flip flashcard"><div class="cl-turn"><div class="cl-face cl-front" aria-hidden="${p.side==='answer'}"><div class="cl-flash-content">${q.clue}</div></div><div class="cl-face cl-back" aria-hidden="${p.side!=='answer'}"><div class="cl-flash-content">${back}</div></div></div></section>`;
    host.querySelectorAll('.cl-front [data-blank]').forEach((el,i)=>{el.textContent='\u00a0';el.classList.add('cram-blank-empty');el.setAttribute('aria-label',`Blank ${i+1}`);});
    host.querySelectorAll('.cl-back [data-blank]').forEach(el=>{
      const slot=q.slots[Number(el.dataset.blank)];if(slot){el.innerHTML=slot.answer_html;el.classList.add('cl-revealed-answer');}
    });
    if(p.side==='answer')flipToAnswer(host.querySelector('.cl-flip'));
  }
  function fill(){
    const q=S.packet.question;if(!q||S.packet.display!=='exam')return;
    S.active=Math.max(0,Math.min(q.slots.length-1,S.active));
    all('#cl-custom [data-blank]').forEach(el=>{
      const i=Number(el.dataset.blank),slot=q.slots[i],pick=S.picks[i];if(!slot)return;
      const answer=S.packet.side==='answer';
      const empty=!answer&&pick==null;
      if(empty){el.textContent='\u00a0';el.classList.remove('cram-blank-lines');}
      else if(window.cramAppearance?.fillBlank)window.cramAppearance.fillBlank(el,slot,answer?slot.answer:slot.choices[pick]);
      else el.textContent=answer?slot.answer:slot.choices[pick];
      el.classList.toggle('cram-blank-empty',empty);el.setAttribute('aria-label',`Blank ${slot.number}`);
      el.classList.toggle('cl-revealed-answer',answer);el.classList.toggle('cl-filled',answer||pick!=null);el.classList.toggle('cl-active',!answer&&q.ready&&i===S.active);
      if(!answer&&q.ready&&i===S.active)el.setAttribute('aria-current','true');else el.removeAttribute('aria-current');
    });
    all('.cl-slot').forEach((el,i)=>{el.hidden=i!==S.active;el.classList.toggle('cl-active-slot',i===S.active);});
  }
  function selectBlank(index,scroll=false){
    const p=S.packet;if(!p||p.display!=='exam'||!p.question.ready||S.pending)return;
    const count=p.question.slots.length;if(!count||!Number.isInteger(index))return;
    const next=(index+count)%count;
    if(next===S.active){
      if(scroll)window.cramAppearance?.showInPane($(`.cl-question-panel [data-blank="${next}"]`),$('.cl-question-panel'));
      return;
    }
    S.active=next;fill();
    const answers=$('.cl-answers');if(answers)answers.scrollTop=0;
    if(scroll)window.cramAppearance?.showInPane($(`.cl-question-panel [data-blank="${S.active}"]`),$('.cl-question-panel'));
  }
  function moveBlank(delta){if(S.packet?.display==='write')S.writeUI?.move(delta);else selectBlank(S.active+delta,true);}
  function writing(){
    const p=S.packet,q=p.question,host=$('#cl-custom');$('#cl-original').hidden=true;
    if(!q.ready){host.innerHTML='<section class="cl-exam write-card"><div class="cl-question-body"><div class="cl-question-panel"><div class="cl-clue">'+q.clue+'</div></div></div><div class="cl-answers"></div></section>';return;}
    host.innerHTML='<section class="cl-exam write-card"><div class="cl-question-body"><div class="cl-question-panel"><div class="cl-clue write-clue">'+window.cramWriting.question(q)+'</div></div></div><div class="cl-answers write-response-host"></div></section>';
    const view=S.writeView||(S.writeView={events:p.writing_events||[],draft:'',target:0});
    if(p.writing_state){view.events=p.writing_events||[];view.state=p.writing_state;}
    S.writeUI=window.cramWriting.mount(host.querySelector('.write-response-host'),host.querySelector('.write-clue'),q,view,{
      revealed:p.side==='answer',autofocus:p.side==='question',review:true,
      submit:({text,target})=>send('write_submit',{text,target}),finish:reveal,
      focus:focused=>send('writing_focus',{focused})
    });
  }
  function exam(){
    const p=S.packet,q=p.question,answer=p.side==='answer',host=$('#cl-custom'),original=$('#cl-original');
    if(original)original.hidden=true;
    // Anki replaces #qa on Show Answer. Retain the same question/option nodes
    // across that replacement rather than recreating unfilled placeholders.
    const key=JSON.stringify([p.cid,p.card_epoch??p.epoch,p.choices_revision||0,q]);
    if(S.exam?.key===key){
      host.querySelectorAll('.cl-feedback').forEach(el=>el.remove());
      if(S.exam.node.parentElement!==host){host.innerHTML='';host.appendChild(S.exam.node);}
    }else{
      host.innerHTML=`<section class="cl-exam"><div class="cl-question-body"><div class="cl-question-panel"><div class="cl-clue">${q.clue}</div></div></div><div class="cl-answers">${q.ready?q.slots.map((slot,i)=>`<div class="cl-slot" data-live-group="${i}">${q.kind==='cloze'?`<div class="cl-slot-label">Blank ${slot.number}${q.slots.length>1?` / ${q.slots.length}`:''}</div>`:''}<div class="cl-choices">${slot.choices.map((text,j)=>`<button type="button" class="cl-choice" data-live-slot="${i}" data-live-choice="${j}"><span class="cl-key">${'ABCD'[j]}</span><span class="cl-choice-text">${esc(window.cramAppearance?.choiceText(slot.answer,text)??text)}</span></button>`).join('')}</div></div>`).join(''):''}</div></section>`;
      S.exam={key,node:host.querySelector('.cl-exam')};
    }
    host.querySelectorAll('[data-live-choice]').forEach(el=>{
      const i=Number(el.dataset.liveSlot),j=Number(el.dataset.liveChoice),slot=q.slots[i];
      el.disabled=answer;el.classList.toggle('selected',S.picks[i]===j);
      el.classList.toggle('correct',answer&&j===slot.correct);
      el.classList.toggle('incorrect',answer&&S.picks[i]===j&&j!==slot.correct);
    });
    if(answer&&q.ready&&S.picks.some(Number.isInteger)){
      const correct=q.slots.filter((slot,i)=>S.picks[i]===slot.correct).length;
      const feedback=document.createElement('div');feedback.className='cl-feedback';feedback.textContent=`${correct} / ${q.slots.length} correct`;host.appendChild(feedback);
    }
    fill();
  }
  function io(){
    const p=S.packet,q=p.question,host=$('#cl-custom');$('#cl-original').hidden=true;
    host.innerHTML=`<section class="cl-io"><div class="cl-io-head"><span class="cl-label">ANKI CRAM · Image occlusion</span><div class="cl-io-tools">${button('io-masks',p.side==='answer'?'Show masks':'Hide masks')}${button('io-minus','−')}<span id="cl-zoom">${Math.round(S.zoom*100)}%</span>${button('io-plus','+')}${button('io-fit','Fit')}${button('io-full',S.full?'Close viewer':'Full screen')}</div></div>${q.clue?`<div class="cl-caption">${q.clue}</div>`:''}<div class="cl-viewport"><div class="cl-image-stage"></div></div>${q.extra&&p.side==='answer'?`<div class="cl-extra">${q.extra}</div>`:''}</section>`;
    const stage=$('.cl-image-stage');
    if(!S.io){const holder=document.createElement('div');holder.innerHTML=q.picture;S.io=holder.firstElementChild;}
    stage.appendChild(S.io);
    S.io.querySelector('svg')?.removeAttribute('aria-hidden');
    S.io.querySelectorAll('.mask.target').forEach((mask,i)=>{mask.setAttribute('role','button');mask.setAttribute('tabindex','0');mask.dataset.maskNumber=String(i+1);});
    if(S.ioSide!==p.side){S.io.classList.toggle('revealed',p.side==='answer');S.io.querySelectorAll('.mask.target').forEach(mask=>mask.classList.remove('io-mask-open','io-mask-closed'));S.ioSide=p.side;}
    maskLabels();
    if(S.full)host.classList.add('cl-full');else host.classList.remove('cl-full');
    const image=S.io.querySelector('img');image.onload=fit;if(image.complete)fit();
  }
  function maskOpen(mask){return S.io.classList.contains('revealed')?!mask.classList.contains('io-mask-closed'):mask.classList.contains('io-mask-open');}
  function maskLabels(){
    S.io?.querySelectorAll('.mask.target').forEach(mask=>{const open=maskOpen(mask);mask.setAttribute('aria-label',`${open?'Hide':'Reveal'} mask ${mask.dataset.maskNumber}`);mask.setAttribute('aria-pressed',String(open));});
    const control=$('[data-live-action="io-masks"]');if(control){const open=S.io.classList.contains('revealed');control.textContent=open?'Show masks':'Hide masks';control.setAttribute('aria-pressed',String(!open));}
  }
  function toggleMask(mask){
    if(!S.io||mask.closest('.io-image')!==S.io)return;
    const open=maskOpen(mask),all=S.io.classList.contains('revealed');
    mask.classList.toggle('io-mask-open',!all&&!open);mask.classList.toggle('io-mask-closed',all&&open);maskLabels();
  }
  function fit(){
    const image=S.io?.querySelector('img'),frame=$('.cl-viewport');if(!image||!frame||!image.naturalWidth)return;
    const width=Math.max(80,Math.min(frame.clientWidth-32,(frame.clientHeight-32)*image.naturalWidth/image.naturalHeight));
    S.io.style.width=Math.round(width*S.zoom)+'px';const value=$('#cl-zoom');if(value)value.textContent=Math.round(S.zoom*100)+'%';
  }
  function status(){
    const p=S.packet,q=p.question,el=$('#cl-notice');if(!el)return;
    if(p.display==='write'){
      if(p.side==='question'&&!q.ready)el.innerHTML=`${p.generating?'<span class="cl-spinner"></span>Preparing answer groups…':esc(p.error||'Preparing answer groups…')}<div class="cl-notice-actions">${button('write_whole','Use full answer')}</div>`;
      else el.textContent=p.error||'';
    }else if(p.display==='exam'&&!q.ready){
      el.innerHTML=`${p.generating?'<span class="cl-spinner"></span>Preparing choices…':esc(p.error||'Choices have not been created for this card.')}<div class="cl-notice-actions">${button('generate',p.generating?'Preparing…':'Create choices')}${p.side==='question'?button('flash','Use original flashcard'):''}</div>`;
      el.querySelector('[data-live-action="generate"]').disabled=p.generating;
    }else if(p.display==='exam'&&p.side==='question'&&q.ready){
      el.innerHTML=`<div class="cl-choice-tools"><span class="cl-choice-message">${p.generating?'Regenerating choices…':esc(p.error||'')}</span>${button('regen_decks','Regenerate deck choices')}${button('regenerate','Regenerate choices')}</div>`;
      el.querySelector('[data-live-action="regenerate"]').disabled=p.generating;
      el.querySelector('[data-live-action="regen_decks"]').disabled=p.generating;
    }else el.textContent=p.error||p.reason||'';
  }
  function draw(){
    const p=S.packet,original=$('#cl-original'),wrapper=original?.closest('.cl-native-scene');
    if(wrapper){wrapper.parentElement.insertBefore(original,wrapper);wrapper.remove();}
    const host=$('#cl-custom');if(host){host.hidden=false;host.classList.remove('cl-full');}
    if(original)original.hidden=false;
    if(p.display==='native')nativeCard();else if(p.display==='flash')flashCard();else if(p.display==='io')io();else if(p.display==='write')writing();else exam();
    applyTextZoom();appearance();status();modeMenu(false);
  }
  function mount(){
    const root=$('#cram-live');if(!root){document.body.classList.remove('cram-live-on');return;}
    if(!$('#cl-photo-viewer'))S.photo=null;
    const p=JSON.parse(root.dataset.packet),same=S.packet?.epoch===p.epoch&&S.packet?.cid===p.cid;
    // Anki's shown hook can run again for the existing DOM. Its initial packet
    // may predate loaded choices; do not tear down the current question/picks.
    if(same&&S.mountedRoot===root&&S.packet.side===p.side&&S.packet.display===p.display)return;
    if(!same){S.picks=[];S.active=0;S.front=null;S.exam=null;S.io=null;S.ioSide=null;S.zoom=1;S.full=false;S.writeUI=null;S.writeView=null;S.modeViews={};S.photo=null;}
    S.packet=p;S.mountedRoot=root;S.textZoom=Math.max(.6,Math.min(2.5,Number(p.text_zoom)||1));S.pending=false;document.body.classList.add('cram-live-on');
    draw();
    if(!S.themeObserver&&typeof MutationObserver==='function'){
      S.themeObserver=new MutationObserver(appearance);S.themeObserver.observe(document.body,{attributes:true,attributeFilter:['class']});
    }
    send('ready');
  }
  function switchMode(p){
    const old=S.packet,root=$('#cram-live');
    if(!old||!root||p.cid!==old.cid||p.card_epoch!==old.card_epoch||p.epoch<=old.epoch||p.side!==old.side)return;
    closePhoto();
    const previous=old.mode||old.display;
    S.modeViews[previous]={picks:S.picks,active:S.active,writeView:S.writeView,scroll:$('.cl-question-panel')?.scrollTop||0};
    const saved=S.modeViews[p.mode]||{};
    S.packet=p;root.dataset.packet=JSON.stringify(p);S.pending=false;S.writeUI=null;
    S.picks=saved.picks||[];S.active=saved.active||0;S.writeView=saved.writeView||null;
    if(old.display==='io'&&p.display==='io'){modeMenu(false);status();}
    else{
      S.full=false;draw();
      const pane=$('.cl-question-panel');if(pane&&saved.scroll)pane.scrollTop=saved.scroll;
    }
    send('ready');
  }
  function receive(p){
    if(!S.packet||p.cid!==S.packet.cid||p.epoch!==S.packet.epoch||p.side!==S.packet.side||!$('#cram-live'))return;
    const becameReady=p.question?.ready&&!S.packet.question?.ready;
    const replaced=(p.choices_revision||0)!==(S.packet.choices_revision||0);
    const wrote=(p.writing_events?.length||0)!==(S.packet.writing_events?.length||0);
    S.packet=p;$('#cram-live').dataset.packet=JSON.stringify(p);
    if(p.display==='write'){
      if(becameReady){writing();applyTextZoom();}
      else if(wrote&&p.writing_state)S.writeUI?.receive({events:p.writing_events,state:p.writing_state});
      else if(p.error)S.writeUI?.failure(p.error);
    }
    if((becameReady||replaced)&&p.display==='exam'){
      if(replaced){S.picks=[];S.active=0;S.pending=false;}
      exam();applyTextZoom();
    }appearance();status();
  }
  function choose(number){
    const p=S.packet;if(!p||p.side!=='question'||p.display!=='exam'||!p.question.ready||S.pending)return;
    const choice=$(`[data-live-slot="${S.active}"][data-live-choice="${number}"]`);choice?.click();
  }
  document.addEventListener('click',event=>{
    if(!$('#cram-live'))return;
    const mode=event.target.closest('[data-live-mode]');
    if(mode){if(!mode.disabled){modeMenu(false);send('switch_mode',{mode:mode.dataset.liveMode});}return;}
    if(!event.target.closest('.cl-settings')&&!$('#cl-mode-menu')?.hidden)modeMenu(false);
    const mask=event.target.closest('.cl-image-stage .mask.target');if(mask){event.preventDefault();event.stopPropagation();toggleMask(mask);return;}
    const option=event.target.closest('[data-live-choice]');
    if(option&&!option.disabled&&S.packet.side==='question'&&!S.pending){
      const i=Number(option.dataset.liveSlot);selectBlank(i);S.picks[i]=Number(option.dataset.liveChoice);
      option.closest('.cl-choices').querySelectorAll('.cl-choice').forEach(el=>el.classList.toggle('selected',el===option));fill();if(i<S.packet.question.slots.length-1)selectBlank(i+1,true);return;
    }
    const blank=event.target.closest('#cl-custom [data-blank]');if(blank&&S.packet.display==='exam'){selectBlank(Number(blank.dataset.blank));return;}
    const action=event.target.closest('[data-live-action]');
    if(action&&!action.disabled){
      switch(action.dataset.liveAction){
        case 'settings':modeMenu($('#cl-mode-menu')?.hidden!==false);break;
        case 'photo-close':closePhoto();break;
        case 'photo-plus':if(S.photo){S.photo.zoom=Math.min(6,S.photo.zoom+.25);fitPhoto();}break;
        case 'photo-minus':if(S.photo){S.photo.zoom=Math.max(.5,S.photo.zoom-.25);fitPhoto();}break;
        case 'photo-fit':if(S.photo){S.photo.zoom=1;fitPhoto();}break;
        case 'io-masks':S.io.classList.toggle('revealed');S.io.querySelectorAll('.mask.target').forEach(mask=>mask.classList.remove('io-mask-open','io-mask-closed'));maskLabels();break;
        case 'io-plus':S.zoom=Math.min(6,S.zoom+.25);fit();break;
        case 'io-minus':S.zoom=Math.max(.5,S.zoom-.25);fit();break;
        case 'io-fit':S.zoom=1;fit();break;
        case 'io-full':S.full=!S.full;$('#cl-custom').classList.toggle('cl-full',S.full);action.textContent=S.full?'Close viewer':'Full screen';fit();break;
        default:send(action.dataset.liveAction);
      }return;
    }
    const flip=event.target.closest('.cl-flip');
    if(['native','flash'].includes(S.packet.display)&&flip&&!event.target.closest('a,button,input,textarea,select,canvas,svg,img')&&(!flashPointer||flashPointer.canFlip(event,flip))){
      if(S.packet.side==='question')reveal();else $('.cl-flip').classList.toggle('is-flipped');
    }
  });
  document.addEventListener('dblclick',event=>{
    const occlusion=event.target.closest('#cram-live .cl-image-stage');
    if(occlusion){event.preventDefault();event.stopPropagation();if(!S.full)$('[data-live-action="io-full"]')?.click();return;}
    const image=event.target.closest('#cram-live #cl-stage img');if(!image||S.photo)return;
    event.preventDefault();event.stopPropagation();
    openPhoto(image);
  });
  document.addEventListener('focusin',event=>{const choice=event.target.closest('#cl-custom [data-live-choice]');if(choice)selectBlank(Number(choice.dataset.liveSlot));});
  document.addEventListener('wheel',event=>{
    if(!$('#cram-live')||!S.packet||!(event.ctrlKey||event.metaKey))return;
    event.preventDefault();event.stopPropagation();
    if(S.photo){S.photo.zoom=Math.max(.5,Math.min(6,S.photo.zoom+(event.deltaY<0?.25:-.25)));fitPhoto();return;}
    if(event.target.closest('.cl-flip,.cl-exam'))setTextZoom(S.textZoom+(event.deltaY<0?.1:-.1));
    else send('view_zoom',{delta:event.deltaY<0?.1:-.1});
  },{passive:false});
  document.addEventListener('keydown',event=>{
    if(!$('#cram-live')||!S.packet)return;
    if(S.photo){if(event.key==='Escape'){event.preventDefault();event.stopPropagation();closePhoto();}return;}
    if($('#cl-mode-menu')?.hidden===false){if(event.key==='Escape'){event.preventDefault();event.stopPropagation();modeMenu(false);$('[data-live-action="settings"]')?.focus({preventScroll:true});}return;}
    if(event.key==='Enter'&&event.target.closest('.cl-image-stage .mask.target')){event.preventDefault();event.stopPropagation();toggleMask(event.target.closest('.mask.target'));return;}
    if(event.key==='Escape'&&S.full){event.preventDefault();S.full=false;$('#cl-custom').classList.remove('cl-full');fit();return;}
    if((event.ctrlKey||event.metaKey)&&event.key==='0'){
      event.preventDefault();if(event.target.closest('.cl-flip,.cl-exam'))setTextZoom(1);else send('view_zoom',{reset:true});return;
    }
    if((event.key===' '||event.code==='Space')&&S.packet.display==='exam'&&S.packet.side==='question'
        &&!event.ctrlKey&&!event.metaKey&&!event.altKey&&!event.shiftKey
        &&!event.target.closest('a,input,textarea,select,[contenteditable],[data-live-action],[data-live-mode]')){
      event.preventDefault();event.stopPropagation();if(!event.repeat)reveal();return;
    }
    if((event.key===' '||event.code==='Space')&&isFlashcard()
        &&!event.ctrlKey&&!event.metaKey&&!event.altKey&&!event.shiftKey
        &&!event.target.closest('a,button,input,textarea,select,[contenteditable]')){
      event.preventDefault();event.stopPropagation();if(!event.repeat)flip();return;
    }
    if(event.ctrlKey||event.metaKey||event.altKey||event.repeat||/INPUT|TEXTAREA|SELECT/.test(event.target.tagName))return;
    if(['native','flash'].includes(S.packet.display)&&['ArrowUp','ArrowDown'].includes(event.key)){
      event.preventDefault();if(S.packet.side==='question')reveal();else $('.cl-flip')?.classList.toggle('is-flipped');return;
    }
    if(S.packet.display==='exam'&&S.packet.question.ready&&['ArrowUp','ArrowDown'].includes(event.key)){
      event.preventDefault();event.stopPropagation();moveBlank(event.key==='ArrowDown'?1:-1);
    }
    // Answer-side MCQ Space, 1–4, E, B and Ctrl+Z stay with Anki/Qt.
  });
  document.addEventListener('keyup',event=>{
    if($('#cram-live')&&S.packet?.display==='exam'&&(event.key===' '||event.code==='Space')
        &&event.target.closest('[data-live-choice]'))event.preventDefault();
  });
  window.addEventListener('resize',()=>{fit();fitPhoto();window.cramAppearance?.fitImages($('#cram-live'));});
  window.cramNative={mount,receive,switchMode,flip,reveal,choose,moveBlank,state:S};
})();
