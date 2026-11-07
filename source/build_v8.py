from pathlib import Path
from lxml import etree as ET
import random, math, html

R=Path(__file__).resolve().parents[1]
SRC=Path('/mnt/data/kerem-aero-living-v7/assets/kerem-living-world.svg')
TARGET=R/'assets'/'kerem-living-world-v8.svg'
NS='http://www.w3.org/2000/svg'; Q=lambda s:f'{{{NS}}}{s}'
root=ET.parse(str(SRC)).getroot();g=root[-1];defs=root.find(Q('defs'))
H=5150
root.set('height',str(H));root.set('viewBox',f'0 0 1200 {H}')
root.set('aria-label','Kerem Kalyoncu — a living Frutiger Aero universe with animated ocean, floating public software projects, professional experience, collaborative products, an engineering constellation, educational journey and contact portals.')
root.find(Q('title')).text='KEREM.AERO V8 — The Living Engineering Ocean'
root.find(Q('desc')).text='Animated continuous Frutiger Aero world by Kerem Kalyoncu. Public GitHub projects, VollSign experience, team projects Inventra and Shifha, engineering toolkit, GDG community and training, professional links. Motion uses CSS inside the SVG.'
clip=defs.find(f".//{Q('clipPath')}[@id='full']/{Q('rect')}");clip.set('height',str(H));clip.set('rx','0')
# The 2200 px v7 backdrop stays intact; lower world meets its natural final blue #075077 at y=2200.
from lxml.etree import SubElement

def E(p, tag, **a):
    x=SubElement(p,Q(tag));
    for k,v in a.items(): x.set('class' if k=='class__' else k.replace('__','-'),str(v))
    return x

def grad(id, colors, kind='linear', **attrib):
    attrs={'id':id}
    attrs.update(attrib)
    node=E(defs,'linearGradient' if kind=='linear' else 'radialGradient',**attrs)
    for off,c,op in colors:
        a={'offset':off,'stop__color':c}
        if op is not None: a['stop__opacity']=op
        E(node,'stop',**a)
    return node

grad('deepSea', [('0','#075077',None),('.14','#075677',None),('.38','#075474',None),('.72','#043559',None),('1','#041d45',None)],x1='0',y1='0',x2='0',y2='1')
grad('midGlass', [('0','#d7ffff','.72'),('.17','#8ff9ff','.32'),('.54','#147fa6','.55'),('1','#09356b','.80')],x1='0',y1='0',x2='.6',y2='1')
grad('pearlescent', [('0','#f7ffff','.98'),('.27','#b7faff','.66'),('.49','#5fcfee','.42'),('.76','#95a7ff','.64'),('1','#e1ffff','.9')],x1='0',y1='0',x2='1',y2='1')
grad('reefVeil', [('0','#2ad4e2','0'),('.32','#3de6f0','.12'),('.7','#2986c8','.1'),('1','#160f5f','.05')],x1='0',y1='0',x2='0',y2='1')
grad('coralLeaf', [('0','#baf9ce',None),('.4','#42d7c2',None),('1','#05759c',None)],x1='0',y1='0',x2='1',y2='1')
grad('purpleOrb', [('0','#f9ffff','.91'),('.24','#c5deff','.38'),('.6','#9b8eff','.3'),('1','#f1ffff','.86')],kind='radial',cx='30%',cy='25%',r='70%')
grad('seaBloom', [('0','#80fef0','.4'),('.48','#08dce6','.17'),('1','#0671aa','0')],kind='radial',cx='50%',cy='50%',r='50%')
# SVG animations already exist; all new animations are CSS keyframes. Compatible as image where SVG CSS animations are supported.
style=defs.find(Q('style'))
style.text=(style.text or '')+'''
    .driftDeep{animation:deepDrift 28s linear infinite alternate}
    .driftDeep2{animation:deepDrift 35s linear -17s infinite alternate-reverse}
    .deepBub{animation:deepRise var(--dur,15s) linear var(--delay,0s) infinite}
    .deepBubInner{animation:bubbleWobble 4.3s ease-in-out infinite alternate}
    .driftObject{animation:deepFloat 7.2s ease-in-out var(--delay,-2s) infinite alternate;transform-box:fill-box;transform-origin:center}
    .driftSlow{animation:deepFloat 12s ease-in-out var(--delay,-4s) infinite alternate;transform-box:fill-box;transform-origin:center}
    .swayPlant{animation:plantBend 5s ease-in-out var(--delay,-2s) infinite alternate;transform-box:fill-box;transform-origin:bottom center}
    .orbitRing{animation:turn 24s linear infinite;transform-box:fill-box;transform-origin:center}
    .orbitReverse{animation:turn 32s linear infinite reverse;transform-box:fill-box;transform-origin:center}
    .probe{animation:probe 7s ease-in-out infinite;stroke-dasharray:8 23;}
    .breathe{animation:breathe 6.3s ease-in-out infinite alternate}
    .lightSweep{animation:lightSweep 11s linear infinite}
    .fishDeep{animation:deepFish var(--dur,25s) linear var(--delay,-9s) infinite}
    .glint8{animation:twinkle var(--dur,4s) ease-in-out var(--delay,0s) infinite}
    @keyframes deepDrift{to{transform:translate(52px,-15px)}}
    @keyframes deepRise{0%{opacity:0;transform:translateY(55px)}8%{opacity:.85}86%{opacity:.72}100%{opacity:0;transform:translateY(-1450px)}}
    @keyframes deepFloat{to{transform:translate(3px,-20px) rotate(.8deg)}}
    @keyframes plantBend{to{transform:rotate(8deg)}}
    @keyframes turn{to{transform:rotate(360deg)}}
    @keyframes probe{to{stroke-dashoffset:-360}}
    @keyframes breathe{to{opacity:.28;transform:scale(1.1)}}
    @keyframes lightSweep{0%{opacity:0;transform:translateX(-300px)}45%{opacity:.42}100%{opacity:0;transform:translateX(1400px)}}
    @keyframes deepFish{from{transform:translateX(-180px)}to{transform:translateX(1550px)}}
    @media (prefers-reduced-motion: reduce){.driftDeep,.driftDeep2,.deepBub,.deepBubInner,.driftObject,.driftSlow,.swayPlant,.orbitRing,.orbitReverse,.probe,.breathe,.lightSweep,.fishDeep,.glint8{animation:none!important}}
'''
# The old v7 ending headline says 'explore ...' like a footer. Remove it so the expanded world does not have a false ending.
for el in list(g):
    if el.tag == Q('text') and el.text and 'EXPLORE THE CODE' in el.text: g.remove(el)
    if el.tag == Q('g') and any((c.tag == Q('path') and (c.get('d') or '').startswith('M90 2130')) for c in el): g.remove(el)
