from pathlib import Path
from PIL import Image
from io import BytesIO
import base64,random,html
ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'assets'
source=Image.open('/mnt/data/a_bright_ultra_detailed_glossy_frutiger_aero_st.png').convert('RGB')
source=source.resize((1800,600),Image.Resampling.LANCZOS)
# preserve left sky while retaining the chrome ring right
source=source.crop((185,0,1615,600)).resize((1430,600),Image.Resampling.LANCZOS)
buf=BytesIO();source.save(buf,'JPEG',quality=85,optimize=True,progressive=True)
img='data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()
random.seed(71)
W,H=1200,2200
svg=[]
S=svg.append
S('''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="2200" viewBox="0 0 1200 2200" role="img" aria-label="Kerem Kalyoncu animated living Frutiger Aero world: drifting clouds, moving sea, floating glass software project capsules and underwater lights.">
<title>KEREM AERO — Living World</title>
<desc>Animated Frutiger Aero personal portfolio featuring Maritime Watch, Restofy, crypto analytics, machine learning, VollSign engineering experience, and links to publicly available work.</desc>
<defs>
 <linearGradient id="worldGradient" x1="0" y1="0" x2="0.11" y2="1"><stop stop-color="#1d9de6"/><stop offset=".23" stop-color="#2dd5f2"/><stop offset=".49" stop-color="#0fadc7"/><stop offset=".76" stop-color="#057e9d"/><stop offset="1" stop-color="#075077"/></linearGradient>
 <linearGradient id="merge" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#36c4ee" stop-opacity="0"/><stop offset=".30" stop-color="#31d0e9" stop-opacity=".30"/><stop offset=".62" stop-color="#1ac7dd" stop-opacity="1"/><stop offset="1" stop-color="#1ac7dd" stop-opacity="1"/></linearGradient>
 <linearGradient id="oceanLight" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#efffff" stop-opacity=".26"/><stop offset=".3" stop-color="#46e6f4" stop-opacity=".07"/><stop offset=".9" stop-color="#8efbff" stop-opacity=".04"/></linearGradient>
 <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#d4ffff" stop-opacity=".63"/><stop offset=".20" stop-color="#77d9fa" stop-opacity=".36"/><stop offset=".50" stop-color="#0877ad" stop-opacity=".45"/><stop offset="1" stop-color="#072e80" stop-opacity=".62"/></linearGradient>
 <linearGradient id="glassDark" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0874ab" stop-opacity=".78"/><stop offset=".45" stop-color="#08678e" stop-opacity=".78"/><stop offset="1" stop-color="#053872" stop-opacity=".83"/></linearGradient>
 <linearGradient id="glassLight" x1="0" y1="0" x2=".6" y2="1"><stop stop-color="#ffffff" stop-opacity=".65"/><stop offset=".28" stop-color="#ddffff" stop-opacity=".22"/><stop offset=".7" stop-color="#b2feff" stop-opacity=".05"/><stop offset="1" stop-color="#ecffff" stop-opacity=".26"/></linearGradient>
 <linearGradient id="softWave" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#d9ffff" stop-opacity=".58"/><stop offset="1" stop-color="#15a6cf" stop-opacity=".02"/></linearGradient>
 <linearGradient id="green" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#cfff74"/><stop offset=".4" stop-color="#3dda97"/><stop offset="1" stop-color="#058d98"/></linearGradient>
 <radialGradient id="bubbleShine" cx="29%" cy="24%" r="78%"><stop stop-color="#ffffff" stop-opacity=".88"/><stop offset=".12" stop-color="#f2ffff" stop-opacity=".17"/><stop offset=".50" stop-color="#6bedfa" stop-opacity=".03"/><stop offset=".86" stop-color="#a3a3fe" stop-opacity=".23"/><stop offset="1" stop-color="#edffff" stop-opacity=".87"/></radialGradient>
 <radialGradient id="blueGlow"><stop stop-color="#b4ffff" stop-opacity=".52"/><stop offset="1" stop-color="#31d1fa" stop-opacity="0"/></radialGradient>
 <radialGradient id="sun"><stop stop-color="#ffffff" stop-opacity=".7"/><stop offset=".15" stop-color="#fff7b8" stop-opacity=".28"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
 <filter id="shadow" x="-30%" y="-30%" width="160%" height="170%"><feGaussianBlur in="SourceAlpha" stdDeviation="11" result="b"/><feOffset in="b" dx="0" dy="16" result="o"/><feComponentTransfer in="o" result="t"><feFuncA type="linear" slope="0.30"/></feComponentTransfer><feMerge><feMergeNode in="t"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="softBlur" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="9"/></filter>
 <filter id="spark" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <clipPath id="full"><rect width="1200" height="2200" rx="18"/></clipPath>
 <clipPath id="radarClip"><circle cx="273" cy="734" r="121"/></clipPath>
 <style><![CDATA[
    .font {font-family: 'Segoe UI', 'Trebuchet MS', Arial, Helvetica, sans-serif}
    .mono {font-family:'Consolas','Courier New',monospace}
    .photodrift {transform-origin:50% 28%; animation:photo 23s ease-in-out infinite alternate}
    .cloud {animation:drift 42s linear infinite}
    .cloud.two {animation-duration:67s;animation-direction:reverse;}
    .swell {animation:swell 7s ease-in-out infinite alternate}
    .swell.two {animation-delay:-3.4s;animation-duration:9s}
    .caustic {animation:shimmer 12s ease-in-out infinite alternate}
    .caustic.alt {animation-delay:-5s;animation-duration:17s}
    .float1{animation:floatA 6.7s ease-in-out infinite alternate}
    .float2{animation:floatB 8.2s ease-in-out infinite alternate}
    .float3{animation:floatA 8.6s ease-in-out -3.1s infinite alternate}
    .float4{animation:floatB 7.3s ease-in-out -2.4s infinite alternate}
    .bubble {animation:rise var(--dur,14s) linear var(--delay,0s) infinite;}
    .bubble g {animation:bubbleWobble 4s ease-in-out infinite alternate}
    .halo {animation:halo 7s ease-in-out infinite alternate}
    .refract {animation:refract 11s linear infinite}
    .glint {animation:twinkle var(--dur,3.4s) ease-in-out var(--delay,0s) infinite}
    .radar {transform-origin:273px 734px; animation:spin 13s linear infinite}
    .boat {animation:boat 4s ease-in-out infinite alternate}
    .steam {animation:steam 3.2s ease-in-out infinite alternate}
    .chartLine {stroke-dasharray:430;animation:trace 9s ease-in-out infinite}
    .coral {transform-box:fill-box;transform-origin:bottom center;animation:coral 4.7s ease-in-out infinite alternate}
    .coral.two {animation-delay:-2.3s;animation-duration:5.8s}
    .jelly {animation:jelly 8s ease-in-out infinite alternate}
    .fish {animation:fishSwim var(--speed,24s) linear var(--delay,-6s) infinite;opacity:.42;}
    .cursor {animation:twinkle 1.7s steps(2) infinite}
    @keyframes photo {to{transform:translate(8px,-3px) scale(1.014)}}
    @keyframes drift {to{transform:translateX(220px)}}
    @keyframes swell {to{transform:translate(-40px,14px)}}
    @keyframes shimmer {0%{transform:translateX(-44px);opacity:.12}100%{transform:translateX(30px);opacity:.62}}
    @keyframes floatA {to{transform:translateY(-18px) rotate(.35deg)}}
    @keyframes floatB {to{transform:translate(7px,-23px) rotate(-.5deg)}}
    @keyframes rise {0%{transform:translateY(70px);opacity:0}8%{opacity:.8}86%{opacity:.65}100%{transform:translateY(-1250px);opacity:0}}
    @keyframes bubbleWobble {to{transform:translateX(11px)}}
    @keyframes halo {to{opacity:.32;transform:scale(1.06)}}
    @keyframes refract {to{stroke-dashoffset:-900}}
    @keyframes twinkle {0%,100%{opacity:.14;transform:scale(.7)}50%{opacity:1;transform:scale(1.3)}}
    @keyframes spin {to{transform:rotate(360deg)}}
    @keyframes boat {to{transform:translateY(-6px) rotate(-1deg)}}
    @keyframes steam {to{transform:translateY(-11px);opacity:.32}}
    @keyframes trace {0%{stroke-dashoffset:430;opacity:.1}30%,85%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:-430;opacity:.2}}
    @keyframes coral {to{transform:rotate(7deg)}}
    @keyframes jelly {to{transform:translate(28px,-58px)}}
    @keyframes fishSwim {from{transform:translateX(-230px)}to{transform:translateX(1410px)}}
    @media (prefers-reduced-motion: reduce) {*,*::before,*::after{animation:none!important;transition:none!important}}
 ]]></style>
</defs>
<g clip-path="url(#full)">
<rect width="1200" height="2200" fill="url(#worldGradient)"/>
<image class="photodrift" href="__EMBED_IMAGE__" x="-115" y="0" width="1430" height="603" preserveAspectRatio="xMidYMid meet"/>
<rect y="425" width="1200" height="270" fill="url(#merge)"/>
<rect y="575" width="1200" height="1625" fill="url(#oceanLight)" opacity=".8"/>
<!-- continuous undersea volume and beams -->
<path d="M20 450L300 450L720 2200L160 2200Z" fill="#d2ffff" opacity=".07"/>
<path d="M600 420L770 420L1150 2200L915 2200Z" fill="#dcffff" opacity=".08"/>
<ellipse cx="920" cy="620" rx="700" ry="450" fill="url(#blueGlow)" opacity=".45"/>
<ellipse cx="180" cy="1660" rx="660" ry="440" fill="url(#blueGlow)" opacity=".3"/>
<circle cx="1005" cy="115" r="260" fill="url(#sun)" class="halo"/>
''')
# Clouds in sky actual animated different visual layers
cloud_paths=[('M-40 254c38-38 83-39 118-18 24-47 98-55 128-11 56-12 98 12 110 43H-40Z',.43),('M690 248c27-27 61-31 84-18 23-38 69-44 106-9 44-7 73 16 88 43H690Z',.37)]
for j,(p,o) in enumerate(cloud_paths):
 S(f'<g class="cloud {"two" if j else ""}" opacity="{o}"><path d="{p}" fill="#ffffff"/><path d="{p}" fill="none" stroke="#f3ffff" stroke-width="2"/></g>')
