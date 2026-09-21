<div align="center">

<img src="./assets/kerem-command-center.svg" alt="Kerem Kalyoncu command center profile banner" width="100%" />

<br />

<a href="https://github.com/KeremKalyoncu?tab=repositories">
  <img src="https://img.shields.io/badge/EXPLORE%20PROJECTS-22D3EE?style=for-the-badge&logo=github&logoColor=020617" alt="Explore projects" />
</a>
<a href="https://keremkalyoncu.github.io/maritime-watch">
  <img src="https://img.shields.io/badge/LIVE%20DEMO-MARITIME%20WATCH-0E7490?style=for-the-badge&logo=googleearth&logoColor=white" alt="Maritime Watch live demo" />
</a>
<a href="https://github.com/KeremKalyoncu">
  <img src="https://img.shields.io/github/followers/KeremKalyoncu?label=FOLLOW&style=for-the-badge&color=164E63&logo=github&logoColor=white" alt="Follow Kerem" />
</a>

<br /><br />

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=19&duration=2600&pause=900&color=67E8F9&center=true&vCenter=true&width=900&lines=Software+Engineer+%26+Systems+Builder.;Live+Telemetry.+Geospatial+Interfaces.+Practical+Automation.;From+raw+operational+signals+to+reliable%2C+useful+software." alt="Animated profile introduction" />

</div>

<br />

<!--
  Navigation
-->

<div align="center">

<a href="#about">[ about ]</a> ·
<a href="#flagship">[ flagship build ]</a> ·
<a href="#projects">[ projects ]</a> ·
<a href="#telemetry">[ telemetry &amp; stats ]</a> ·
<a href="#stack">[ stack ]</a> ·
<a href="#contact">[ contact ]</a>

</div>

<br />

<a id="about"></a>

## `01` / About the builder

I’m **Kerem Kalyoncu**, a Software Engineer based in **İstanbul, Türkiye**.

I engineer software where **digital systems intersect with the physical world**: real-time operational streams, geospatial mapping, automated workflows, and high-clarity interfaces that turn complex telemetry into reliable decisions.

I care about deterministic reliability over fragile hype. Every system should solve a tangible problem across its entire lifecycle:

```text
operational problem
        ↓
accurate telemetry & signal
        ↓
deterministic logic & engine
        ↓
clear, intuitive interface
        ↓
measurable, real-world outcome
```

<div align="center">

| `CURRENT STATUS` | `COMMUNITY` | `ENGINEERING FOCUS` | `LOCATION` |
| :---: | :---: | :---: | :---: |
| `BUILDING & SHIPPING` | `GDG ON CAMPUS DOĞUŞ` | `REAL-TIME × GIS × AUTOMATION` | `ISTANBUL, TR` |

</div>

<br />

<div align="center">

<a href="https://github.com/KeremKalyoncu?tab=repositories">
  <img src="https://img.shields.io/badge/PUBLIC%20REPOSITORIES-15-0F172A?style=flat-square&logo=github&logoColor=67E8F9" alt="Public repositories" />
</a>
<a href="https://github.com/KeremKalyoncu">
  <img src="https://img.shields.io/badge/STATUS-OPEN%20TO%20OPPORTUNITIES%20%26%20COLLABORATION-0F172A?style=flat-square&logo=github&logoColor=34D399" alt="Open to opportunities" />
</a>

</div>

<br />

<a id="flagship"></a>

## `02` / Flagship build — Maritime Watch Türkiye

<div align="center">

<a href="https://github.com/KeremKalyoncu/maritime-watch">
  <img src="./assets/maritime-watch-banner.svg" alt="Maritime Watch Türkiye - Real-Time Marine Safety Platform" width="100%" />
</a>

<br /><br />

<a href="https://keremkalyoncu.github.io/maritime-watch">
  <img src="https://img.shields.io/badge/OPEN%20LIVE%20DASHBOARD-22D3EE?style=for-the-badge&logo=googleearth&logoColor=020617" alt="Open live dashboard" />
</a>
<a href="https://keremkalyoncu.github.io/maritime-watch/stats.html">
  <img src="https://img.shields.io/badge/LIVE%20STATISTICS-REPORT-0F172A?style=for-the-badge&logo=google-analytics&logoColor=67E8F9" alt="Maritime Watch statistics report" />
</a>
<a href="https://keremkalyoncu.github.io/maritime-watch/data/feed.xml">
  <img src="https://img.shields.io/badge/RSS-LIVE%20FEED-0F172A?style=for-the-badge&logo=rss&logoColor=F59E0B" alt="Maritime Watch RSS feed" />
</a>
<a href="https://github.com/KeremKalyoncu/maritime-watch">
  <img src="https://img.shields.io/badge/EXPLORE%20SOURCE%20CODE-164E63?style=for-the-badge&logo=github&logoColor=white" alt="Read source code" />
