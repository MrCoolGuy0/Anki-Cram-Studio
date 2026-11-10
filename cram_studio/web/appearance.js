/* Shared, profile-only presentation for MAIN CRAM, ANKI CRAM and their previews. */
(()=>{
  'use strict';
  // Display only: keep original options, answer indices and cached text intact.
  function choiceText(answer,option){
    answer=String(answer??'');option=String(option??'');
    if(option===answer||answer.toUpperCase()===answer.toLowerCase())return option;
    if(answer===answer.toUpperCase())return option.toUpperCase();
    if(answer===answer.toLowerCase())return option.toLowerCase();
    const words=answer.match(/[\p{L}\p{M}]+/gu)||[];
    const acronym=w=>w.length>1&&w.length<=5&&w===w.toUpperCase();
    const title=w=>w[0]===w[0].toUpperCase()&&w.slice(1)===w.slice(1).toLowerCase();
    const capital=w=>w[0].toUpperCase()+w.slice(1).toLowerCase();
    // Preserve mixed-case identifiers, and acronyms in ordinary title/sentence case.
    const word=w=>acronym(w)||!title(w)&&w!==w.toLowerCase()&&w!==w.toUpperCase()?w:capital(w);
    if(words.length&&words.some(w=>title(w)&&!acronym(w))&&words.every(w=>title(w)||acronym(w)))
      return option.replace(/[\p{L}\p{M}]+/gu,word);
    if(words.length&&title(words[0])&&words.slice(1).every(w=>w===w.toLowerCase()||acronym(w))){
      let first=true;
      return option.replace(/[\p{L}\p{M}]+/gu,w=>{
        const keep=acronym(w)||!title(w)&&w!==w.toLowerCase()&&w!==w.toUpperCase();
        const text=keep?w:first?capital(w):w.toLowerCase();first=false;return text;
      });
    }
    return option;
  }
  function blankText(slot,option){
    // The stored option/cache stays untouched. Correct answers have source HTML,
    // which distinguishes soft pasted newlines from BRs, paragraphs and lists.
    if(option===slot.answer&&slot.answer_html){
      const source=document.createElement('div'),out=[],lists=[];
      source.innerHTML=slot.answer_html;
      const blocks=new Set(['p','div','blockquote','h1','h2','h3','h4','pre','tr']);
      const line=()=>{
        while(out.length&&/^[ \t]+$/.test(out.at(-1)))out.pop();
        if(out.length&&!out.at(-1).endsWith('\n'))out.push('\n');
      };
      function visit(node,pre=false){
        if(node.nodeType===3){out.push(pre?node.textContent:node.textContent.replace(/\s+/g,' '));return;}
        const tag=node.tagName?.toLowerCase();
        if(tag==='ol'||tag==='ul'){line();lists.push({tag,value:Number(node.getAttribute('start')||1)-1});}
        else if(tag==='li'){
          line();const list=lists.at(-1);
          if(list){list.value=Number(node.getAttribute('value')||list.value+1);out.push('  '.repeat(lists.length-1)+(list.tag==='ol'?list.value+'. ':'• '));}
        }else if(tag==='br'||blocks.has(tag))line();
        else if((tag==='td'||tag==='th')&&out.length&&!out.at(-1).endsWith('\n'))out.push('\t');
        for(const child of node.childNodes)visit(child,pre||tag==='pre');
        if(tag==='ol'||tag==='ul'){lists.pop();line();}
        else if(tag==='li'||blocks.has(tag))line();
      }
      visit(source);
      return out.join('').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
    }
    const text=choiceText(slot.answer,option);
    // Generated numbered/bulleted enumerations retain their visible line layout.
    const markers=text.match(/(?:^|\n)\s*(?:\d+[.)]|[•*\-])\s+\S/g)||[];
    return markers.length>1?text:text.replace(/\s+/g,' ').trim();
  }
  function fillBlank(node,slot,option){
    const text=blankText(slot,option);node.textContent=text;
    node.classList.toggle('cram-blank-lines',text.includes('\n'));
  }
  const roles=['background','card','text','accent','border','selection','correct','incorrect','question','buttonBackground','buttonText','revealBackground','revealText','primaryText','selectionText','correctBackground','incorrectBackground','answerText','answerBackground'];
  const harmonies=[
    {id:'current',label:'Current automatic',description:'Keeps the existing automatic palette.'},
    {id:'monochromatic',label:'Monochromatic',description:'One hue in lighter and darker tones.'},
    {id:'analogous',label:'Analogous',description:'Neighboring hues for a softer palette.'},
    {id:'complementary',label:'Complementary',description:'Opposite hues for stronger contrast.'},
    {id:'split_complementary',label:'Split complementary',description:'Two supporting hues beside the opposite hue.'},
    {id:'triadic',label:'Triadic',description:'Three hues spaced evenly around the wheel.'},
    {id:'tetradic',label:'Tetradic · rectangle',description:'Two complementary color pairs.'},
    {id:'square',label:'Square',description:'Four hues spaced evenly around the wheel.'}
  ];
  const defaults={
    main:{light:{background:'#ffffff',card:'#ffffff',text:'#282e3e',accent:'#4255ff',border:'#e9edf4',selection:'#f0f2ff',correct:'#138468',incorrect:'#c3474f',correctBackground:'#e9f7f1',incorrectBackground:'#fff1f1'},dark:{background:'#0d1226',card:'#171e36',text:'#f4f5ff',accent:'#a0a9ff',border:'#303a56',selection:'#293359',correct:'#75d6b1',incorrect:'#ff9caa',correctBackground:'#193e38',incorrectBackground:'#432b3c'}},
    anki:{light:{background:'#ffffff',card:'#ffffff',text:'#282e3e',accent:'#4255ff',border:'#e5e8f2',selection:'#f0f2ff',correct:'#148368',incorrect:'#c34550',correctBackground:'#e8f7ef',incorrectBackground:'#fff0f1'},dark:{background:'#0e1427',card:'#192039',text:'#f0f3ff',accent:'#a4adff',border:'#34405b',selection:'#2b3559',correct:'#83d8b4',incorrect:'#ffacb6',correctBackground:'#1c4038',incorrectBackground:'#482c3b'}}
  };
  const maps={main:{background:'--bg',card:'--panel',text:'--ink',accent:'--primary',border:'--line',selection:'--tint',correct:'--green',incorrect:'--red'},anki:{background:'--cl-bg',card:'--cl-panel',text:'--cl-text',accent:'--cl-accent',border:'--cl-line',selection:'--cl-tint',correct:'--cl-good',incorrect:'--cl-bad'}};
  const shared={buttonBackground:'--cram-button-bg',buttonText:'--cram-button-text',revealBackground:'--cram-reveal-bg',revealText:'--cram-reveal-text',primaryText:'--cram-on-accent',selectionText:'--cram-selection-text',correctBackground:'--cram-correct-bg',incorrectBackground:'--cram-incorrect-bg',answerText:'--cram-answer-text',answerBackground:'--cram-answer-bg'};
  function normalizeImages(raw){
    const out={};if(!raw||typeof raw!=='object')return out;
    for(const target of ['background','card']){
      const image=raw[target];if(!image||typeof image!=='object'||typeof image.data!=='string'||image.data.length>350000)continue;
      const match=image.data.match(/^data:image\/(png|jpeg);base64,([A-Za-z0-9+/]+={0,2})$/);if(!match||match[2].length%4||match[2].length*.75-(match[2].endsWith('==')?2:match[2].endsWith('=')?1:0)>262144)continue;
      if(match[1]==='png'?!match[2].startsWith('iVBORw0KGgo'):!match[2].startsWith('/9j/'))continue;
      const opacity=image.opacity??35,overlay=image.overlay??35,smart=image.smart??true;
      if(![opacity,overlay].every(n=>typeof n==='number'&&Number.isFinite(n)&&n>=0&&n<=100)||typeof smart!=='boolean')continue;
      out[target]={data:image.data,name:typeof image.name==='string'?image.name.replace(/[\x00-\x1f\x7f]/g,'').slice(0,100)||'Image':'Image',opacity:Math.round(opacity*10)/10,overlay:Math.round(overlay*10)/10,smart};
    }
    return out;
  }
  function normalize(raw={}){
    const out={version:1,size:{width:null,height:null},examSize:{width:null,height:null},examLayout:{questionHeight:60,choiceTextSize:18},colors:{light:{flash:{},exam:{}},dark:{flash:{},exam:{}}}};
    for(const sizeKey of ['size','examSize'])for(const [key,lo,hi] of [['width',35,100],['height',30,85]]){
      const n=raw?.[sizeKey]?.[key];if(typeof n==='number'&&Number.isFinite(n)&&n>=lo&&n<=hi)out[sizeKey][key]=Math.round(n*10)/10;
    }
    for(const [key,lo,hi] of [['questionHeight',30,75],['choiceTextSize',12,32]]){
      const n=raw?.examLayout?.[key];if(typeof n==='number'&&Number.isFinite(n)&&n>=lo&&n<=hi)out.examLayout[key]=Math.round(n*10)/10;
    }
    for(const theme of ['light','dark'])for(const view of ['flash','exam']){
      const palette=out.colors[theme][view];
      if(raw?.colors?.[theme]?.[view]?.auto===true)palette.auto=true;
      const choice=raw?.colors?.[theme]?.[view]?.harmony;if(choice!=='current'&&harmonies.some(h=>h.id===choice))palette.harmony=choice;
      for(const role of roles){const color=raw?.colors?.[theme]?.[view]?.[role];if(typeof color==='string'&&/^#[a-f\d]{6}$/i.test(color))palette[role]=color.toLowerCase();}
    }
    const images=normalizeImages(raw?.images);if(Object.keys(images).length)out.images=images;
    return out;
  }
  function blend(a,b,amount){return '#'+[1,3,5].map(i=>Math.round(parseInt(a.slice(i,i+2),16)*amount+parseInt(b.slice(i,i+2),16)*(1-amount)).toString(16).padStart(2,'0')).join('');}
  function luminance(color){return [1,3,5].reduce((sum,i,n)=>{const c=parseInt(color.slice(i,i+2),16)/255;return sum+(c<=.04045?c/12.92:Math.pow((c+.055)/1.055,2.4))*[.2126,.7152,.0722][n];},0);}
  function contrast(a,b){const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
  function readable(color,background){
    if(contrast(color,background)>=4.5)return color;
    const target=contrast('#000000',background)>contrast('#ffffff',background)?'#000000':'#ffffff';
    for(let n=1;n<=20;n++){const candidate=blend(target,color,n/20);if(contrast(candidate,background)>=4.5)return candidate;}
    return target;
  }
  function harmony(card,dark,fallback){
    const [r,g,b]=[1,3,5].map(i=>parseInt(card.slice(i,i+2),16)/255),hi=Math.max(r,g,b),lo=Math.min(r,g,b),d=hi-lo;
    if(d<.08)return fallback;
    let h=hi===r?((g-b)/d)%6:hi===g?(b-r)/d+2:(r-g)/d+4;h=((h*60+180)%360+360)%360;
    const s=.62,l=dark?.73:.36,c=(1-Math.abs(2*l-1))*s,x=c*(1-Math.abs(h/60%2-1)),m=l-c/2;
    const rgb=h<60?[c,x,0]:h<120?[x,c,0]:h<180?[0,c,x]:h<240?[0,x,c]:h<300?[x,0,c]:[c,0,x];
    return '#'+rgb.map(n=>Math.round((n+m)*255).toString(16).padStart(2,'0')).join('');
  }
  function hslInfo(color){
    const [r,g,b]=[1,3,5].map(i=>parseInt(color.slice(i,i+2),16)/255),hi=Math.max(r,g,b),lo=Math.min(r,g,b),c=hi-lo,l=(hi+lo)/2;
    const h=!c?0:((hi===r?((g-b)/c)%6:hi===g?(b-r)/c+2:(r-g)/c+4)*60+360)%360;
    return {h,s:c?c/(1-Math.abs(2*l-1)):0,l,c};
  }
  function hslHex(h,s,l){
    h=(h%360+360)%360;const c=(1-Math.abs(2*l-1))*s,x=c*(1-Math.abs(h/60%2-1)),m=l-c/2;
    const rgb=h<60?[c,x,0]:h<120?[x,c,0]:h<180?[0,c,x]:h<240?[0,x,c]:h<300?[x,0,c]:[c,0,x];
    return '#'+rgb.map(n=>Math.round((n+m)*255).toString(16).padStart(2,'0')).join('');
  }
  function harmonyColors(card,dark,fallback,id='current'){
    if(id==='current'||!harmonies.some(item=>item.id===id)){
      const primary=harmony(card,dark,fallback);return {primary,secondary:primary,tertiary:primary,hues:[card,primary],neutral:false};
    }
    const base=hslInfo(card),neutral=base.c<.025,h=neutral?hslInfo(fallback).h:base.h;
    const saturation=neutral&&id==='monochromatic'?0:.62,light=dark?.73:.36;
    const offsets={monochromatic:[0,0,0],analogous:[30,-30,0],complementary:[180,0,180],split_complementary:[150,210,0],triadic:[120,240,0],tetradic:[180,60,240],square:[180,90,270]}[id];
    const [primary,secondary,tertiary]=offsets.map(offset=>hslHex(h+offset,saturation,light));
    return {primary,secondary,tertiary,hues:[...new Set([card,primary,secondary,tertiary])],neutral};
  }
  function palette(config,mode,theme,view){
    if(view==='write')view='exam';
    const custom=normalize(config).colors[theme][view],b=defaults[mode][theme],p={...b,...custom},changed=Object.keys(custom).length>0;
    const put=(role,color)=>{if(!custom[role])p[role]=color;};
    if(custom.auto){
      const dark=luminance(p.card)<.2,anchor=dark?'#000000':'#ffffff',expanded=!!custom.harmony,colors=harmonyColors(p.card,dark,b.accent,custom.harmony);
      const page=blend(p.card,anchor,.66);
      put('background',expanded?blend(colors.tertiary,page,dark?.10:.055):page);put('text',readable(b.text,p.card));
      put('accent',readable(colors.primary,p.card));put('border',expanded?blend(colors.tertiary,p.card,.28):blend(p.text,p.card,.18));
      put('buttonBackground',expanded?blend(colors.tertiary,blend(p.card,anchor,.62),dark?.10:.045):blend(p.card,anchor,.62));put('buttonText',readable(p.text,p.buttonBackground));
      put('selection',blend(p.accent,p.buttonBackground,dark?.24:.10));
      put('correctBackground',blend(b.correct,p.buttonBackground,.13));put('correct',readable(b.correct,p.correctBackground));
      put('incorrectBackground',blend(b.incorrect,p.buttonBackground,.13));put('incorrect',readable(b.incorrect,p.incorrectBackground));
      // Revealed answers deliberately derive from the accent, never from Correct.
      put('answerBackground',blend(expanded?colors.secondary:p.accent,p.card,.10));put('answerText',readable(expanded?colors.secondary:p.accent,p.answerBackground));
      put('revealBackground',blend(expanded?colors.secondary:p.accent,p.buttonBackground,expanded?.14:.08));put('revealText',readable(expanded?colors.secondary:p.text,p.revealBackground));
      if(expanded)put('question',blend(colors.tertiary,p.card,dark?.12:.065));
    }else{
      put('buttonBackground',p.card);put('buttonText',readable(p.text,p.buttonBackground));
      put('correctBackground',changed?blend(p.correct,p.card,.13):b.correctBackground);
      put('incorrectBackground',changed?blend(p.incorrect,p.card,.13):b.incorrectBackground);
      put('answerBackground',blend(p.accent,p.card,.10));put('answerText',readable(p.accent,p.answerBackground));
      put('revealBackground',p.buttonBackground);put('revealText',readable(p.buttonText,p.revealBackground));
    }
    put('question',blend(p.accent,p.card,theme==='dark'?.075:.035));
    put('selectionText',readable(p.buttonText,p.selection));put('primaryText',changed?readable('#ffffff',p.accent):theme==='dark'&&mode==='main'?'#101630':'#ffffff');
    delete p.auto;delete p.harmony;return p;
  }
  function imageForegrounds(config,p,theme,view,target){
    if(view==='write')view='exam';
    if(target==='background')return [p.text,p.accent];
    // With an untouched palette, Basic answers use the ordinary card text.
    return Object.keys(config.colors?.[theme]?.[view]||{}).length?[p.text,p.answerText]:[p.text];
  }
  function imagePresentation(image,base,foregrounds){
    if(!image)return {alpha:0,style:'none'};
    let alpha=image.opacity/100*(1-image.overlay/100);
    if(image.smart){
      const minimums=foregrounds.map(color=>Math.min(4.5,contrast(color,base)));
      while(alpha>0&&foregrounds.some((color,i)=>['#000000','#ffffff'].some(pixel=>contrast(color,blend(pixel,base,alpha))+1e-7<minimums[i])))alpha=alpha<.01?0:alpha-.01;
    }
    alpha=Math.max(0,alpha);const rgb=[1,3,5].map(i=>parseInt(base.slice(i,i+2),16)).join(','),veil=`rgba(${rgb},${Math.round((1-alpha)*10000)/10000})`;
    return {alpha,style:alpha?`linear-gradient(${veil},${veil}),url("${image.data}")`:'none'};
  }
  function resize(start,dx,dy,axis,viewport){
    return {width:Math.round(Math.max(35,Math.min(100,start.width+(axis.includes('x')?dx/viewport.width*200:0)))*10)/10,
      height:Math.round(Math.max(30,Math.min(85,viewport.maxHeight??85,start.height+(axis.includes('y')?dy/viewport.height*100:0)))*10)/10};
  }
  function apply(root,raw,mode,view,dark){
    if(!root)return;
    root.classList.toggle('cram-writing',view==='write');if(view==='write')view='exam';
    mode=mode==='anki'?'anki':'main';const config=normalize(raw),theme=dark?'dark':'light';
    const extras=mode==='main'?['--muted','--soft','--green-tint','--red-tint','--primary-hover']:['--cl-muted','--cl-soft','--cl-good-bg','--cl-bad-bg'];
    for(const name of [...Object.values(maps[mode]),...Object.values(shared),...extras,'--cram-correct-text','--cram-incorrect-text','--cram-card-width','--cram-card-height','--cram-card-ratio','--cram-question-panel','--cram-blank-active','--cram-question-shadow','--cram-card-image','--cram-page-image'])root.style.removeProperty(name);
    for(const name of ['--cram-question-track','--cram-choices-track','--cram-choice-font'])root.style.removeProperty(name);
    root.classList.remove('cram-sized-flash','cram-sized-exam','cram-custom-width','cram-answer-text-custom','cram-answer-bg-custom');
    if(mode==='anki'){document.body.style.removeProperty('--cram-live-canvas');document.body.style.removeProperty('--cram-page-image');}
    if(!['flash','exam'].includes(view))return;
    const chosen=config.colors[theme][view],p=palette(config,mode,theme,view);
    if(Object.keys(chosen).length){
      if(chosen.auto||chosen.answerText)root.classList.add('cram-answer-text-custom');
      if(chosen.answerBackground)root.classList.add('cram-answer-bg-custom');
      const put=(key,value)=>root.style.setProperty(key,value);
      for(const [role,key] of Object.entries({...maps[mode],...shared}))if(role!=='answerBackground'||chosen.answerBackground)put(key,p[role]);
      put('--cram-correct-text',p.correct);put('--cram-incorrect-text',p.incorrect);
      if(mode==='main'){
        put('--muted',chosen.auto?readable(blend(p.text,p.card,.67),p.card):blend(p.text,p.card,.67));put('--soft',blend(p.text,p.card,.05));
        put('--green-tint',p.correctBackground);put('--red-tint',p.incorrectBackground);put('--primary-hover',blend(p.accent,p.text,.85));
      }else{
        put('--cl-muted',chosen.auto?readable(blend(p.text,p.card,.67),p.card):blend(p.text,p.card,.67));put('--cl-soft',blend(p.text,p.card,.05));put('--cl-good-bg',p.correctBackground);put('--cl-bad-bg',p.incorrectBackground);
        document.body.style.setProperty('--cram-live-canvas',p.background);
      }
    }
    const page=imagePresentation(config.images?.background,p.background,imageForegrounds(config,p,theme,view,'background'));
    const card=imagePresentation(config.images?.card,p.card,imageForegrounds(config,p,theme,view,'card'));
    root.style.setProperty('--cram-page-image',page.style);root.style.setProperty('--cram-card-image',card.style);
    if(mode==='anki')document.body.style.setProperty('--cram-page-image',page.style);
    if(view==='exam'){
      root.style.setProperty('--cram-question-track',config.examLayout.questionHeight+'fr');
      root.style.setProperty('--cram-choices-track',(100-config.examLayout.questionHeight)+'fr');
      root.style.setProperty('--cram-choice-font',config.examLayout.choiceTextSize+'px');
      root.style.setProperty('--cram-question-panel',p.question);
      root.style.setProperty('--cram-blank-active',blend(p.accent,p.question,dark?.18:.09));
      root.style.setProperty('--cram-question-shadow',dark?'0 5px 22px #00000033,0 1px 4px #00000020':`0 4px 18px ${p.text}12,0 1px 4px ${p.text}09`);
    }
    const size=config[view==='exam'?'examSize':'size'];
    if(size.width!==null||size.height!==null){
      const geometry=sizeGeometry(size,mode,view);root.classList.add('cram-sized-'+view);
      if(size.width!==null){root.classList.add('cram-custom-width');root.style.setProperty('--cram-card-width',size.width+'%');}
      root.style.setProperty('--cram-card-ratio',String(geometry.ratio));
      root.style.setProperty('--cram-card-height',`calc(var(--cram-scene-height,100vh) * ${geometry.height/100})`);
    }
    fitImages(root);
  }
  // Saved percentages describe a reference scene. Keep its aspect ratio in the
  // real reviewer, whose webview already excludes Anki's native answer bar.
  function sizeGeometry(size,mode,view='flash'){
    if(view==='write')view='exam';
    const sceneHeight=mode==='anki'?828:900,areaWidth=1360-(mode==='anki'?40:60);
    const defaultWidth=mode==='anki'?1140:1080;
    const defaultHeight=mode==='anki'?sceneHeight*.74:view==='exam'?660:522;
    const width=size.width??defaultWidth/areaWidth*100,height=size.height??defaultHeight/sceneHeight*100;
    return {width,height,areaWidth,sceneHeight,reserve:mode==='anki'?122:240,ratio:(areaWidth*width/100)/(sceneHeight*height/100)};
  }
  function projectSize(size,mode,view,areaWidth,sceneHeight){
    const g=sizeGeometry(size,mode,view),height=Math.min(sceneHeight*g.height/100,Math.max(180,sceneHeight-g.reserve));
    const width=Math.min(areaWidth*(size.width??100)/100,height*g.ratio);
    return {width,height:width/g.ratio,ratio:g.ratio};
  }
  const imageListeners=new WeakSet();
  function fitImages(root){
    if(!root||typeof getComputedStyle!=='function')return;
    root.querySelectorAll('.flash-face,.cl-face').forEach(face=>{
      const content=face.querySelector('.face-content,.cl-flash-content,.cl-original-content');if(!content)return;
      const style=getComputedStyle(face),number=key=>parseFloat(style[key])||0;
      const width=face.clientWidth-number('paddingLeft')-number('paddingRight')-10;
      const height=face.clientHeight-number('paddingTop')-number('paddingBottom')-10;
      const images=content.querySelectorAll('img');
      images.forEach(image=>{
        if(!imageListeners.has(image)){imageListeners.add(image);image.addEventListener('load',()=>{if(image.isConnected)fitImages(root);});}
        if(width<=0||height<=0||!image.naturalWidth||!image.naturalHeight)return;
        // Enlarge small attached photos, retaining aspect ratio. Text and multiple
        // images still get normal scrolling; text zoom never shrinks the content.
        const room=height*(content.textContent.trim()?0.68:1)/Math.max(1,images.length);
        const target=Math.max(1,Math.min(width,room*image.naturalWidth/image.naturalHeight));
        image.style.setProperty('width',Math.round(target)+'px','important');
        image.style.setProperty('height','auto','important');image.style.setProperty('max-height','none','important');
        image.style.setProperty('max-width','100%','important');image.style.setProperty('object-fit','contain');
      });
    });
  }
  // Clickable blanks/masks are controls, not selection or image-drag handles.
  // Keep ordinary question text, form fields and right-click menus available.
  function studyScrollbar(event){
    const el=event.target?.nodeType===3?event.target.parentElement:event.target;
    if(!Number.isFinite(event.clientX)||!Number.isFinite(event.clientY)||!el?.getBoundingClientRect)return false;
    const rect=el.getBoundingClientRect(),x=event.clientX-rect.left,y=event.clientY-rect.top;
    return el.scrollHeight>el.clientHeight&&el.offsetWidth-el.clientWidth>2&&(x>=(el.clientLeft||0)+el.clientWidth||x<(el.clientLeft||0))||
      el.scrollWidth>el.clientWidth&&el.offsetHeight-el.clientHeight>2&&(y>=(el.clientTop||0)+el.clientHeight||y<(el.clientTop||0));
  }
  function preventStudySelection(root,selector){
    if(!root)return;
    const guard=event=>{
      if(event.type==='mousedown'&&event.button!==undefined&&event.button!==0)return;
      if(studyScrollbar(event))return;
      const element=event.target?.nodeType===3?event.target.parentElement:event.target;
      if(element?.closest?.('input,textarea,select,[contenteditable],button,a'))return;
      const control=element?.closest?.(selector);if(!control)return;
      event.preventDefault();
      // Cancel an existing browser range only if it overlaps the clicked area.
      const selection=window.getSelection?.();
      if(selection&&selection.rangeCount){
        for(let i=0;i<selection.rangeCount;i++){
          try{if(selection.getRangeAt(i).intersectsNode(control)){selection.removeAllRanges();break;}}catch(_){/* A detached range needs no cleanup. */}
        }
      }
      // Cancelling mousedown must not take keyboard focus away from SVG masks.
      if(event.type==='mousedown'&&control.getAttribute('tabindex')==='0')control.focus?.({preventScroll:true});
    };
    for(const type of ['mousedown','selectstart','dragstart'])root.addEventListener(type,guard);
  }
  // Clicks flip, including text. Only a drag selects; its release cannot flip.
  function flashcardPointer(root,selector){
    const doc=root?.ownerDocument||document,textRoots='.face-content,.cl-flash-content,.cl-original-content,.card-heading';
    const controls='a,button,input,textarea,select,[contenteditable],canvas,svg';
    const element=node=>node?.nodeType===3?node.parentElement:node;
    const inside=(node,parent)=>{for(let n=element(node);n;n=n.parentElement)if(n===parent)return true;return false;};
    let press=null;
    function caret(event,card){
      if(!Number.isFinite(event.clientX)||!Number.isFinite(event.clientY))return null;
      try{
        let node,offset;
        if(doc.caretPositionFromPoint){const p=doc.caretPositionFromPoint(event.clientX,event.clientY);node=p?.offsetNode;offset=p?.offset;}
        else if(doc.caretRangeFromPoint){const p=doc.caretRangeFromPoint(event.clientX,event.clientY);node=p?.startContainer;offset=p?.startOffset;}
        if(node?.nodeType===3&&inside(node,card)&&element(node)?.closest(textRoots)&&Number.isInteger(offset))return {node,offset};
      }catch(_){}
      return null;
    }
    function overText(event,card){
      const target=element(event.target),content=target?.closest?.(textRoots);
      if(!content||!inside(content,card)||target.closest('img,.cram-blank-empty'))return false;
      if(!Number.isFinite(event.clientX)||!Number.isFinite(event.clientY)||!doc.createRange)return Boolean(content.textContent.trim());
      const x=event.clientX,y=event.clientY,hit=rect=>rect.width>0&&rect.height>0&&x>=rect.left&&x<=rect.right&&y>=rect.top&&y<=rect.bottom;
      let node=null,offset=0,caretAvailable=false;
      try{
        if(doc.caretPositionFromPoint){const point=doc.caretPositionFromPoint(x,y);node=point?.offsetNode;offset=point?.offset;caretAvailable=true;}
        else if(doc.caretRangeFromPoint){const point=doc.caretRangeFromPoint(x,y);node=point?.startContainer;offset=point?.startOffset;caretAvailable=true;}
        if(caretAvailable){
          if(node?.nodeType!==3||!inside(node,content))return false;
          const range=doc.createRange(),text=node.textContent||'';
          for(const i of [offset-1,offset])if(i>=0&&i<text.length&&/\S/.test(text[i])){
            range.setStart(node,i);range.setEnd(node,i+1);if(Array.from(range.getClientRects()).some(hit))return true;
          }
          return false;
        }
        // Older web engines: use text-line rectangles, never the element box.
        if(doc.createTreeWalker){
          const walker=doc.createTreeWalker(content,4),range=doc.createRange();
          while((node=walker.nextNode()))if(node.textContent.trim()){
            range.selectNodeContents(node);if(Array.from(range.getClientRects()).some(hit))return true;
          }
          return false;
        }
      }catch(_){/* Preserve copyability if this engine cannot measure a range. */}
      return Boolean(content.textContent.trim());
    }
    function selected(card,clear=false){
      const selection=window.getSelection?.();if(!selection||selection.isCollapsed!==false)return false;
      for(let i=0;i<selection.rangeCount;i++)try{
        if(selection.getRangeAt(i).intersectsNode(card)){if(clear)selection.removeAllRanges();return true;}
      }catch(_){}
      return false;
    }
    root?.addEventListener('mousedown',event=>{
      press=null;if(event.button!==undefined&&event.button!==0)return;
      const target=element(event.target),card=target?.closest?.(selector);
      if(!card||target.closest(controls)||studyScrollbar(event))return;
      press={card,text:overText(event,card),x:event.clientX,y:event.clientY,moved:false,down:true,repeated:event.detail>1,anchor:caret(event,card)};
      selected(card,true);
      if(!press.text||press.repeated)event.preventDefault();
    });
    doc.addEventListener('mousemove',event=>{
      if(!press?.down)return;
      if(Number.isFinite(press.x)&&Math.hypot(event.clientX-press.x,event.clientY-press.y)>5)press.moved=true;
      // A repeated/background press cancels browser word/paragraph selection.
      // If it becomes a drag, restore a real text range from the pressed caret.
      if(press.moved&&(!press.text||press.repeated)&&press.anchor){
        const point=caret(event,press.card),selection=window.getSelection?.();
        if(point&&selection)try{
          if(selection.setBaseAndExtent)selection.setBaseAndExtent(press.anchor.node,press.anchor.offset,point.node,point.offset);
          else if(selection.collapse&&selection.extend){selection.collapse(press.anchor.node,press.anchor.offset);selection.extend(point.node,point.offset);}
        }catch(_){}
      }
    });
    doc.addEventListener('mouseup',()=>{if(press)press.down=false;});
    root?.addEventListener('selectstart',event=>{
      const card=element(event.target)?.closest?.(selector);
      if(card&&press?.card===card&&!press.moved&&(!press.text||press.repeated))event.preventDefault();
    });
    window.addEventListener('blur',()=>{press=null;});
    return {canFlip(event,card){
      if(!card||event.button!==undefined&&event.button!==0||element(event.target)?.closest?.(controls)||studyScrollbar(event))return false;
      const gesture=press?.card===card&&event.detail!==0?press:null;
      if(gesture){if(gesture.moved)return false;selected(card,true);return true;}
      return !selected(card);
    }};
  }
  function applyBottom(raw,view,dark){
    if(view==='write')view='exam';
    const body=document.body;if(!body)return;
    for(const key of ['--cram-button-bg','--cram-button-text','--cram-reveal-bg','--cram-reveal-text'])body.style.removeProperty(key);
    body.classList.remove('cram-bottom-custom');
    const config=normalize(raw),theme=dark?'dark':'light';
    if(!['flash','exam'].includes(view)||!Object.keys(config.colors[theme][view]).length)return;
    const p=palette(config,'anki',theme,view);body.classList.add('cram-bottom-custom');
    for(const role of ['buttonBackground','buttonText','revealBackground','revealText'])body.style.setProperty(shared[role],p[role]);
  }
  function showInPane(target,pane){
    if(!target?.getBoundingClientRect||!pane?.getBoundingClientRect)return;
    const t=target.getBoundingClientRect(),p=pane.getBoundingClientRect();
    if(t.top<p.top+8)pane.scrollTop+=t.top-p.top-8;
    else if(t.bottom>p.bottom-8)pane.scrollTop+=Math.min(t.top-p.top-8,t.bottom-p.bottom+8);
  }
  window.cramAppearance={choiceText,blankText,fillBlank,roles,harmonies,harmonyColors,defaults,normalize,palette,resize,sizeGeometry,projectSize,fitImages,preventStudySelection,flashcardPointer,showInPane,apply,applyBottom,blend,contrast,luminance,normalizeImages,imagePresentation,imageForegrounds};
  if(window.cramBottomConfig){
    let lastDark=null;
    const isDark=()=>document.body.classList.contains('nightMode')||document.body.classList.contains('night_mode');
    window.cramBottomAppearance=data=>{window.cramBottomConfig=data;lastDark=isDark();applyBottom(data.config,data.view,lastDark);};
    const ready=()=>window.cramBottomAppearance(window.cramBottomConfig);
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
    const observe=()=>{if(typeof MutationObserver==='function')new MutationObserver(()=>{if(isDark()!==lastDark)ready();}).observe(document.body,{attributes:true,attributeFilter:['class']});};
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',observe,{once:true});else observe();
  }
})();
