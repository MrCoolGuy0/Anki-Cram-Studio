"""Bounded local appearance images; no media, network or collection writes."""
from __future__ import annotations
import base64
import binascii
import math
import re
from pathlib import Path

MAX_IMAGE_BYTES=256*1024

def normalize_images(raw):
    if not isinstance(raw,dict):raise ValueError('Invalid appearance images.')
    out={}
    for target in ('background','card'):
        if target not in raw:continue
        item=raw[target]
        if not isinstance(item,dict):raise ValueError('Invalid appearance image.')
        data=item.get('data','')
        if not isinstance(data,str) or len(data)>350000:raise ValueError('Choose a smaller appearance image.')
        match=re.fullmatch(r'data:image/(png|jpeg);base64,([A-Za-z0-9+/]+={0,2})',data)
        if not match:raise ValueError('Choose a PNG or JPEG appearance image.')
        try:decoded=base64.b64decode(match[2],validate=True)
        except (ValueError,binascii.Error):raise ValueError('The appearance image is invalid.') from None
        if len(decoded)>MAX_IMAGE_BYTES or not (decoded.startswith(b'\x89PNG\r\n\x1a\n') if match[1]=='png' else decoded.startswith(b'\xff\xd8\xff')):
            raise ValueError('The appearance image is invalid or too large.')
        image={'data':data}
        name=item.get('name','Image')
        if not isinstance(name,str):raise ValueError('Invalid image name.')
        image['name']=re.sub(r'[\x00-\x1f\x7f]','',name)[:100] or 'Image'
        for key,default in (('opacity',35),('overlay',35)):
            n=item.get(key,default)
            if isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n) or not 0<=n<=100:raise ValueError('Image '+key+' must be between 0 and 100%.')
            image[key]=round(n,1)
        smart=item.get('smart',True)
        if not isinstance(smart,bool):raise ValueError('Invalid image readability setting.')
        image['smart']=smart;out[target]=image
    return out

def choose_image(parent):
    # Qt is supplied by Anki. Keep imports lazy so validation needs no GUI.
    from aqt.qt import QFileDialog,QImageReader,QSize,Qt,QBuffer,QIODevice
    filename,_=QFileDialog.getOpenFileName(parent,'Choose a Cram image','','Images (*.png *.jpg *.jpeg *.webp *.bmp)')
    if not filename:return None
    source=Path(filename)
    if not source.is_file() or source.stat().st_size>30*1024*1024:raise ValueError('Choose an image smaller than 30 MB.')
    reader=QImageReader(filename);reader.setAutoTransform(True);size=reader.size()
    if not size.isValid() or size.width()*size.height()>40000000:raise ValueError('Choose an image up to 40 megapixels.')
    reader.setScaledSize(size.scaled(QSize(1600,1600),Qt.AspectRatioMode.KeepAspectRatio))
    image=reader.read()
    if image.isNull():raise ValueError('Anki could not open this image. Try PNG or JPEG.')
    image=image.scaled(QSize(1600,1600),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
    extension='png' if image.hasAlphaChannel() else 'jpeg'
    while True:
        for quality in ([80,65,50] if extension=='jpeg' else [-1]):
            buffer=QBuffer();buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            if not image.save(buffer,'PNG' if extension=='png' else 'JPEG',quality):raise ValueError('Anki could not prepare this image.')
            encoded=bytes(buffer.data());buffer.close()
            if len(encoded)<=MAX_IMAGE_BYTES:
                data='data:image/'+extension+';base64,'+base64.b64encode(encoded).decode('ascii')
                return normalize_images({'card':{'data':data,'name':source.name}})['card']
        if max(image.width(),image.height())<=96:raise ValueError('Choose a simpler image.')
        image=image.scaled(QSize(max(1,int(image.width()*.8)),max(1,int(image.height()*.8))),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
