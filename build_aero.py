from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
import math, random, zipfile, os

OUT=Path(__file__).resolve().parent
AS=OUT/'assets'; AS.mkdir(parents=True,exist_ok=True)
SRC=[Image.open(Path(__file__).parent/'sources/original-aero-world-1.jpg').convert('RGB'),Image.open(Path(__file__).parent/'sources/original-aero-world-2.jpg').convert('RGB')]
W=1600
FONT='/usr/share/fonts/opentype/inter'
fonts={'thin':'InterDisplay-Light.otf','regular':'InterDisplay-Regular.otf','medium':'InterDisplay-Medium.otf','semibold':'InterDisplay-SemiBold.otf','bold':'InterDisplay-Bold.otf','extra':'InterDisplay-ExtraBold.otf'}
cache={}
def font(size,weight='regular'):
 k=(size,weight)
 if k not in cache:
  p=Path(FONT)/fonts[weight]
  if not p.exists():
   opts=[Path('C:/Windows/Fonts/segoeui.ttf'),Path('C:/Windows/Fonts/arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
   p=next((f for f in opts if f.exists()),None)
  cache[k]=ImageFont.truetype(str(p),size) if p else ImageFont.load_default()
 return cache[k]
ink=(12,60,92); deep=(7,44,73); blue=(1,122,168); turquoise=(1,157,182); green=(1,130,125)

def rgba(c,a):return tuple(c[:3])+(a,)
def bg(h,source=0,anchor=.5,tint=None):
 img=SRC[source]; iw,ih=img.size; ratio=max(W/iw,h/ih); nw,nh=round(iw*ratio),round(ih*ratio)
 scale=img.resize((nw,nh),Image.Resampling.LANCZOS)
 x=int((nw-W)*anchor); y=int((nh-h)*.5)
 layer=scale.crop((x,y,x+W,y+h)).convert('RGBA')
 if tint:
  overlay=Image.new('RGBA',(W,h),tint)
  layer=Image.alpha_composite(layer,overlay)
 # subtle extra sheen at top
 overlay=Image.new('RGBA',(W,h),(0,0,0,0)); d=ImageDraw.Draw(overlay)
 for j in range(0,h,2):
  a=int(15*max(0,1-j/(h*.74)))
  d.rectangle((0,j,W,j+2),fill=(238,253,255,a))
 return Image.alpha_composite(layer,overlay)

def glass(base,rect,opacity=216,r=38,shade='white',shadow=80):
 x,y,x2,y2=map(int,rect); w=x2-x;h=y2-y
 mask=Image.new('L',(w,h),0);md=ImageDraw.Draw(mask);md.rounded_rectangle((0,0,w-1,h-1),radius=r,fill=255)
 # shadow
 sm=Image.new('L',(W,base.height),0);sd=ImageDraw.Draw(sm);sd.rounded_rectangle((x+2,y+9,x2+2,y2+9),radius=r,fill=shadow)
 alpha=sm.filter(ImageFilter.GaussianBlur(22))
 sh=Image.new('RGBA',base.size,(10,65,83,0));sh.putalpha(alpha);base.alpha_composite(sh)
 # backdrop frosting
 cut=base.crop((x,y,x2,y2)).filter(ImageFilter.GaussianBlur(11))
 base.paste(cut,(x,y),mask)
 layer=Image.new('RGBA',(w,h),(0,0,0,0));px=layer.load()
 if shade=='white': ctop=(255,255,255); cb=(229,251,252)
 elif shade=='aqua': ctop=(250,255,255); cb=(193,247,250)
 elif shade=='mint': ctop=(248,255,251); cb=(191,250,220)
 elif shade=='orange': ctop=(255,252,246);cb=(255,231,208)
 else: ctop=(240,252,255);cb=(184,218,252)
 for j in range(h):
  t=j/max(1,h-1)
  rr=int(ctop[0]*(1-t)+cb[0]*t); gg=int(ctop[1]*(1-t)+cb[1]*t); bb=int(ctop[2]*(1-t)+cb[2]*t)
  a=int(opacity*(.91+.09*math.cos(t*math.pi)))
  for i in range(w):px[i,j]=(rr,gg,bb,a)
 layer.putalpha(Image.composite(layer.getchannel('A'),Image.new('L',(w,h),0),mask))
 base.alpha_composite(layer,(x,y))
 d=ImageDraw.Draw(base,'RGBA');d.rounded_rectangle((x+.9,y+.9,x2-1,y2-1),radius=r,outline=(255,255,255,225),width=3)
 d.arc((x+8,y+8,x2-8,y2-6),180,335,fill=(255,255,255,135),width=3)
 d.arc((x+9,y+9,x2-9,y2-6),15,90,fill=(36,160,195,60),width=2)
 # glossy shine across top pane
 shine=Image.new('RGBA',(w,h),(0,0,0,0));ds=ImageDraw.Draw(shine,'RGBA')
 ds.rounded_rectangle((10,6,w-10,max(26,int(h*.33))),radius=max(10,int(r*.7)),fill=(255,255,255,30))
 shine.putalpha(Image.composite(shine.getchannel('A'),Image.new('L',(w,h),0),mask))
 base.alpha_composite(shine,(x,y))

def txt(im,xy,s,size,color=deep,weight='regular',anchor=None,stroke=0):
 ImageDraw.Draw(im).text(xy,s,font=font(size,weight),fill=color,anchor=anchor,stroke_width=stroke,stroke_fill=(255,255,255) if stroke else None)

def line(im,xy,pts,color=(34,146,187,175),width=4):
 ImageDraw.Draw(im,'RGBA').line(pts,fill=color,width=width,joint='curve')

def bubble(im,cx,cy,r,opacity=170):
 # soap spheres using multiring highlights and translucent interior
 L=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(L,'RGBA')
 d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(228,251,253,16),outline=(250,255,255,opacity),width=max(2,int(r*.04)))
 d.arc((cx-r+5,cy-r+5,cx+r-5,cy+r-5),215,330,fill=(255,255,255,220),width=max(2,int(r*.075)))
 d.arc((cx-r+4,cy-r+4,cx+r-4,cy+r-4),5,100,fill=(81,233,250,115),width=max(2,int(r*.055)))
 d.arc((cx-r+4,cy-r+4,cx+r-4,cy+r-4),110,200,fill=(246,107,245,80),width=max(1,int(r*.04)))
 d.ellipse((cx-r*.49,cy-r*.61,cx-r*.12,cy-r*.31),fill=(255,255,255,175))
 im.alpha_composite(L)

def sparkle(im,x,y,r=20):
 L=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(L,'RGBA')
 d.line((x-r,y,x+r,y),fill=(255,255,255,210),width=2)
 d.line((x,y-r,x,y+r),fill=(255,255,255,210),width=2)
 d.ellipse((x-3,y-3,x+3,y+3),fill=(255,255,255,230))
 im.alpha_composite(L)

def pill(im,rect,label,color=(29,121,154),fill=(255,255,255,157),size=22):
 x,y,x2,y2=rect;d=ImageDraw.Draw(im,'RGBA');d.rounded_rectangle(rect,radius=(y2-y)//2,fill=fill,outline=(255,255,255,200),width=2)
 txt(im,((x+x2)//2,(y+y2)//2),label,size,color,'semibold',anchor='mm')

def windowbar(im,rect,title,tag=''):
 x,y,x2,y2=rect
 d=ImageDraw.Draw(im,'RGBA')
 d.rounded_rectangle((x,y,x2,y+58),radius=21,fill=(255,255,255,90),outline=(255,255,255,168),width=2)
 for i,c in enumerate([(250,127,114),(255,212,105),(90,215,169)]):d.ellipse((x+20+i*23,y+21,x+29+i*23,y+30),fill=(*c,235))
 txt(im,(x+110,y+29),title.upper(),23,deep,'semibold',anchor='lm')
 if tag:txt(im,(x2-21,y+29),tag,19,(44,113,145),'medium',anchor='rm')

def data_ui(im,rect,mode='map'):
 x,y,x2,y2=rect
 d=ImageDraw.Draw(im,'RGBA')
 # grid
 for xx in range(x+25,x2-20,48):d.line((xx,y+35,xx,y2-30),fill=(3,111,150,45),width=2)
 for yy in range(y+40,y2-20,44):d.line((x+26,yy,x2-25,yy),fill=(3,111,150,45),width=2)
 if mode=='map':
  # abstract strait geometry, not an accurate chart
  route=[(x+75,y2-85),(x+150,y2-126),(x+220,y2-135),(x+280,y2-193),(x+360,y2-209),(x+425,y2-285),(x+540,y2-300)]
  d.line(route,fill=(255,255,255,190),width=34,joint='curve');d.line(route,fill=(0,156,195,160),width=25,joint='curve');d.line(route,fill=(0,90,148,190),width=4,joint='curve')
  for n,(xx,yy) in enumerate(route[1::2]):
   d.ellipse((xx-12,yy-12,xx+12,yy+12),fill=(255,255,255,250),outline=(2,162,188,255),width=5)
  for i in range(6):
   xx=x+65+i*100; yy=y2-48-i*12
   d.ellipse((xx-3,yy-3,xx+3,yy+3),fill=(22,151,174,130))
 elif mode=='market':
  random.seed(11)
  px=x+50
  for i in range(10):
   h=math.sin(i*.8)*45 +i*11
   cx=px+i*45; cy=y2-88-h; top=cy-36;bottom=cy+36
   good=i%3!=0; c=(36,188,149,215) if good else (255,132,125,215)
   d.line((cx,top-15,cx,bottom+16),fill=c,width=4)
   d.rounded_rectangle((cx-13,top,cx+13,bottom),radius=3,fill=c)
  d.arc((x+40,y+90,x2-30,y2+30),195,331,fill=(255,255,255,132),width=3)
 elif mode=='ml':
  random.seed(22)
  for i in range(54):
   xx=x+48+random.random()*(x2-x-100)
   yy=y2-76-(xx-x)*.22+random.gauss(0,44)
   d.ellipse((xx-5,yy-5,xx+5,yy+5),fill=(13,120+int(random.random()*80),190,160))
  d.line((x+50,y2-95,x2-55,y+125),fill=(34,134,224,235),width=6)
 elif mode=='library':
  colors=[(7,139,174),(21,174,149),(253,178,84),(23,108,160),(101,187,196),(248,153,94)]
  for i,c in enumerate(colors):
   xx=x+58+i*76; dy=10+(i%3)*18
   d.rounded_rectangle((xx,y+90+dy,xx+51,y2-72),radius=7,fill=(*c,225),outline=(255,255,255,230),width=3)
   d.rounded_rectangle((xx+11,y+100+dy,xx+16,y2-84),radius=2,fill=(255,255,255,100))
  d.rounded_rectangle((x+36,y2-82,x2-36,y2-60),radius=10,fill=(14,114,136,220))

def save(im,name,quality=88):
 p=AS/name; im.convert('RGB').save(p,optimize=True,quality=quality,subsampling=0,progressive=True);print(name,p.stat().st_size)
 return name

# 01: sunlit start, full world. Type set high-contrast within frosted air.
h=795;im=bg(h,0,anchor=.49)
# slight left tone panel shading
glass(im,(90,115,940,620),opacity=222,r=52)
windowbar(im,(116,143,912,202),'WELCOME TO MY DIGITAL WORLD','AERO // 2026')
txt(im,(153,256),'KEREM',122,deep,'extra')
txt(im,(153,371),'KALYONCU',116,(0,123,165),'extra')
txt(im,(163,502),'SOFTWARE ENGINEER',34,deep,'semibold')
txt(im,(164,555),'Building systems with clarity and purpose.',28,(24,102,131),'medium')
# small floating panel on right not a fake click
glass(im,(1110,478,1520,649),opacity=196,r=34)
txt(im,(1152,533),'A LITTLE DIFFERENT',20,(0,132,159),'semibold')
txt(im,(1152,584),'Backends. Data. Design.',27,deep,'semibold')
pill(im,(115,666,340,726),'OPEN SOURCE',size=20)
pill(im,(356,666,571,726),'REAL PROJECTS',size=20)
pill(im,(586,666,807,726),'ISTANBUL, TR',size=20)
for a in [(1070,125,46),(1490,357,28),(1024,420,18)]:bubble(im,*a)
sparkle(im,1400,95,25)
save(im,'01-welcome.jpg',90)

# 02: engineering identity, window not markdown header.
h=580;im=bg(h,1,anchor=.28,tint=(211,247,252,64))
glass(im,(75,70,1017,499),opacity=225,r=45)
windowbar(im,(97,92,995,152),'ABOUT THE BUILDER','PERSONAL.WINDOW')
txt(im,(132,191),'I build things that work.',54,deep,'bold')
txt(im,(134,271),'Backend systems, useful interfaces and',31,(24,89,115),'medium')
txt(im,(134,313),'data-driven products — designed to solve',31,(24,89,115),'medium')
txt(im,(134,355),'real problems, not just look impressive.',31,(24,89,115),'medium')
pill(im,(132,420,380,474),'ENGINEERING',size=19)
pill(im,(394,420,595,474),'SYSTEMS',size=19)
pill(im,(609,420,847,474),'AUTOMATION',size=19)
glass(im,(1071,142,1520,430),opacity=213,r=39)
txt(im,(1122,202),'NOW BUILDING',22,(1,126,163),'bold')
txt(im,(1122,249),'Reliable APIs',38,deep,'semibold')
txt(im,(1122,303),'Thoughtful UX',36,deep,'semibold')
txt(im,(1122,365),'Cloud-ready systems',27,(21,106,144),'medium')
for a in [(1070,80,18),(1497,86,42)]:bubble(im,*a)
save(im,'02-about.jpg')

# 03: Flagship ocean, a genuine product explainer displayed as floating map window
h=760;im=bg(h,0,anchor=.71,tint=(1,126,172,92))
glass(im,(70,100,790,672),opacity=226,r=43)
windowbar(im,(93,125,765,185),'FEATURED PROJECT','01 / PUBLIC')
txt(im,(112,238),'Maritime',82,deep,'extra')
txt(im,(112,326),'Watch Türkiye',72,(0,122,165),'extra')
txt(im,(115,439),'From weather and vessel signals',28,deep,'medium')
txt(im,(115,481),'to clearer decisions at sea.',28,deep,'medium')
pill(im,(114,544,312,597),'PYTHON',size=19)
pill(im,(325,544,520,597),'AIS + GIS',size=19)
pill(im,(532,544,723,597),'PWA',size=19)
txt(im,(116,629),'VIEW PROJECT  ↗',20,(1,121,160),'bold')
glass(im,(823,138,1525,630),opacity=201,r=43)
windowbar(im,(842,153,1505,213),'COASTAL INTELLIGENCE','SYSTEM VIEW')
data_ui(im,(850,219,1500,602),'map')
txt(im,(888,580),'Illustrative interface · not a navigation chart',17,(20,92,127),'medium')
sparkle(im,1535,90,18)
save(im,'03-maritime.jpg')

# 04: Restofy feature, orange cast balanced with original aero aqua
h=570;im=bg(h,1,anchor=.7,tint=(251,226,203,88))
glass(im,(75,65,1000,506),opacity=218,r=42,shade='orange')
windowbar(im,(94,84,982,144),'TEAM PROJECT  /  OPEN REPOSITORY','IN DEVELOPMENT')
txt(im,(126,196),'Restofy',100,(155,76,23),'extra')
txt(im,(132,316),'QR restaurant management platform',32,(121,76,47),'semibold')
txt(im,(132,372),'Microservices • orders • kitchen workflows',26,(111,83,64),'medium')
pill(im,(131,430,360,480),'SPRING BOOT',color=(142,77,44),size=19)
pill(im,(375,430,565,480),'NEXT.JS',color=(142,77,44),size=19)
pill(im,(580,430,825,480),'POSTGRESQL',color=(142,77,44),size=19)
glass(im,(1060,101,1530,474),opacity=219,r=40,shade='orange')
# restaurant flow of icons: QR matrix, order ticket, dine plate
d=ImageDraw.Draw(im,'RGBA')
q_x,q_y=1130,179
for i in range(11):
 for j in range(11):
  if ((i*13+j*7+i*j*3)%9)<5:
   d.rounded_rectangle((q_x+i*15,q_y+j*15,q_x+i*15+11,q_y+j*15+11),radius=2,fill=(209,104,43,216))
d.ellipse((1390,203,1495,308),outline=(216,117,47,220),width=15)
d.arc((1416,229,1468,281),25,310,fill=(255,255,255,210),width=7)
txt(im,(1298,399),'SCAN  →  ORDER  →  SERVE',24,(121,76,47),'bold',anchor='mm')
save(im,'04-restofy.jpg')

# 05: Crypto tracking
h=535;im=bg(h,0,anchor=.83,tint=(51,149,183,94))
glass(im,(85,64,868,479),opacity=223,r=43)
windowbar(im,(102,84,849,145),'OPEN SOURCE / JAVA DESKTOP','PUBLIC REPO')
txt(im,(132,189),'Crypto Tracker',79,deep,'extra')
txt(im,(134,309),'Live market data and price alerts.',30,deep,'medium')
pill(im,(132,390,299,449),'JAVA',size=22)
pill(im,(315,390,522,449),'BINANCE API',size=20)
pill(im,(538,390,729,449),'DESKTOP',size=20)
glass(im,(899,87,1527,453),opacity=201,r=40)
windowbar(im,(920,106,1506,165),'MARKET FLOW','ILLUSTRATION')
data_ui(im,(932,163,1496,425),'market')
save(im,'05-crypto.jpg')

# 06: ML experimentation
h=550;im=bg(h,1,anchor=.37,tint=(207,224,255,84))
glass(im,(85,73,852,485),opacity=223,r=43,shade='blue')
windowbar(im,(104,93,830,153),'MACHINE LEARNING / RESEARCH','PUBLIC REPO')
txt(im,(139,207),'Machine Learning',70,deep,'extra')
txt(im,(143,312),'From noisy data to tested models.',29,(25,96,133),'medium')
pill(im,(143,391,360,449),'SCIKIT-LEARN',size=19)
pill(im,(374,391,529,449),'PANDAS',size=19)
pill(im,(543,391,756,449),'REGRESSION',size=19)
glass(im,(888,90,1525,474),opacity=208,r=41,shade='blue')
windowbar(im,(907,109,1503,166),'HOUSING PRICE MODEL','MODEL VIEW')
data_ui(im,(917,173,1496,442),'ml')
save(im,'06-machine-learning.jpg')

# 07: Churn learning
h=490;im=bg(h,0,anchor=.65,tint=(173,223,250,115))
glass(im,(85,63,920,424),opacity=220,r=41)
windowbar(im,(105,85,903,146),'DATA LAB / CLASSIFICATION','PUBLIC REPO')
txt(im,(142,204),'Customer Churn',72,deep,'extra')
txt(im,(142,292),'Compare classifiers. Understand trade-offs.',27,(24,90,129),'medium')
pill(im,(140,353,341,409),'CLASSIFICATION',size=18)
pill(im,(356,353,554,409),'F1 / RECALL',size=18)
pill(im,(569,353,814,409),'FEATURE ENGINEERING',size=18)
glass(im,(1020,84,1510,404),opacity=200,r=39)
# abstract confusion matrix and segmented classification
D=ImageDraw.Draw(im,'RGBA')
for i in range(2):
 for j in range(2):
  xx=1080+j*161;yy=154+i*108
  D.rounded_rectangle((xx,yy,xx+142,yy+93),radius=18,fill=(48+30*j,154+28*i,181+18*j,135),outline=(255,255,255,200),width=3)
  txt(im,(xx+71,yy+45),['TP','FP','FN','TN'][i*2+j],30,deep,'bold',anchor='mm')
save(im,'07-churn.jpg')

# 08: Library system
h=520;im=bg(h,1,anchor=.9,tint=(190,249,226,72))
glass(im,(90,70,866,464),opacity=224,r=42,shade='mint')
windowbar(im,(106,89,847,147),'PYTHON / DATA SYSTEM','PUBLIC REPO')
txt(im,(144,208),'Library System',76,deep,'extra')
txt(im,(146,309),'Borrowing workflows, SQLite, audit logs.',28,(14,89,116),'medium')
pill(im,(146,389,328,442),'PYTHON',size=20)
pill(im,(345,389,524,442),'SQLITE',size=20)
pill(im,(541,389,742,442),'CLI TOOLS',size=20)
glass(im,(927,86,1534,448),opacity=209,r=42,shade='mint')
windowbar(im,(946,105,1512,164),'BOOKS & RECORDS','SYSTEM VIEW')
data_ui(im,(955,177,1511,430),'library')
save(im,'08-library.jpg')

# 09: SKILLS panel, frutiger translucent tabs, no markdown
h=620;im=bg(h,0,anchor=.28,tint=(238,252,249,99))
glass(im,(67,52,1530,575),opacity=209,r=47)
windowbar(im,(89,76,1509,133),'ENGINEERING TOOLBOX','WHAT I USE')
txt(im,(120,183),'Technologies behind the work.',49,deep,'bold')
cards=[(118,268,750,375,'BACKEND','Java · Spring Boot · C# · ASP.NET Core'),(783,268,1460,375,'FRONTEND','TypeScript · React · Next.js · UI systems'),(118,394,750,506,'DATA / AI','Python · Pandas · NumPy · scikit-learn'),(783,394,1460,506,'INFRASTRUCTURE','Docker · PostgreSQL · GitHub Actions · Git')]
for x,y,x2,y2,name,items in cards:
 glass(im,(x,y,x2,y2),opacity=218,r=23,shade='white',shadow=40)
 txt(im,(x+28,y+25),name,20,(1,134,163),'bold')
 txt(im,(x+28,y+67),items,23,deep,'semibold')
save(im,'09-toolbox.jpg')

# 10: professional experience linked to company, not attributed code.
h=570;im=bg(h,1,anchor=.56,tint=(225,246,250,105))
glass(im,(75,68,1034,497),opacity=228,r=44)
windowbar(im,(96,91,1011,149),'PROFESSIONAL EXPERIENCE','ENGINEERING + QA')
txt(im,(135,213),'VollSign',101,deep,'extra')
txt(im,(142,329),'Software Engineering · Functional QA',32,(19,91,118),'semibold')
txt(im,(143,387),'Development, API checks and end-to-end UI flows.',27,(31,103,130),'medium')
pill(im,(141,435,417,485),'VISIT VOLLSIGN.COM',size=19)
glass(im,(1082,130,1530,434),opacity=199,r=37)
d=ImageDraw.Draw(im,'RGBA');d.rounded_rectangle((1166,186,1404,365),radius=18,fill=(255,255,255,156),outline=(39,167,185,142),width=3)
d.line((1202,238,1332,238),fill=(28,135,171,120),width=8)
d.line((1202,271,1352,271),fill=(28,135,171,95),width=7)
d.line((1202,304,1292,304),fill=(28,135,171,95),width=7)
# signature stroke
p=[(1285,339),(1304,321),(1316,342),(1337,306),(1355,329),(1380,292)]
d.line(p,fill=(4,173,181,230),width=7,joint='curve')
bubble(im,1493,117,30)
save(im,'10-vollsign.jpg')

# 11: contact finale with close of sunlit image, branded and pure visual
h=590;im=bg(h,0,anchor=.52,tint=(226,251,252,25))
glass(im,(82,72,1514,489),opacity=190,r=53)
windowbar(im,(107,94,1490,160),'END OF DESKTOP','LET’S BUILD SOMETHING USEFUL')
txt(im,(157,218),'Good software feels effortless.',66,deep,'bold')
txt(im,(162,307),'Built with curiosity. Engineered with care.',37,(3,127,161),'medium')
pill(im,(163,396,489,466),'EXPLORE MY GITHUB ↗',size=23)
pill(im,(507,396,844,466),'PUBLIC REPOSITORIES ↗',size=22)
bubble(im,1308,311,71);bubble(im,1449,391,27)
sparkle(im,1328,240,24)
save(im,'11-connect.jpg',90)

# Manifest / readme; designed all-image mode. Inline HTML only; alt is accessible description.
scenes=[
 ('01-welcome.jpg',None,'Kerem Kalyoncu — Software Engineer. Frutiger Aero welcome screen.'),
 ('02-about.jpg',None,'About Kerem: software engineer focused on backend systems, useful interfaces and data-driven products.'),
 ('03-maritime.jpg','https://github.com/KeremKalyoncu/maritime-watch','Maritime Watch Türkiye — public geospatial and maritime decision-support application. Open repository.'),
 ('04-restofy.jpg','https://github.com/software-lecture-labs/Restofy','Restofy — public team project, QR restaurant management with Spring Boot microservices and Next.js. Open repository.'),
 ('05-crypto.jpg','https://github.com/KeremKalyoncu/KriptoParaTakip','Crypto Tracker — Java desktop cryptocurrency tracking with Binance API. Open repository.'),
 ('06-machine-learning.jpg','https://github.com/KeremKalyoncu/ml-final-odev','Machine Learning — California Housing regression and model comparison. Open repository.'),
 ('07-churn.jpg','https://github.com/KeremKalyoncu/ml-ara-odev','Customer Churn — classification and recall analysis. Open repository.'),
 ('08-library.jpg','https://github.com/KeremKalyoncu/Gelismis_Kutuphane_Sistemi','Library System — Python SQLite borrowing and log management. Open repository.'),
 ('09-toolbox.jpg',None,'Technology stack: Java, Spring Boot, C#, ASP.NET Core, TypeScript, React, Next.js, Python, Docker and PostgreSQL.'),
 ('10-vollsign.jpg','https://vollsign.com','VollSign professional experience: software engineering and functional QA. Visit official company website.'),
 ('11-connect.jpg','https://github.com/KeremKalyoncu?tab=repositories','Explore Kerem Kalyoncu public repositories on GitHub.'),
]
lines=['<!-- KEREM / AERO v5 | Visual GitHub profile: accessible descriptions via alt text. -->','<div align="center">']
for name,url,alt in scenes:
 image=f'<img src="./assets/{name}" width="100%" alt="{alt}" />'
 if url:image=f'<a href="{url}">{image}</a>'
 lines.append(image)
lines.extend(['</div>',''])
(OUT/'README.md').write_text('\n'.join(lines),encoding='utf-8')

# create hero and web scaled composite for the user (render visual only, no artificial section text)
ims=[Image.open(AS/name).convert('RGB') for name,_,_ in scenes]
preview=Image.new('RGB',(W,sum(im.height for im in ims)),(255,255,255))
y=0
for im in ims:preview.paste(im,(0,y));y+=im.height
preview.save(OUT/'AERO-V5-FULL-PREVIEW.jpg',quality=77,optimize=True,progressive=True,subsampling=0)
preview.resize((960,int(preview.height*960/W)),Image.Resampling.LANCZOS).save(OUT/'AERO-V5-QUICK-PREVIEW.jpg',quality=81,optimize=True,progressive=True)

SETUP='''# KEREM / AERO — V5 installation

## What changed
- 100% visual profile: **no Markdown headings, tables, badges or paragraphs between scenes**.
- 11 full-width authored image panels, with compact explanatory text **inside** the images.
- Public GitHub projects are individually clickable; VollSign links to its official website.
- Liquid Internet and private work are excluded from project showcase.
- The linked projects and company are not presented as realtime telemetry or invented live demos.
- Every image includes meaningful alternative text for accessibility.

## Installation without disturbing existing README
1. Extract this ZIP.
2. Clone `KeremKalyoncu/KeremKalyoncu` using GitHub Desktop.
3. Create a new branch: `feat/aero-v5`.
4. Replace `README.md` with this package's `README.md`.
5. Copy ALL files in this package's `assets/` into your repo's `assets/` (do not delete existing assets).
6. Commit and push the branch.
7. Preview at `https://github.com/KeremKalyoncu/KeremKalyoncu/blob/feat/aero-v5/README.md`.
8. Review links, mobile readability, and content, then open a PR to `main` if happy.

## Technical notes
- GitHub profile README does not allow scripting/layout CSS like a regular website. Each wide image is a single clickable surface, not draggable desktop windows.
- These JPG assets render consistently within GitHub's sanitization limitations.
- Some UI drawings (charts, map view, QR code) are **illustrative art**, not actual product screenshots nor live data; do not portray them as such.
- Images need the exact relative path under `assets/`.
- The scripts and legacy Actions from your old profile are **not** modified; once the new README is published the old issue-ops hooks may need disabling because the new README intentionally omits their target sections. Existing scripts can remain until you decide to clean up.
- If you want actual live widgets or interactive windows, implement them in your own website; this README is a visual gallery constrained by GitHub's renderer.

## Customization
Run `python build_aero.py` (requires Pillow) to regenerate the images. The background art included at the repo level is used in this generated package version, but the bundled script expects the two preexisting local original scene file paths. To make rebuilding portable, update `SRC` in the script to point to your own images. No fonts are redistributed.
'''
(OUT/'SETUP.md').write_text(SETUP,encoding='utf-8')
# Ensure actual portable script: distribute exact art under sources
sources=OUT/'sources';sources.mkdir(exist_ok=True)
for i,source in enumerate(SRC):
 source.save(sources/f'original-aero-world-{i+1}.jpg',quality=84,optimize=True)
script=(OUT/'build_aero.py').read_text(encoding='utf-8')
script=script.replace("Image.open(Path(__file__).parent/'sources/original-aero-world-1.jpg')", "Image.open(Path(__file__).parent/'sources/original-aero-world-1.jpg')").replace("Image.open(Path(__file__).parent/'sources/original-aero-world-2.jpg')", "Image.open(Path(__file__).parent/'sources/original-aero-world-2.jpg')")
(OUT/'build_aero.py').write_text(script,encoding='utf-8')
(OUT/'SETUP.md').write_text(SETUP.replace('The background art included at the repo level is used in this generated package version, but the bundled script expects the two preexisting local original scene file paths. To make rebuilding portable, update `SRC` in the script to point to your own images.', 'The `sources/` folder contains the visual backgrounds used by the build script. Regenerate by running the script from any directory. For another look, replace these image files with your own scene artwork.'),encoding='utf-8')
# zip only files necessary (include sources for reproducibility but no full preview inside to keep small)
zipfile_path=OUT/'Kerem-Aero-V5-Visual-README.zip'
with zipfile.ZipFile(zipfile_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for f in [OUT/'README.md',OUT/'SETUP.md',OUT/'build_aero.py',*AS.glob('*.jpg'),*sources.glob('*.jpg')]:
  z.write(f,arcname=str(f.relative_to(OUT)))
print('ZIP',zipfile_path.stat().st_size,'bytes',len(scenes),'sections')
print('PREVIEW',preview.size)