# The continuous undersea extends seamlessly; draw beneath existing top-world objects.
background=ET.Element(Q('rect'),x='0',y='2196',width='1200',height=str(H-2195),fill='url(#deepSea)')
g.insert(1,background)
E(g,'rect',x='0',y='2175',width='1200',height='2975',fill='url(#reefVeil)',opacity='.6')
# Organic light beams and drifting beams: no section backgrounds nor dividing bars.
for i,(x,w,rot) in enumerate([(25,175,-18),(400,220,9),(685,240,16),(1020,160,-9)]):
    gg=E(g,'g',opacity='.12',transform=f'translate({x} 2200) rotate({rot})')
    E(gg,'path',d=f'M0 0 L{w} 0 L{w*1.5} 2600 L{-w*.7} 2600 Z',fill='url(#pearlescent)',opacity='.15',class__='driftDeep' if i%2 else 'driftDeep2')
# Distant reef / sea plants across 2200-5100
random.seed(826)
for side in ['left','right']:
    x0=30 if side=='left' else 1148
    for i in range(15):
        y=random.randint(2260,5060); dx=random.uniform(22,150)*(1 if side=='left' else -1); h=random.randint(95,330)
        gg=E(g,'g',transform=f'translate({x0+random.randint(-25,25)} {y})',opacity=str(round(random.uniform(.2,.65),2)),class__='swayPlant',style=f'--delay:-{random.uniform(0,5):.1f}s')
        E(gg,'path',d=f'M0 0 Q{dx*.4} {-h*.44} {dx} {-h} Q{dx*.24} {-h*.52} 0 0Z',fill='url(#coralLeaf)')
        if i%3==0:
            E(gg,'path',d=f'M0 0 Q{-dx*.6} {-h*.24} {-dx*.4} {-h*.74}',stroke='#aaffef',stroke__width='4',stroke__opacity='.42',fill='none')
# Blurred ambient glow zones
for x,y,r in [(210,2380,240),(940,2620,270),(530,3020,330),(1040,3540,240),(160,4010,260),(680,4630,450),(510,5030,250)]:
    E(g,'circle',cx=str(x),cy=str(y),r=str(r),fill='url(#seaBloom)',class__='breathe',opacity='.6')
