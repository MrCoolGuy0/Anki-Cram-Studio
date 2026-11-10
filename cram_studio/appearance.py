"""Validated profile-only Cram appearance. Never reads or writes the collection."""
from __future__ import annotations
import math
import re
from .appearance_images import normalize_images

ROLES=('background','card','text','accent','border','selection','correct','incorrect','question','buttonBackground','buttonText','revealBackground','revealText','primaryText','selectionText','correctBackground','incorrectBackground','answerText','answerBackground')
HARMONIES=('monochromatic','analogous','complementary','split_complementary','triadic','tetradic','square')

def normalize_appearance(value):
    if not isinstance(value,dict):raise ValueError('Invalid appearance settings.')
    out={'version':1,'size':{'width':None,'height':None},'examSize':{'width':None,'height':None},'examLayout':{'questionHeight':60,'choiceTextSize':18},'colors':{}}
    for size_key in ('size','examSize'):
        size=value.get(size_key,{})
        if not isinstance(size,dict):raise ValueError('Invalid card size.')
        for key,lo,hi in (('width',35,100),('height',30,85)):
            number=size.get(key)
            if number is None:continue
            if isinstance(number,bool) or not isinstance(number,(int,float)) or not math.isfinite(number) or not lo<=number<=hi:
                raise ValueError(f'{key.title()} must be between {lo} and {hi}%.')
            out[size_key][key]=round(number,1)
    layout=value.get('examLayout',{})
    if not isinstance(layout,dict):raise ValueError('Invalid multiple-choice layout.')
    for key,lo,hi in (('questionHeight',30,75),('choiceTextSize',12,32)):
        number=layout.get(key,out['examLayout'][key])
        if isinstance(number,bool) or not isinstance(number,(int,float)) or not math.isfinite(number) or not lo<=number<=hi:
            raise ValueError('Invalid multiple-choice '+key+'.')
        out['examLayout'][key]=round(number,1)
    colors=value.get('colors',{})
    if not isinstance(colors,dict):raise ValueError('Invalid Cram colors.')
    for theme in ('light','dark'):
        group=colors.get(theme,{})
        if not isinstance(group,dict):raise ValueError('Invalid color theme.')
        out['colors'][theme]={}
        for view in ('flash','exam'):
            palette=group.get(view,{})
            if not isinstance(palette,dict):raise ValueError('Invalid card colors.')
            out['colors'][theme][view]={}
            if 'harmony' in palette:
                harmony=palette['harmony']
                if harmony not in ('current',)+HARMONIES:raise ValueError('Choose a valid color harmony.')
                if harmony!='current':out['colors'][theme][view]['harmony']=harmony
            if 'auto' in palette:
                if not isinstance(palette['auto'],bool):raise ValueError('Invalid automatic color setting.')
                if palette['auto']:out['colors'][theme][view]['auto']=True
            for role in ROLES:
                if role not in palette:continue
                color=palette[role]
                if not isinstance(color,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',color):
                    raise ValueError('Choose a valid color for '+role+'.')
                out['colors'][theme][view][role]=color.lower()
    images=normalize_images(value.get('images',{}))
    if images:out['images']=images
    return out

def get_appearance(store):
    try:return normalize_appearance(store.data['preferences'].get('appearance',{}))
    except (ValueError,TypeError,KeyError):return normalize_appearance({})

def save_appearance(store,value):
    value=normalize_appearance(value)
    with store.lock:
        preferences=store.data['preferences'];existed='appearance' in preferences;previous=preferences.get('appearance')
        preferences['appearance']=value
        try:store.save()
        except Exception:
            if existed:preferences['appearance']=previous
            else:preferences.pop('appearance',None)
            raise
    return value
