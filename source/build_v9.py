from pathlib import Path
from lxml import etree as ET
from lxml.etree import SubElement
import random

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'assets' / 'kerem-living-world-v8.svg'
TARGET = ROOT / 'assets' / 'kerem-living-world-v9.svg'
NS = 'http://www.w3.org/2000/svg'
Q = lambda s: f'{{{NS}}}{s}'

def build_v9_clean():
    print(f"Loading {SRC}...")
    root = ET.parse(str(SRC)).getroot()
    defs = root.find(Q('defs'))
    g = root[-1]  # main canvas group
    H = 5150

    root.set('aria-label', "Kerem Kalyoncu — living Frutiger Aero engineering universe with animated ocean, public software fleet, collaborative systems and contact portal.")
    title = root.find(Q('title'))
    if title is not None:
        title.text = 'KEREM.AERO — The Living Engineering Ocean'
    desc = root.find(Q('desc'))
    if desc is not None:
        desc.text = 'Animated continuous Frutiger Aero world by Kerem Kalyoncu. Public GitHub projects, VollSign experience, Inventra and Shifha platforms, engineering constellation, GDG leadership and contact portal.'

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

    # High quality gradients
    grad('gaugeBeam', [('0', '#7dd3fc', '.7'), ('.5', '#38bdf8', '.4'), ('1', '#0369a1', '.1')], x1='0', y1='0', x2='0', y2='1')
    grad('scanPulse', [('0', '#ffffff', '0'), ('.5', '#7dd3fc', '.85'), ('1', '#0284c7', '0')], x1='0', y1='0', x2='0', y2='1')

    # Subtle CSS additions
    style = defs.find(Q('style'))
    extra_css = '''
    /* === V9 REFINED HUD === */
    .gaugeLine { stroke: #38bdf8; stroke-width: 1.2; stroke-opacity: 0.35; }
    .gaugeTick { stroke: #7dd3fc; stroke-width: 1.2; stroke-opacity: 0.55; }
    .gaugeTickMajor { stroke: #e0f2fe; stroke-width: 1.8; stroke-opacity: 0.85; }
    .gaugeNumber { font-family: 'Consolas', 'Courier New', monospace; font-size: 8.5px; font-weight: 700; fill: #7dd3fc; letter-spacing: 0.8px; opacity: 0.65; }
    .gaugeScanner { animation: scanRail 14s linear infinite; }
    @keyframes scanRail { 0% { transform: translateY(80px); opacity: 0; } 5% { opacity: 0.8; } 95% { opacity: 0.8; } 100% { transform: translateY(5060px); opacity: 0; } }
    
    .bioParticle { animation: bioDrift var(--dur, 8s) ease-in-out var(--del, 0s) infinite alternate; transform-box: fill-box; transform-origin: center; }
    @keyframes bioDrift { 0% { transform: translate(0, 0); opacity: 0.2; } 50% { transform: translate(12px, -30px); opacity: 0.75; } 100% { transform: translate(-8px, -60px); opacity: 0.2; } }
    '''
    style.text = (style.text or '') + extra_css

    # ==========================================================
    # ULTRA-SLIM VERTICAL DEPTH RULER (Strictly x=22 to x=54)
    # NEVER overlaps cards (all cards start at x >= 76)
    # ==========================================================
    ruler = E(g, 'g', id='depthRuler')
    E(ruler, 'line', x1='28', y1='100', x2='28', y2='5050', class__='gaugeLine')
    
    # Gliding subtle light
    scanner = E(ruler, 'g', class__='gaugeScanner')
    E(scanner, 'rect', x='26', y='0', width='4', height='70', rx='2', fill='url(#scanPulse)')

    # Discrete depth numbers every 500m (strictly width < 30px)
    depths = [
        (120, "0000m"),
        (600, "0500m"),
        (1100, "1000m"),
        (1600, "1500m"),
        (2100, "2000m"),
        (2600, "2500m"),
        (3100, "3000m"),
        (3600, "3500m"),
        (4100, "4000m"),
        (4600, "4500m"),
        (5050, "5000m"),
    ]

    for y, label in depths:
        # Tick line
        E(ruler, 'line', x1='23', y1=str(y), x2='33', y2=str(y), class__='gaugeTickMajor')
        E(ruler, 'circle', cx='28', cy=str(y), r='2', fill='#ffffff', opacity='.75')
        # Tiny subtle number right next to it (x=36, never passes x=65)
        t = E(ruler, 'text', x='36', y=str(y + 3), class__='gaugeNumber')
        t.text = label

    # Minor ticks every 100m
    for y in range(200, 5050, 100):
        if y % 500 != 0:
            E(ruler, 'line', x1='25', y1=str(y), x2='31', y2=str(y), class__='gaugeTick')

    # ==========================================================
    # BIOLUMINESCENT AMBIENCE PARTICLES (y=2400 to y=5100)
    # Kept outside cards and text zones
    # ==========================================================
    random.seed(42)
    bio_g = E(g, 'g', id='bioluminescence')
    for _ in range(30):
        bx = random.randint(75, 1125)
        by = random.randint(2350, 5080)
        dur = random.uniform(6, 12)
        del_s = random.uniform(0, 8)
        color = random.choice(['#38bdf8', '#5eead4', '#a78bfa', '#93c5fd'])
        
        node = E(bio_g, 'g', class__='bioParticle', style=f'--dur:{dur:.1f}s;--del:-{del_s:.1f}s')
        E(node, 'circle', cx=str(bx), cy=str(by), r=str(random.choice([1.8, 2.5, 3.2])), fill=color, opacity='.65')

    print(f"Writing clean V9 to {TARGET}...")
    TARGET.write_bytes(ET.tostring(root, encoding='utf-8', xml_declaration=False))
    print(f"Generated clean V9: {TARGET} (Size: {TARGET.stat().st_size:,} bytes)")

if __name__ == '__main__':
    build_v9_clean()