# wave crests overlap fade
for i in range(4):
 y=482+i*41
 S(f'<g class="swell {"two" if i%2 else ""}" opacity="{.18+i*.04:.2f}"><path d="M-90 {y} Q75 {y-30} 230 {y+1}T530 {y}T830 {y}T1230 {y}T1580 {y}V{y+32}H-90Z" fill="url(#softWave)" stroke="#e4ffff" stroke-width="{3-i*.45}"/></g>')
# caustics throughout, under everything, no card borders
for i in range(32):
 y=615+i*46; start=random.randint(-160,120); extent=random.randint(320,850)
 d=f'M{start} {y} Q{start+170} {y-18} {start+extent//2} {y+2}T{start+extent} {y}'
 S(f'<path class="caustic {"alt" if i%2 else ""}" d="{d}" fill="none" stroke="#b7ffff" stroke-opacity="{random.uniform(.07,.23):.2f}" stroke-width="{random.uniform(1.4,4):.1f}" stroke-linecap="round"/>')
# strings of rising bubbles; later overlays bigger
for i in range(56):
 cx=random.randint(18,1182);cy=random.randint(760,2290);r=random.choices([3,5,7,10,14],[2,4,6,5,1])[0]
 duration=random.randint(9,24);delay=-random.randint(0,24)
 S(f'<g class="bubble" style="--dur:{duration}s;--delay:{delay}s"><g><circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#bubbleShine)" stroke="#deffff" stroke-opacity=".43" stroke-width="1"/><ellipse cx="{cx-r*.24:.1f}" cy="{cy-r*.43:.1f}" rx="{r*.21:.1f}" ry="{r*.13:.1f}" fill="white" opacity=".6"/></g></g>')