# Roaming fish silhouettes; silhouettes kept away from text.
for i in range(13):
    y=random.randint(2270,5030);x=random.randint(-350,-20);s=round(random.uniform(.55,1.55),2)
    gg=E(g,'g',transform=f'translate({x} {y}) scale({s})',class__='fishDeep',style=f'--dur:{random.randint(28,60)}s;--delay:-{random.randint(0,50)}s',opacity='.32')
    E(gg,'path',d='M0 0 C22 -14 48 -14 72 0 C45 15 22 14 0 0 M-3 0 L-23 -18 L-21 18Z',fill='#94ecff')
    E(gg,'circle',cx='52',cy='-2',r='2.5',fill='#04355b')
# Deep bubbles; same coordinate system and world space as V7
for i in range(110):
    x=random.randint(32,1172);y=random.randint(2250,5220);rad=random.randint(4,21)
    gr=E(g,'g',class__='deepBub',style=f'--dur:{random.uniform(11,25):.1f}s;--delay:-{random.uniform(0,20):.1f}s')
    b=E(gr,'g',class__='deepBubInner')
    E(b,'circle',cx=str(x),cy=str(y),r=str(rad),fill='url(#bubbleShine)',stroke='#f8ffff',stroke__width='.9',stroke__opacity='.7',opacity=str(random.uniform(.23,.66)))
    if rad>10: E(b,'path',d=f'M{x-rad*.3:.1f} {y-rad*.54:.1f} q{rad*.37:.1f} {-rad*.27:.1f} {rad*.74:.1f} {-rad*.06:.1f}',fill='none',stroke='#fff',stroke__width='2',stroke__opacity='.56')
# General helpers: all body labels are embedded in the animated SVG. No Markdown sections.
def text(p,x,y,value,size=24,weight=500,color='#edffff',spacing=None,anchor=None,cls='font',opacity=None):
    a={'x':str(x),'y':str(y),'font__size':str(size),'font__weight':str(weight),'fill':color,'class__':cls}
    if spacing is not None: a['letter__spacing']=str(spacing)
    if anchor: a['text__anchor']=anchor
    if opacity: a['opacity']=str(opacity)
    n=E(p,'text',**a);n.text=value;return n

def pod(x,y,w,h,kind='wide',floatcls='driftObject',delay='-2s',stroke='#d8ffff'):
    gg=E(g,'g',class__=floatcls,style=f'--delay:{delay}')
    E(gg,'rect',x=x+5,y=y+14,width=w,height=h,rx=42,fill='#042b64',opacity='.24',filter='url(#softBlur)')
    E(gg,'rect',x=x,y=y,width=w,height=h,rx=42,fill='url(#midGlass)',stroke=stroke,stroke__width='2.4',stroke__opacity='.78')
    E(gg,'path',d=f'M{x+48} {y+16} Q{x+int(w/2)} {y-5} {x+w-48} {y+16}',fill='none',stroke='#fff',stroke__opacity='.66',stroke__width='3.4')
    E(gg,'path',d=f'M{x+26} {y+h-29} Q{x+w/2} {y+h+3} {x+w-26} {y+h-29}',fill='none',stroke='#6cedfc',stroke__opacity='.37',stroke__width='2')
    return gg

def small_orb(p,cx,cy,r,label=None,color='#d9ffff'):
    E(p,'circle',cx=cx,cy=cy,r=r+9,fill='none',stroke='#b9ffff',stroke__width='1.5',stroke__opacity='.42',stroke__dasharray='4 16',class__='orbitRing')
    E(p,'circle',cx=cx,cy=cy,r=r,fill='url(#bubbleShine)',stroke='#f3ffff',stroke__width='2.2',stroke__opacity='.85')
    E(p,'circle',cx=cx-r*.28,cy=cy-r*.31,r=r*.15,fill='#fff',opacity='.55')
    if label:text(p,cx,cy+12,label,36,800,color,anchor='middle')

def scene_header(x,y,kicker,heading,desc):
    text(g,x,y,kicker,18,750,'#b2fff4',spacing=4)
    text(g,x,y+65,heading,49,820,'#ffffff')
    text(g,x,y+110,desc,23,520,'#d6fcff')

