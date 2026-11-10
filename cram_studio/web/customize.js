(()=>{
  'use strict';
  function init(){
    const root=document.getElementById('cram-customize');if(!root)return;
    const A=window.cramAppearance,S={config:A.normalize({}),mode:'main',theme:'light',view:'flash',face:'question',panel:'size',assets:'',ready:false,locator:null,locateSerial:0,imagePending:false,inspect:false,selectedColor:null};
    const $=s=>root.querySelector(s),esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const profileView=()=>S.view==='write'?'exam':S.view;
    const owns=(object,key)=>Object.prototype.hasOwnProperty.call(object,key);
    const labels={background:'Page background',card:'Card',text:'Card text',accent:'Accent / primary button',border:'Borders',selection:'Selected background',selectionText:'Selected text',correct:'Correct choice text',correctBackground:'Correct choice background',incorrect:'Wrong choice text',incorrectBackground:'Wrong choice background',question:'Question panel',buttonBackground:'Button background',buttonText:'Button text',revealBackground:'Reveal / Show clue background',revealText:'Reveal / Show clue text',primaryText:'Primary button text',answerText:'Revealed answer text',answerBackground:'Cloze answer highlight'};
    const send=(action,data={})=>{if(typeof pycmd==='function')pycmd('cram_custom:'+JSON.stringify({action,...data}));};
    function message(){const frame=$('iframe');if(frame?.contentWindow)frame.contentWindow.postMessage({type:'cram-preview-config',config:S.config,mode:S.mode,theme:S.theme,view:S.view,face:S.face,panel:S.panel,locate:S.locator,inspect:S.inspect&&S.panel==='colors',colorLabels:Object.fromEntries([...root.querySelectorAll('[data-locate-color]')].map(el=>[el.dataset.locateColor,el.textContent]))},'*');}
    function fit(){const frame=$('iframe'),clip=$('.cu-preview');if(!frame||!clip)return;const scale=Math.max(.15,Math.min(clip.clientWidth/1360,clip.clientHeight/900));frame.style.width='1360px';frame.style.height='900px';frame.style.transform=`translate(-50%,-50%) scale(${scale})`;}
    function scheme(custom){return !Object.keys(custom).length?'default':custom.auto&&Object.keys(custom).every(key=>['auto','card','harmony'].includes(key))?'auto':'custom';}
    function harmonyFields(custom,p){
      const selected=custom.harmony||'current',choice=A.harmonies.find(item=>item.id===selected)||A.harmonies[0];
      const colors=A.harmonyColors(p.card,A.luminance(p.card)<.2,A.defaults[S.mode][S.theme].accent,selected);
      return `<label class="cu-field"><span>Color harmony</span><select id="harmony" ${custom.auto?'':'disabled'} title="Choose Automatic from card to use a harmony">${A.harmonies.map(item=>`<option value="${item.id}" ${item.id===selected?'selected':''}>${item.label}</option>`).join('')}</select></label><div class="cu-harmony-hues" aria-label="Generated harmony hues" title="Generated hues; manual color overrides stay fixed.">${colors.hues.map(color=>`<span style="background:${color}" title="${color}" aria-label="${color}"></span>`).join('')}</div><small class="cu-harmony-note">${custom.auto?choice.description:'Choose Automatic from card to use a harmony.'}${custom.auto&&colors.neutral&&selected!=='monochromatic'?' Neutral cards use the existing accent as a hue anchor.':''}</small>`;
    }
    function updateHarmonyFields(){const host=$('#cu-harmony');if(host){const custom=S.config.colors[S.theme][profileView()];host.innerHTML=harmonyFields(custom,A.palette(S.config,S.mode,S.theme,S.view));}}
    function colorFields(custom,p){
      const groups=[['Card and page',['card','background','text','accent','border',...(S.view!=='flash'?['question']:[])]],['Revealed answer',['answerText','answerBackground']],['Buttons',['buttonBackground','buttonText',...(S.mode==='main'?['primaryText']:[]),...(S.view==='flash'||S.view==='write'||S.mode==='anki'?['revealBackground','revealText']:[])]],...(S.view!=='flash'||S.mode==='main'?[['Answer feedback',[...(S.view==='write'?[]:['correct','correctBackground']),'incorrect','incorrectBackground',...(S.view==='exam'?['selection','selectionText']:[])]]]:[])];
      return groups.map(([title,roles],index)=>`<details class="cu-color-group" data-color-group="${title.toLowerCase().replace(/[^a-z]+/g,'-')}" ${index===0?'open':''}><summary>${title}</summary><div class="cu-color-entries">${roles.map(role=>{
        const auto=role!=='card'&&!owns(custom,role),disabled=auto?'disabled':'',label=S.mode==='anki'&&role.startsWith('reveal')?({revealBackground:'Show Answer background',revealText:'Show Answer text'}[role]):S.view==='write'?({buttonText:'Input / button text',buttonBackground:'Input / button background',incorrect:'Mismatch text',incorrectBackground:'Mismatch background'}[role]||labels[role]):S.view==='flash'?({correct:'Got it text',correctBackground:'Got it background',incorrect:'Still learning text',incorrectBackground:'Still learning background'}[role]||labels[role]):labels[role];
        return `<div class="cu-color-entry ${S.selectedColor===role?'cu-picked-color':''}" data-color-entry="${role}"><div class="cu-color-label"><span class="cu-color-name" data-locate-color="${role}" role="button" tabindex="0" title="Double-click to locate in preview">${label}</span>${role==='card'?'':`<label class="cu-auto"><input id="${role}-auto" data-auto="${role}" type="checkbox" ${auto?'checked':''}> Auto</label>`}</div><div class="cu-color-row"><input type="color" id="color-${role}" data-color="${role}" aria-label="${label} color" value="${p[role]}" ${disabled}><input class="cu-hex" id="hex-${role}" data-hex="${role}" aria-label="${label} hex color" maxlength="7" value="${p[role]}" ${disabled}></div></div>`;
      }).join('')}</div></details>`).join('');
    }
    function imageFields(){
      const p=A.palette(S.config,S.mode,S.theme,S.view);
      return `<div class="cu-images">${['background','card'].map(target=>{
        const image=S.config.images?.[target],title=target==='background'?'Page background':'Card surface',presentation=A.imagePresentation(image,target==='background'?p.background:p.card,A.imageForegrounds(S.config,p,S.theme,S.view,target));
        return `<section class="cu-image-section"><h2>${title}</h2>${image?`<img class="cu-image-thumb" src="${esc(image.data)}" alt="${esc(image.name)}"><div class="cu-image-name" title="${esc(image.name)}">${esc(image.name)}</div>`:'<div class="cu-image-empty">No image</div>'}<div class="cu-image-actions"><button data-image-upload="${target}" ${S.imagePending?'disabled':''}>${image?'Replace image':'Upload image'}</button>${image?`<button data-image-remove="${target}">Remove</button>`:''}</div>${image?`<label class="cu-field"><span>Image opacity <output id="opacity-value-${target}">${image.opacity}%</output></span><input id="image-opacity-${target}" data-image-target="${target}" data-image-setting="opacity" type="range" min="0" max="100" step="1" value="${image.opacity}"></label><label class="cu-field"><span>Readability overlay <output id="overlay-value-${target}">${image.overlay}%</output></span><input id="image-overlay-${target}" data-image-target="${target}" data-image-setting="overlay" type="range" min="0" max="100" step="1" value="${image.overlay}"></label><label class="cu-image-smart" title="Fades the image when needed to preserve text contrast; buttons keep their solid colors."><input type="checkbox" data-image-target="${target}" data-image-setting="smart" ${image.smart?'checked':''}> Smart readability</label><small class="cu-image-effective" id="image-effective-${target}">Visible image: ${Math.round(presentation.alpha*100)}%</small>`:''}</section>`;
      }).join('')}<button class="cu-reset" data-custom="reset-images">Remove all images</button><small class="cu-image-scope">Shared by MAIN CRAM and ANKI CRAM, in both themes.</small></div>`;
    }
    function updateImageReadouts(){const p=A.palette(S.config,S.mode,S.theme,S.view);for(const target of ['background','card']){
      const image=S.config.images?.[target];if(!image)continue;
      for(const key of ['opacity','overlay']){const el=$('#'+key+'-value-'+target);if(el)el.textContent=image[key]+'%';}
      const el=$('#image-effective-'+target);if(el)el.textContent='Visible image: '+Math.round(A.imagePresentation(image,target==='background'?p.background:p.card,A.imageForegrounds(S.config,p,S.theme,S.view,target)).alpha*100)+'%';
    }}
    function inspectorControls(){
      const button=$('#pick-preview');if(button){button.textContent=S.inspect?'Stop picking':'Pick from preview';button.setAttribute('aria-pressed',String(S.inspect));}
      const status=$('#picked-color');if(status){const name=S.selectedColor?$('[data-locate-color="'+S.selectedColor+'"]'):null;status.textContent=name?name.textContent+($('#'+S.selectedColor+'-auto')?.checked?' · Auto':''):'';}
    }
    function selectColor(role,scroll=false){
      if(!A.roles.includes(role))return;
      const row=$('[data-color-entry="'+role+'"]');if(!row)return;
      S.selectedColor=role;root.querySelectorAll('.cu-picked-color').forEach(el=>el.classList.remove('cu-picked-color'));row.classList.add('cu-picked-color');
      row.closest('details')?.setAttribute('open','');
      if(scroll){row.scrollIntoView?.({block:'nearest',behavior:'smooth'});const input=$('#hex-'+role);if(input&&!input.disabled)input.focus({preventScroll:true});else row.querySelector('[data-locate-color]')?.focus({preventScroll:true});}
      inspectorControls();
    }
    function locateColor(el){const role=el?.dataset.locateColor;if(!A.roles.includes(role))return;S.inspect=false;selectColor(role);S.locator={role,label:el.textContent,id:++S.locateSerial};inspectorControls();message();}
    const sizeKey=()=>S.view!=='flash'?'examSize':'size';
    function fields(){
      if(S.panel==='images')return imageFields();
      if(S.panel==='size')return `<div class="cu-fields"><label class="cu-field"><span>Width</span><div class="cu-unit"><input id="size-width" type="number" min="35" max="100" step="0.1" placeholder="Auto" value="${S.config[sizeKey()].width??''}"><span>%</span></div></label><label class="cu-field"><span>Height</span><div class="cu-unit"><input id="size-height" type="number" min="30" max="85" step="0.1" placeholder="Auto" value="${S.config[sizeKey()].height??''}"><span>%</span></div></label>${S.view!=='flash'?`<label class="cu-field"><span>Question panel height</span><div class="cu-unit"><input id="exam-question-height" data-exam-layout="questionHeight" type="number" min="30" max="75" step="1" value="${S.config.examLayout.questionHeight}"><span>%</span></div></label><label class="cu-field"><span>${S.view==='write'?'Input text size':'Choice text size'}</span><div class="cu-unit"><input id="exam-choice-size" data-exam-layout="choiceTextSize" type="number" min="12" max="32" step="1" value="${S.config.examLayout.choiceTextSize}"><span>px</span></div></label>`:''}</div><button class="cu-reset" data-custom="reset-size">Reset to default size</button>`;
      const custom=S.config.colors[S.theme][profileView()],p=A.palette(S.config,S.mode,S.theme,S.view);
      return `<div class="cu-fields"><label class="cu-field"><span>Color scheme</span><select id="scheme"><option value="default" ${scheme(custom)==='default'?'selected':''}>Default</option><option value="auto" ${scheme(custom)==='auto'?'selected':''}>Automatic from card</option><option value="custom" ${scheme(custom)==='custom'?'selected':''}>Custom</option></select></label><div id="cu-harmony">${harmonyFields(custom,p)}</div><div class="cu-colors">${colorFields(custom,p)}</div></div><button class="cu-reset" data-custom="reset-colors">Reset all colors</button>`;
    }
    function syncFields(){
      const host=$('#cu-fields');if(!host)return;
      const groups=new Map([...host.querySelectorAll('[data-color-group]')].map(el=>[el.dataset.colorGroup,el.getAttribute('open')!==null]));
      const sidebar=$('.cu-sidebar'),top=sidebar?.scrollTop,focus=document.activeElement?.id;
      host.innerHTML=fields();
      host.querySelectorAll('[data-color-group]').forEach(el=>{if(groups.has(el.dataset.colorGroup)){if(groups.get(el.dataset.colorGroup))el.setAttribute('open','');else el.removeAttribute('open');}});
      if(focus)$('#'+focus)?.focus();if(sidebar&&top!==undefined)sidebar.scrollTop=top;
      inspectorControls();
    }
    function render(){
      root.innerHTML=`<div class="cu-shell"><header class="cu-header"><h1>CUSTOMIZE CRAM</h1><span class="cu-scope">MAIN CRAM + ANKI CRAM</span></header><div class="cu-workspace"><aside class="cu-sidebar"><nav class="cu-nav"><button class="${S.panel==='size'?'active':''}" data-custom="size">Card size</button><button class="${S.panel==='colors'?'active':''}" data-custom="colors">CUSTOMIZE CRAM COLOR</button><button class="${S.panel==='images'?'active':''}" data-custom="images">Background &amp; card images</button></nav><div id="cu-fields">${fields()}</div></aside><section class="cu-preview-panel"><div class="cu-preview-controls"><label>Preview<select id="preview-mode"><option value="main" ${S.mode==='main'?'selected':''}>MAIN CRAM</option><option value="anki" ${S.mode==='anki'?'selected':''}>ANKI CRAM</option></select></label><label>Theme<select id="preview-theme"><option value="light" ${S.theme==='light'?'selected':''}>Light</option><option value="dark" ${S.theme==='dark'?'selected':''}>Dark</option></select></label><label>Card<select id="preview-view"><option value="flash" ${S.view==='flash'?'selected':''}>Flashcards</option><option value="exam" ${S.view==='exam'?'selected':''}>Multiple choice</option><option value="write" ${S.view==='write'?'selected':''}>Writing</option></select></label><label>Side<select id="preview-face"><option value="question" ${S.face==='question'?'selected':''}>Question</option><option value="answer" ${S.face==='answer'?'selected':''}>Answer</option></select></label></div><div class="cu-pick-tools ${S.panel==='colors'?'':'cu-hidden'}"><button id="pick-preview" data-custom="pick-preview" aria-pressed="${S.inspect}">${S.inspect?'Stop picking':'Pick from preview'}</button><span id="picked-color" role="status" aria-live="polite"></span></div><div class="cu-preview"><iframe title="Cram appearance preview" sandbox="allow-scripts allow-same-origin"></iframe></div></section></div><footer class="cu-footer"><span id="cu-status" class="cu-status" role="status"></span><div class="cu-footer-actions"><button data-custom="cancel">Cancel</button><button class="primary" data-custom="save">Save</button></div></footer></div>`;
      const frame=$('iframe'),base=esc(S.assets);
      frame.onload=()=>{fit();message();};
      frame.srcdoc=`<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="${base}app.css"><link rel="stylesheet" href="${base}live.css"><link rel="stylesheet" href="${base}live-bottom.css"><link rel="stylesheet" href="${base}appearance.css"><link rel="stylesheet" href="${base}writing.css"><script defer src="${base}appearance.js"><\/script><script defer src="${base}writing.js"><\/script><script defer src="${base}customize-preview.js"><\/script></head><body></body></html>`;
      fit();
    }
    function invalid(){return [...root.querySelectorAll('input.invalid')].length>0;}
    root.addEventListener('dblclick',e=>{const name=e.target.closest('[data-locate-color]');if(name){e.preventDefault();locateColor(name);}});
    root.addEventListener('keydown',e=>{if(e.key==='Escape'&&S.inspect){e.preventDefault();e.stopPropagation();S.inspect=false;inspectorControls();message();return;}const name=e.target.closest('[data-locate-color]');if(name&&['Enter',' '].includes(e.key)){e.preventDefault();locateColor(name);}});
    root.addEventListener('click',e=>{
      const upload=e.target.closest('[data-image-upload]'),remove=e.target.closest('[data-image-remove]');
      if(upload&&!S.imagePending){S.imagePending=true;syncFields();send('choose-image',{target:upload.dataset.imageUpload});return;}
      if(remove){delete S.config.images[remove.dataset.imageRemove];if(!Object.keys(S.config.images).length)delete S.config.images;syncFields();message();return;}
      const action=e.target.closest('[data-custom]')?.dataset.custom;if(!action)return;
      if(['size','colors','images'].includes(action)){S.locator=null;S.inspect=false;S.selectedColor=null;S.panel=action;render();}
      else if(action==='pick-preview'){S.inspect=!S.inspect;S.locator=null;inspectorControls();message();}
      else if(action==='reset-images'){delete S.config.images;syncFields();message();}
      else if(action==='reset-size'){S.config[sizeKey()]={width:null,height:null};if(S.view!=='flash')S.config.examLayout=A.normalize({}).examLayout;syncFields();message();}
      else if(action==='reset-colors'){S.config.colors=A.normalize({}).colors;syncFields();message();}
      else if(action==='cancel')send('cancel');
      else if(action==='save'){if(invalid()){$('#cu-status').textContent='Check the highlighted values.';return;}send('save',{config:S.config});}
    });
    root.addEventListener('change',e=>{
      if(e.target.id?.startsWith('preview-')){S.locator=null;S.selectedColor=null;}
      if(e.target.dataset.imageSetting==='smart'){const image=S.config.images?.[e.target.dataset.imageTarget];if(image){image.smart=e.target.checked;updateImageReadouts();message();}}
      if(e.target.id==='preview-mode'){S.mode=e.target.value;syncFields();message();}
      if(e.target.id==='preview-theme'){S.theme=e.target.value;syncFields();message();}
      if(e.target.id==='preview-view'){S.view=e.target.value;syncFields();message();$('#cu-status').textContent=S.view==='write'?'Writing shares the multiple-choice question-card settings.':'';}
      if(e.target.id==='preview-face'){S.face=e.target.value;message();}
      if(e.target.id==='scheme'){
        const prior=S.config.colors[S.theme][profileView()],p=A.palette(S.config,S.mode,S.theme,S.view);
        const next=e.target.value==='default'?{}:e.target.value==='auto'?{auto:true,card:prior.card||p.card}:{...p,auto:true};
        if(e.target.value!=='default'&&prior.harmony)next.harmony=prior.harmony;
        S.config.colors[S.theme][profileView()]=next;syncFields();message();
      }
      if(e.target.id==='harmony'){
        const custom=S.config.colors[S.theme][profileView()],choice=e.target.value;
        if(custom.auto&&A.harmonies.some(item=>item.id===choice)){if(choice==='current')delete custom.harmony;else custom.harmony=choice;syncFields();message();}
      }
      if(e.target.dataset.auto){
        const role=e.target.dataset.auto,custom=S.config.colors[S.theme][profileView()];
        if(e.target.checked)delete custom[role];else custom[role]=A.palette(S.config,S.mode,S.theme,S.view)[role];
        syncFields();message();
      }
    });
    root.addEventListener('input',e=>{
      if(e.target.dataset.examLayout){const input=e.target,key=input.dataset.examLayout,n=Number(input.value),valid=input.value!==''&&Number.isFinite(n)&&n>=Number(input.min||input.getAttribute('min'))&&n<=Number(input.max||input.getAttribute('max'));input.classList.toggle('invalid',!valid);if(valid){S.config.examLayout[key]=n;message();}return;}
      const input=e.target;if(['opacity','overlay'].includes(input.dataset.imageSetting)){const image=S.config.images?.[input.dataset.imageTarget],n=Number(input.value);if(image&&Number.isFinite(n)&&n>=0&&n<=100){image[input.dataset.imageSetting]=n;updateImageReadouts();message();}return;}
      const key=input.id?.startsWith('size-')?input.id.slice(5):null;
      if(key){const n=input.value===''?null:Number(input.value),lo=key==='width'?35:30,hi=key==='width'?100:85,valid=n===null||Number.isFinite(n)&&n>=lo&&n<=hi;input.classList.toggle('invalid',!valid);if(valid){S.config[sizeKey()][key]=n;message();}}
      const role=input.dataset.color||input.dataset.hex;
      if(role){const valid=/^#[a-f\d]{6}$/i.test(input.value);input.classList.toggle('invalid',!valid);if(valid){
        const custom=S.config.colors[S.theme][profileView()];
        // A first card color starts a coordinated palette. Existing manual palettes stay intact.
        if(role==='card'&&!Object.keys(custom).length)custom.auto=true;
        custom[role]=input.value.toLowerCase();$('#scheme').value=scheme(custom);
        const p=A.palette(S.config,S.mode,S.theme,S.view);
        for(const key of A.roles){const color=$('#color-'+key),hex=$('#hex-'+key),auto=$('#'+key+'-auto');
          if(color)color.value=p[key];if(hex&&hex!==input)hex.value=p[key];
          if(auto){auto.checked=!owns(custom,key);if(color)color.disabled=auto.checked;if(hex)hex.disabled=auto.checked;}
        }
        updateHarmonyFields();message();}}
      $('#cu-status').textContent='';
    });
    window.addEventListener('message',e=>{
      const frame=$('iframe');if(!frame||e.source!==frame.contentWindow)return;
      const data=e.data||{};
      if(data.type==='cram-preview-ready'){frame.classList.add('ready');message();}
      if(data.type==='cram-preview-resize'&&S.panel==='size'&&(!data.view||data.view===S.view)){S.config[sizeKey()]=A.normalize({[sizeKey()]:data.size})[sizeKey()];for(const key of ['width','height'])if($('#size-'+key))$('#size-'+key).value=S.config[sizeKey()][key]??'';}
      if(data.type==='cram-preview-locate-done')S.locator=null;
      if(data.type==='cram-preview-inspect-done'){S.inspect=false;inspectorControls();}
      if(data.type==='cram-preview-picked'&&S.panel==='colors'&&S.inspect&&data.mode===S.mode&&data.view===S.view&&data.theme===S.theme&&data.face===S.face)selectColor(data.role,true);
      if(data.type==='cram-preview-context'){S.face=data.face==='answer'?'answer':'question';if(['main','anki'].includes(data.mode))S.mode=data.mode;if(['flash','exam','write'].includes(data.view))S.view=data.view;$('#preview-face').value=S.face;$('#preview-mode').value=S.mode;$('#preview-view').value=S.view;syncFields();}
      if(data.type==='cram-preview-face'){S.face=data.face==='answer'?'answer':'question';$('#preview-face').value=S.face;}
    });
    window.addEventListener('resize',fit);
    if(typeof ResizeObserver==='function')new ResizeObserver(fit).observe(root);
    window.cramCustomize={state:S,receive(event,data){
      if(event==='load'){S.config=A.normalize(data.config);S.assets=data.assets;S.theme=data.dark?'dark':'light';S.ready=true;document.body.classList.toggle('custom-dark',!!data.dark);render();}
      if(event==='image'){S.imagePending=false;if(data.image&&['background','card'].includes(data.target)){const images=A.normalizeImages({[data.target]:data.image});if(images[data.target]){S.config.images={...S.config.images,...images};}}syncFields();message();}
      if(event==='error'){S.imagePending=false;if(S.panel==='images')syncFields();const el=$('#cu-status');if(el)el.textContent=data;}
    }};
    let attempts=0;const connect=()=>{if(typeof pycmd==='function')send('ready');else if(++attempts<400)setTimeout(connect,25);else root.innerHTML='<div class="custom-loading">Close and reopen CUSTOMIZE CRAM.</div>';};connect();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