# school of translucent fish, in the same underwater world
for i in range(13):
 cy=random.choice([950,1420,1460,1820,2090]) + random.randint(-30,30)
 cx=random.randint(-260,-40)
 scale=random.uniform(.44,1.03)
 dur=random.randint(21,44)
 delay=-random.randint(0,40)
 S(f'<g class="fish" style="--speed:{dur}s;--delay:{delay}s"><g transform="translate({cx} {cy}) scale({scale:.2f})"><path d="M-18 0Q6 -15 22 0Q7 13-18 0Z" fill="#d8ffff" opacity=".7"/><path d="M-16 0L-33 -12V12Z" fill="#e4ffff" opacity=".55"/><circle cx="13" cy="-2" r="1.5" fill="#07587d"/></g></g>')
# high atmosphere title
S('''<g filter="url(#shadow)">
<rect x="59" y="75" width="708" height="245" rx="52" fill="#005a94" opacity=".29"/>
<rect x="60" y="75" width="706" height="242" rx="52" fill="url(#glassLight)" stroke="#f8ffff" stroke-opacity=".64" stroke-width="2"/>
<path d="M86 128Q130 85 706 96" fill="none" stroke="white" stroke-width="6" opacity=".47" stroke-linecap="round"/>
<text x="104" y="158" class="font" fill="#eaffff" font-size="21" font-weight="700" letter-spacing="6">WELCOME TO MY WORLD</text>
<text x="100" y="228" class="font" font-size="62" font-weight="800" fill="#ffffff" letter-spacing="-2" stroke="#197cc5" stroke-width=".5" paint-order="stroke">Kerem Kalyoncu</text>
<text x="105" y="269" class="font" font-size="25" font-weight="600" fill="#ffffff">Software Engineer  <tspan fill="#c3ffff">/</tspan>  Backend · AI · Systems</text>
</g>
<g class="float2"><circle cx="986" cy="321" r="62" fill="url(#bubbleShine)" stroke="#e9ffff" stroke-width="4" opacity=".76"/><path d="M956 294q24-34 59-15" stroke="white" stroke-width="8" fill="none" opacity=".58" stroke-linecap="round"/></g>
<g class="glint" style="--dur:3.4s;--delay:-1s" transform="translate(840 161)"><path d="M-16 0H16M0-16V16" stroke="white" stroke-width="3" stroke-linecap="round"/></g>
<g class="glint" style="--dur:4.8s" transform="translate(1094 368)"><path d="M-13 0H13M0-13V13" stroke="white" stroke-width="3"/></g>
''')
# feature visual components funcs

