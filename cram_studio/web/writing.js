/* Writing controls shared by MAIN, native reviewer and appearance previews.
   Matching is performed by the Python controller. No scheduler/grade calls here. */
(()=>{
  'use strict';
  const escape=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function question(q){return q.kind==='cloze'?q.writing.template:q.clue+'<div class="write-targets">'+q.writing.template+'</div>';}
  function mount(host,clue,q,view,options={}){
    const plan=q.writing,items=plan.items;
    view.events??=[];view.draft??='';view.target??=0;
    view.state??={accepted:[],remaining:items.map((_,i)=>i),missed:[],target:0,complete:false,last:{status:'idle'}};
    host.innerHTML='<div class="write-root"><div class="write-progress" aria-live="polite"></div><div class="write-entry-row"><textarea class="write-input" rows="1" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" aria-label="Written answer"></textarea><button type="button" class="write-enter">Enter answer</button></div><div class="write-feedback" role="status" aria-live="polite"></div></div>';
    const input=host.querySelector('.write-input'),enter=host.querySelector('.write-enter'),progress=host.querySelector('.write-progress'),feedback=host.querySelector('.write-feedback'),root=host.querySelector('.write-root');
    clue.classList.toggle('write-cloze',q.kind==='cloze');
    input.value=view.draft;
    let pending=false,reviewMiss=null;
    const checking=!!(options.review||options.practice);
    function canReveal(){return checking&&reviewMiss&&reviewMiss.text===input.value&&reviewMiss.target===view.target;}
    function actionLabel(){if(checking)enter.textContent=canReveal()?'Reveal answer':'Check answer';}
    function changed(){options.changed?.(view);}
    function fitInput(){
      if(!Number.isFinite(input.scrollHeight))return;
      const scroll=input.scrollTop;input.style.height='auto';input.style.height=(input.scrollHeight+4)+'px';input.scrollTop=scroll;
    }
    function showTarget(i=view.anchor??view.target){
      if(!Number.isInteger(i)||!items[i])return;
      view.anchor=i;
      const show=()=>{
        if(!clue.isConnected)return;
        const target=clue.querySelector(`[data-write-item="${view.anchor}"]`);
        if(target)window.cramAppearance?.showInPane(target,clue.closest('.question-panel,.cl-question-panel')||clue);
      };
      show();
      // Native reveal remounts the card before its saved sizing/text zoom is
      // reapplied. Check again after that layout, without scrolling the page.
      if(typeof requestAnimationFrame==='function')requestAnimationFrame(show);
    }
    function fill(reveal=false){
      if(reveal)options.revealed=true;
      const accepted=new Set(view.state.accepted),all=reveal||options.revealed;
      clue.querySelectorAll('[data-write-item]').forEach(node=>{
        const i=Number(node.dataset.writeItem),part=Number(node.dataset.writePiece||0),item=items[i];if(!item)return;
        const show=all||accepted.has(i),first=part===0;
        node.hidden=!first&&!show;
        node.classList.toggle('cram-blank-empty',!show&&first);node.classList.toggle('filled',!!show);node.classList.toggle('cl-filled',!!show);
        node.classList.toggle('active',!all&&!accepted.has(i)&&view.target===i);node.classList.toggle('cl-active',!all&&!accepted.has(i)&&view.target===i);
        node.classList.toggle('revealed-answer',!!show);node.classList.toggle('cl-revealed-answer',!!show);
        if(show){if(item.html&&first)node.innerHTML=item.html;else node.textContent=item.parts[part]??item.answer;}
        else node.textContent=first?'\u00a0':'';
      });
      progress.textContent=checking&&all?`${items.length} / ${items.length} revealed`:`${accepted.size} / ${items.length}`;
      const done=view.state.complete||options.revealed;
      input.readOnly=!!done;enter.disabled=!!done||pending;input.disabled=pending;
      input.setAttribute('aria-label',`Written answer ${Math.min(items.length,view.target+1)} of ${items.length}`);
      const status=view.state.last?.status;
      actionLabel();
      const failed=['wrong','incomplete'].includes(status)&&!pending&&!done;
      root.classList.toggle('write-error',failed);
      feedback.textContent=!options.revealed&&failed?(status==='incomplete'?'Answer incomplete. Add the missing part or reveal.':'Not a match. Try again or reveal.'):'';
      options.complete?.(!!done);
      if(reveal)showTarget();
    }
    function focus(){if(!options.revealed&&!view.state.complete){input.focus({preventScroll:true});options.focus?.(true);}}
    function select(i){
      const remaining=view.state.remaining||[];if(!remaining.length)return;
      if(!remaining.includes(i))i=remaining[0];
      reviewMiss=null;view.target=i;fill();focus();changed();
      showTarget(i);
    }
    function move(delta){const r=view.state.remaining||[];if(!r.length)return;const i=Math.max(0,r.indexOf(view.target));select(r[(i+delta+r.length)%r.length]);}
    function submit(){
      if(pending||options.revealed)return;
      view.anchor=view.target;
      if(view.state.complete){options.finish?.();return;}
      if(canReveal()){input.blur?.();options.focus?.(false);options.finish?.();return;}
      view.draft=input.value;if(!view.draft.trim()){
        if(checking){input.blur?.();options.focus?.(false);options.finish?.();}
        return;
      }
      pending=true;fill();changed();
      options.submit?.({text:view.draft,target:view.target,events:view.events});
    }
    function receive(data){
      const checked=pending,previous=new Set(view.state.accepted),target=view.target;
      pending=false;view.events=data.events;view.state=data.state;
      const added=view.state.accepted.filter(i=>!previous.has(i));
      if(added.length)view.anchor=added.includes(target)?target:added[0];
      if(data.state.last.status==='correct'){view.draft='';input.value='';view.target=data.state.target;fitInput();}
      fill();changed();
      // A final match finishes checking. A miss stays editable;
      // another Enter without editing explicitly chooses to reveal instead.
      if(checked&&checking&&view.state.last.status!=='correct'){
        reviewMiss={text:input.value,target:view.target};actionLabel();
      }else if(checked)reviewMiss=null;
      if(checked&&checking&&view.state.complete){
        input.blur?.();options.focus?.(false);showTarget();options.finish?.();return;
      }
      if(view.state.complete){input.blur?.();options.focus?.(false);options.finishedInput?.();}
      else focus();
      if(checked||added.length)showTarget();
    }
    input.addEventListener('input',()=>{reviewMiss=null;view.draft=input.value;fitInput();actionLabel();changed();});
    input.addEventListener('focus',()=>options.focus?.(true));input.addEventListener('blur',()=>{view.draft=input.value;options.focus?.(false);changed();});
    input.addEventListener('keydown',event=>{
      if(event.isComposing||event.keyCode===229)return;
      if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();event.stopPropagation();if(!event.repeat)submit();}
      else if(event.altKey&&['ArrowUp','ArrowDown'].includes(event.key)){event.preventDefault();event.stopPropagation();if(!event.repeat)move(event.key==='ArrowUp'?-1:1);}
      else if(event.key==='Escape'){event.preventDefault();event.stopPropagation();input.blur?.();options.focus?.(false);}
    });
    enter.addEventListener('click',submit);
    clue.addEventListener('click',event=>{const n=event.target.closest?.('[data-write-item]');if(n)select(Number(n.dataset.writeItem));});
    fill();if(options.autofocus!==false)focus();
    fitInput();if(typeof requestAnimationFrame==='function')requestAnimationFrame(()=>{if(input.isConnected)fitInput();});
    if(options.revealed||Number.isInteger(view.anchor))showTarget();
    clue.addEventListener('load',()=>{if(Number.isInteger(view.anchor))showTarget();},true);
    return {view,receive,select,move,submit,fill,focus,input,failure:message=>{pending=false;fill();feedback.textContent=message;focus();}};
  }
  window.cramWriting={question,mount};
})();
