import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const USERNAME = 'KeremKalyoncu';

function getCompassDirection(deg) {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const index = Math.round(deg / 22.5) % 16;
  return directions[index];
}

async function fetchLiveMarineTelemetry() {
  console.log('[Telemetry] Fetching real-time Istanbul Strait marine & weather data...');
  let marine = {
    windKnots: 12.4,
    gustKnots: 16.8,
    directionCompass: 'NE',
    waveHeight: 0.6,
    temperature: 20.4,
    status: 'GO',
    statusColor: '#34D399',
    timestamp: new Date().toISOString().replace('T', ' ').substring(0, 16) + ' UTC'
  };

  try {
    const [weatherRes, marineRes] = await Promise.all([
      fetch('https://api.open-meteo.com/v1/forecast?latitude=41.0082&longitude=28.9784&current=temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m'),
      fetch('https://marine-api.open-meteo.com/v1/marine?latitude=41.0082&longitude=28.9784&current=wave_height')
    ]);

    if (weatherRes.ok) {
      const w = await weatherRes.json();
      if (w.current) {
        const speedKmh = w.current.wind_speed_10m || 10;
        const gustsKmh = w.current.wind_gusts_10m || speedKmh * 1.3;
        marine.windKnots = +(speedKmh * 0.539957).toFixed(1);
        marine.gustKnots = +(gustsKmh * 0.539957).toFixed(1);
        marine.temperature = +(w.current.temperature_2m || 20).toFixed(1);
        marine.directionCompass = getCompassDirection(w.current.wind_direction_10m || 45);
      }
    }

    if (marineRes.ok) {
      const m = await marineRes.json();
      if (m.current && m.current.wave_height !== null) {
        marine.waveHeight = +Math.max(0.2, m.current.wave_height).toFixed(1);
      }
    }

    // Deterministic go / caution / no-go decision calculus
    if (marine.gustKnots > 24 || marine.waveHeight > 1.8) {
      marine.status = 'NO-GO';
      marine.statusColor = '#EF4444';
    } else if (marine.gustKnots > 16 || marine.waveHeight > 1.1) {
      marine.status = 'CAUTION';
      marine.statusColor = '#FBBF24';
    } else {
      marine.status = 'GO (SAFE)';
      marine.statusColor = '#34D399';
    }

    console.log(`[Telemetry] Marine conditions verified: Wind=${marine.windKnots}kt (${marine.directionCompass}), Wave=${marine.waveHeight}m, Status=${marine.status}`);
  } catch (err) {
    console.warn(`[Telemetry] Live marine fetch warning: ${err.message}. Using deterministic standby.`);
  }

  return marine;
}

async function fetchGitHubMetrics() {
  console.log(`[Telemetry] Fetching live metrics for user: ${USERNAME}...`);
  let userData = { public_repos: 15, followers: 3 };
  let languages = [
    { name: 'Python', percentage: 40, color: '#38BDF8', count: 5 },
    { name: 'JavaScript', percentage: 22, color: '#FCD34D', count: 2 },
    { name: 'Java', percentage: 18, color: '#FB923C', count: 2 },
    { name: 'C#', percentage: 10, color: '#A78BFA', count: 1 },
    { name: 'SQL / GIS', percentage: 10, color: '#34D399', count: 2 }
  ];

  try {
    const headers = { 'User-Agent': 'Mozilla/5.0' };
    if (process.env.GITHUB_TOKEN) {
      headers['Authorization'] = `token ${process.env.GITHUB_TOKEN}`;
    }

    const [uRes, rRes] = await Promise.all([
      fetch(`https://api.github.com/users/${USERNAME}`, { headers }),
      fetch(`https://api.github.com/users/${USERNAME}/repos?per_page=100`, { headers })
    ]);

    if (uRes.ok) {
      const u = await uRes.json();
      userData.public_repos = u.public_repos || userData.public_repos;
      userData.followers = u.followers || userData.followers;
    }

    if (rRes.ok) {
      const repos = await rRes.json();
      const langCount = {};
      let total = 0;
      for (const r of repos) {
        if (!r.fork && r.language) {
          langCount[r.language] = (langCount[r.language] || 0) + 1;
          total++;
        }
      }
      if (total > 0) {
        const langColors = {
          'Python': '#38BDF8',
          'JavaScript': '#FCD34D',
          'Java': '#FB923C',
          'C#': '#A78BFA',
          'HTML': '#F43F5E',
          'CSS': '#38BDF8',
          'Jupyter Notebook': '#34D399'
        };

        const sorted = Object.entries(langCount).sort((a, b) => b[1] - a[1]);
        languages = sorted.slice(0, 5).map(([name, count]) => ({
          name,
          count,
          percentage: Math.round((count / total) * 100),
          color: langColors[name] || '#38BDF8'
        }));
      }
    }
  } catch (err) {
    console.warn(`[Telemetry] GitHub API warning: ${err.message}.`);
  }

  return { userData, languages };
}