def glass_box(x,y,w,h,rx=50):
 return (f'<rect x="{x}" y="{y+8}" width="{w}" height="{h}" rx="{rx}" fill="#003d69" opacity=".18" filter="url(#softBlur)"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#glassDark)" stroke="#e1ffff" stroke-opacity=".77" stroke-width="3"/>'
         f'<path d="M{x+rx-9} {y+9} H{x+w-rx+5}Q{x+w-12} {y+9} {x+w-12} {y+rx-10}" fill="none" stroke="white" stroke-opacity=".37" stroke-width="6" stroke-linecap="round"/>')
# ambient floating island banks
S('''<path d="M-20 865 Q220 809 475 846T1200 838L1200 1047Q920 1040 680 1080T-30 1060Z" fill="#d8ffff" opacity=".045"/>
<path d="M-30 1480Q140 1435 315 1488T735 1490T1230 1440" fill="none" stroke="#e4ffff" stroke-opacity=".14" stroke-width="17"/>
''')
# Maritime Watch main capsule
S('<g class="float1">')
S(glass_box(76,595,1048,325,62))
S('''<circle cx="273" cy="748" r="132" fill="#2bc2ee" opacity=".24"/>
<circle cx="273" cy="748" r="123" fill="#003d89" opacity=".36" stroke="#b6ffff" stroke-opacity=".58" stroke-width="2"/>
<g clip-path="url(#radarClip)">
<circle cx="273" cy="734" r="110" fill="#0f9bc7" opacity=".13"/>
<g stroke="#c9ffff" stroke-opacity=".25" fill="none"><circle cx="273" cy="734" r="35"/><circle cx="273" cy="734" r="69"/><circle cx="273" cy="734" r="108"/><path d="M150 734H396M273 611V857"/></g>
<path class="radar" d="M273 734L273 614A120 120 0 0 1 390 761Z" fill="#a0ffff" opacity=".20"/>
<g class="boat"><path d="M173 759Q223 779 355 757L328 801Q254 825 195 794Z" fill="#f1ffff" opacity=".95"/><path d="M203 757V722H302V756" fill="#f2ffff" stroke="#227d9f" stroke-width="3"/><rect x="222" y="701" width="60" height="21" rx="4" fill="#e7ffff"/><path d="M249 696V657M260 657H272M276 696V666" fill="none" stroke="white" stroke-width="5"/><path d="M185 824Q258 804 343 822" fill="none" stroke="#dcffff" stroke-width="5"/></g>
</g>
<text x="440" y="692" class="font" font-weight="800" font-size="43" fill="white">Maritime Watch</text>
<text x="440" y="735" class="font" font-weight="700" font-size="21" fill="#bafffc" letter-spacing="2">REAL-TIME MARITIME INTELLIGENCE</text>
<text x="440" y="785" class="font" font-size="25" fill="#f1ffff">Weather · AIS · Spatial alerts</text>
<text x="440" y="826" class="font" font-size="21" fill="#deffff">Decision support for Turkish waters.</text>
<rect x="440" y="858" width="255" height="34" rx="17" fill="#e4ffff" opacity=".25"/>
<text x="465" y="881" class="font" font-size="16" font-weight="700" fill="#fff">PYTHON  ·  LEAFLET  ·  PWA</text>
</g>
''')
# Restofy left, crypto right positions moved to stagger
S('<g class="float2">'+glass_box(82,988,503,359,60))
S('''<circle cx="332" cy="1095" r="88" fill="url(#bubbleShine)" stroke="#fcffff" stroke-opacity=".53" stroke-width="2"/>
<g class="steam" stroke="#fefeff" stroke-width="6" stroke-linecap="round" fill="none" opacity=".78"><path d="M290 1110q-16-23 6-45t0-32"/><path d="M326 1109q-16-23 6-45t0-32"/><path d="M360 1110q-16-23 6-45t0-32"/></g>
<path d="M250 1178Q255 1124 329 1121Q403 1130 410 1178Z" fill="#ffb443" stroke="#fff3d0" stroke-width="4"/><ellipse cx="330" cy="1181" rx="94" ry="10" fill="#fff0c3"/><circle cx="330" cy="1116" r="11" fill="#fff1bc"/>
<text x="138" y="1254" class="font" font-size="39" font-weight="800" fill="white">Restofy</text>
<text x="138" y="1290" class="font" font-size="20" fill="#efffff">Restaurant QR platform</text>
<text x="138" y="1315" class="font" font-size="16" fill="#ccffff">Spring Boot · Microservices · Team</text>
</g>
''')
S('<g class="float3">'+glass_box(620,1026,496,361,57))
S('''<circle cx="868" cy="1140" r="92" fill="#2fe4a8" opacity=".15" stroke="#c1ffef" stroke-width="3"/>
<g stroke="#70ffd6" stroke-width="2" opacity=".25"><path d="M755 1170H991M755 1130H991M755 1090H991M790 1040V1230M830 1040V1230M870 1040V1230M910 1040V1230M950 1040V1230"/></g>
<path class="chartLine" d="M752 1192L795 1176L825 1160L860 1173L889 1102L928 1137L990 1085" fill="none" stroke="#b2ffe0" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
<text x="686" y="1285" class="font" font-size="37" font-weight="800" fill="white">KriptoParaTakip</text>
<text x="686" y="1322" class="font" font-size="19" fill="#eaffff">Live market data and alerts</text>
<text x="686" y="1350" class="font" font-size="16" fill="#bbffe6">Java · API Integration · Desktop</text>
</g>
''')
# underwater medusa softly
S('''<g class="jelly" opacity=".40" transform="translate(1038 1452)"><path d="M-49 8Q-50-65 0-66Q50-65 49 8Q10 25-49 8Z" fill="url(#bubbleShine)" stroke="#dfffff" stroke-width="3"/><path d="M-38 14Q-51 88-28 132M-18 20Q-5 88-22 146M7 22Q21 80 8 133M34 14Q56 90 38 145" fill="none" stroke="#d6ffff" stroke-width="5" stroke-linecap="round"/></g>''')
# ML left and library right
S('<g class="float4">'+glass_box(82,1451,536,284,60))
S('''<g transform="translate(217 1523)">
<path d="M0 37L84 0L145 48L80 98ZM84 0L80 98M0 37L145 48M80 98L175 121L145 48" stroke="#c8f9ff" stroke-width="4" fill="none" opacity=".8"/>
<g fill="url(#bubbleShine)" stroke="#d9ffff" stroke-width="2"><circle cx="0" cy="37" r="15"/><circle cx="84" cy="0" r="17"/><circle cx="145" cy="48" r="16"/><circle cx="80" cy="98" r="20"/><circle cx="175" cy="121" r="13"/></g>
</g>
<text x="130" y="1671" class="font" font-size="35" font-weight="800" fill="white">Machine Learning Lab</text>
<text x="130" y="1704" class="font" font-size="18" fill="#e9ffff">Python · Scikit-learn · Data analysis</text>
</g>
''')
S('<g class="float1">'+glass_box(651,1513,460,276,62))
S('''<g transform="translate(804 1557)"><path d="M-70 30Q-28 2 0 27Q32 3 72 30V115Q38 88 0 107Q-33 89-70 115Z" fill="#efffff" stroke="#a6fbff" stroke-width="4"/><path d="M0 27V108" stroke="#38bedb" stroke-width="5"/><path d="M-49 48L-20 41M22 45L50 50M-49 68L-18 59M22 65L52 72" stroke="#2ab6df" stroke-width="4" stroke-linecap="round"/></g>
<text x="715" y="1720" class="font" font-size="34" font-weight="800" fill="white">Library System</text>
<text x="715" y="1752" class="font" font-size="17" fill="#dfffff">Python · SQLite · Automation</text>
</g>
''')
# undersea floor grasses flowing
for i in range(26):
 x=random.randint(-20,1220);height=random.randint(65,160)
 y=2200
 S(f'<g class="coral {"two" if i%2 else ""}" opacity="{random.uniform(.45,.85):.2f}"><path d="M{x} {y+25}Q{x-random.randint(15,45)} {y-height//2} {x+random.randint(-50,50)} {y-height}" fill="none" stroke="url(#green)" stroke-width="{random.randint(7,14)}" stroke-linecap="round"/></g>')