</a>

</div>

### The Problem It Solves

Standard marine weather reports state raw numbers: *24 knots of wind, 1.8 metres wave height*. To a maritime operator or small craft captain, raw numbers do not answer the real question:

> **"Can my vessel safely depart right now, and by what exact time must I return?"**

**Maritime Watch Türkiye** translates multi-source weather forecasts, live AIS feeds, and navigational warnings into vessel-specific **Go / Caution / No-Go departure and safe return windows** across Turkish waters and the Turkish Straits.

### Architectural Highlights

<table>
<tr>
<td width="50%" valign="top">

#### 🛟 Decision Support Engine
- Vessel-class safety windows (open boat, small yacht, commercial craft)
- Dynamic wind gust & wave threshold calculations
- 06:00 daily operational maritime briefings
- Deterministic go / caution / no-go states

</td>
<td width="50%" valign="top">

#### 📡 Live Maritime Intelligence
- Real-time AIS vessel tracking & speed telemetry
- Closest Point of Approach (**CPA**) collision risk
- Sudden speed-drop anomaly detection in heavy traffic
- Turkish Straits passage monitoring

</td>
</tr>
<tr>
<td width="50%" valign="top">

#### 🆘 Safety & Offline Resilience
- Telegram emergency assistant bot
- `/neredeyim` nearest refuge-port spatial lookup
- `/mayday` VHF Channel 16 distress communication templates
- Offline PWA with cached nautical map layers

</td>
<td width="50%" valign="top">

#### 🌱 Ultra-Low Power Infrastructure
- Deterministic rule engine (**0 LLM in live safety loop**)
- Automated GitHub Actions data processing pipeline
- 24/7 Telegram sentinel operating on a recycled device
- Dedicated Samsung Galaxy Note 4 edge node (~1.2W)

</td>
</tr>
</table>

### Signal & Data Ingestion Pipeline

```mermaid
flowchart LR
    A[AIS Ingestion] --> D[Core Pipeline]
    B[Marine Weather & Wave APIs] --> D
    C[Navigational Bulletins] --> D
    D --> E[Deterministic Rule Engine]
    E --> F[CPA Risk & Anomaly Detector]
    E --> G[Go / No-Go Departure Window]
    F --> H[Live Leaflet Map & RSS Feed]
    G --> H
    F --> I[24/7 Telegram Sentinel]
    G --> I
    H --> J[Safe Maritime Decision]
    I --> J
    style A fill:#082F49,stroke:#22D3EE,color:#E0F2FE
    style B fill:#082F49,stroke:#22D3EE,color:#E0F2FE
    style C fill:#082F49,stroke:#22D3EE,color:#E0F2FE
    style D fill:#164E63,stroke:#67E8F9,color:#F8FAFC
    style E fill:#164E63,stroke:#67E8F9,color:#F8FAFC
    style F fill:#0F172A,stroke:#A78BFA,color:#F8FAFC
    style G fill:#0F172A,stroke:#A78BFA,color:#F8FAFC
    style H fill:#0F172A,stroke:#22D3EE,color:#F8FAFC
    style I fill:#0F172A,stroke:#22D3EE,color:#F8FAFC
    style J fill:#064E3B,stroke:#34D399,color:#ECFDF5
```

<br />

<a id="projects"></a>

## `03` / Selected work & repositories

<table>
<tr>
<td width="50%" valign="top">

### ⚓ [Maritime Watch](https://github.com/KeremKalyoncu/maritime-watch)
Flagship real-time marine safety & AIS intelligence platform for Turkish waters. Includes deterministic departure windows, low-power edge node, and spatial alerts.

`Python` `Leaflet` `AIS` `Geospatial` `PWA`

</td>
<td width="50%" valign="top">

### 📚 [Gelişmiş Kütüphane Sistemi](https://github.com/KeremKalyoncu/Gelismis_Kutuphane_Sistemi)
A robust library management system featuring relational SQLite storage, transactional borrowing workflows, and detailed audit logging.

