/* One overview button. Never wrap, restyle or move another control. */
(()=>{
  if(window.cramEntryMount)return;
  let observer=null,queued=false,lastControls=null;
  const visual=['background-color','background-image','color','border-top-width','border-right-width','border-bottom-width','border-left-width','border-top-style','border-right-style','border-bottom-style','border-left-style','border-top-color','border-right-color','border-bottom-color','border-left-color','border-top-left-radius','border-top-right-radius','border-bottom-left-radius','border-bottom-right-radius','padding-top','padding-right','padding-bottom','padding-left','font-family','font-size','font-weight','font-style','line-height','letter-spacing','text-transform','box-shadow','box-sizing','min-height'];
  const stable='display:inline-flex!important;align-items:center!important;justify-content:center!important;align-self:stretch!important;vertical-align:middle!important;height:auto!important;white-space:nowrap!important;flex:0 0 auto!important;width:auto!important;max-width:none!important;transform:none!important;translate:none!important;scale:none!important;animation:none!important;transition:none!important;';
  function match(button,reference){
    const cls=reference.className||'';
    if(button.className!==cls)button.className=cls;
    // ID/structural selectors in themes need not apply to our new button.
    // Snapshot the actual native shape, not Anki's unrelated default pill.
    if(reference.matches(':hover,:active')&&button.hasAttribute('style'))return;
    const cs=getComputedStyle(reference),style=visual.map(p=>p+':'+cs.getPropertyValue(p)+'!important;').join('')+stable;
    if(button.getAttribute('style')!==style)button.setAttribute('style',style);
  }
  function visible(el){return el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden';}
  function place(){
    queued=false;if(!document.body)return;
    document.getElementById('cram-entry-buttons')?.remove();document.getElementById('cram-entry-style')?.remove();
    let ours=document.getElementById('cram-anki-overview');
    const controls=[...document.querySelectorAll('button,a,input[type=button]')].filter(el=>el!==ours&&visible(el));
    const label=el=>(el.textContent||el.value||'').trim();
    const reference=controls.find(el=>/^Description$/i.test(label(el)))||controls.find(el=>/^Empty$/i.test(label(el)))||controls.find(el=>/^Options$/i.test(label(el)));
    const duplicate=!!reference&&controls.some(el=>/^Options$/i.test(label(el)));
    if(lastControls!==duplicate&&typeof pycmd==='function'){lastControls=duplicate;pycmd('cram_overview_controls:'+(duplicate?'1':'0'));}
    if(!reference)return;
    if(!ours){
      ours=document.createElement('button');ours.id='cram-anki-overview';ours.type='button';ours.textContent='ANKI CRAM';ours.title='Study using Anki’s schedule';
      ours.addEventListener('click',()=>{if(typeof pycmd==='function')pycmd('cram_live_open');});
    }
    match(ours,reference);
    // Study List owns the place directly after the native control. Respect it
    // instead of both observers moving their buttons there every 150 ms.
    const study=document.getElementById('studylist_overview_button');
    const anchor=study&&study.parentElement===reference.parentElement?study:reference;
    if(anchor.nextElementSibling!==ours)anchor.insertAdjacentElement('afterend',ours);
  }
  window.cramEntryMount=()=>{
    place();
    if(!observer&&typeof MutationObserver==='function'){
      observer=new MutationObserver(()=>{if(!queued){queued=true;requestAnimationFrame(place);}});
      observer.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','style','hidden']});
    }
  };
})();