# ----- 2200-2890: Team products floating among living reefs -----
scene_header(90,2260,'CO-BUILT WORLDS','From code to real products','Cross-functional projects beyond the public repository list')
p=pod(85,2436,510,329,delay='-1.3s',stroke='#a5ffea')
small_orb(p,177,2516,45,'I')
text(p,245,2496,'INVENTRA',31,800,'#ffffff')
text(p,245,2534,'Inventory + workforce platform',20,600,'#b8ffff')
for j,line in enumerate(['ASP.NET Core  ·  React  ·  Material UI','Inventory, staff & operational workflows','Collaborative product  ·  Public live demo']):text(p,140,2598+j*39,line,20,500,'#f4ffff')
p=pod(621,2480,497,329,delay='-3.8s',stroke='#c8c4ff')
small_orb(p,710,2557,45,'+','#e7dcff')
text(p,773,2541,'SHIFHA',31,800,'#ffffff')
text(p,773,2580,'AI-assisted healthcare concept',19,600,'#d3e3ff')
for j,line in enumerate(['Web & mobile clinical workflows','Information access for medical teams','Collaborative project  ·  2026']):text(p,670,2643+j*39,line,20,500,'#f4ffff')
# Energy stream travels between cards, organic not horizontal divider
E(g,'path',d='M581 2803 C668 2850 724 2837 802 2852 S1036 2933 1060 2892',fill='none',stroke='#9cfaf9',stroke__width='4',stroke__opacity='.65',stroke__dasharray='8 23',class__='probe')
# Small jellyfish above the workbench
j=E(g,'g',transform='translate(1065 2312)',class__='driftSlow',opacity='.78')
E(j,'path',d='M-42 17 C-47 -30 34 -41 47 18 Q0 53 -42 17',fill='url(#purpleOrb)',stroke='#f1ffff',stroke__opacity='.65',stroke__width='3')
for x in [-28,-12,10,24]:E(j,'path',d=f'M{x} 31 q{-x*.5:.0f} 52 {x*.28:.0f} 107',stroke='#cbfaff',stroke__opacity='.7',stroke__width='3',fill='none')
# ----- 2890-3560: Technology constellation -----
scene_header(92,2956,'THE ENGINEERING REEF','Systems that connect','Tools grouped by the problems they help solve')
# glowing hub behind semantic competency modules
E(g,'circle',cx='601',cy='3340',r='175',fill='none',stroke='#8dffff',stroke__width='3',stroke__dasharray='15 27',stroke__opacity='.5',class__='orbitRing')
E(g,'circle',cx='601',cy='3340',r='122',fill='none',stroke='#bbfaff',stroke__width='1.7',stroke__opacity='.38',class__='orbitReverse')
E(g,'circle',cx='601',cy='3340',r='91',fill='url(#bubbleShine)',stroke='#efffff',stroke__opacity='.8',stroke__width='3')
text(g,601,3322,'BUILD',24,800,'#ffffff',anchor='middle',spacing=2)
text(g,601,3354,'TEST',24,800,'#ffffff',anchor='middle',spacing=2)
text(g,601,3386,'SHIP',24,800,'#ffffff',anchor='middle',spacing=2)
rows=[
(110,3144,390,157,'BACKEND & SYSTEMS','Java · Spring Boot · C# / .NET', '#a1fff1'),
(700,3144,390,157,'WEB & EXPERIENCE','React · Next.js · TypeScript', '#c6f9ff'),
(110,3435,390,157,'DATA & INTELLIGENCE','Python · Pandas · scikit-learn','#f7d4ff'),
(700,3435,390,157,'DELIVERY & QUALITY','Docker · PostgreSQL · CI · QA','#d9ffe7')]
for x,y,w,h,name,tech,clr in rows:
    p=pod(x,y,w,h,delay=f'-{random.randint(1,6)}s')
    text(p,x+29,y+62,name,21,850,clr,spacing=1.0)
    text(p,x+29,y+106,tech,22,520,'#ffffff')
for path in ['M500 3224 Q554 3251 554 3310','M700 3224 Q646 3251 646 3310','M500 3514 Q554 3463 554 3422','M700 3514 Q646 3463 646 3422']:
    E(g,'path',d=path,stroke='#bafaff',stroke__width='3',stroke__opacity='.45',stroke__dasharray='7 20',class__='probe',fill='none')