function calculateSpiderPoints(cx, cy, r, values) {
  // values: array of 5 ratios between 0 and 1
  return values.map((val, i) => {
    const angle = (Math.PI * 2 / 5) * i - (Math.PI / 2);
    const x = +(cx + Math.cos(angle) * r * val).toFixed(1);
    const y = +(cy + Math.sin(angle) * r * val).toFixed(1);
    return `${x},${y}`;
  }).join(' ');
}

function generateSvg({ marine, userData, languages }) {
  const repoCount = userData.public_repos || 15;

  // Spider radar parameters
  const spiderCX = 166;
  const spiderCY = 114;
  const spiderR = 64;
  // Capabilities: Telemetry (95%), GIS (92%), Data (88%), Edge (85%), Automation (90%)
  const capabilities = [0.95, 0.92, 0.88, 0.85, 0.90];
  const spiderPoints = calculateSpiderPoints(spiderCX, spiderCY, spiderR, capabilities);

  const gridLevels = [0.25, 0.5, 0.75, 1.0];

  return `<svg width="1200" height="340" viewBox="0 0 1200 340" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="hud-bg" x1="0" y1="0" x2="1200" y2="340" gradientUnits="userSpaceOnUse">
      <stop stop-color="#020617"/>
      <stop offset="0.5" stop-color="#07192F"/>
      <stop offset="1" stop-color="#031021"/>
    </linearGradient>

    <linearGradient id="hud-panel" x1="0" y1="0" x2="1" y2="1">
      <stop stop-color="#061226" stop-opacity="0.95"/>
      <stop offset="1" stop-color="#020713" stop-opacity="0.98"/>
    </linearGradient>

    <linearGradient id="spider-fill" x1="0" y1="0" x2="1" y2="1">
      <stop stop-color="#38BDF8" stop-opacity="0.4"/>
      <stop offset="1" stop-color="#0284C7" stop-opacity="0.15"/>
    </linearGradient>

    <pattern id="grid-dots" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#38BDF8" fill-opacity="0.08"/>
    </pattern>

    <clipPath id="hud-clip">
      <rect width="1200" height="340" rx="18"/>
    </clipPath>
  </defs>

  <style>
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    .sans { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    .pulse-dot { animation: pulse 1.8s infinite; }
  </style>

  <g clip-path="url(#hud-clip)">
    <!-- Base Canvas -->
    <rect width="1200" height="340" fill="url(#hud-bg)"/>
    <rect width="1200" height="340" fill="url(#grid-dots)"/>

    <!-- Header Telemetry Strip -->
    <g transform="translate(48, 24)">
      <rect width="250" height="24" rx="4" fill="#0369A1" fill-opacity="0.25" stroke="#0284C7" stroke-width="1"/>
      <circle cx="12" cy="12" r="3.5" fill="${marine.statusColor}" class="pulse-dot"/>
      <text x="24" y="16" fill="#7DD3FC" class="mono" font-size="10.5" font-weight="700" letter-spacing="1.5">LIVING TELEMETRY HUD</text>
      
      <!-- Live Marine Weather Badge -->
      <g transform="translate(266, 0)">
        <rect width="640" height="24" rx="4" fill="#041E38" stroke="#0E7490" stroke-width="1"/>
        <text x="12" y="16" fill="#38BDF8" class="mono" font-size="10.5" font-weight="700">● LIVE BOSPORUS:</text>
        <text x="136" y="16" fill="#E2E8F0" class="mono" font-size="10.5">WIND: ${marine.windKnots} KT ${marine.directionCompass} (GUSTS ${marine.gustKnots} KT) · WAVE: ${marine.waveHeight}M · ${marine.temperature}°C · DEPARTURE: <tspan fill="${marine.statusColor}" font-weight="800">${marine.status}</tspan></text>
      </g>

      <!-- Sync Time -->
      <text x="1104" y="16" text-anchor="end" fill="#64748B" class="mono" font-size="10">SYNC: ${marine.timestamp}</text>
    </g>

    <!-- 3-PANEL SYSTEM GRID -->
    <g transform="translate(48, 62)">
      
      <!-- PANEL 1: Multi-Axis Capability Radar (Spider Chart) -->
      <g transform="translate(0, 0)">
        <rect width="350" height="246" rx="10" fill="url(#hud-panel)" stroke="#0E7490" stroke-width="1.2"/>
        <path d="M0 8C0 3.58172 3.58172 0 8 0H342C346.418 0 350 3.58172 350 8V28H0V8Z" fill="#071933"/>
        <text x="14" y="18" fill="#38BDF8" class="mono" font-size="11" font-weight="700">01 // CAPABILITY RADAR (SPIDER HUD)</text>

        <!-- Spider Grid -->
        <g transform="translate(8, 20)">
          <!-- Concentric Pentagons -->
          ${gridLevels.map(lvl => `
            <polygon points="${calculateSpiderPoints(spiderCX, spiderCY, spiderR, [lvl, lvl, lvl, lvl, lvl])}" stroke="#0E7490" stroke-width="0.8" stroke-opacity="0.35" fill="none"/>
          `).join('')}

          <!-- Spoke Axes -->
          ${[0, 1, 2, 3, 4].map(i => {
            const angle = (Math.PI * 2 / 5) * i - (Math.PI / 2);
            const x = +(spiderCX + Math.cos(angle) * spiderR).toFixed(1);
            const y = +(spiderCY + Math.sin(angle) * spiderR).toFixed(1);
            return `<line x1="${spiderCX}" y1="${spiderCY}" x2="${x}" y2="${y}" stroke="#0E7490" stroke-width="0.8" stroke-opacity="0.4"/>`;
          }).join('')}

          <!-- Filled Capability Polygon -->
          <polygon points="${spiderPoints}" fill="url(#spider-fill)" stroke="#38BDF8" stroke-width="1.8"/>

          <!-- Glowing Vertex Dots -->
          ${capabilities.map((val, i) => {
            const angle = (Math.PI * 2 / 5) * i - (Math.PI / 2);
            const x = +(spiderCX + Math.cos(angle) * spiderR * val).toFixed(1);
            const y = +(spiderCY + Math.sin(angle) * spiderR * val).toFixed(1);
            return `<circle cx="${x}" cy="${y}" r="3" fill="#38BDF8"/>`;
          }).join('')}

          <!-- Axis Labels -->
          <text x="${spiderCX}" y="${spiderCY - spiderR - 6}" text-anchor="middle" fill="#7DD3FC" class="mono" font-size="8.5" font-weight="700">TELEMETRY 95%</text>
          <text x="${spiderCX + spiderR + 10}" y="${spiderCY - 16}" text-anchor="start" fill="#7DD3FC" class="mono" font-size="8.5" font-weight="700">GIS 92%</text>
          <text x="${spiderCX + 38}" y="${spiderCY + spiderR + 14}" text-anchor="start" fill="#7DD3FC" class="mono" font-size="8.5" font-weight="700">DATA 88%</text>
          <text x="${spiderCX - 38}" y="${spiderCY + spiderR + 14}" text-anchor="end" fill="#7DD3FC" class="mono" font-size="8.5" font-weight="700">EDGE 85%</text>
          <text x="${spiderCX - spiderR - 10}" y="${spiderCY - 16}" text-anchor="end" fill="#7DD3FC" class="mono" font-size="8.5" font-weight="700">AUTO 90%</text>
        </g>
      </g>

      <!-- PANEL 2: Verified Codebase Languages -->
      <g transform="translate(378, 0)">
        <rect width="350" height="246" rx="10" fill="url(#hud-panel)" stroke="#1D4ED8" stroke-width="1.2"/>
        <path d="M0 8C0 3.58172 3.58172 0 8 0H342C346.418 0 350 3.58172 350 8V28H0V8Z" fill="#0C234D"/>
        <text x="14" y="18" fill="#60A5FA" class="mono" font-size="11" font-weight="700">02 // CODEBASE LANGUAGE MATRIX</text>

        <!-- Dynamic Language Rows -->
        <g transform="translate(18, 44)">
          ${languages.map((l, i) => `
          <g transform="translate(0, ${i * 38})">
            <text x="0" y="14" fill="#E2E8F0" class="mono" font-size="11.5" font-weight="600">${l.name}</text>
            <text x="314" y="14" text-anchor="end" fill="#94A3B8" class="mono" font-size="11">${l.percentage}%</text>
            <rect x="0" y="20" width="314" height="6" rx="3" fill="#09162C"/>
            <rect x="0" y="20" width="${Math.max(12, Math.round((l.percentage / 100) * 314))}" height="6" rx="3" fill="${l.color}"/>
          </g>`).join('')}
        </g>
      </g>

      <!-- PANEL 3: Node & Operational Health -->
      <g transform="translate(756, 0)">
        <rect width="348" height="246" rx="10" fill="url(#hud-panel)" stroke="#059669" stroke-width="1.2"/>
        <path d="M0 8C0 3.58172 3.58172 0 8 0H340C344.418 0 348 3.58172 348 8V28H0V8Z" fill="#052E23"/>
        <text x="14" y="18" fill="#34D399" class="mono" font-size="11" font-weight="700">03 // OPERATIONAL EDGE TELEMETRY</text>

        <g transform="translate(16, 44)">
          <!-- Node 1 -->
          <g transform="translate(0, 0)">
            <rect width="316" height="42" rx="6" fill="#02140E" stroke="#047857" stroke-width="1"/>
            <circle cx="16" cy="21" r="4" fill="#34D399"/>
            <text x="28" y="18" fill="#E2E8F0" class="mono" font-size="10.5" font-weight="700">SAMSUNG NOTE 4 EDGE NODE</text>
            <text x="28" y="32" fill="#6EE7B7" class="mono" font-size="9.5">POWER: ~1.2W · 24/7 TERMINAL SENTINEL</text>
          </g>

          <!-- Node 2 -->
          <g transform="translate(0, 50)">
            <rect width="316" height="42" rx="6" fill="#02140E" stroke="#047857" stroke-width="1"/>
            <circle cx="16" cy="21" r="4" fill="#38BDF8"/>
            <text x="28" y="18" fill="#E2E8F0" class="mono" font-size="10.5" font-weight="700">PUBLIC REPOSITORIES: ${repoCount}</text>
            <text x="28" y="32" fill="#7DD3FC" class="mono" font-size="9.5">COMMUNITY: GDG ON CAMPUS DOĞUŞ</text>
          </g>

          <!-- Node 3 -->
          <g transform="translate(0, 100)">
            <rect width="316" height="42" rx="6" fill="#02140E" stroke="#047857" stroke-width="1"/>
            <circle cx="16" cy="21" r="4" fill="#F59E0B"/>
            <text x="28" y="18" fill="#E2E8F0" class="mono" font-size="10.5" font-weight="700">DETERMINISTIC EVAL MOTOR</text>
            <text x="28" y="32" fill="#FCD34D" class="mono" font-size="9.5">200+ SCENARIOS · 0 LLM IN CRITICAL LOOP</text>
          </g>

          <!-- Node 4 -->
          <g transform="translate(0, 150)">
            <rect width="316" height="34" rx="6" fill="#030F1A" stroke="#0284C7" stroke-width="1"/>
            <text x="158" y="21" text-anchor="middle" fill="#7DD3FC" class="mono" font-size="10" font-weight="700" letter-spacing="1.5">FAIL-SAFE // 100% LOCAL RUNTIME</text>
          </g>
        </g>
      </g>

    </g>

    <!-- Outer Border -->
    <rect x="1" y="1" width="1198" height="338" rx="17" stroke="#0284C7" stroke-opacity="0.4"/>
  </g>
</svg>`;
}

async function run() {
  const [marine, gitHub] = await Promise.all([
    fetchLiveMarineTelemetry(),
    fetchGitHubMetrics()
  ]);

  const svg = generateSvg({
    marine,
    userData: gitHub.userData,
    languages: gitHub.languages
  });

  const outPath = path.join(rootDir, 'assets', 'developer-telemetry.svg');
  fs.writeFileSync(outPath, svg, 'utf8');
  console.log(`[Telemetry] Successfully generated upgraded living telemetry SVG: ${outPath}`);
}

run();
