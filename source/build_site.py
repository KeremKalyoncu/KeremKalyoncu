from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
SVG=(ROOT/'assets'/'kerem-living-world.svg').read_text(encoding='utf-8')
links=[
 ('Maritime Watch · Live public project','https://keremkalyoncu.github.io/maritime-watch',76,595,1048,325),
 ('Restofy · Public team repository','https://github.com/software-lecture-labs/Restofy',82,988,503,359),
 ('KriptoParaTakip · Public Java project','https://github.com/KeremKalyoncu/KriptoParaTakip',620,1026,496,361),
 ('Machine Learning · Public ML work','https://github.com/KeremKalyoncu/ml-final-odev',82,1451,536,284),
 ('Library System · Public Python project','https://github.com/KeremKalyoncu/Gelismis_Kutuphane_Sistemi',651,1513,460,276),
 ('VollSign · Official website','https://vollsign.com',113,1845,977,223),
]
parts=[]
for name,link,x,y,w,h in links:
 parts.append(f'<a class="hotspot" href="{link}" target="_blank" rel="noopener noreferrer" aria-label="{name}"><title>{name}</title><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="60" fill="transparent"/></a>')
parts.append('<circle id="pointerLight" cx="-500" cy="-500" r="170" fill="url(#blueGlow)" opacity=".33" pointer-events="none"/>')
SVG=SVG.replace('</g></svg>',''.join(parts)+'</g></svg>')
html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#17b4e2"/><meta name="description" content="The living Frutiger Aero world of software engineer Kerem Kalyoncu. Explore open-source projects and engineering experience."/>
<title>KEREM.AERO — A Living Engineering World</title>
<style>
*{{box-sizing:border-box}} html{{background:#0c7caa; scroll-behavior:smooth}}body{{margin:0; min-height:100vh; background:linear-gradient(170deg,#9eeeff,#10bbd4,#014e7b);display:flex;justify-content:center;color:white;font-family:Segoe UI,Arial,sans-serif}}
.world{{width:100%;max-width:1200px;margin:0 auto;position:relative;line-height:0;overflow:hidden;isolation:isolate;box-shadow:0 0 95px #044a6e66}}.world>svg{{display:block;width:100%;height:auto}}
.hotspot rect{{cursor:pointer;stroke:transparent;stroke-width:3;transition:fill .3s,stroke .3s}}.hotspot:hover rect,.hotspot:focus-visible rect{{fill:#fff;fill-opacity:.09;stroke:#d8ffff;stroke-opacity:.8}}.hotspot:focus{{outline:none}}
.controls{{position:fixed;right:clamp(10px,3vw,40px);top:clamp(10px,2vw,30px);z-index:10;display:flex;gap:8px}}
.controls button{{color:white;background:rgba(0,101,151,.58);border:1px solid #d5ffffab;border-radius:40px;padding:10px 18px;backdrop-filter:blur(14px);box-shadow:0 6px 24px #053b6077;font:600 14px Segoe UI,Arial;cursor:pointer}}
.controls button:hover{{background:rgba(6,138,183,.8)}}.world.paused *{{animation-play-state:paused!important}}
@media(max-width:600px){{.controls button{{font-size:11px;padding:8px 10px}}.controls{{top:8px;right:8px}}}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
</style></head><body>
<div class="controls"><button id="motion" aria-pressed="false" title="Toggle motion">Ⅱ Pause motion</button><button id="github" title="GitHub projects">GitHub ↗</button></div>
<main class="world" id="world">{SVG}</main>
<script>
const stage=document.getElementById('world');const motion=document.getElementById('motion'); const g=document.getElementById('pointerLight');const graphic=stage.querySelector('svg');const NS='http://www.w3.org/2000/svg';
motion.addEventListener('click',()=>{{const paused=stage.classList.toggle('paused');motion.textContent=paused?'▶ Resume motion':'Ⅱ Pause motion';motion.setAttribute('aria-pressed',String(paused))}});
document.getElementById('github').addEventListener('click',()=>window.open('https://github.com/KeremKalyoncu?tab=repositories','_blank','noopener'));
let pending=false, xx=-500, yy=-500;
stage.addEventListener('pointermove',(e)=>{{const r=graphic.getBoundingClientRect();xx=(e.clientX-r.left)*1200/r.width;yy=(e.clientY-r.top)*2200/r.height;if(!pending){{pending=true;requestAnimationFrame(()=>{{g.setAttribute('cx',xx);g.setAttribute('cy',yy);pending=false}})}}}});
stage.addEventListener('pointerleave',()=>{{g.setAttribute('cx',-500);g.setAttribute('cy',-500)}});
const reduced=window.matchMedia('(prefers-reduced-motion:reduce)').matches;
stage.addEventListener('pointerdown',(e)=>{{if(reduced||stage.classList.contains('paused')||e.target.closest('.hotspot'))return;const r=graphic.getBoundingClientRect(),x=(e.clientX-r.left)*1200/r.width,y=(e.clientY-r.top)*2200/r.height;
for(let i=0;i<7;i++){{const c=document.createElementNS(NS,'circle'),radius=3+Math.random()*9;c.setAttribute('cx',x+(Math.random()-.5)*95);c.setAttribute('cy',y);c.setAttribute('r',radius);c.setAttribute('stroke','#e6ffff');c.setAttribute('fill','url(#bubbleShine)');c.style.pointerEvents='none';graphic.appendChild(c);const a=c.animate([{{transform:'translateY(0px)',opacity:.75}},{{transform:`translate(${{(Math.random()-.5)*70}}px,-${{100+Math.random()*170}}px)`,opacity:0}}],{{duration:1700+Math.random()*1200,fill:'forwards',easing:'ease-out'}});a.onfinish=()=>c.remove()}}
}});
</script></body></html>'''
(ROOT/'index.html').write_text(html,encoding='utf-8')
readme='''<div align="center">
<a href="https://github.com/KeremKalyoncu?tab=repositories">
<img src="assets/kerem-living-world.svg" width="100%" alt="Kerem Kalyoncu — living Frutiger Aero portfolio. Animated clouds, sea, floating project capsules, marine radar, bubbles, and career highlights. Click to explore public projects." />
</a>
</div>
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
(ROOT/'PUBLISH.md').write_text('''# KEREM.AERO V7 — installation

## What is actually moving?

The GitHub README uses **one animated SVG**, not a long PNG. The SVG animates clouds, sunlight, caustics, surface waves, 56 bubbles, fish, project capsules, a radar sweep, a boat, a market trend, restaurant steam, jellyfish, and seagrass. The illustration background is embedded as a JPEG inside the SVG so the asset is fully self-contained. It is not a static raster animation.

## Safe test

1. Open the `KeremKalyoncu/KeremKalyoncu` repository in GitHub Desktop.
2. Create a branch, e.g., `feat/aero-living-v7`.
3. Copy `README.md` to the repository root (replacing the old README only in the branch).
4. Copy `assets/kerem-living-world.svg` to the repository `assets/` folder, preserving your existing assets.
5. Commit and push the branch, then open the branch's `README.md` on GitHub to verify the animation.
6. Merge the branch only when satisfied.

## Project links

In a GitHub README, an SVG embedded as `<img>` cannot act as a full interactive app: individual project tiles inside the image are **not individually clickable**. The complete GitHub image is linked to the public repo list instead.

`index.html` is an optional separate interactive website version. Its project capsules have independent links, mouse-following light, click-to-spawn bubbles, and a motion-pause button. It can be deployed using GitHub Pages (Deploy from a branch, root). Only after GitHub Pages is confirmed working should you point the README image link at that website.

## Important

- No JavaScript runs in the GitHub README. Motion uses CSS SVG animation only.
- Some GitHub clients, reduced-motion settings and SVG rendering environments can suppress animation; static fallback remains legible.
- `V7-MOTION-PREVIEW.gif` is only for viewing a short motion sample. The README uses SVG, not GIF.
- The project summaries and links are based on public repositories. Restofy is a team project; VollSign is professional experience.
''',encoding='utf-8')
print('index.html',len(html),'README',len(readme),'hotspots',len(links))
# Verify parse on full inlined SVG and links
etree.fromstring(SVG.encode())