`Python` `SQLite` `Data Architecture` `Logging`

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 💹 [KriptoParaTakip](https://github.com/KeremKalyoncu/KriptoParaTakip)
Desktop cryptocurrency intelligence application built in Java, streaming live price telemetry and market movements in real time.

`Java` `Real-Time Data` `Desktop GUI` `API Integration`

</td>
<td width="50%" valign="top">

### 📊 [Titanic Veri Analizi](https://github.com/KeremKalyoncu/Titanic_Veri_Analizi)
In-depth exploratory data analysis and feature engineering on survival patterns, passenger demographics, and correlation matrices.

`Jupyter` `Pandas` `NumPy` `Matplotlib` `Seaborn`

</td>
</tr>
<tr>
<td width="50%" valign="top">

### ⛽ [Benzin İstasyonu Otomasyonu](https://github.com/KeremKalyoncu/Benzin_Istasyonu_Otamasyon)
An enterprise domain automation tool modeling pump inventory, daily transactions, and fuel-station operational logic.

`C#` `.NET` `Enterprise Automation` `Workflows`

</td>
<td width="50%" valign="top">

### 🎨 [Dinamik CSS Portfolyo](https://github.com/KeremKalyoncu/Dinamik-Css-Portfolyo)
Interactive frontend showcase focusing on responsive layouts, CSS animations, and vanilla JavaScript state handling.

`JavaScript` `CSS3` `UI/UX` `Interactive Design`

</td>
</tr>
</table>

<div align="center">

<a href="https://github.com/KeremKalyoncu?tab=repositories">
  <img src="https://img.shields.io/badge/EXPLORE%20ALL-REPOSITORIES-0F172A?style=for-the-badge&logo=github&logoColor=67E8F9" alt="View all repositories" />
</a>

</div>

<br />

<a id="telemetry"></a>

## `04` / Contribution art & GitHub telemetry

### 🐍 Contribution Stream

The contribution snake navigates and harvests commits automatically via GitHub Actions:

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./output/github-contribution-grid-snake.svg" />
  <img src="./output/github-contribution-grid-snake.svg" alt="Animated contribution snake" width="100%" />
</picture>

</div>

<br />

### 🌌 3D Isometric Contribution Landscape

Generated daily using GitHub Actions to visualize commitment volume, frequency, and density:

<div align="center">

<img src="./profile-3d-contrib/profile-night-rainbow.svg" alt="3D contribution calendar" width="100%" />

<br /><br />

<img src="https://streak-stats.demolab.com?user=KeremKalyoncu&theme=tokyonight&hide_border=true&background=0B1220&ring=22D3EE&fire=67E8F9&currStreakLabel=67E8F9&sideLabels=CBD5E1&dates=94A3B8" alt="GitHub contribution streak" />

</div>

<br />

<a id="stack"></a>

## `05` / Technology constellation

<div align="center">

<img src="https://skillicons.dev/icons?i=python,javascript,java,cs,sqlite,html,css,git,github,leaflet&perline=10" alt="Core Technologies" />

<br /><br />

| Category | Technologies &amp; Tools |
| :--- | :--- |
| **Core Languages** | `Python` · `JavaScript` · `Java` · `C#` · `SQL` · `HTML5` · `CSS3` |
| **Data &amp; Analysis** | `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `SQLite` |
| **Geospatial &amp; Systems** | `Leaflet.js` · `AIS Decoding` · `REST APIs` · `IoT Edge Computing` · `PWA` |
| **Automation &amp; CI/CD** | `GitHub Actions` · `Cron Telemetry` · `Telegram Bot API` · `Linux / Bash` |

</div>

<br />

## `06` / Engineering principles

<div align="center">

```text
┌────────────────────────────────────────────────────────────────────────┐
│  01. BUILD FOR THE PHYSICAL PROBLEM, NOT FOR TRANSIENT TECH HYPE       │
│  02. RAW NUMBERS ARE NOT ENOUGH; ALWAYS DELIVER ACTIONABLE DECISIONS   │
│  03. ZERO LLM IN THE CRITICAL REAL-TIME SAFETY PATH                    │
│  04. RECYCLE HARDWARE & MAXIMIZE EFFICIENCY (1.2W OVER EXPENSIVE CLOUD)│
│  05. SHIP WORKING PROTOTYPES FAST; HARDEN THROUGH EMPIRICAL TESTING    │
└────────────────────────────────────────────────────────────────────────┘
```

</div>

<br />

<a id="contact"></a>

## `07` / Connect & open channel

Are you building systems with **real-time telemetry, maps, automation, or data-driven software**?

I am open to **software engineering opportunities, high-impact collaborations, and ambitious technical projects**.

<div align="center">

<a href="https://github.com/KeremKalyoncu">
  <img src="https://img.shields.io/badge/GITHUB%20PROFILE-22D3EE?style=for-the-badge&logo=github&logoColor=020617" alt="Open GitHub profile" />
</a>
<a href="https://github.com/KeremKalyoncu?tab=issues">
  <img src="https://img.shields.io/badge/START%20A%20CONVERSATION-164E63?style=for-the-badge&logo=github&logoColor=white" alt="Start a conversation" />
</a>

<br /><br />

<img src="https://komarev.com/ghpvc/?username=KeremKalyoncu&style=for-the-badge&color=0891B2&label=PROFILE+SIGNALS" alt="Profile views" />

<br /><br />

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:22D3EE,50:0E7490,100:020617&height=120&section=footer&animation=fadeIn" alt="Animated footer wave" width="100%" />

</div>