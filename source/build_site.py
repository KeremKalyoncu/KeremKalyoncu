from pathlib import Path
from lxml import etree as ET
from html import escape

ROOT = Path(__file__).resolve().parents[1]
svg_path = ROOT / 'assets' / 'kerem-living-world-v9.svg'

if not svg_path.exists():
    print("V9 SVG not found, running build_v9.py first...")
    from build_v9 import build_v9
    build_v9()

svg = svg_path.read_text(encoding='utf-8')

# Hotspots for the interactive standalone site
hotspots = [
    ('Maritime Watch — live tactical marine dashboard', 'https://keremkalyoncu.github.io/maritime-watch', 76, 595, 1048, 325),
    ('Restofy — public team repository', 'https://github.com/software-lecture-labs/Restofy', 82, 988, 503, 359),
    ('KriptoParaTakip — public Java repository', 'https://github.com/KeremKalyoncu/KriptoParaTakip', 620, 1026, 496, 361),
    ('ML and Data Lab — public regression project', 'https://github.com/KeremKalyoncu/ml-final-odev', 82, 1451, 536, 284),
    ('Library System — public Python repository', 'https://github.com/KeremKalyoncu/Gelismis_Kutuphane_Sistemi', 651, 1513, 460, 276),
    ('VollSign — enterprise signature company', 'https://vollsign.com', 113, 1845, 977, 223),
    ('Inventra — cloud workforce & inventory platform', 'https://x-etc.online', 85, 2436, 510, 329),
    ('Shifha — clinical workflow AI protocol', 'https://www.linkedin.com/in/kerem-kalyoncu/', 621, 2480, 497, 329),
    ('Java & Spring Boot — Restofy architecture', 'https://github.com/software-lecture-labs/Restofy', 110, 3144, 390, 157),
    ('Web Engineering — React & TypeScript systems', 'https://github.com/KeremKalyoncu?tab=repositories', 700, 3144, 390, 157),
    ('Machine Learning & Data Intelligence', 'https://github.com/KeremKalyoncu/ml-ara-odev', 110, 3435, 390, 157),
    ('Delivery & Quality — Docker, PostgreSQL, CI', 'https://github.com/KeremKalyoncu?tab=repositories', 700, 3435, 390, 157),
    ('Doğuş University — Software Engineering BSc', 'https://www.linkedin.com/in/kerem-kalyoncu/', 97, 3860, 475, 158),
    ('GDG on Campus Doğuş — Community Lead', 'https://tr.linkedin.com/company/gdg-on-campus-dogus', 649, 3992, 455, 173),
    ('Huawei AI Academy — Data Science & ML', 'https://www.linkedin.com/in/kerem-kalyoncu/', 100, 4170, 474, 174),
    ('Certifications & Learning Milestones', 'https://www.linkedin.com/in/kerem-kalyoncu/', 638, 4303, 463, 167),
    ('Connect & Open Channels — LinkedIn', 'https://www.linkedin.com/in/kerem-kalyoncu/', 315, 4781, 575, 212)
]

anchors = ''.join(
    f'<a class="hotspot" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="{escape(name, quote=True)}"><title>{escape(name)}</title><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="42" fill="transparent"/></a>'
    for name, url, x, y, w, h in hotspots
)

fx = '<circle id="pointerLight" cx="-500" cy="-500" r="220" fill="url(#blueGlow)" opacity=".36" pointer-events="none"/>'
svg_interactive = svg.replace('</g></svg>', anchors + fx + '</g></svg>')

site = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
  <meta name="theme-color" content="#159dc9"/>
  <meta name="description" content="Explore Kerem Kalyoncu's living Frutiger Aero engineering ocean — interactive depth gauge, real-time telemetry, public software fleet, collaborative systems and open water portal."/>
  <title>KEREM.AERO V9 — The Living Engineering Ocean</title>
  <style>
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; background: #075077; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: linear-gradient(165deg, #34bfe8, #075077 55%, #041d45);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #e0f2fe;
    }}
    main {{
      width: 100%;
      max-width: 1200px;
      margin: auto;
      line-height: 0;
      position: relative;
      overflow: hidden;
      isolation: isolate;
      box-shadow: 0 0 100px #001c4699;
    }}
    main > svg {{ width: 100%; height: auto; display: block; }}
    .controls {{
      position: fixed;
      z-index: 100;
      left: 50%;
      transform: translateX(-50%);
      top: clamp(8px, 1.8vw, 18px);
      display: flex;
      flex-wrap: nowrap;
      align-items: center;
      gap: 6px;
      background: #063b6acc;
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      padding: 6px 10px;
      border: 1px solid #c3ffff80;
      border-radius: 99px;
      max-width: calc(100vw - 16px);
      box-shadow: 0 8px 32px #00284688;
    }}
    .controls button, .controls a {{
      color: #fff;
      font: 600 12.5px 'Segoe UI', Arial, sans-serif;
      text-decoration: none;
      white-space: nowrap;
      border-radius: 50px;
      border: 1px solid transparent;
      padding: 8px 12px;
      cursor: pointer;
      background: transparent;
      transition: all .2s ease;
    }}
    .controls button:hover, .controls a:hover,
    .controls button:focus-visible, .controls a:focus-visible {{
      outline: none;
      background: #e3ffff33;
      border: 1px solid #d9ffff88;
      box-shadow: 0 0 12px #38bdf888;
    }}
    .controls a.btn-cta {{
      background: linear-gradient(135deg, #0284c7, #0ea5e9);
      border: 1px solid #7dd3fc;
    }}
    .hotspot rect {{
      cursor: pointer;
      stroke: transparent;
      stroke-width: 3;
      transition: fill .25s, stroke .25s;
    }}
    .hotspot:hover rect, .hotspot:focus-visible rect {{
      fill: #ffffff;
      fill-opacity: .12;
      stroke: #7dd3fc;
      stroke-opacity: .8;
      filter: drop-shadow(0 0 10px #38bdf8);
    }}
    .hotspot:focus {{ outline: none; }}
    .paused * {{ animation-play-state: paused !important; }}
    .depth-indicator {{
      position: fixed;
      left: 18px;
      bottom: 18px;
      color: #7dd3fc;
      background: #063b6ad9;
      border: 1px solid #38bdf866;
      border-radius: 16px;
      padding: 8px 14px;
      font: 700 11.5px 'Consolas', monospace;
      z-index: 100;
      backdrop-filter: blur(14px);
      box-shadow: 0 4px 20px #00000066;
    }}
    .help {{
      position: fixed;
      right: 18px;
      bottom: 18px;
      color: #eaffff;
      background: #063b6ac0;
      border: 1px solid #ddffff55;
      border-radius: 20px;
      padding: 8px 15px;
      font: 11.5px 'Segoe UI', Arial, sans-serif;
      pointer-events: none;
      z-index: 99;
      backdrop-filter: blur(12px);
    }}
    @media(max-width: 850px) {{
      .controls {{ top: 4px; padding: 4px 6px; gap: 3px; }}
      .controls button, .controls a {{ font-size: 10px; padding: 6px 8px; }}
      .help {{ display: none; }}
      .depth-indicator {{ left: 8px; bottom: 8px; font-size: 10px; padding: 6px 10px; }}
    }}
    @media(prefers-reduced-motion: reduce) {{
      html {{ scroll-behavior: auto; }}
      main * {{ animation: none !important; }}
    }}
  </style>
</head>
<body>
  <nav class="controls" aria-label="Ocean navigation">
    <button type="button" data-jump="0">☀️ 0m Surface</button>
    <button type="button" data-jump="650">🚢 650m Maritime</button>
    <button type="button" data-jump="1050">🫧 1000m Fleet</button>
    <button type="button" data-jump="2450">🌐 2450m Inventra</button>
    <button type="button" data-jump="3250">⚙️ 3250m Stack</button>
    <button type="button" data-jump="4750">🌌 4800m Portal</button>
    <button id="soundToggle" type="button" aria-pressed="false">🔊 Ocean Sound</button>
    <button id="motion" type="button" aria-pressed="false">Ⅱ Pause</button>
    <a href="https://github.com/KeremKalyoncu" class="btn-cta" target="_blank" rel="noopener noreferrer">GitHub Profile ↗</a>
  </nav>

  <main id="world">
    {svg_interactive}
  </main>

  <div class="depth-indicator" id="depthHUD">DEPTH: 0000M // EPIPELAGIC</div>
  <div class="help">Click glowing panels · Click ocean to spawn bubbles</div>

  <script>
    const world = document.getElementById('world');
    const graphic = world.querySelector('svg');
    const light = document.getElementById('pointerLight');
    const motion = document.getElementById('motion');
    const soundToggle = document.getElementById('soundToggle');
    const depthHUD = document.getElementById('depthHUD');
    const ns = 'http://www.w3.org/2000/svg';
    let paused = false;

    // Pause/Resume Motion
    motion.addEventListener('click', () => {{
      paused = !paused;
      world.classList.toggle('paused', paused);
      motion.textContent = paused ? '▶ Resume' : 'Ⅱ Pause';
      motion.setAttribute('aria-pressed', String(paused));
    }});

    // Procedural Ocean Web Audio API Generator
    let audioCtx = null;
    let oceanGain = null;
    let soundActive = false;

    function initOceanAudio() {{
      if (audioCtx) return;
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContext();

      // Procedural Ocean Wave Hum (Pink/Brown noise + lowpass filter)
      const bufferSize = audioCtx.sampleRate * 2;
      const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      let b0 = 0, b1 = 0, b2 = 0;
      for (let i = 0; i < bufferSize; i++) {{
        const white = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        output[i] = (b0 + b1 + b2) * 0.08;
      }}

      const whiteNoise = audioCtx.createBufferSource();
      whiteNoise.buffer = noiseBuffer;
      whiteNoise.loop = true;

      const filter = audioCtx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 320;

      // Filter LFO for gentle wave swells
      const lfo = audioCtx.createOscillator();
      lfo.frequency.value = 0.15; // 6.6s wave cycle
      const lfoGain = audioCtx.createGain();
      lfoGain.gain.value = 180;
      lfo.connect(lfoGain);
      lfoGain.connect(filter.frequency);
      lfo.start();

      oceanGain = audioCtx.createGain();
      oceanGain.gain.value = 0.001;

      whiteNoise.connect(filter);
      filter.connect(oceanGain);
      oceanGain.connect(audioCtx.destination);
      whiteNoise.start();
    }}

    soundToggle.addEventListener('click', () => {{
      initOceanAudio();
      if (audioCtx.state === 'suspended') audioCtx.resume();
      soundActive = !soundActive;
      soundToggle.setAttribute('aria-pressed', String(soundActive));
      if (soundActive) {{
        soundToggle.textContent = '🔈 Mute';
        oceanGain.gain.setTargetAtTime(0.35, audioCtx.currentTime, 0.4);
      }} else {{
        soundToggle.textContent = '🔊 Ocean Sound';
        oceanGain.gain.setTargetAtTime(0.001, audioCtx.currentTime, 0.3);
      }}
    }});

    // Depth HUD on Scroll
    window.addEventListener('scroll', () => {{
      const totalH = graphic.getBoundingClientRect().height;
      const scrollPos = window.scrollY;
      const ratio = Math.min(1, Math.max(0, scrollPos / (totalH - window.innerHeight)));
      const depthMeters = Math.round(ratio * 5150);

      let zone = 'EPIPELAGIC';
      if (depthMeters > 4500) zone = 'HADAL TRENCH';
      else if (depthMeters > 3000) zone = 'ABYSSOPELAGIC';
      else if (depthMeters > 1800) zone = 'BATHYPELAGIC';
      else if (depthMeters > 800) zone = 'MESOPELAGIC';

      depthHUD.textContent = `DEPTH: ${{String(depthMeters).padStart(4, '0')}}M // ${{zone}}`;
    }}, {{ passive: true }});

    // Smooth Jump Navigation
    document.querySelectorAll('[data-jump]').forEach(b => b.addEventListener('click', () => {{
      const y = +b.dataset.jump;
      const bounds = graphic.getBoundingClientRect();
      const scale = bounds.width / 1200;
      window.scrollTo({{
        top: window.scrollY + bounds.top + y * scale - 70,
        behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
      }});
    }}));

    // Pointer Light
    let raf = 0, px = -500, py = -500;
    world.addEventListener('pointermove', e => {{
      if (e.pointerType === 'touch') return;
      const r = graphic.getBoundingClientRect();
      px = (e.clientX - r.left) * 1200 / r.width;
      py = (e.clientY - r.top) * 5150 / r.height;
      if (!raf) raf = requestAnimationFrame(() => {{
        light.setAttribute('cx', px);
        light.setAttribute('cy', py);
        raf = 0;
      }});
    }});
    world.addEventListener('pointerleave', () => {{
      light.setAttribute('cx', -500);
      light.setAttribute('cy', -500);
    }});

    // Click to Spawn Real Physics Bubbles
    world.addEventListener('pointerdown', e => {{
      if (paused || e.target.closest('.hotspot') || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      const rect = graphic.getBoundingClientRect();
      const x = (e.clientX - rect.left) * 1200 / rect.width;
      const y = (e.clientY - rect.top) * 5150 / rect.height;

      for (let i = 0; i < 8; i++) {{
        const c = document.createElementNS(ns, 'circle');
        const z = 4 + Math.random() * 12;
        c.setAttribute('cx', x + (Math.random() - .5) * 120);
        c.setAttribute('cy', y);
        c.setAttribute('r', z);
        c.setAttribute('stroke', '#eaffff');
        c.setAttribute('stroke-width', '1.2');
        c.setAttribute('fill', 'url(#bubbleShine)');
        c.style.pointerEvents = 'none';
        graphic.appendChild(c);

        const driftX = (Math.random() - .5) * 110;
        const driftY = -(150 + Math.random() * 260);
        const a = c.animate([
          {{ transform: 'translate(0px, 0px) scale(0.8)', opacity: .95 }},
          {{ transform: `translate(${{driftX}}px, ${{driftY}}px) scale(1.15)`, opacity: 0 }}
        ], {{
          duration: 1500 + Math.random() * 2000,
          easing: 'cubic-bezier(0.2, 0.8, 0.4, 1)',
          fill: 'forwards'
        }});
        a.onfinish = () => c.remove();
      }}
    }});
  </script>
</body>
</html>
'''

(ROOT / 'index.html').write_text(site, encoding='utf-8')
print("Successfully generated index.html")

# ==========================================================
# MASTERPIECE README.md
# ==========================================================
readme = '''<div align="center">

<!-- AERO GLASS ACTION BAR -->
<a href="https://keremkalyoncu.github.io/KeremKalyoncu">
  <img src="https://img.shields.io/badge/🚀%20ENTER%20INTERACTIVE%203D%20OCEAN-0284C7?style=for-the-badge&logo=googleearth&logoColor=white" alt="Interactive 3D Aero Ocean" />
</a>
<a href="https://keremkalyoncu.github.io/maritime-watch">
  <img src="https://img.shields.io/badge/🚢%20MARITIME%20WATCH%20LIVE-0E7490?style=for-the-badge&logo=safari&logoColor=white" alt="Maritime Watch Live Demo" />
</a>
<a href="https://x-etc.online">
  <img src="https://img.shields.io/badge/📦%20INVENTRA%20PLATFORM-059669?style=for-the-badge&logo=react&logoColor=white" alt="Inventra Platform" />
</a>
<a href="https://www.linkedin.com/in/kerem-kalyoncu/">
  <img src="https://img.shields.io/badge/💼%20LINKEDIN%20PROFILE-1D4ED8?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Profile" />
</a>
<a href="https://github.com/KeremKalyoncu?tab=repositories">
  <img src="https://img.shields.io/badge/📁%20PUBLIC%20FLEET-041D45?style=for-the-badge&logo=github&logoColor=38BDF8" alt="Explore Repositories" />
</a>

<br /><br />

<!-- QUICK JUMP TELEMETRY BAR -->
<code>[ <a href="#flagship">01_MARITIME_WATCH</a> ]</code> ·
<code>[ <a href="#fleet">02_SOFTWARE_FLEET</a> ]</code> ·
<code>[ <a href="#platforms">03_CO_BUILT_PLATFORMS</a> ]</code> ·
<code>[ <a href="#telemetry">04_LIVING_TELEMETRY</a> ]</code> ·
<code>[ <a href="#stack">05_TECH_REEF</a> ]</code> ·
<code>[ <a href="#connect">06_CONNECT</a> ]</code>

<br /><br />

<!-- THE CONTINUOUS LIVING OCEAN (V9 ULTRA) -->
<a href="https://keremkalyoncu.github.io/KeremKalyoncu">
  <img src="assets/kerem-living-world-v9.svg" width="100%" alt="Kerem Kalyoncu — living Frutiger Aero ultra universe with real-time oceanographic depth gauge, animated sonar telemetry, public software fleet, collaborative platforms, engineering reef and contact portal. Click to enter interactive mode."/>
</a>

<br /><br />

<!-- REAL-TIME BOSPHORUS & DEVELOPER TELEMETRY HUD -->
<a id="telemetry"></a>
<a href="https://keremkalyoncu.github.io/maritime-watch">
  <img src="assets/developer-telemetry.svg" width="100%" alt="Living Developer Telemetry HUD — Real-time Bosphorus Marine Conditions and Verified Capability Matrix"/>
</a>

<br /><br />

<!-- LIVING CONTRIBUTION STREAM -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="output/github-contribution-grid-snake.svg" />
  <img src="output/github-contribution-grid-snake.svg" alt="Animated contribution snake" width="100%" />
</picture>

<br /><br />

<!-- STATS & PROFILE SIGNAL BADGES -->
<a href="https://github.com/KeremKalyoncu">
  <img src="https://streak-stats.demolab.com?user=KeremKalyoncu&theme=tokyonight&hide_border=true&background=041D45&ring=38BDF8&fire=34D399&currStreakLabel=38BDF8&sideLabels=E0F2FE&dates=7DD3FC" alt="GitHub contribution streak" />
</a>

<br /><br />

<img src="https://komarev.com/ghpvc/?username=KeremKalyoncu&style=for-the-badge&color=0284C7&label=PROFILE+SIGNALS" alt="Profile views" />

</div>

<br />

<!--
  ATS & RECRUITER EXECUTIVE SPECIFICATIONS
-->
<a id="flagship"></a>
<a id="fleet"></a>
<a id="platforms"></a>
<a id="stack"></a>
<a id="connect"></a>

<details>
  <summary><b>🔍 Click to expand Plain Text & ATS Executive Specifications</b></summary>
  <br />

### 👤 Profile Overview
- **Name:** Kerem Kalyoncu
- **Role:** Software Engineer
- **Location:** İstanbul, Türkiye (41.0082° N, 28.9784° E)
- **Education:** Doğuş University — Software Engineering, BSc (2023 — 2027)
- **Leadership:** GDG on Campus Doğuş — Design & Social Media Team Lead
- **Training:** Huawei × AI Academy (Data Science & Machine Learning), BTK AI Fundamentals

---

### 🚢 Key Engineering Projects
1. **[Maritime Watch Türkiye](https://keremkalyoncu.github.io/maritime-watch)** *(Live Production System)*
   - Translates multi-source weather forecasts, real-time AIS telemetry, and Turkish navigational warnings into vessel-specific departure decisions (`Go / Caution / No-Go`).
   - *Stack:* Python, Leaflet.js, Open-Meteo, PWA, Edge Computing.
2. **[Inventra](https://x-etc.online)** *(Cloud Workforce & Inventory Platform)*
   - Full enterprise workflow platform for staff management, inventory auditing, and operational pipelines.
   - *Stack:* ASP.NET Core, React, Material UI, PostgreSQL.
3. **[Restofy](https://github.com/software-lecture-labs/Restofy)** *(Restaurant Microservices)*
   - Scalable QR menu and order dispatching backend built for high concurrency.
   - *Stack:* Java, Spring Boot, Microservices, Docker.
4. **[KriptoParaTakip](https://github.com/KeremKalyoncu/KriptoParaTakip)** *(Financial Market Engine)*
   - Live telemetry, price tracking, and automated volatility alerts.
   - *Stack:* Java, REST APIs, Desktop GUI, JSON Pipelines.
5. **[Shifha](https://www.linkedin.com/in/kerem-kalyoncu/)** *(Clinical AI Protocol)*
   - Collaborative medical information routing and automated clinician decision support.
   - *Stack:* React Native, Python, Medical NLP.

---

### ⚙️ Core Technical Constellation
- **Backend & Systems:** Java, Spring Boot, C#, ASP.NET Core, Python, REST APIs, Microservices.
- **Web & Interface:** TypeScript, React, Next.js, HTML5/CSS3, Frutiger Aero Vector Design, Leaflet.js.
- **Data & Intelligence:** Python, Pandas, NumPy, scikit-learn, SQLite, DuckDB, Machine Learning Pipelines.
- **Delivery & DevOps:** Docker, PostgreSQL, GitHub Actions, Linux/Bash, Continuous Integration (CI/CD).

---

### 📬 Connect & Channels
- **GitHub:** [github.com/KeremKalyoncu](https://github.com/KeremKalyoncu)
- **LinkedIn:** [linkedin.com/in/kerem-kalyoncu](https://www.linkedin.com/in/kerem-kalyoncu/)
- **Live Interactive Experience:** [keremkalyoncu.github.io/KeremKalyoncu](https://keremkalyoncu.github.io/KeremKalyoncu)

</details>

<br />

<div align="center">
  <sub>Engineered with deterministic precision & Frutiger Aero aesthetics · Kerem Kalyoncu © 2026</sub>
</div>
'''

(ROOT / 'README.md').write_text(readme, encoding='utf-8')
print("Successfully generated README.md")