S('''<ellipse cx="600" cy="2169" rx="900" ry="160" fill="#c1ffff" opacity=".09"/>
<!-- luminous experience island -->
<g class="float2">''')
S(glass_box(113,1845,977,223,63))
S('''<circle cx="244" cy="1952" r="68" fill="url(#bubbleShine)" stroke="#f2ffff" stroke-opacity=".67" stroke-width="3"/>
<text x="243" y="1973" text-anchor="middle" class="font" font-size="58" font-weight="900" fill="white">V</text>
<text x="347" y="1926" class="font" font-size="24" font-weight="700" fill="#c4ffff" letter-spacing="4">PROFESSIONAL EXPERIENCE</text>
<text x="343" y="1984" class="font" font-size="57" font-weight="800" fill="white">VollSign</text>
<text x="346" y="2024" class="font" font-size="23" fill="#f0ffff">Software Engineer  ·  Development / QA / Testing</text>
</g>
<g fill="none" stroke="#d9ffff" stroke-width="3" opacity=".55"><path d="M90 2130Q320 2070 540 2135T1130 2134"/><path d="M180 2167Q450 2120 680 2165T1300 2157"/></g>
<text x="600" y="2157" text-anchor="middle" class="font" font-weight="700" font-size="23" fill="white" letter-spacing="2">EXPLORE THE CODE · GITHUB.COM/KEREMKALYONCU</text>
''')
S('</g></svg>')
output=''.join(svg).replace('__EMBED_IMAGE__',img)
(ASSET/'kerem-living-world.svg').write_text(output,encoding='utf-8')
print('svg size',len(output),'hero_jpg',len(buf.getvalue()),'motion keyframes',output.count('@keyframes'),'bubbles',output.count('class="bubble"'))
