#!/usr/bin/env python3
"""Deterministic, editable raster-art builder for the Kerem AERO V4 GitHub profile.
All image assets remain local. Requires Pillow and bundled landscape-source.png.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math, random
random.seed(24)
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'; ASSETS.mkdir(exist_ok=True)
WALLPAPER=ROOT/'source'/'landscape-source.png'
BG=Image.open(WALLPAPER).convert('RGB')
# Fonts are local design-time dependencies only; never include them in the release.
BOLD='/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
EXTRA='/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf'
MED='/usr/share/fonts/opentype/inter/Inter-Medium.otf'
SEMI='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
REG='/usr/share/fonts/opentype/inter/Inter-Regular.otf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
NAVY=(6,57,94,255)
CYAN=(1,132,186,255)
INK=(9,52,74,255)
SOFT=(45,104,130,255)
WHITE=(255,255,255,255)

def f(sz, w='reg'):
    return ImageFont.truetype({'reg':REG,'med':MED,'semi':SEMI,'bold':BOLD,'extra':EXTRA,'mono':MONO}[w], sz)

def paint_text(im, xy, value, size, color=INK, weight='reg', stroke=0, shadow=False, anchor=None):
    d=ImageDraw.Draw(im,'RGBA')
    font=f(size,weight)
    if shadow:d.text((xy[0]+2,xy[1]+3),value,font=font,fill=(255,255,255,175),anchor=anchor)
    d.text(xy,value,font=font,fill=color,anchor=anchor,stroke_width=stroke,stroke_fill=color)

def gradient(w,h,top,bottom):
    g=Image.new('RGB',(w,h));pix=g.load()
    for y in range(h):
        t=y/max(1,h-1); c=tuple(int(top[k]*(1-t)+bottom[k]*t) for k in range(3))
        ImageDraw.Draw(g).line((0,y,w,y),fill=c)
    return g.convert('RGBA')

def roundrect(im,bbox,r,fill,outline=None,width=2):
    ImageDraw.Draw(im,'RGBA').rounded_rectangle(bbox,radius=r,fill=fill,outline=outline,width=width)

def glass(im, box, r=34, tint=(250,255,255,185), blur=14, outline=(255,255,255,225),shadow=True, glossy=True):
    x0,y0,x1,y1=map(int,box); ww=x1-x0;hh=y1-y0
    if shadow:
        sh=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(sh,'RGBA');
        d.rounded_rectangle((x0+7,y0+13,x1+8,y1+17),radius=r,fill=(0,61,89,75));im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    crop=im.crop((x0,y0,x1,y1)).filter(ImageFilter.GaussianBlur(blur))
    crop=Image.alpha_composite(crop,Image.new('RGBA',(ww,hh),tint))
    mask=Image.new('L',(ww,hh),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,ww-1,hh-1),radius=r,fill=255)
    im.paste(crop,(x0,y0),mask)
    d=ImageDraw.Draw(im,'RGBA');d.rounded_rectangle((x0,y0,x1,y1),radius=r,outline=outline,width=3)
    if glossy:
        d.arc((x0+6,y0+5,x1-6,y1-5),186,350,fill=(255,255,255,118),width=2)
        d.line((x0+r,y0+4,x1-r,y0+4),fill=(255,255,255,125),width=2)

def glow(im,xy,radius,col=(224,253,255,140),blur=30):
    lay=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(lay,'RGBA');x,y=xy
    d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=col);im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))

def orb(im,x,y,r,accent=(200,247,255), label=None):
    glow(im,(x,y),r,(255,255,255,80),18)
    d=ImageDraw.Draw(im,'RGBA');
    for dr in range(r,0,-1):
        t=dr/r
        d.ellipse((x-dr,y-dr,x+dr,y+dr),fill=(accent[0],accent[1],accent[2],int((1-t)*23+5)))
    d.ellipse((x-r,y-r,x+r,y+r),outline=(255,255,255,245),width=max(3,r//18))
    d.arc((x-r+4,y-r+4,x+r-4,y+r-4),192,318,fill=(255,255,255,245),width=max(3,r//13))
    d.ellipse((x-int(r*.65),y-int(r*.71),x+int(r*.2),y-int(r*.41)),fill=(255,255,255,140))
    if label:paint_text(im,(x,y),label,int(r*.66),CYAN,'bold',anchor='mm')

def pill(im,bbox,label,fill=(243,255,255,196),color=INK,size=24):
    glass(im,bbox,19,fill,5,shadow=False,glossy=False)
    x0,y0,x1,y1=bbox
    paint_text(im,(x0+21,(y0+y1)//2),label,size,color,'semi',anchor='lm')

def save(im,name,quality=89):
    p=ASSETS/name
    if p.suffix.lower() in ('.jpg','.jpeg'):
        im.convert('RGB').save(p,quality=quality,optimize=True,subsampling=0)
    else:im.save(p,optimize=True)
    print(f'{p.name}  {im.size}  {p.stat().st_size//1024} KiB')

def crop_cover(im,w,h):
    iw,ih=im.size;fact=max(w/iw,h/ih)
    s=im.resize((int(iw*fact)+2,int(ih*fact)+2),Image.Resampling.LANCZOS)
    ox=(s.width-w)//2;oy=(s.height-h)//2
    return s.crop((ox,oy,ox+w,oy+h)).convert('RGBA')

def add_top_window_bar(im,x,y,w,title,right=''):
    glass(im,(x,y,x+w,y+65),27,(243,254,255,178),9,shadow=False)
    d=ImageDraw.Draw(im,'RGBA')
    for i,c in enumerate(((255,111,126,255),(255,194,89,255),(74,206,152,255))):
        d.ellipse((x+20+i*30,y+24,x+32+i*30,y+36),fill=c,outline=(255,255,255,210),width=2)
    paint_text(im,(x+124,y+22),title,24,NAVY,'semi')
    if right:paint_text(im,(x+w-31,y+22),right,19,SOFT,'med',anchor='ra')

def card_base(kind,w=1000,h=550):
    colors={
     'restofy':((245,255,255),(163,227,215)),
     'crypto':((221,246,255),(121,204,233)),
     'ml':((237,246,255),(193,209,255)),
     'library':((226,252,244),(141,225,208)),
    }
    a,b=colors[kind]; im=gradient(w,h,a,b)
    for _ in range(5):
        cx=random.randint(0,w);cy=random.randint(0,h);rad=random.randint(70,220)
        glow(im,(cx,cy),rad,(255,255,255,80),55)
    # transparent glass lines in the background
    d=ImageDraw.Draw(im,'RGBA')
    for q in (0,1,2):
        rx=450+80*q;ry=120-35*q
        d.arc((rx,ry,rx+540,ry+430),193,335,fill=(255,255,255,80),width=5)
    add_top_window_bar(im,26,22,948,'KEREM.OS / OPEN WINDOWS','PUBLIC WORK')
    glass(im,(34,103,966,511),34,(248,255,255,136),12)
    return im

# -- Wide HERO ------------------------------------------------------------
W,H=1800,760
hero=crop_cover(BG,W,H)
add_top_window_bar(hero,34,26,1732,'KEREM.OS  /  PERSONAL DESKTOP','ISTANBUL  ·  AERO EDITION')
# left introductory glass window
glass(hero,(64,142,1128,618),44,(245,253,255,198),16)
roundrect(hero,(98,166,620,211),20,(255,255,255,164),outline=(255,255,255,190))
paint_text(hero,(120,176),'HELLO, WORLD  /  NICE TO MEET YOU',23,CYAN,'semi')
paint_text(hero,(112,224),'Kerem',153,NAVY,'extra',shadow=True)
paint_text(hero,(119,372),'Kalyoncu',103,(3,126,171,255),'bold',shadow=True)
paint_text(hero,(125,505),'Software Engineer  ·  Systems Builder',33,NAVY,'semi')
paint_text(hero,(128,554),'BACKEND  /  DATA  /  HUMAN-CENTERED INTERFACES',22,SOFT,'mono')
# flotating desktop widget top right (leave scenic ring partially visible)
glass(hero,(1281,383,1715,586),37,(235,255,255,163),11)
paint_text(hero,(1313,413),'DESKTOP SHORTCUTS',24,CYAN,'semi')
for i,(a,b) in enumerate([('01','Public projects'),('02','Engineering experience'),('03','How I build')]):
    yy=462+i*40
    orb(hero,1338,yy,16,label=a[-1]);paint_text(hero,(1370,yy),b,23,NAVY,'med',anchor='lm')
# bottom dock
p=hero
for i,(name,accent) in enumerate([('WORK',(116,213,250)),('EXPERIENCE',(172,224,255)),('PROCESS',(180,250,212)),('STACK',(198,225,255)),('CONNECT',(251,230,171))]):
    x=275+i*260
    glass(p,(x,666,x+230,736),31,(249,255,255,187),8,shadow=False)
    orb(p,x+37,701,21,accent);paint_text(p,(x+73,701),name,20,NAVY,'semi',anchor='lm')
save(hero,'aero-v4-hero.jpg',91)

# -- Maritime hero / flagship panel --------------------------------------
W,H=1800,570
sea=gradient(W,H,(195,243,253),(53,171,215))
# translucent cloud/sun glows
for cx,cy,rad in [(1530,90,230),(260,60,190),(1320,440,170)]:glow(sea,(cx,cy),rad,(252,255,255,115),58)
d=ImageDraw.Draw(sea,'RGBA')
for i in range(17):
    y=330+i*20
    d.arc((-180,y-180,2040,y+300),10,165,fill=(255,255,255,65),width=4)
add_top_window_bar(sea,34,25,1732,'MARITIME WATCH / FEATURED APPLICATION','01  ·  PUBLIC REPO')
glass(sea,(67,118,1040,505),44,(243,254,255,211),16)
paint_text(sea,(115,151),'SIGNALS  →  DECISIONS',27,(3,113,163,255),'semi')
paint_text(sea,(110,211),'Maritime',105,NAVY,'bold')
paint_text(sea,(113,320),'Watch Türkiye',86,(1,118,177,255),'bold')
paint_text(sea,(120,431),'SEA CONDITIONS   /   GEOSPATIAL MAP   /   RULE ENGINE',23,SOFT,'mono')
# right-sided bespoke simulated app dashboard/glass map, not real screenshot
glass(sea,(1100,116,1723,513),37,(240,254,255,196),15)
roundrect(sea,(1127,141,1694,186),19,(237,250,255,200),outline=(255,255,255,230))
paint_text(sea,(1148,147),'MAP / TURKISH STRAITS',23,NAVY,'semi')
paint_text(sea,(1673,149),'DEMO VISUAL',17,SOFT,'med',anchor='ra')
# draw map-ish contours with robust gradient and grids
d=ImageDraw.Draw(sea,'RGBA')
for i in range(8):d.line((1128,206+i*35,1692,206+i*35),fill=(7,128,165,39),width=2)
for i in range(10):d.line((1134+i*57,197,1134+i*57,481),fill=(7,128,165,35),width=2)
coast=[(1150,446),(1212,420),(1260,398),(1283,369),(1340,355),(1365,322),(1430,318),(1470,285),(1530,267),(1590,245),(1678,226)]
d.line(coast,fill=(8,145,144,218),width=14,joint='curve')
d.line([(x,y-13) for x,y in coast],fill=(244,255,255,190),width=4,joint='curve')
d.line([(1156,427),(1250,390),(1352,356),(1450,318),(1544,303),(1652,249)],fill=(19,118,175,235),width=5,joint='curve')
for x,y,c in [(1208,403,(27,197,138)),(1394,340,(24,188,149)),(1554,281,(245,177,69)),(1637,271,(15,176,222))]:
    d.ellipse((x-15,y-15,x+15,y+15),fill=(*c,255),outline=(255,255,255,255),width=5)
# physical map note
pill(sea,(1372,450,1673,490),'Vessel-aware analysis',size=19)
save(sea,'aero-v4-maritime.jpg',91)

# -- Open-window cards ---------------------------------------------------
rest=card_base('restofy')
paint_text(rest,(75,143),'Restofy',101,NAVY,'bold')
paint_text(rest,(81,278),'QR → restaurant operations',33,SOFT,'med')
pill(rest,(77,436,510,483),'SPRING BOOT   /   TEAM',size=22)
# orange QR restaurant graphic: gently glossy tablet and custom logo-esque plate
orb(rest,786,308,132,(255,231,210))
d=ImageDraw.Draw(rest,'RGBA')
d.ellipse((701,223,871,393),outline=(255,102,22,247),width=15)
d.ellipse((730,252,842,364),outline=(255,146,75,190),width=8)
# 3 QR finders around the plate
for xx,yy in [(725,195),(862,340),(685,366)]:
    d.rounded_rectangle((xx,yy,xx+38,yy+38),radius=5,fill=(254,110,36,255))
    d.rounded_rectangle((xx+7,yy+7,xx+31,yy+31),radius=2,fill=(255,255,255,220))
    d.rounded_rectangle((xx+14,yy+14,xx+24,yy+24),radius=2,fill=(254,110,36,255))
save(rest,'aero-v4-restofy.png')

crypt=card_base('crypto')
paint_text(crypt,(70,145),'Crypto Tracker',75,NAVY,'bold')
paint_text(crypt,(79,259),'Real-time market monitoring',31,SOFT,'med')
pill(crypt,(77,436,486,484),'JAVA   /   LIVE API DATA',size=21)
# chart window right
roundrect(crypt,(648,180,922,416),29,(5,72,111,225),outline=(255,255,255,220),width=4)
d=ImageDraw.Draw(crypt,'RGBA')
for yy in range(225,411,42):d.line((671,yy,904,yy),fill=(206,253,255,53),width=2)
bars=[(687,344,316),(719,313,295),(750,334,269),(781,273,228),(812,244,276),(843,263,202),(872,209,182)]
for i,(xx,from_y,to_y) in enumerate(bars):
    up=to_y<from_y; col=(99,245,192,245) if up else (255,154,141,238)
    d.line((xx+10,max(to_y-16,193),xx+10,min(from_y+22,398)),fill=col,width=4)
    d.rounded_rectangle((xx,max(min(from_y,to_y),195),xx+20,min(max(from_y,to_y),402)),radius=4,fill=col)
paint_text(crypt,(672,196),'MARKET / DEMO',14,(184,250,255,255),'mono')
save(crypt,'aero-v4-crypto.png')

ml=card_base('ml')
paint_text(ml,(74,153),'Machine Learning',57,NAVY,'bold')
paint_text(ml,(81,260),'Train. Compare. Understand.',32,SOFT,'med')
pill(ml,(77,436,481,485),'PYTHON   /   SCIKIT-LEARN',size=21)
# glass analytics visual
roundrect(ml,(633,169,922,420),24,(249,255,255,196),outline=(255,255,255,250))
d=ImageDraw.Draw(ml,'RGBA')
for yy in range(216,407,38):d.line((655,yy,902,yy),fill=(87,118,201,49),width=2)
for xx in range(673,903,46):d.line((xx,193,xx,409),fill=(87,118,201,36),width=2)
random.seed(44)
for i in range(31):
    xx=670+i*7+random.randint(-12,12)
    yy=int(364-0.52*(xx-673)+random.gauss(0,31))
    yy=max(199,min(394,yy))
    rr=random.randint(4,7)
    d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(40,130,209,200))
d.line([(658,375),(906,233)],fill=(80,68,202,235),width=7)
roundrect(ml,(658,180,826,206),12,(223,240,255,220))
paint_text(ml,(674,182),'MODEL LAB / DEMO',16,(72,88,171,255),'mono')
save(ml,'aero-v4-ml.png')

lib=card_base('library')
paint_text(lib,(70,146),'Library System',75,NAVY,'bold')
paint_text(lib,(78,259),'A useful little data system',31,SOFT,'med')
pill(lib,(77,436,472,484),'PYTHON   /   SQLITE',size=21)
# shelves / books vector illustration in circular glass scene
orb(lib,791,308,134,(214,255,238))
d=ImageDraw.Draw(lib,'RGBA')
colors=[(5,132,170,248),(41,182,156,247),(91,124,207,249),(245,164,83,249)]
for i,col in enumerate(colors):
    xx=696+i*53;top=234-(i%2)*15;bot=371
    d.rounded_rectangle((xx,top,xx+43,bot),radius=8,fill=col,outline=(255,255,255,210),width=3)
    d.line((xx+11,top+40,xx+31,top+40),fill=(255,255,255,225),width=4)
    d.line((xx+11,top+54,xx+31,top+54),fill=(255,255,255,170),width=3)
d.rounded_rectangle((680,372,923,392),radius=8,fill=(4,105,123,209),outline=(255,255,255,230),width=3)
save(lib,'aero-v4-library.png')

# -- VollSign professional experience ------------------------------------
W,H=1800,480
ex=gradient(W,H,(227,247,255),(170,221,242))
for cx,cy,r in [(1520,210,260),(310,250,210),(990,60,180)]:glow(ex,(cx,cy),r,(255,255,255,110),58)
d=ImageDraw.Draw(ex,'RGBA')
for i in range(8):d.arc((1040-i*40,-190+i*25,1970-i*18,760-i*18),195,344,fill=(255,255,255,100),width=5)
add_top_window_bar(ex,33,24,1735,'KEREM.OS / PROFESSIONAL EXPERIENCE','WORK / NOT OPEN-SOURCE')
glass(ex,(70,109,1076,418),39,(248,254,255,215),16)
paint_text(ex,(120,131),'CURRENT WORK   /   SOFTWARE ENGINEERING',26,CYAN,'semi')
paint_text(ex,(119,188),'VollSign',107,NAVY,'bold')
paint_text(ex,(125,324),'Software development · Functional QA',32,SOFT,'med')
# document workflow concept panel
glass(ex,(1170,107,1720,420),34,(249,255,255,200),12)
paint_text(ex,(1206,129),'DOCUMENT WORKFLOWS',26,NAVY,'semi')
for i,(num,label,tx) in enumerate([('01','DOCUMENT','create'),('02','SIGNATURE','approve'),('03','WORKFLOW','complete')]):
    y=189+74*i
    roundrect(ex,(1207,y,1688,y+62),20,(236,250,255,216),outline=(255,255,255,230))
    orb(ex,1239,y+30,19,label=num[-1])
    paint_text(ex,(1280,y+29),label,23,NAVY,'semi',anchor='lm')
    paint_text(ex,(1661,y+30),tx.upper(),18,SOFT,'med',anchor='rm')
save(ex,'aero-v4-vollsign.jpg',91)

# -- Engineering loop visual --------------------------------------------
W,H=1800,330
flow=gradient(W,H,(227,252,255),(170,228,239))
for cx,cy,r in [(1500,0,200),(210,270,220)]:glow(flow,(cx,cy),r,(255,255,255,100),42)
glass(flow,(38,25,1760,303),38,(247,255,255,161),14,shadow=False)
paint_text(flow,(78,54),'UNDER THE GLASS',42,NAVY,'bold')
paint_text(flow,(80,114),'The engineering is the experience.',25,SOFT,'med')
steps=[('01','PROBLEM'),('02','BOUNDARIES'),('03','IMPLEMENT'),('04','VERIFY'),('05','ITERATE')]
for i,(number,title) in enumerate(steps):
    x=77+i*347;y=177
    if i>0:
        d=ImageDraw.Draw(flow,'RGBA');d.line((x-40,y+43,x-12,y+43),fill=(29,147,184,215),width=5)
        d.polygon((x-17,y+35,x-4,y+43,x-17,y+51),fill=(29,147,184,215))
    glass(flow,(x,y,x+295,y+86),23,(255,255,255,193),6,shadow=False)
    orb(flow,x+38,y+43,26,label=number[-1])
    paint_text(flow,(x+78,y+44),title,25,NAVY,'semi',anchor='lm')
save(flow,'aero-v4-process.png')

# -- Footer --------------------------------------------------------------
W,H=1800,220
foot=crop_cover(BG,W,610).crop((0,340,1800,560)).convert('RGBA')
glass(foot,(37,23,1763,196),43,(244,255,255,208),13,shadow=False)
paint_text(foot,(92,53),'Make it useful. Make it human.',73,NAVY,'bold')
paint_text(foot,(98,148),'CURIOUS BY DESIGN  /  DELIBERATE BY ENGINEERING',24,CYAN,'semi')
save(foot,'aero-v4-footer.jpg',91)

# -- Branded assembled visual preview (not GitHub native render) ---------
CW=1540; margin=64; width=CW-2*margin
blocks=[]
def add(imname, full=True):
    im=Image.open(ASSETS/imname).convert('RGB')
    if full:im.thumbnail((width,4000),Image.Resampling.LANCZOS)
    else:im.thumbnail(((width-30)//2,600),Image.Resampling.LANCZOS)
    return im
heroim=add('aero-v4-hero.jpg');mar=add('aero-v4-maritime.jpg'); exp=add('aero-v4-vollsign.jpg');flo=add('aero-v4-process.png');footim=add('aero-v4-footer.jpg')
cards=[add('aero-v4-restofy.png',False),add('aero-v4-crypto.png',False),add('aero-v4-ml.png',False),add('aero-v4-library.png',False)]
# preview includes explanatory headings in theme, rescale to nice phone-size review
height=100+heroim.height+102+mar.height+115+2*(max(c.height for c in cards)+26)+120+exp.height+109+flo.height+107+footim.height+100
prev=Image.new('RGB',(CW,height),(245,251,253))
pr=ImageDraw.Draw(prev,'RGB')
def prev_txt(s,x,y,sz=38):paint_text(prev,(x,y),s,sz,(5,60,95,255),'bold')
y=33;prev_txt('KEREM.OS   /   AERO DESKTOP V4',margin,y,35);y+=65
prev.paste(heroim,(margin,y));y+=heroim.height+50
prev_txt('01  /  FLAGSHIP',margin,y,39);y+=55
prev.paste(mar,(margin,y));y+=mar.height+51
prev_txt('02  /  OPEN WINDOWS',margin,y,39);y+=66
for j in range(2):
    c1,c2=cards[j*2:j*2+2];prev.paste(c1,(margin,y));prev.paste(c2,(margin+c1.width+30,y));y+=max(c1.height,c2.height)+30
y+=24;prev_txt('03  /  PROFESSIONAL EXPERIENCE',margin,y,39);y+=62
prev.paste(exp,(margin,y));y+=exp.height+38
prev_txt('04  /  HOW I BUILD',margin,y,39);y+=64
prev.paste(flo,(margin,y));y+=flo.height+44
prev.paste(footim,(margin,y));y+=footim.height+49
pr.text((margin,y-5),'VISUAL CONCEPT PREVIEW   /   NOT A GITHUB RENDERED SCREENSHOT',font=f(18,'mono'),fill=(79,125,145))
prev=prev.crop((0,0,CW,y+35));prev.save(ROOT/'AERO-V4-PREVIEW.jpg',quality=89,optimize=True)
print('AERO-V4-PREVIEW.jpg',prev.size,(ROOT/'AERO-V4-PREVIEW.jpg').stat().st_size//1024,'KiB')
