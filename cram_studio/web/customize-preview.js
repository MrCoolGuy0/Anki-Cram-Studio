/* Synthetic preview only. No collection, review bridge, API or scheduling calls. */
(()=>{
  'use strict';
  function init(){
    const A=window.cramAppearance,S={config:A.normalize({}),mode:'main',theme:'light',view:'flash',face:'question',panel:'size',pick:null,locator:null,lastLocate:0,inspect:false,colorLabels:{},inspectItems:[]};
    A.preventStudySelection(document,'.session .exam-card .ct-blank,.session .flash-card .cram-blank-empty,.session .flash-card img,.session .exam-card img,#cram-live .cl-clue .ct-blank,#cram-live .cl-flip .cram-blank-empty,#cram-live .cl-flip img,#cram-live .cl-exam img');
    const flashPointer=A.flashcardPointer(document,'.flash-card,.cl-flip');
    // Browser NodeLists are iterable but have no .find(); keep every consumer consistent.
    const $=s=>document.querySelector(s),all=s=>Array.from(document.querySelectorAll(s)),post=data=>window.parent.postMessage(data,'*');
    const choices=['Tissue','Organ','Cell','System'];
    const clue='<b>Levels of organization</b><br>Groups of similar cells form a <span class="ct-blank cram-blank-empty" data-sample-blank aria-label="Blank 1">\u00a0</span>.';
    const answer='<b>Levels of organization</b><br>Groups of similar cells form a <span class="ct-blank cl-revealed-answer revealed-answer">tissue</span>.';
    const style=document.createElement('style');style.textContent=`
      html,body{overflow:hidden}body{height:100vh}#cram-live{--cram-scene-height:calc(100vh - 72px)}.sample-footer{position:fixed;bottom:0;left:0;right:0;height:72px;display:flex;align-items:center;justify-content:center;background:var(--soft,#f6f7fb);border-top:1px solid var(--line,#e5e8f2)}.sample-footer button{border:1px solid var(--line);border-radius:9px;padding:12px 20px;background:var(--panel);font-size:14px;margin:0 5px}.sample-footer #middle{display:flex;align-items:center;justify-content:center}.preview-resize{position:fixed;z-index:99;display:grid;place-items:center;width:28px;height:28px;border:2px solid #4255ff;border-radius:7px;color:#4255ff;background:white;padding:0;font:700 17px/1 Arial;box-shadow:0 2px 8px #0002;touch-action:none}.preview-resize[data-axis=x]{cursor:ew-resize}.preview-resize[data-axis=y]{cursor:ns-resize}.preview-resize[data-axis=xy]{cursor:nwse-resize}.cram-size-preview{outline:2px dashed #4255ff;outline-offset:4px}.sample-face-controls{display:flex;justify-content:center;gap:12px;margin-top:15px}.sample-face-controls button{min-height:46px;min-width:160px}.session .card-heading{pointer-events:none}
      #preview-locator{position:fixed;inset:0;z-index:120;pointer-events:none;font:600 14px/1.4 "Segoe UI",Arial,sans-serif}.preview-locate-ring{position:absolute;border:3px solid #4255ff;border-radius:9px;box-shadow:0 0 0 2px white;pointer-events:none}.preview-locate-label{position:absolute;display:flex;align-items:center;gap:12px;max-width:330px;padding:10px 12px;background:#ffffff;color:#202b45;border:2px solid #4255ff;border-radius:10px;box-shadow:0 4px 16px #202b4533}.preview-locate-label button{pointer-events:auto!important;cursor:pointer;border:0!important;background:transparent!important;color:#202b45!important;font-size:20px!important;padding:0 3px!important;min-height:0!important;margin:0!important}.preview-locate-arrow{position:absolute;inset:0;width:100%;height:100%;overflow:visible}.preview-locate-arrow path{fill:none;stroke:#4255ff;stroke-width:2.5}.preview-locate-arrow circle{fill:#4255ff}.preview-locate-label strong{font-size:13px}.preview-locate-label small{display:block;margin-top:3px;color:#586780;font-size:11px}.preview-locate-label i{display:inline-block;width:12px;height:12px;border:1px solid #ccd0de;border-radius:3px;vertical-align:middle;margin-right:5px}
    `;document.head.appendChild(style);
    const inspectStyle=document.createElement('style');inspectStyle.textContent=`
      body.cram-inspecting,body.cram-inspecting *{cursor:crosshair!important}body.cram-inspecting .card-heading{pointer-events:auto!important}
      #preview-inspect-ring{position:fixed;z-index:118;pointer-events:none;box-sizing:border-box;border:2px solid #4255ff;border-radius:6px;box-shadow:0 0 0 1px #ffffffcc}
      #preview-inspect-menu{position:fixed;z-index:130;width:360px;max-width:calc(100vw - 24px);max-height:calc(100vh - 24px);overflow:auto;border:2px solid #4255ff;border-radius:12px;background:#fff;color:#202b45;box-shadow:0 8px 30px #202b4540;padding:14px;font:16px/1.4 "Segoe UI",Arial,sans-serif}
      #preview-inspect-menu *{cursor:default!important}#preview-inspect-menu header{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:10px}#preview-inspect-menu header button{font-size:24px;color:#202b45;padding:0 5px}#preview-inspect-menu small{display:block;font-size:13px;color:#586780;margin:6px 0}#preview-inspect-menu button[data-inspect-index]{display:flex;gap:10px;align-items:center;text-align:left;width:100%;border:1px solid #e2e6f0;background:#f8f9fd;color:#202b45;border-radius:7px;padding:9px 10px;margin-top:7px;cursor:pointer!important;font:15px/1.4 "Segoe UI",Arial,sans-serif}#preview-inspect-menu button[data-inspect-index]:hover{border-color:#4255ff;background:#eef0ff}#preview-inspect-menu button[data-inspect-index] *{cursor:pointer!important}#preview-inspect-menu i{display:block;flex:0 0 24px;height:24px;border:1px solid #aeb7c8;border-radius:5px}#preview-inspect-menu code{font-size:12px}#preview-inspect-menu button span{min-width:0}#preview-inspect-menu button small{margin:2px 0 0}
      /* Inspect the current state, without hover temporarily repainting a choice. */
      .cram-inspecting .session .choice:hover:not(.selected):not(.right):not(.wrong){background:var(--cram-button-bg,var(--panel));color:var(--cram-button-text,var(--ink));border-color:var(--line)}
      .cram-inspecting #cram-live .cl-choice:hover:not(.selected):not(.correct):not(.incorrect){background:var(--cram-button-bg,var(--cl-panel));color:var(--cram-button-text,var(--cl-text));border-color:var(--cl-line)}
      .cram-inspecting .session .primary:hover{background:var(--primary)}.cram-inspecting .session .flash-controls .secondary:hover{background:var(--cram-reveal-bg,var(--panel));color:var(--cram-reveal-text,var(--ink));border-color:var(--line)}
    `;document.head.appendChild(inspectStyle);
    function root(){return S.mode==='anki'?$('#cram-live'):$('.session');}
    function frame(){return S.mode==='anki'?$(S.view!=='flash'?'.cl-exam':'.cl-flip'):$(S.view!=='flash'?'.exam-card':'.flash-card');}
    function apply(){A.apply(root(),S.config,S.mode,S.view,S.theme==='dark');A.applyBottom(S.config,S.mode==='anki'?S.view:'',S.theme==='dark');document.body.classList.toggle('cram-inspecting',S.inspect);if(!S.inspect)dismissInspector();place();}
    function palette(){document.documentElement.classList.toggle('cram-dark',S.theme==='dark');document.body.className=S.mode==='anki'?'cram-live-on'+(S.theme==='dark'?' nightMode':''):'';}
    function options(){return choices.map((value,i)=>{
      const checked=S.face==='answer',pick=S.pick??(checked?1:null),state=checked?(i===0?(S.mode==='anki'?'correct':'right'):i===pick?(S.mode==='anki'?'incorrect':'wrong'):''):i===pick?'selected':'';
      return `<button type="button" class="${S.mode==='anki'?'cl-choice':'choice'} ${state}" data-sample-choice="${i}"><span class="${S.mode==='anki'?'cl-key':'choice-key'}">${'ABCD'[i]}</span><span class="${S.mode==='anki'?'cl-choice-text':'grow choice-text'}">${value}</span></button>`;
    }).join('');}
    function render(){
      palette();
      const flipped=S.face==='answer'?'is-flipped':'';
      if(S.mode==='main'){
        document.body.innerHTML=`<main class="session"><header class="session-header"><div class="study-mode"><span class="main-mode-label"><strong>MAIN CRAM</strong><small>${S.view==='flash'?'Flashcards':S.view==='write'?'Writing':'Learn'}</small><small>Practice only · Schedule unchanged</small></span></div><div class="session-progress"><strong>1 / 20</strong><div class="session-deck">Sample deck</div></div><div class="header-actions"><button class="btn ghost" disabled>Settings</button><button class="icon-btn" disabled>×</button></div></header><div class="session-main"><div class="progress-track"><div class="progress-fill" style="width:5%"></div></div>${S.view==='flash'?`<section class="panel study-card flash-card ${flipped}" tabindex="0" role="button" aria-label="Flip sample flashcard"><div class="card-heading"><span>${S.face==='answer'?'Answer':'Clue'}</span></div><div class="flash-turn"><div class="flash-face"><div class="face-content clue">${clue}</div></div><div class="flash-face flash-back"><div class="face-content clue">${answer}</div></div></div></section><div class="flash-controls"><button class="btn bad">Still learning</button><button class="btn secondary" data-sample-flip>${S.face==='answer'?'Show clue':'Reveal answer'}</button><button class="btn good">Got it</button></div>`:`<section class="panel study-card exam-card"><div class="card-heading"><span>Blank 1</span></div><div class="question-panel"><div class="clue">${clue}</div></div><div class="choice-section"><div class="slot-group ${S.face==='question'?'active-slot':''}"><div class="slot-label">Blank 1</div><div class="choices">${options()}</div></div></div><div class="card-footer"><span>${S.face==='answer'?'0 / 1 correct':''}</span><button class="btn primary" data-sample-flip>${S.face==='answer'?'Continue':'Check answer'}</button></div></section>`}</div></main>`;
      }else{
        document.body.innerHTML=`<section id="cram-live"><header class="cl-header"><span class="cl-brand">ANKI CRAM</span><div class="cl-context"><div class="cl-deck">Sample deck</div><div class="cl-status">Anki reviews · Ratings update your schedule</div></div><button class="cl-exit" disabled>×</button></header><div id="cl-stage"><div id="cl-custom">${S.view==='flash'?`<section class="cl-flip cl-compiled-flash ${flipped}" tabindex="0" role="button" aria-label="Flip sample flashcard"><div class="cl-turn"><div class="cl-face cl-front"><div class="cl-flash-content">${clue}</div></div><div class="cl-face cl-back"><div class="cl-flash-content">${answer}</div></div></div></section>`:`<section class="cl-exam"><div class="cl-question-body"><div class="cl-question-panel"><div class="cl-clue">${clue}</div></div></div><div class="cl-answers"><div class="cl-slot ${S.face==='question'?'cl-active-slot':''}"><div class="cl-slot-label">Blank 1</div><div class="cl-choices">${options()}</div></div></div></section>${S.face==='answer'?'<div class="cl-feedback">0 / 1 correct</div>':''}`}</div></div></section><div class="sample-footer"><div id="middle">${S.face==='answer'?['Again','Hard','Good','Easy'].map((name,i)=>`<button data-ease="${i+1}">${name}</button>`).join(''):'<button id="ansbut" data-sample-flip>Show Answer</button>'}</div></div>`;
      }
      if(S.view==='write'){
        const card=frame(),host=$(S.mode==='anki'?'.cl-answers':'.choice-section'),clueNode=$(S.mode==='anki'?'.cl-clue':'.question-panel .clue');
        card.classList.add('write-card');
        const heading=card.querySelector('.card-heading span');if(heading)heading.textContent='Writing';
        const sample={kind:'basic',clue:'<b>Favorite fruits</b>',writing:{kind:'list',ordered:false,template:'The fruits are <span class="ct-blank" data-write-item="0" data-write-piece="0">\u00a0</span>, <span class="ct-blank" data-write-item="1" data-write-piece="0">\u00a0</span>, and <span class="ct-blank" data-write-item="2" data-write-piece="0">\u00a0</span>.',items:['banana','mango','lemon'].map(word=>({answer:word,parts:[word]}))}};
        clueNode.innerHTML=window.cramWriting.question(sample);
        const view={events:[],draft:'',target:0,state:{accepted:S.face==='answer'?[0,1,2]:[],remaining:S.face==='answer'?[]:[0,1,2],missed:[],complete:S.face==='answer',target:0,last:{status:'idle'}}};
        let ui;
        ui=window.cramWriting.mount(host,clueNode,sample,view,{revealed:S.face==='answer',autofocus:false,finish:flip,submit:entry=>{
          const i=sample.writing.items.findIndex(item=>item.answer===entry.text.trim().toLowerCase());
          const accepted=[...view.state.accepted];if(i>=0&&!accepted.includes(i))accepted.push(i);
          const remaining=[0,1,2].filter(i=>!accepted.includes(i));
          ui.receive({events:[...view.events,entry],state:{accepted,remaining,missed:[],complete:!remaining.length,target:remaining[0]||0,last:{status:i>=0?'correct':'wrong'}}});
        }});
        if(S.mode==='main')$('.card-footer').innerHTML='<button class="btn secondary" data-sample-flip>Reveal remaining</button><button class="btn primary" data-sample-flip>'+ (S.face==='answer'?'Continue':'Check answer')+'</button>';
        if(S.locator?.role.startsWith('incorrect')){
          host.querySelector('.write-root').classList.add('write-error');host.querySelector('.write-feedback').textContent='Not a match. Try again or reveal.';
        }
      }
      if(S.mode==='main'&&S.view==='flash'&&S.locator?.role==='primaryText')$('.flash-controls').innerHTML='<div class="feedback right">Correct</div><div class="flash-nav"><button class="btn secondary" data-sample-flip>Show clue</button></div><button class="btn primary" data-sample-flip>Continue</button>';
      const blank=$('[data-sample-blank]');if(blank&&S.view!=='flash'){
        const selected=S.pick??(S.face==='answer'?1:null);
        blank.classList.toggle('active',S.mode==='main'&&S.face==='question');blank.classList.toggle('cl-active',S.mode==='anki'&&S.face==='question');
        blank.classList.toggle('cl-revealed-answer',S.face==='answer'&&S.mode==='anki');
        const empty=S.face!=='answer'&&selected===null;
        blank.classList.toggle('cram-blank-empty',empty);blank.classList.toggle('filled',!empty);blank.classList.toggle('cl-filled',!empty);
        blank.classList.toggle('revealed-answer',S.face==='answer'&&S.mode==='main');
        blank.textContent=S.face==='answer'?'Tissue':empty?'\u00a0':choices[selected];
      }
      if(S.panel==='size'){
        frame()?.classList.add('cram-size-preview');
        for(const [axis,label,icon] of [['x','Resize width','↔'],['y','Resize height','↕'],['xy','Resize width and height','⋱']]){
          const handle=document.createElement('button');handle.className='preview-resize';handle.dataset.axis=axis;handle.setAttribute('data-axis',axis);handle.setAttribute('aria-label',label);handle.title=label;handle.textContent=icon;document.body.appendChild(handle);
        }
      }
      apply();requestAnimationFrame(()=>{place();placeLocator();});
    }
    const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    let locateTimer=null;
    function clearLocator(notify=true){
      const restore=S.locator?.role==='primaryText'&&S.view==='flash'&&!S.locator.exact;clearTimeout(locateTimer);S.locator=null;$('#preview-locator')?.remove();
      if(restore)render();if(notify)post({type:'cram-preview-locate-done'});
    }
    function locatorSpec(role=S.locator?.role){
      const anki=S.mode==='anki',flash=S.view==='flash';if(!role)return null;
      const face=anki?(S.face==='answer'?'.cl-back':'.cl-front'):(S.face==='answer'?'.flash-back':'.flash-face');
      const spec=(element,property,kind)=>element?{element,property,kind}:null;
      const choice=(state='')=>all(anki?'.cl-choice':'.choice').find(el=>state?el.classList.contains(state):!['selected','correct','incorrect','right','wrong'].some(name=>el.classList.contains(name)));
      const choiceSpec=(el,text)=>spec(text?(el?.querySelector(anki?'.cl-choice-text':'.choice-text')||el):el,text?'color':'background-color',text?'text':'choice-surface');
      if(S.view==='write'){
        if(role.startsWith('correct'))return null;
        if(role==='buttonBackground'||role==='buttonText')return spec($('.write-enter'),role==='buttonText'?'color':'background-color',role==='buttonText'?'text':'choice-surface');
        if(role.startsWith('correct')||role.startsWith('incorrect'))return spec($('.write-feedback'),role.endsWith('Background')?'background-color':'color',role.endsWith('Background')?'choice-surface':'text');
        if(role.startsWith('reveal'))return spec($(anki?'#ansbut':'.write-card .secondary'),role==='revealText'?'color':'background-color',role==='revealText'?'text':'choice-surface');
      }
      if(role==='background')return spec(anki?document.body:root(),'background-color','page');
      if(role==='card'||role==='border')return spec(flash?$(face):$(anki?'.cl-exam':'.exam-card'),role==='border'?'border-top-color':'background-color',role==='border'?'border':'surface');
      if(role==='text'){
        const container=flash?$(face+(anki?' .cl-flash-content':' .face-content')):$(anki?'.cl-clue':'.question-panel .clue');
        return spec(container?.querySelector('b')||container,'color','text');
      }
      if(role==='question')return spec($(anki?'.cl-question-panel':'.question-panel'),'background-color','surface');
      if(role==='accent')return spec($(anki?'.cl-brand':flash?'.progress-fill':'.primary'),anki?'color':'background-color',anki?'text':flash?'highlight':'choice-surface');
      if(role==='answerText'||role==='answerBackground')return spec($(anki?'.cl-revealed-answer':'.revealed-answer'),role==='answerText'?'color':'background-color',role==='answerText'?'text':'highlight');
      if(role.startsWith('reveal'))return spec($(anki?'#ansbut':'.flash-controls [data-sample-flip]'),role==='revealText'?'color':'background-color',role==='revealText'?'text':'choice-surface');
      if(role==='primaryText')return spec($('.primary'),'color','text');
      if(role.startsWith('correct')||role.startsWith('incorrect')){
        const wrong=role.startsWith('incorrect'),text=!role.endsWith('Background');
        return flash?spec($(wrong?'.btn.bad':'.btn.good'),text?'color':'background-color',text?'text':'choice-surface'):choiceSpec(choice(anki?(wrong?'incorrect':'correct'):(wrong?'wrong':'right')),text);
      }
      if(role.startsWith('selection'))return choiceSpec(choice('selected'),role==='selectionText');
      if(role.startsWith('button')){
        const text=role==='buttonText';
        if(anki&&flash)return spec(all('.sample-footer #middle button')[1],text?'color':'background-color',text?'text':'choice-surface');
        return choiceSpec(choice(),text);
      }
      return null;
    }
    function computedHex(element,property){
      if(typeof getComputedStyle!=='function')return null;
      const style=getComputedStyle(element),value=style.getPropertyValue?.(property)||style[property.replace(/-([a-z])/g,(_,c)=>c.toUpperCase())];
      if(!value)return null;if(/^#[a-f0-9]{6}$/i.test(value))return value.toLowerCase();
      const rgb=value.match(/^rgba?\(\s*(\d+)[, ]+\s*(\d+)[, ]+\s*(\d+)(?:\s*[,/]\s*([.\d]+))?\s*\)$/i);
      if(!rgb)return value;return !rgb[4]||Number(rgb[4])===1?'#'+rgb.slice(1,4).map(n=>Number(n).toString(16).padStart(2,'0')).join(''):'transparent';
    }
    function locatorRect(spec){
      let r=spec.element.getBoundingClientRect();const w=window.innerWidth||1360,h=window.innerHeight||900;
      if(spec.kind==='text'&&typeof document.createRange==='function'){
        const range=document.createRange();range.selectNodeContents(spec.element);const text=range.getBoundingClientRect();if(text.width&&text.height)r=text;range.detach?.();
      }
      if(spec.kind==='page'){
        const card=frame()||$(S.mode==='anki'?'.cl-exam':'.exam-card'),cr=card?.getBoundingClientRect();
        return {left:Math.max(8,Math.min(w-32,(cr?.left||36)/2-8)),top:Math.max(90,Math.min(h-160,(cr?.top||120)+80)),width:16,height:42};
      }
      if(spec.kind==='border')return {left:r.left+r.width/2-24,top:r.top,width:48,height:1};
      if(spec.kind==='surface')return {left:r.right-32,top:r.top+14,width:17,height:17};
      if(spec.kind==='choice-surface')return {left:r.right-13,top:r.top+Math.max(0,(r.height-8)/2),width:7,height:Math.min(8,r.height)};
      return r;
    }
    function placeLocator(){
      $('#preview-locator')?.remove();if(!S.locator)return;
      const spec=S.locator.exact?.element?.isConnected?S.locator.exact:locatorSpec();
      if(!spec){const notice=document.createElement('div');notice.id='preview-locator';notice.setAttribute('role','status');notice.dataset.colorRole=S.locator.role;notice.innerHTML=`<div class="preview-locate-label" style="left:20px;top:100px"><span><strong>${escape(S.locator.label)}</strong><small>No separate component uses this setting in this preview.</small></span><button data-close-locator aria-label="Close color locator">×</button></div>`;document.body.appendChild(notice);return;}
      const expected=A.palette(S.config,S.mode,S.theme,S.view)[S.locator.role];let actual=computedHex(spec.element,spec.property);
      const mismatch=actual&&actual!==expected,w=window.innerWidth||1360,h=window.innerHeight||900,r=locatorRect(spec);
      const left=Math.max(5,r.left-4),top=Math.max(5,r.top-4),width=Math.max(4,Math.min(w-left-5,r.width+8)),height=Math.max(4,Math.min(h-top-5,r.height+8));
      const labelX=Math.max(12,Math.min(w-340,left+width+22)),labelY=Math.max(12,Math.min(h-110,top>110?top-94:top+height+20)),anchorX=left+width/2,anchorY=top+height/2;
      const overlay=document.createElement('div');overlay.id='preview-locator';overlay.setAttribute('role','status');overlay.dataset.colorRole=S.locator.role;overlay.dataset.colorProperty=spec.property;overlay.dataset.colorTarget=spec.element.className||spec.element.id||spec.element.tagName;
      overlay.dataset.settingColor=expected;overlay.dataset.shownColor=actual||'';
      const imageBase=S.locator.role==='background'&&spec.kind==='page'&&S.config.images?.background||S.locator.role==='card'&&spec.kind==='surface'&&S.config.images?.card;
      const type=spec.property==='color'?'Text':spec.property==='border-top-color'?'Border':imageBase?'Base under image':'Background';
      const pointer=`<div class="preview-locate-ring" style="left:${left}px;top:${top}px;width:${width}px;height:${height}px"></div><svg class="preview-locate-arrow" viewBox="0 0 ${w} ${h}" aria-hidden="true"><path d="M${labelX+16} ${labelY+26} L${anchorX} ${anchorY}"/><circle cx="${anchorX}" cy="${anchorY}" r="4"/></svg>`;
      // The binding identifies the control. Default/inherited styling can differ from
      // its editable palette value; report both instead of dropping the pointer.
      overlay.innerHTML=pointer+`<div class="preview-locate-label" style="left:${labelX}px;top:${labelY}px"><span><strong>${escape(S.locator.label)}</strong><small><i style="background:${expected}"></i>Setting: ${expected} · ${type}</small>${mismatch?`<small>Shown: ${escape(actual)} · current style</small>`:''}</span><button data-close-locator aria-label="Close color locator">×</button></div>`;document.body.appendChild(overlay);
    }
    function locate(request){
      if(!request||!A.roles.includes(request.role))return;
      clearTimeout(locateTimer);S.locator={role:request.role,label:String(request.label||request.role).slice(0,90)};S.lastLocate=request.id;
      dismissInspector();
      if(S.mode==='main'&&(S.view==='exam'&&(['answerText','answerBackground'].includes(request.role)||request.role.startsWith('reveal'))||S.view==='flash'&&request.role.startsWith('button'))){S.mode='anki';S.locator.label+=' · ANKI CRAM';}
      if(['answerText','answerBackground','primaryText'].includes(request.role)||request.role.startsWith('correct')||request.role.startsWith('incorrect')||S.mode==='anki'&&S.view==='flash'&&request.role.startsWith('button'))S.face='answer';
      else if(['text','question'].includes(request.role)||request.role.startsWith('reveal')||request.role.startsWith('selection'))S.face='question';
      if(request.role.startsWith('selection')||request.role.startsWith('correct')||request.role.startsWith('incorrect'))S.pick=1;
      render();post({type:'cram-preview-context',face:S.face,mode:S.mode,view:S.view});locateTimer=setTimeout(()=>clearLocator(),7000);
    }
    function dismissInspector(){
      $('#preview-inspect-menu')?.remove();$('#preview-inspect-ring')?.remove();S.inspectItems=[];
    }
    function inspectorCandidates(target){
      const items=[],anki=S.mode==='anki',label=role=>S.colorLabels[role]||role;
      const allowed=role=>A.roles.includes(role)&&(!Object.keys(S.colorLabels).length||Object.prototype.hasOwnProperty.call(S.colorLabels,role));
      const add=(role,part,element,property,kind)=>{if(element&&allowed(role))items.push({role,label:label(role),part,spec:{element,property,kind}});};
      const use=(role,part)=>{const spec=locatorSpec(role);if(spec)add(role,part,spec.element,spec.property,spec.kind);};
      const targetElement=target?.nodeType===3?target.parentElement:target;if(!targetElement?.closest)return {items,title:'Preview',note:'',element:root()};
      const input=targetElement.closest('.write-input,.write-enter,.write-feedback');
      if(input){
        if(input.classList.contains('write-feedback')){
          if(input.closest('.write-error')){add('incorrect','Feedback text',input,'color','text');add('incorrectBackground','Feedback background',input,'background-color','choice-surface');}
        }else {add('buttonText','Input / button text',input,'color','text');add('buttonBackground','Input / button background',input,'background-color','choice-surface');add('border','Border',input,'border-top-color','border');}
        return {items,title:'Writing response',element:input,note:''};
      }
      const choice=targetElement.closest('[data-sample-choice]');
      if(choice){
        const correct=choice.classList.contains(anki?'correct':'right'),wrong=choice.classList.contains(anki?'incorrect':'wrong'),selected=choice.classList.contains('selected');
        const color=correct?'correct':wrong?'incorrect':selected?'selectionText':'buttonText',surface=correct?'correctBackground':wrong?'incorrectBackground':selected?'selection':'buttonBackground';
        const badge=targetElement.closest(anki?'.cl-key':'.choice-key');
        if(badge&&selected){add('accent','Letter text',badge,'color','text');add('card','Letter circle',badge,'background-color','highlight');}
        add(color,'Choice text',choice.querySelector(anki?'.cl-choice-text':'.choice-text'),'color','text');
        add(surface,'Choice background',choice,'background-color','choice-surface');
        add(correct?'correct':wrong?'incorrect':selected?'accent':'border','Choice border',choice,'border-top-color','border');
        return {items,title:badge?'Letter circle and choice':'Answer choice',element:badge||choice,note:badge&&!selected?'The letter circle uses automatic shades, with no separate color setting. These controls change the surrounding choice.':''};
      }
      const button=targetElement.closest('button');
      if(button){
        if(button.closest('.sample-footer')){
          const reveal=button.id==='ansbut';add(reveal?'revealText':'buttonText','Button text',button,'color','text');add(reveal?'revealBackground':'buttonBackground','Button background',button,'background-color','choice-surface');
          return {items,title:reveal?'Show Answer':'Anki rating button',element:button,note:'Rating labels and intervals stay controlled by Anki.'};
        }
        const primary=button.classList.contains('primary'),good=button.classList.contains('good'),bad=button.classList.contains('bad'),reveal=button.hasAttribute?button.hasAttribute('data-sample-flip')&&!primary:button.getAttribute('data-sample-flip')!==null&&!primary;
        if(primary||good||bad||reveal){
          add(primary?'primaryText':good?'correct':bad?'incorrect':'revealText','Button text',button,'color','text');
          add(primary?'accent':good?'correctBackground':bad?'incorrectBackground':'revealBackground','Button background',button,'background-color','choice-surface');
          if(reveal||good||bad)add(good?'correct':bad?'incorrect':'border','Button border',button,'border-top-color','border');
          return {items,title:'Study button',element:button,note:''};
        }
      }
      const card=targetElement.closest('.flash-card,.cl-flip,.exam-card,.cl-exam'),panel=targetElement.closest('.question-panel,.cl-question-panel');
      if(card){
        const answer=targetElement.closest('.revealed-answer,.cl-revealed-answer'),blank=targetElement.closest('.ct-blank'),label=targetElement.closest('.slot-label,.cl-slot-label'),mutedLabel=targetElement.closest('.card-heading')||label&&!label.closest('.active-slot,.cl-active-slot');
        if(answer){add('answerText','Answer text',answer,'color','text');add('answerBackground','Answer highlight',answer,'background-color','highlight');}
        else if(blank)add('accent','Blank text',blank,'color','text');
        else if(label&&!mutedLabel)add('accent','Active blank label',label,'color','text');
        else {
          const text=targetElement.closest('.face-content,.cl-flash-content,.cl-clue,.question-panel .clue');
          if(text)add('text','Card text',targetElement.closest('b,strong')||text,'color','text');
        }
        if(panel)add('question','Question panel background',panel,'background-color','surface');
        use('card','Card background');use('border','Card border');
        return {items,title:answer?'Revealed cloze answer':blank?'Cloze blank':panel?'Question panel':'Flashcard',element:answer||blank||panel||locatorSpec('card')?.element||card,
          note:mutedLabel?'This label uses an automatic muted shade, with no separate color setting.':blank&&!answer&&S.view!=='flash'?'The active blank shade is derived from Accent and Question panel.':S.config.images?.card?'Card background is the base color underneath your image.':''};
      }
      if(targetElement.closest('.progress-fill,.cl-brand'))use('accent','Accent');
      use('background','Page background');
      return {items,title:'Page and interface',element:targetElement,note:targetElement.closest('.session-header,.cl-header,.cl-feedback')?'These labels share theme styles and automatic shades, with no separate color setting.':''};
    }
    function hoverInspector(target){
      if(!S.inspect||$('#preview-inspect-menu')||target?.closest?.('#preview-locator,#preview-inspect-menu'))return;
      const found=inspectorCandidates(target),element=found.element;if(!element)return;
      const r=element.getBoundingClientRect(),w=window.innerWidth||1360,h=window.innerHeight||900;
      // Intersect all four edges with the visible iframe before drawing. Page
      // containers may extend below it; clamping only left/top clips the rest.
      const left=Math.max(5,r.left-3),top=Math.max(5,r.top-3),right=Math.min(w-5,r.right+3),bottom=Math.min(h-5,r.bottom+3);
      if(right<=left||bottom<=top){$('#preview-inspect-ring')?.remove();return;}
      const ring=$('#preview-inspect-ring')||document.createElement('div');ring.id='preview-inspect-ring';
      ring.style.left=left+'px';ring.style.top=top+'px';ring.style.width=(right-left)+'px';ring.style.height=(bottom-top)+'px';if(!ring.isConnected)document.body.appendChild(ring);
    }
    function inspect(target,x=window.innerWidth/2,y=window.innerHeight/2){
      clearLocator(false);dismissInspector();const found=inspectorCandidates(target);S.inspectItems=found.items;
      const colors=A.palette(S.config,S.mode,S.theme,S.view),menu=document.createElement('div');menu.id='preview-inspect-menu';menu.setAttribute('role','dialog');menu.setAttribute('aria-label','Choose a color setting');
      menu.innerHTML=`<header><strong>${escape(found.title)}</strong><button data-close-inspector aria-label="Close component picker">×</button></header>${found.note?`<small>${escape(found.note)}</small>`:''}${found.items.length?'':'<small>No separate color setting for this component.</small>'}${found.items.map((item,index)=>{
        const shown=computedHex(item.spec.element,item.spec.property),value=shown&&/^#[a-f0-9]{6}$/i.test(shown)?shown:colors[item.role];
        return `<button data-inspect-index="${index}" data-inspect-role="${item.role}"><i style="background:${value}"></i><span><strong>${escape(item.part)}</strong><small>${escape(item.label)} · <code>${escape(shown||colors[item.role])}</code></small></span></button>`;
      }).join('')}`;document.body.appendChild(menu);
      const r=menu.getBoundingClientRect(),w=window.innerWidth||1360,h=window.innerHeight||900;
      menu.style.left=Math.max(12,Math.min(w-r.width-12,x+12))+'px';menu.style.top=Math.max(12,Math.min(h-r.height-12,y+12))+'px';
      menu.querySelector('button[data-inspect-index]')?.focus({preventScroll:true});
    }
    function chooseInspected(index){
      const item=S.inspectItems[index];if(!item)return;
      dismissInspector();S.locator={role:item.role,label:item.label,exact:item.spec};placeLocator();
      post({type:'cram-preview-picked',role:item.role,property:item.spec.property,mode:S.mode,view:S.view,theme:S.theme,face:S.face});
    }
    function place(){
      const card=frame();if(S.panel!=='size'||!card)return;
      const r=card.getBoundingClientRect();all('.preview-resize').forEach(handle=>{
        const axis=handle.dataset.axis;handle.style.left=(axis==='y'?r.left+r.width/2:r.right)-14+'px';handle.style.top=(axis==='x'?r.top+r.height/2:r.bottom)-14+'px';
      });
    }
    function flip(){if(S.inspect)return;S.face=S.face==='answer'?'question':'answer';render();post({type:'cram-preview-face',face:S.face});}
    document.addEventListener('click',e=>{
      if(e.target.closest('[data-close-locator]')){clearLocator();return;}
      const item=e.target.closest('[data-inspect-index]');if(item){e.preventDefault();chooseInspected(Number(item.dataset.inspectIndex));return;}
      if(e.target.closest('[data-close-inspector]')){dismissInspector();return;}
      if(e.target.closest('#preview-inspect-menu'))return;
      if(S.inspect){e.preventDefault();e.stopPropagation();inspect(e.target,e.clientX,e.clientY);return;}
      if(e.target.closest('.preview-resize'))return;
      const choice=e.target.closest('[data-sample-choice]');if(choice&&S.face==='question'){S.pick=Number(choice.dataset.sampleChoice);render();return;}
      const card=e.target.closest('.flash-card,.cl-flip');
      if(e.target.closest('[data-sample-flip]')||S.view==='flash'&&card&&flashPointer.canFlip(e,card))flip();
    });
    document.addEventListener('keydown',e=>{if(/INPUT|TEXTAREA|SELECT/.test(e.target?.tagName||'')&&!S.inspect)return;if(e.key==='Escape'&&S.inspect){e.preventDefault();S.inspect=false;clearLocator(false);dismissInspector();document.body.classList.remove('cram-inspecting');post({type:'cram-preview-inspect-done'});return;}if(e.key==='Escape'&&S.locator){e.preventDefault();clearLocator();return;}if(S.inspect)return;if(e.code==='Space'&&!e.repeat&&!e.ctrlKey&&!e.metaKey){e.preventDefault();flip();}});
    document.addEventListener('pointermove',e=>{if(S.inspect)hoverInspector(e.target);});
    const clearHover=()=>$('#preview-inspect-ring')?.remove();
    document.documentElement.addEventListener('pointerleave',clearHover);
    document.addEventListener('pointerout',e=>{if(!e.relatedTarget)clearHover();});
    window.addEventListener('blur',clearHover);
    let drag=null;
    document.addEventListener('pointerdown',e=>{
      const handle=e.target.closest('.preview-resize');if(!handle||S.panel!=='size')return;
      e.preventDefault();e.stopPropagation();const size=S.config[S.view!=='flash'?'examSize':'size'],g=A.sizeGeometry(size,S.mode,S.view);
      drag={x:e.clientX,y:e.clientY,axis:handle.dataset.axis,start:{width:g.width,height:g.height},viewport:{width:g.areaWidth,height:g.sceneHeight},handle,id:e.pointerId};
      handle.setPointerCapture(e.pointerId);
    });
    document.addEventListener('pointermove',e=>{
      if(!drag||e.pointerId!==drag.id)return;e.preventDefault();
      const next=A.resize(drag.start,e.clientX-drag.x,e.clientY-drag.y,drag.axis,drag.viewport);
      const key=S.view!=='flash'?'examSize':'size';
      if(drag.axis.includes('x'))S.config[key].width=next.width;if(drag.axis.includes('y'))S.config[key].height=next.height;
      apply();post({type:'cram-preview-resize',view:S.view,size:S.config[key]});
    });
    const release=e=>{if(drag&&e.pointerId===drag.id){const d=drag;drag=null;if(d.handle.hasPointerCapture(d.id))d.handle.releasePointerCapture(d.id);}};
    document.addEventListener('pointerup',release);document.addEventListener('pointercancel',release);document.addEventListener('lostpointercapture',()=>{drag=null;});
    window.addEventListener('resize',()=>{clearHover();place();placeLocator();});
    window.addEventListener('message',e=>{
      if(e.source!==window.parent||e.data?.type!=='cram-preview-config')return;
      const p=e.data,key=[S.mode,S.theme,S.view,S.face,S.panel].join('|');
      S.config=A.normalize(p.config);S.mode=p.mode==='anki'?'anki':'main';S.theme=p.theme==='dark'?'dark':'light';S.view=['exam','write'].includes(p.view)?p.view:'flash';S.face=p.face==='answer'?'answer':'question';S.panel=['colors','images'].includes(p.panel)?p.panel:'size';
      S.inspect=p.inspect===true&&S.panel==='colors';S.colorLabels=Object.fromEntries(A.roles.filter(role=>typeof p.colorLabels?.[role]==='string').map(role=>[role,p.colorLabels[role].slice(0,90)]));
      if(key!==[S.mode,S.theme,S.view,S.face,S.panel].join('|')){dismissInspector();if(S.locator?.exact)clearLocator(false);}
      if(p.locate&&p.locate.id!==S.lastLocate){locate(p.locate);return;}
      if(!p.locate&&S.locator&&(!S.locator.exact||!S.inspect))clearLocator(false);
      if(key!==[S.mode,S.theme,S.view,S.face,S.panel].join('|')||!root())render();else {apply();placeLocator();}
    });
    post({type:'cram-preview-ready'});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
