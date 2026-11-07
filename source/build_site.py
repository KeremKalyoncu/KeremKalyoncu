from pathlib import Path
from lxml import etree as ET
from html import escape
ROOT=Path(__file__).resolve().parents[1]
svg=(ROOT/'assets'/'kerem-living-world-v8.svg').read_text(encoding='utf-8')
# All click areas are website-only. GitHub does NOT expose individual click areas inside an <img> SVG.
hotspots=[
('Maritime Watch — live dashboard','https://keremkalyoncu.github.io/maritime-watch',76,595,1048,325),
('Restofy — public team repository','https://github.com/software-lecture-labs/Restofy',82,988,503,359),
('KriptoParaTakip — public Java repository','https://github.com/KeremKalyoncu/KriptoParaTakip',620,1026,496,361),
('ML and Data Lab — public regression project','https://github.com/KeremKalyoncu/ml-final-odev',82,1451,536,284),
('Library System — public Python repository','https://github.com/KeremKalyoncu/Gelismis_Kutuphane_Sistemi',651,1513,460,276),
('VollSign — company website','https://vollsign.com',113,1845,977,223),
('Inventra — publicly linked team project demo','https://x-etc.online',85,2436,510,329),
('Shifha — portfolio and work details','https://www.linkedin.com/in/kerem-kalyoncu/',621,2480,497,329),
('Java and Spring Boot — Restofy repository','https://github.com/software-lecture-labs/Restofy',110,3144,390,157),
('Web engineering — public projects','https://github.com/KeremKalyoncu?tab=repositories',700,3144,390,157),
('Machine learning — public work','https://github.com/KeremKalyoncu/ml-ara-odev',110,3435,390,157),
('CI, QA and Docker — code repository index','https://github.com/KeremKalyoncu?tab=repositories',700,3435,390,157),
('Doğuş University — LinkedIn education','https://www.linkedin.com/in/kerem-kalyoncu/',97,3860,475,158),
('GDG on Campus — community','https://tr.linkedin.com/company/gdg-on-campus-dogus',649,3992,455,173),
('Huawei HSD bootcamp — profile','https://www.linkedin.com/in/kerem-kalyoncu/',100,4170,474,174),
('Certifications — LinkedIn','https://www.linkedin.com/in/kerem-kalyoncu/',638,4303,463,167),
('Connect — LinkedIn','https://www.linkedin.com/in/kerem-kalyoncu/',315,4781,575,212)]
# Insert before final group close of SVG to preserve SVG references from local defs.
anchors=''.join(f'<a class="hotspot" href="{escape(url,quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="{escape(name,quote=True)}"><title>{escape(name)}</title><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="42" fill="transparent"/></a>' for name,url,x,y,w,h in hotspots)
fx='<circle id="pointerLight" cx="-500" cy="-500" r="190" fill="url(#blueGlow)" opacity=".32" pointer-events="none"/>'
svg=svg.replace('</g></svg>',anchors+fx+'</g></svg>')
ET.fromstring(svg.encode())
site='''<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/><meta name="theme-color" content="#159dc9"/>
<meta name="description" content="Explore Kerem Kalyoncu's animated Frutiger Aero engineering universe — public open-source projects, collaboration, professional experience, education and community."/>
<title>KEREM.AERO V8 — The Living Engineering Ocean</title><style>
*{box-sizing:border-box} html{scroll-behavior:smooth;background:#075077}body{margin:0;min-height:100vh;background:linear-gradient(160deg,#34bfe8,#075077 58%,#041d45);font-family:Segoe UI,Arial,sans-serif}
main{width:100%;max-width:1200px;margin:auto;line-height:0;position:relative;overflow:hidden;isolation:isolate;box-shadow:0 0 90px #001c4677}main>svg{width:100%;height:auto;display:block}
.controls{position:fixed;z-index:10;left:50%;transform:translateX(-50%);top:clamp(8px,2vw,18px);display:flex;gap:7px;background:#063b6aa8;backdrop-filter:blur(19px);padding:7px;border:1px solid #c3ffff70;border-radius:99px;max-width:calc(100vw - 14px);box-shadow:0 6px 25px #00284666}
.controls button,.controls a{color:#fff;font:600 13px Segoe UI,Arial,sans-serif;text-decoration:none;white-space:nowrap;border-radius:50px;border:1px solid transparent;padding:10px 14px;cursor:pointer;background:transparent}
.controls button:hover,.controls a:hover,.controls button:focus-visible,.controls a:focus-visible{outline:none;background:#e3ffff2a;border:1px solid #d9ffff77}
.hotspot rect{cursor:pointer;stroke:transparent;stroke-width:3;transition:fill .2s,stroke .2s}.hotspot:hover rect,.hotspot:focus-visible rect{fill:#fff;fill-opacity:.10;stroke:#d6ffff;stroke-opacity:.65}.hotspot:focus{outline:none}
.paused *{animation-play-state:paused!important} .help{position:fixed;right:15px;bottom:15px;color:#eaffff;background:#063b6ac0;border:1px solid #ddffff55;border-radius:22px;padding:9px 16px;font:12px Segoe UI,Arial,sans-serif;pointer-events:none;z-index:11;backdrop-filter:blur(10px)}
@media(max-width:700px){.controls{top:5px;padding:3px}.controls button,.controls a{font-size:10px;padding:8px 6px}.help{right:6px;bottom:7px;font-size:10px;padding:6px 10px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}main *{animation:none!important}}
</style></head><body>
<nav class="controls" aria-label="World navigation">
<button type="button" data-jump="0">☀️ Welcome</button><button type="button" data-jump="940">🌊 Projects</button><button type="button" data-jump="2260">🫧 Products</button><button type="button" data-jump="2950">⚙️ Stack</button><button type="button" data-jump="3700">🌱 Journey</button><button id="motion" type="button" aria-pressed="false">Ⅱ Pause</button><a href="https://github.com/KeremKalyoncu" target="_blank" rel="noopener noreferrer">GitHub ↗</a>
</nav>
<main id="world">'''+svg+'''</main><div class="help">Click the glowing panels · Click water to make bubbles</div>
<script>
const world=document.getElementById('world');const graphic=world.querySelector('svg');const light=document.getElementById('pointerLight');const ns='http://www.w3.org/2000/svg';
const motion=document.getElementById('motion');let paused=false;motion.addEventListener('click',()=>{paused=!paused;world.classList.toggle('paused',paused);motion.textContent=paused?'▶ Resume':'Ⅱ Pause';motion.setAttribute('aria-pressed',String(paused));});
document.querySelectorAll('[data-jump]').forEach(b=>b.addEventListener('click',()=>{const y=+b.dataset.jump;const bounds=graphic.getBoundingClientRect();const scale=bounds.width/1200;window.scrollTo({top:window.scrollY+bounds.top+y*scale-70,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});}));
let raf=0,px=-500,py=-500;world.addEventListener('pointermove',e=>{if(e.pointerType==='touch')return;const r=graphic.getBoundingClientRect();px=(e.clientX-r.left)*1200/r.width;py=(e.clientY-r.top)*5150/r.height;if(!raf)raf=requestAnimationFrame(()=>{light.setAttribute('cx',px);light.setAttribute('cy',py);raf=0});});
world.addEventListener('pointerleave',()=>{light.setAttribute('cx',-500);light.setAttribute('cy',-500);});
world.addEventListener('pointerdown',e=>{if(paused||e.target.closest('.hotspot')||matchMedia('(prefers-reduced-motion:reduce)').matches)return;const rect=graphic.getBoundingClientRect(),x=(e.clientX-rect.left)*1200/rect.width,y=(e.clientY-rect.top)*5150/rect.height;
for(let i=0;i<7;i++){let c=document.createElementNS(ns,'circle');let z=4+Math.random()*11;c.setAttribute('cx',x+(Math.random()-.5)*110);c.setAttribute('cy',y);c.setAttribute('r',z);c.setAttribute('stroke','#eaffff');c.setAttribute('fill','url(#bubbleShine)');c.style.pointerEvents='none';graphic.appendChild(c);let a=c.animate([{transform:'translateY(0px)',opacity:.9},{transform:`translate(${(Math.random()-.5)*100}px,-${140+Math.random()*230}px)`,opacity:0}],{duration:1400+Math.random()*1800,easing:'ease-out',fill:'forwards'});a.onfinish=()=>c.remove();}
});
</script></body></html>'''
(ROOT/'index.html').write_text(site,encoding='utf-8')
(ROOT/'README.md').write_text('''<div align="center">
<a href="https://github.com/KeremKalyoncu?tab=repositories">
<img src="assets/kerem-living-world-v8.svg" width="100%" alt="Kerem Kalyoncu's living Frutiger Aero engineering universe. Animated sea, bubbles, reef, public software projects, team products, VollSign experience, engineering toolkit, GDG community, academic journey and contact information. Click for public repositories."/>
</a>
</div>
''',encoding='utf-8')
(ROOT/'INSTALL.md').write_text('''# KEREM.AERO V8 — Installation

## What is different from V7?

V8 is a **single 1200×5150 SVG** that stays animated without JavaScript in image-enabled browsers. It extends the V7 sea, adding Inventra, Shifha, engineering technologies, Doğuş University, GDG community, HSD bootcamp, certification highlights and a collaboration portal. There are no stacked PNG/JPG section strips. The upper scenery uses one embedded photograph as its texture, but the world, animation and information layers are vector SVG.

## GitHub README installation (safe)

1. Open `KeremKalyoncu/KeremKalyoncu` in GitHub Desktop.
2. Create branch `feat/kerem-aero-v8` (do not modify main yet).
3. Copy this package's `README.md` to the profile repository root.
4. Copy `assets/kerem-living-world-v8.svg` into the existing `assets/` folder. **Merge files; do not delete the old folder.**
5. Commit, push branch and preview its README on GitHub.
6. Merge a pull request only if satisfied.

## Interaction and GitHub limitations

The animated SVG uses CSS animations and no JavaScript for GitHub rendering. Some clients or reduced-motion settings may suppress animations. The graphic is one image in GitHub, so its internal cards are NOT individually clickable; clicking the whole image opens the public GitHub repositories list.

For individual clickable cards, moving cursor light, bubble creation and scene navigation, deploy `index.html` as an **optional separate site**. It is self-contained and requires no libraries/CDN. You may open it locally. For GitHub Pages, create a separate repository for the landing page and put this `index.html` in its root; configure Pages to deploy from that branch. Do not overwrite the existing personal website when experimenting.

## Provenance and accuracy notes

- Personal public GitHub repositories were checked, and only public repositories were linked as public source code.
- Restofy is a team repository (`software-lecture-labs/Restofy`).
- Inventra and Shifha are collaborative LinkedIn portfolio projects; do not imply their private source is available.
- VollSign is professional experience with a link to the website provided by the profile owner.
- University, GDG role and the HSD-related data science bootcamp were checked against public LinkedIn profile information.
- This is a designed portfolio, not live system health telemetry. No performance, safety, uptime or production guarantees are claimed.
- GitHub may sanitize SVG behaviors and animations. Test on the target GitHub client before deploying.

## URLs

- GitHub profile: https://github.com/KeremKalyoncu
- LinkedIn profile: https://www.linkedin.com/in/kerem-kalyoncu/
- VollSign: https://vollsign.com
- Maritime Watch: https://github.com/KeremKalyoncu/maritime-watch
- Restofy: https://github.com/software-lecture-labs/Restofy
- Inventra live demo (linked from LinkedIn): https://x-etc.online
- GDG: https://tr.linkedin.com/company/gdg-on-campus-dogus
''',encoding='utf-8')
print('Built site with',len(hotspots),'individual hotspots; HTML length',len(site))
