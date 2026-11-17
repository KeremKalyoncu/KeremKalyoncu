from pathlib import Path
from lxml import etree as ET
from lxml.etree import SubElement
import random, math

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'assets' / 'kerem-living-world-v8.svg'
TARGET = ROOT / 'assets' / 'kerem-living-world-v9.svg'
NS = 'http://www.w3.org/2000/svg'
Q = lambda s: f'{{{NS}}}{s}'

def build_v9():
    print(f"Loading {SRC}...")
    root = ET.parse(str(SRC)).getroot()
    defs = root.find(Q('defs'))
    g = root[-1]  # main canvas group
    H = 5150

    root.set('aria-label', "Kerem Kalyoncu — living Frutiger Aero ultra universe with real-time oceanographic depth gauge, animated sonar telemetry, public software fleet, collaborative platforms, engineering reef and contact portal.")
    title = root.find(Q('title'))
    if title is not None:
        title.text = 'KEREM.AERO V9 — The Living Engineering Ocean (Ultra Edition)'
    desc = root.find(Q('desc'))
    if desc is not None:
        desc.text = 'Animated continuous Frutiger Aero world by Kerem Kalyoncu. Live depth gauge HUD, sonar telemetry, public GitHub projects, VollSign experience, Inventra and Shifha platforms, engineering constellation, GDG leadership and contact portal.'

    def E(p, tag, **a):
        x = SubElement(p, Q(tag))
        for k, v in a.items():
            x.set('class' if k == 'class__' else k.replace('__', '-'), str(v))
        return x

    def grad(id, colors, kind='linear', **attrib):
        attrs = {'id': id}
        attrs.update(attrib)
        node = E(defs, 'linearGradient' if kind == 'linear' else 'radialGradient', **attrs)
        for off, c, op in colors:
            a = {'offset': off, 'stop__color': c}
            if op is not None:
                a['stop__opacity'] = op
            E(node, 'stop', **a)
        return node

    # New Gradients for V9
    grad('depthGlow', [('0', '#38bdf8', '.85'), ('.3', '#06b6d4', '.65'), ('.7', '#0284c7', '.45'), ('1', '#0369a1', '.15')], x1='0', y1='0', x2='0', y2='1')
    grad('scannerGlow', [('0', '#ffffff', '0'), ('.5', '#38bdf8', '.95'), ('1', '#06b6d4', '0')], x1='0', y1='0', x2='0', y2='1')
    grad('sonarGreen', [('0', '#34d399', '.8'), ('.6', '#059669', '.2'), ('1', '#047857', '0')], kind='radial', cx='50%', cy='50%', r='50%')
    grad('sonarCyan', [('0', '#38bdf8', '.85'), ('.5', '#0284c7', '.25'), ('1', '#0369a1', '0')], kind='radial', cx='50%', cy='50%', r='50%')
    grad('hudGlass', [('0', '#0a2e5c', '.65'), ('.5', '#061d3d', '.8'), ('1', '#031024', '.9')], x1='0', y1='0', x2='1', y2='1')

    # Extend CSS in style tag
    style = defs.find(Q('style'))
    extra_css = '''
    /* === V9 ULTRA AERO HUD & TELEMETRY === */
    .depthTick { stroke: #38bdf8; stroke-width: 1.5; stroke-opacity: 0.65; }
    .depthTickMajor { stroke: #e0f2fe; stroke-width: 2.2; stroke-opacity: 0.95; }
    .depthText { font-family: 'Consolas', 'Courier New', monospace; font-size: 10px; font-weight: 700; fill: #7dd3fc; letter-spacing: 1px; }
    .depthBadge { font-family: 'Consolas', 'Courier New', monospace; font-size: 9.5px; font-weight: 800; fill: #bae6fd; letter-spacing: 1.2px; }
    .scannerBeam { animation: scanTravel 16s cubic-bezier(0.4, 0, 0.2, 1) infinite; }
    @keyframes scanTravel { 0% { transform: translateY(60px); opacity: 0; } 5% { opacity: 0.9; } 95% { opacity: 0.9; } 100% { transform: translateY(5080px); opacity: 0; } }
    
    .sonarWave { animation: sonarRing 4.5s cubic-bezier(0.1, 0.5, 0.4, 1) infinite; transform-box: fill-box; transform-origin: center; pointer-events: none; }
    .sonarWaveDelay { animation: sonarRing 4.5s cubic-bezier(0.1, 0.5, 0.4, 1) -2.25s infinite; transform-box: fill-box; transform-origin: center; pointer-events: none; }
    @keyframes sonarRing { 0% { r: 18px; opacity: 0.9; stroke-width: 3.5px; } 50% { opacity: 0.45; } 100% { r: 180px; opacity: 0; stroke-width: 0.5px; } }
    
    .statusPill { animation: pillGlow 3s ease-in-out infinite alternate; }
    @keyframes pillGlow { 0% { filter: drop-shadow(0 0 2px #38bdf8); } 100% { filter: drop-shadow(0 0 8px #38bdf8); } }
    
    .ledGreen { animation: ledBlink 1.8s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
    .ledCyan { animation: ledBlink 2.4s ease-in-out -0.6s infinite; transform-box: fill-box; transform-origin: center; }
    .ledAmber { animation: ledBlink 2s ease-in-out -1.2s infinite; transform-box: fill-box; transform-origin: center; }
    @keyframes ledBlink { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.35; transform: scale(0.85); } }
    
    .biolumOrb { animation: bioFloat var(--dur, 7s) ease-in-out var(--delay, 0s) infinite alternate; transform-box: fill-box; transform-origin: center; }
    @keyframes bioFloat { 0% { transform: translate(0, 0) scale(0.85); opacity: 0.25; } 50% { transform: translate(14px, -35px) scale(1.15); opacity: 0.85; } 100% { transform: translate(-10px, -70px) scale(0.9); opacity: 0.2; } }
    '''
    style.text = (style.text or '') + extra_css

    # ==========================================================
    # 1. DEPTH GAUGE & OCEANOGRAPHIC HUD (LEFT MARGIN x=38)
    # ==========================================================
    hud = E(g, 'g', id='oceanDepthGauge')
    
    # Continuous vertical glass beam
    E(hud, 'rect', x='37', y='80', width='4', height='4990', rx='2', fill='url(#depthGlow)', opacity='.45')
    E(hud, 'line', x1='39', y1='80', x2='39', y2='5070', stroke='#38bdf8', stroke__width='1.5', stroke__opacity='.7')
    
    # Gliding Scanner Light
    scanner = E(hud, 'g', class__='scannerBeam')
    E(scanner, 'rect', x='33', y='0', width='12', height='120', rx='6', fill='url(#scannerGlow)')
    E(scanner, 'circle', cx='39', cy='60', r='4', fill='#ffffff', opacity='.9')

    # Depth markers and zones
    depth_markers = [
        (0, 110, "0000M", "EPIPELAGIC // SURFACE (41.0082°N, 28.9784°E)"),
        (250, 360, "0250M", None),
        (500, 610, "0500M", None),
        (650, 740, "0650M", "SURFACE RADAR // MARITIME WATCH INTEL"),
        (850, 950, "0850M", None),
        (1000, 1100, "1000M", "MESOPELAGIC // RESTOFY & OPEN FLEET"),
        (1250, 1350, "1250M", None),
        (1500, 1600, "1500M", "DATA LAB // REGRESSION & AUTOMATION"),
        (1850, 1950, "1850M", "ENTERPRISE // VOLLSIGN INFRASTRUCTURE"),
        (2200, 2300, "2200M", "BATHYPELAGIC // TWILIGHT ARCHITECTURE"),
        (2450, 2550, "2450M", "CO-BUILT PLATFORMS // INVENTRA & SHIFHA"),
        (2800, 2900, "2800M", None),
        (3150, 3250, "3150M", "ABYSSOPELAGIC // BACKEND & SYSTEMS CORE"),
        (3450, 3550, "3450M", "CLOUD DELIVERY // DOCKER · PG · CI"),
        (3800, 3900, "3800M", "ACADEMIC CONTINUUM // DOĞUŞ BSc"),
        (4050, 4150, "4050M", "COMMUNITY LEADERSHIP // GDG ON CAMPUS"),
        (4350, 4450, "4350M", "AI ACADEMY // HUAWEI MACHINE LEARNING"),
        (4650, 4750, "4650M", "HADAL TRENCH // KEREM KALYONCU"),
        (5000, 5080, "5000M", "OPEN WATER PORTAL // GITHUB × LINKEDIN")
    ]

    for depth, y, depth_str, label in depth_markers:
        is_major = label is not None
        tick_len = 16 if is_major else 9
        stroke_cls = 'depthTickMajor' if is_major else 'depthTick'
        
        # Tick line
        E(hud, 'line', x1='31', y1=str(y), x2=str(31 + tick_len), y2=str(y), class__=stroke_cls)
        
        # Glowing node
        node_r = '3.5' if is_major else '2'
        E(hud, 'circle', cx='39', cy=str(y), r=node_r, fill='#ffffff' if is_major else '#38bdf8', opacity='.9' if is_major else '.6')
        
        # Depth number text
        t = E(hud, 'text', x='52', y=str(y + 4), class__='depthText')
        t.text = depth_str
        if is_major:
            t.set('fill', '#ffffff')
            t.set('font-weight', '800')
            
        # Major Zone Label (Horizontal badge)
        if label:
            # Badge background
            bw = len(label) * 6.5 + 16
            E(hud, 'rect', x='50', y=str(y + 11), width=str(bw), height='18', rx='5', fill='url(#hudGlass)', stroke='#38bdf8', stroke__width='.9', stroke__opacity='.55')
            E(hud, 'circle', cx='58', cy=str(y + 20), r='2.5', fill='#38bdf8', class__='ledCyan')
            bt = E(hud, 'text', x='66', y=str(y + 23), class__='depthBadge')
            bt.text = label

    # ==========================================================
    # 2. SONAR EXPANSION RINGS
    # ==========================================================
    sonar_group = E(g, 'g', id='sonarRings')
    
    # Sonar at Maritime Watch Radar (cx=273, cy=734)
    E(sonar_group, 'circle', cx='273', cy='734', r='18', fill='none', stroke='#34d399', class__='sonarWave')
    E(sonar_group, 'circle', cx='273', cy='734', r='18', fill='none', stroke='#38bdf8', class__='sonarWaveDelay')
    
    # Sonar at Tech Constellation Core (cx=601, cy=3340)
    E(sonar_group, 'circle', cx='601', cy='3340', r='22', fill='none', stroke='#38bdf8', class__='sonarWave')
    E(sonar_group, 'circle', cx='601', cy='3340', r='22', fill='none', stroke='#818cf8', class__='sonarWaveDelay')
    
    # Sonar at Abyss Portal (cx=600, cy=4893)
    E(sonar_group, 'circle', cx='600', cy='4893', r='25', fill='none', stroke='#2dd4bf', class__='sonarWave')
    E(sonar_group, 'circle', cx='600', cy='4893', r='25', fill='none', stroke='#a78bfa', class__='sonarWaveDelay')

    # ==========================================================
    # 3. LIVE STATUS BADGES ON KEY PROJECT CARDS
    # ==========================================================
    status_group = E(g, 'g', id='liveStatusBadges')
    
    def add_status_badge(x, y, text, led_color='#34d399', led_class='ledGreen', w=230):
        b = E(status_group, 'g', transform=f'translate({x} {y})', class__='statusPill')
        E(b, 'rect', x='0', y='0', width=str(w), height='24', rx='12', fill='#031938', stroke=led_color, stroke__width='1.2', opacity='.9')
        E(b, 'circle', cx='12', cy='12', r='4', fill=led_color, class__=led_class)
        t = E(b, 'text', x='22', y='16', class__='mono', font__size='10.5', font__weight='700', fill='#e0f2fe', letter__spacing='1')
        t.text = text
        return b

    # Maritime Watch Status Pill
    add_status_badge(440, 642, "● LIVE AIS STREAM · ACTIVE", '#34d399', 'ledGreen', 215)
    
    # Restofy Status Pill
    add_status_badge(136, 1205, "● MICROSERVICES · PRODUCTION", '#38bdf8', 'ledCyan', 235)
    
    # KriptoParaTakip Status Pill
    add_status_badge(686, 1235, "● REAL-TIME FOREX & CRYPTO", '#fbbf24', 'ledAmber', 225)

    # Inventra Status Pill
    add_status_badge(245, 2455, "● CLOUD WORKFORCE · LIVE DEMO", '#34d399', 'ledGreen', 245)

    # Shifha Status Pill
    add_status_badge(773, 2498, "● CLINICAL PROTOCOL · 2026", '#a78bfa', 'ledCyan', 230)

    # ==========================================================
    # 4. BIOLUMINESCENT PARTICLES IN DEEP SEA (y=2600 to y=5100)
    # ==========================================================
    random.seed(999)
    bio_group = E(g, 'g', id='bioluminescentParticles')
    for i in range(45):
        bx = random.randint(70, 1130)
        by = random.randint(2400, 5100)
        br = random.uniform(2.5, 6.5)
        dur = random.uniform(5, 11)
        del_s = random.uniform(0, 8)
        color = random.choice(['#38bdf8', '#34d399', '#2dd4bf', '#a78bfa', '#f472b6'])
        
        bg_node = E(bio_group, 'g', class__='biolumOrb', style=f'--dur:{dur:.1f}s;--delay:-{del_s:.1f}s')
        E(bg_node, 'circle', cx=str(bx), cy=str(by), r=str(br + 4), fill=color, opacity='.25')
        E(bg_node, 'circle', cx=str(bx), cy=str(by), r=str(br), fill=color, stroke='#ffffff', stroke__width='.8', stroke__opacity='.8', opacity='.75')

    # Save V9 SVG
    print(f"Writing {TARGET}...")
    TARGET.write_bytes(ET.tostring(root, encoding='utf-8', xml_declaration=False))
    print(f"Successfully generated V9: {TARGET} (Size: {TARGET.stat().st_size:,} bytes)")

if __name__ == '__main__':
    build_v9()