# ----- 3650-4400: Education and community journey -----
scene_header(92,3701,'THE CURRENT THAT SHAPED ME','Learning, building, leading','Engineering practice, community and continuous education')
# glowing meandering cable across journey, no hard dividing lines
E(g,'path',d='M614 3820 C494 3897 718 3986 617 4063 S491 4222 615 4314',stroke='#a6f7ff',stroke__width='13',stroke__opacity='.13',fill='none')
E(g,'path',d='M614 3820 C494 3897 718 3986 617 4063 S491 4222 615 4314',stroke='#c7ffff',stroke__width='3',stroke__opacity='.7',stroke__dasharray='11 23',class__='probe',fill='none')
items=[
(97,3860,475,158,'2023—2027','DOĞUŞ UNIVERSITY','Software Engineering · BSc', '#b0f7ff'),
(649,3992,455,173,'2025—2026','GDG ON CAMPUS','Social Media & Design Team Captain', '#caffc3'),
(100,4170,474,174,'2026','HUAWEI × AI ACADEMY','Data Science & Machine Learning', '#e4d4ff'),
(638,4303,463,167,'2025 / 2026','LEARNING MILESTONES','BTK AI fundamentals · GDG Core Team','#d5fbff')]
for x,y,w,h,date,name,desc,accent in items:
    p=pod(x,y,w,h,floatcls='driftSlow',delay=f'-{random.randint(1,8)}s')
    E(p,'circle',cx=x+43,cy=y+50,r='9',fill=accent,opacity='.92')
    text(p,x+65,y+57,date,18,730,accent,spacing=1.4)
    text(p,x+29,y+107,name,25,840,'#ffffff')
    text(p,x+29,y+143,desc,20,490,'#e6ffff')
# seabed organisms around lower edge
for x,y,size in [(18,4445,1.2),(1078,4440,1.2),(45,4810,1),(1150,4850,1.1),(920,5050,1.4),(237,5030,1.6)]:
    group=E(g,'g',transform=f'translate({x} {y}) scale({size})',class__='swayPlant')
    for a in [-35,-16,0,18,39]:
        E(group,'path',d=f'M0 85 Q{a*1.4} 30 {a} {-random.randint(45,100)}',fill='none',stroke=random.choice(['#56f3d8','#95f9c3','#a9e6ff']),stroke__width='8',stroke__linecap='round',stroke__opacity='.66')
# ----- 4510-5090: Connection portal / closing scene with real references -----
scene_header(88,4639,'OPEN WATER','Let’s build what matters','Practical engineering, thoughtful interfaces, curious teams')
E(g,'ellipse',cx='600',cy='4893',rx='456',ry='205',fill='url(#seaBloom)',opacity='.75')
ring=E(g,'g',class__='orbitRing')
E(ring,'ellipse',cx='601',cy='4905',rx='382',ry='149',stroke='#d9ffff',stroke__width='3.5',stroke__opacity='.45',stroke__dasharray='9 29',fill='none')
E(ring,'ellipse',cx='601',cy='4905',rx='337',ry='114',stroke='#eaffff',stroke__width='2',stroke__opacity='.2',fill='none')
for x,y,r in [(234,4836,20),(1047,4830,22),(840,5025,16),(320,5011,14)]:small_orb(g,x,y,r)
p=pod(315,4781,575,212,floatcls='driftSlow',delay='-3s',stroke='#eafffb')
text(p,601,4854,'KEREM KALYONCU',40,850,'#ffffff',anchor='middle')
text(p,601,4902,'SOFTWARE ENGINEER  ·  ISTANBUL',19,720,'#c7fff4',anchor='middle',spacing=1.2)
text(p,601,4947,'GITHUB   •   LINKEDIN   •   PROJECT DEMOS',19,650,'#f7ffff',anchor='middle')
text(g,601,5092,'KEEP EXPLORING  ·  GITHUB.COM/KEREMKALYONCU',21,750,'#cefaff',anchor='middle',spacing=2)
# small drifting light sparkle flecks
for i in range(65):
    x=random.randint(25,1180); y=random.randint(2200,5100)
    gl=E(g,'g',class__='glint8',style=f'--dur:{random.uniform(3,8):.1f}s;--delay:-{random.uniform(0,6):.1f}s')
    E(gl,'circle',cx=x,cy=y,r=str(random.choice([1.5,2.1,2.6,3.1])),fill='#efffff',opacity='.62')
# Ensure all coordinates are within extended viewbox. UTF8 labels inside vector are selectable in SVG viewer.
TARGET.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=False))
ET.parse(str(TARGET))
print('Wrote',TARGET,'size',TARGET.stat().st_size,'height',H)
