import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const USERNAME = 'KeremKalyoncu';

async function fetchTelemetry() {
  console.log(`[Telemetry] Fetching live metrics for user: ${USERNAME}...`);
  
  let userData = {
    public_repos: 15,
    followers: 3,
    following: 5
  };

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

    const userRes = await fetch(`https://api.github.com/users/${USERNAME}`, { headers });
    if (userRes.ok) {
      const u = await userRes.json();
      userData.public_repos = u.public_repos || userData.public_repos;
      userData.followers = u.followers || userData.followers;
      userData.following = u.following || userData.following;
      console.log(`[Telemetry] User data verified: ${userData.public_repos} repos.`);
    }

    const reposRes = await fetch(`https://api.github.com/users/${USERNAME}/repos?per_page=100`, { headers });
    if (reposRes.ok) {
      const repos = await reposRes.json();
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
    console.warn(`[Telemetry] API fetch warning: ${err.message}. Proceeding with deterministic fallback metrics.`);
  }

  return { userData, languages };
}

function generateSvg({ userData, languages }) {
  const repoCount = userData.public_repos || 15;
  const followers = userData.followers || 3;

  return `<svg width="1200" height="320" viewBox="0 0 1200 320" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="hud-bg" x1="0" y1="0" x2="1200" y2="320" gradientUnits="userSpaceOnUse">
      <stop stop-color="#020617"/>
      <stop offset="0.5" stop-color="#09182E"/>
      <stop offset="1" stop-color="#041224"/>
    </linearGradient>

    <linearGradient id="hud-card" x1="0" y1="0" x2="1" y2="1">
      <stop stop-color="#050E1F" stop-opacity="0.95"/>
      <stop offset="1" stop-color="#020713" stop-opacity="0.98"/>
    </linearGradient>

    <linearGradient id="bar-cyan" x1="0" y1="0" x2="1" y2="0">
      <stop stop-color="#0284C7"/>
      <stop offset="1" stop-color="#38BDF8"/>
    </linearGradient>

    <pattern id="grid-dots" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#38BDF8" fill-opacity="0.08"/>
    </pattern>

    <clipPath id="hud-clip">
      <rect width="1200" height="320" rx="18"/>
    </clipPath>
  </defs>

  <style>
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    .sans { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    .pulse-dot { animation: pulse 1.8s infinite; }
  </style>

  <g clip-path="url(#hud-clip)">
    <!-- Canvas Base -->
    <rect width="1200" height="320" fill="url(#hud-bg)"/>
    <rect width="1200" height="320" fill="url(#grid-dots)"/>

    <!-- Header Telemetry Strip -->
    <g transform="translate(48, 26)">
      <rect width="240" height="24" rx="4" fill="#0369A1" fill-opacity="0.25" stroke="#0284C7" stroke-width="1"/>
      <circle cx="12" cy="12" r="3.5" fill="#34D399" class="pulse-dot"/>
      <text x="24" y="16" fill="#7DD3FC" class="mono" font-size="10.5" font-weight="700" letter-spacing="1.5">TELEMETRY HUD // METRICS</text>
      <text x="256" y="16" fill="#64748B" class="mono" font-size="11">● 100% RUNTIME UPTIME // ZERO EXTERNAL DEPENDENCY</text>
    </g>

    <!-- 3-PANEL SYSTEM GRID -->
    <g transform="translate(48, 64)">
      
      <!-- PANEL 1: GitHub Repos & Signal Metrics -->
      <g transform="translate(0, 0)">
        <rect width="345" height="226" rx="10" fill="url(#hud-card)" stroke="#0E7490" stroke-width="1.2"/>
        <path d="M0 8C0 3.58172 3.58172 0 8 0H337C341.418 0 345 3.58172 345 8V28H0V8Z" fill="#071933"/>
        <text x="14" y="18" fill="#38BDF8" class="mono" font-size="11" font-weight="700">01 // REPOSITORY &amp; ACTIVITY</text>

        <!-- Metric Cards -->
        <g transform="translate(16, 44)">
          <!-- Repos -->
          <g transform="translate(0, 0)">
            <rect width="150" height="74" rx="6" fill="#020817" stroke="#164E63" stroke-width="1"/>
            <text x="14" y="24" fill="#94A3B8" class="mono" font-size="10.5" font-weight="600">PUBLIC REPOS</text>
            <text x="14" y="58" fill="#F8FAFC" class="sans" font-size="28" font-weight="900">${repoCount}</text>
            <circle cx="130" cy="22" r="4" fill="#38BDF8"/>
          </g>

          <!-- Followers / Community -->
          <g transform="translate(162, 0)">
            <rect width="150" height="74" rx="6" fill="#020817" stroke="#164E63" stroke-width="1"/>
            <text x="14" y="24" fill="#94A3B8" class="mono" font-size="10.5" font-weight="600">COMMUNITY</text>
            <text x="14" y="54" fill="#34D399" class="mono" font-size="14" font-weight="800">GDG DOĞUŞ</text>
            <text x="14" y="68" fill="#64748B" class="mono" font-size="9.5">CAMPUS CORE</text>
          </g>
        </g>

        <!-- Operational Status -->
        <g transform="translate(16, 134)">
          <rect width="312" height="74" rx="6" fill="#020B1A" stroke="#1E3A8A" stroke-width="1"/>
          <text x="14" y="22" fill="#38BDF8" class="mono" font-size="10.5" font-weight="700">SYSTEM HEALTH &amp; CI PIPELINE</text>
          <text x="14" y="44" fill="#E2E8F0" class="mono" font-size="11">● ACTIONS: <tspan fill="#34D399" font-weight="700">PASSING</tspan> (SNAKE + 3D)</text>
          <text x="14" y="62" fill="#94A3B8" class="mono" font-size="10">FAIL-SAFE: LOCAL CACHE ENABLED</text>
        </g>
      </g>

      <!-- PANEL 2: Language Matrix -->
      <g transform="translate(378, 0)">
        <rect width="345" height="226" rx="10" fill="url(#hud-card)" stroke="#1D4ED8" stroke-width="1.2"/>
        <path d="M0 8C0 3.58172 3.58172 0 8 0H337C341.418 0 345 3.58172 345 8V28H0V8Z" fill="#0C234D"/>
        <text x="14" y="18" fill="#60A5FA" class="mono" font-size="11" font-weight="700">02 // CODEBASE LANGUAGE MATRIX</text>

        <!-- Dynamic Language Rows -->
        <g transform="translate(16, 40)">
          ${languages.map((l, i) => `
          <g transform="translate(0, ${i * 34})">
            <text x="0" y="14" fill="#E2E8F0" class="mono" font-size="11.5" font-weight="600">${l.name}</text>
            <text x="312" y="14" text-anchor="end" fill="#94A3B8" class="mono" font-size="11">${l.percentage}%</text>
            <rect x="0" y="20" width="312" height="6" rx="3" fill="#0A162B"/>
            <rect x="0" y="20" width="${Math.max(12, Math.round((l.percentage / 100) * 312))}" height="6" rx="3" fill="${l.color}"/>
          </g>`).join('')}
        </g>
      </g>

      <!-- PANEL 3: Engineering Capabilities & Architecture -->
      <g transform="translate(756, 0)">
        <rect width="348" height="226" rx="10" fill="url(#hud-card)" stroke="#059669" stroke-width="1.2"/>
        <path d="M0 8C0 3.58172 3.58172 0 8 0H340C344.418 0 348 3.58172 348 8V28H0V8Z" fill="#052E23"/>
        <text x="14" y="18" fill="#34D399" class="mono" font-size="11" font-weight="700">03 // ARCHITECTURAL CAPABILITY</text>

        <!-- Feature Stack List -->
        <g transform="translate(16, 44)">
          <g transform="translate(0, 0)">
            <rect width="316" height="34" rx="5" fill="#02140E" stroke="#047857" stroke-width="1"/>
            <circle cx="16" cy="17" r="4" fill="#34D399"/>
            <text x="30" y="21" fill="#E2E8F0" class="mono" font-size="11" font-weight="600">Real-Time Telemetry &amp; AIS CPA</text>
          </g>

          <g transform="translate(0, 42)">
            <rect width="316" height="34" rx="5" fill="#02140E" stroke="#047857" stroke-width="1"/>
            <circle cx="16" cy="17" r="4" fill="#38BDF8"/>
            <text x="30" y="21" fill="#E2E8F0" class="mono" font-size="11" font-weight="600">Geospatial Mapping &amp; Leaflet</text>
          </g>

          <g transform="translate(0, 84)">
            <rect width="316" height="34" rx="5" fill="#02140E" stroke="#047857" stroke-width="1"/>
            <circle cx="16" cy="17" r="4" fill="#F59E0B"/>
            <text x="30" y="21" fill="#E2E8F0" class="mono" font-size="11" font-weight="600">Low-Power Edge Nodes (~1.2W)</text>
          </g>

          <g transform="translate(0, 126)">
            <rect width="316" height="34" rx="5" fill="#02140E" stroke="#047857" stroke-width="1"/>
            <circle cx="16" cy="17" r="4" fill="#A78BFA"/>
            <text x="30" y="21" fill="#E2E8F0" class="mono" font-size="11" font-weight="600">Deterministic Rule Engine (0 LLM)</text>
          </g>
        </g>
      </g>

    </g>

    <!-- Outer Highlight Border -->
    <rect x="1" y="1" width="1198" height="318" rx="17" stroke="#0284C7" stroke-opacity="0.4"/>
  </g>
</svg>`;
}

async function run() {
  const telemetry = await fetchTelemetry();
  const svg = generateSvg(telemetry);
  const outPath = path.join(rootDir, 'assets', 'developer-telemetry.svg');
  fs.writeFileSync(outPath, svg, 'utf8');
  console.log(`[Telemetry] Successfully generated SVG: ${outPath}`);
}

run();
