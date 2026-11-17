"""Canonical shared specification for Obsidian Atlas (M1 README SVGs & M2 Interactive Site).

Pure Python standard-library module containing JSON-serializable primitives only.
Zero third-party dependencies so both `source/build_readme_svgs.py` and
`source/build_site.py` run cleanly from repository root.
"""

from __future__ import annotations

PALETTE: dict[str, str] = {
    "bg_void": "#060E18",        # Deep Sapphire Night (frames cleanly on GitHub Dark #0d1117)
    "bg_plate": "#0A1829",       # Aero Sapphire Glass Plate
    "bg_bay": "#071220",         # Recessed Hydro-Glass Bay
    "bg_hover": "#102640",       # Luminous Aqua Hover Glass
    "border_grid": "#163654",    # Crisp Aero Glass Hairlines
    "border_active": "#256394",  # Specular Cyan Frame
    "ink_primary": "#F0FAFF",    # >16:1 Crystal Ice White
    "ink_secondary": "#9EC5E2",  # >7:1 Soft Aero Mist Blue
    "ink_caption": "#75A1C2",    # >5.5:1 Muted Aqua Caption
    "accent_orange": "#00D4FF",  # Luminous Aero Electric Cyan (primary beacon, CTAs)
    "accent_amber": "#38BDF8",   # Crystal Sky Aqua (coordinates, timeline)
    "accent_emerald": "#34D399", # Bioluminescent Seafoam Mint (GO state, live status)
    "accent_indigo": "#7DD3FC",  # Soft Pearl Ice Cyan (AI/ML & community)
}

FONTS: dict[str, str] = {
    "mono": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
    "sans": '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
}

BRAND: dict[str, str] = {
    "monograph": "KEREM KALYONCU // ISTANBUL SYSTEMS & AI",
    "revision": "BOSPHORUS STRAIT · ISTANBUL",
    "plate_code": "ISTANBUL, TR // SYSTEMS & AI",
    "topo_label": "BOSPHORUS STRAIT",
    "topo_datum": "RUMELİ × ANADOLU",
}

PROFILE: dict = {
    "name": "Kerem Kalyoncu",
    "handle": "KeremKalyoncu",
    "title": "Software Engineer · Systems, Telemetry & AI",
    "role_short": "SOFTWARE ENGINEER",
    "location": "İstanbul, Türkiye",
    "location_upper": "İSTANBUL, TÜRKİYE",
    "coordinates": "41.0082° N, 28.9784° E",
    "coordinates_compact": "41.0082° N · 28.9784° E",
    "lat": "41.0082° N",
    "lon": "28.9784° E",
    "sector_code": "IST // TR-34",
    "university": "Doğuş University",
    "degree": "Software Engineering, BSc",
    "graduation_years": "2023–2027",
    "degree_badge": "DOĞUŞ BSc '23–'27",
    "lead": "Full-Stack Systems, Maritime Telemetry & Applied AI",
    "bio_lines": [
        "BSc Software Engineering at Doğuş University (2023–2027).",
        "Building production web systems, microservices & ML pipelines.",
    ],
    "kpi_line": "SYSTEMS: 06 CORE  ·  ROLE: GDG DESIGN LEAD  ·  HUAWEI AI ACADEMY",
    "summary": (
        "Software Engineer in İstanbul engineering deterministic telemetry pipelines, "
        "geospatial safety engines, microservices, and clinical/ML decision systems."
    ),
    "principles": [
        "Build for the physical operational loop, not transient hype.",
        "Raw metrics are insufficient; deliver actionable human decisions.",
        "Zero LLM in critical real-time safety loops.",
        "Maximize hardware efficiency (~1.2W recycled edge node over costly cloud).",
    ],
    "links": {
        "github": "https://github.com/KeremKalyoncu",
        "linkedin": "https://www.linkedin.com/in/kerem-kalyoncu/",
        "site": "https://keremkalyoncu.github.io/KeremKalyoncu/",
    },
}

PROJECTS: list[dict] = [
    {
        "id": "maritime-watch",
        "code": "SYS-01",
        "title": "Maritime Watch Türkiye",
        "tagline": "Deterministic AIS telemetry & weather safety engine",
        "category": "Production Systems",
        "status": "LIVE",
        "accent": "accent_emerald",
        "stack": ["Python", "Leaflet.js", "Open-Meteo", "AIS", "PWA", "Edge Computing"],
        "plate_pills": ["Python", "Leaflet.js", "PWA", "Edge IoT"],
        "plate_desc_lines": [
            "Multi-source weather, AIS & NAVTEX",
            "telemetry into Go/Caution/No-Go.",
        ],
        "plate_metric": "EDGE: ~1.2W NODE · OPEN-METEO · AIS",
        "url": "https://keremkalyoncu.github.io/maritime-watch",
        "repo_url": "https://github.com/KeremKalyoncu/maritime-watch",
        "sub_repos": [
            {
                "name": "Live Telemetry Map",
                "url": "https://keremkalyoncu.github.io/maritime-watch",
            },
            {
                "name": "GitHub Repository",
                "url": "https://github.com/KeremKalyoncu/maritime-watch",
            },
        ],
        "summary": (
            "Translates multi-source marine weather forecasts, real-time AIS telemetry, "
            "and Turkish navigational warnings into deterministic Go / Caution / No-Go "
            "departure and safe-return decisions."
        ),
        "problem": (
            "Standard forecasts output raw knots and wave heights without vessel-specific "
            "thresholds or offline refuge routing during signal loss."
        ),
        "tradeoffs": [
            "Deterministic rule engine (0 LLM calls in critical safety loop) for predictable, auditable thresholds.",
            "Runs 24/7 on a recycled Samsung Galaxy Note 4 (~1.2W) edge node instead of always-on cloud VMs.",
            "Offline-capable Leaflet.js PWA paired with Telegram /neredeyim & /mayday emergency sentinel.",
        ],
        "metrics": [
            "200+ deterministic scenarios",
            "0 LLM in critical safety loop",
            "~1.2W Galaxy Note 4 edge node",
            "06:00 daily Strait briefing",
        ],
        "diagram_type": "pipeline",
        "arch_nodes": [
            {"id": "ais", "label": "AIS Stream", "role": "ingest", "tier": 0},
            {"id": "weather", "label": "Open-Meteo", "role": "ingest", "tier": 0},
            {"id": "core", "label": "Note 4 Rule Core (~1.2W)", "role": "compute", "tier": 1},
            {"id": "pwa", "label": "Leaflet PWA", "role": "output", "tier": 2},
            {"id": "tg", "label": "Telegram Sentinel", "role": "output", "tier": 2},
        ],
        "arch_edges": [
            ("ais", "core", "Class A/B"),
            ("weather", "core", "Wave/Wind"),
            ("core", "pwa", "Go/No-Go"),
            ("core", "tg", "/mayday"),
        ],
    },
    {
        "id": "inventra",
        "code": "SYS-02",
        "title": "Inventra",
        "tagline": "Cloud workforce & multi-warehouse inventory platform",
        "category": "Production Systems",
        "status": "PRODUCTION",
        "accent": "accent_orange",
        "stack": ["ASP.NET Core", "React", "Material UI", "PostgreSQL"],
        "plate_pills": ["ASP.NET Core", "React", "MUI", "PostgreSQL"],
        "plate_desc_lines": [
            "Cloud workforce & inventory platform",
            "with multi-warehouse SKU tracking.",
        ],
        "plate_metric": "LIVE: X-ETC.ONLINE · POSTGRESQL",
        "url": "https://x-etc.online",
        "repo_url": None,
        "sub_repos": [],
        "summary": (
            "Enterprise cloud workforce scheduling, multi-warehouse inventory auditing, "
            "and operational workflow platform deployed in production."
        ),
        "problem": (
            "Small and mid-scale teams juggle disconnected spreadsheets for shift rosters, "
            "SKU stock levels, and audit trails."
        ),
        "tradeoffs": [
            "Strongly typed ASP.NET Core REST API backed by transactional PostgreSQL for audit integrity.",
            "Componentized React + Material UI dashboard designed for rapid warehouse and shift updates.",
        ],
        "metrics": [
            "Live production at x-etc.online",
            "ACID inventory transactions",
            "Unified workforce & SKU workflows",
        ],
        "diagram_type": "hub",
        "arch_nodes": [
            {"id": "ui", "label": "React + MUI Client", "role": "client", "tier": 0},
            {"id": "api", "label": "ASP.NET Core API", "role": "compute", "tier": 1},
            {"id": "pg", "label": "PostgreSQL Store", "role": "storage", "tier": 2},
            {"id": "audit", "label": "Workforce & Stock Audit", "role": "output", "tier": 2},
        ],
        "arch_edges": [
            ("ui", "api", "REST/JWT"),
            ("api", "pg", "EF Core"),
            ("api", "audit", "Ledger"),
        ],
    },
    {
        "id": "restofy",
        "code": "SYS-03",
        "title": "Restofy",
        "tagline": "Distributed restaurant QR menu & order microservices",
        "category": "Backend & Microservices",
        "status": "ACTIVE",
        "accent": "accent_amber",
        "stack": ["Java", "Spring Boot", "Microservices", "Docker"],
        "plate_pills": ["Java", "Spring Boot", "Docker", "REST"],
        "plate_desc_lines": [
            "Restaurant QR menu & distributed",
            "order-dispatch microservice fleet.",
        ],
        "plate_metric": "STACK: SPRING BOOT · DOCKER FLEET",
        "url": "https://github.com/software-lecture-labs/Restofy",
        "repo_url": "https://github.com/software-lecture-labs/Restofy",
        "sub_repos": [],
        "summary": (
            "Collaborative restaurant QR menu and high-concurrency order dispatching "
            "microservices architecture built with Spring Boot and Docker."
        ),
        "problem": (
            "Peak dining hours create bursty table-side order concurrency that bottlenecks "
            "monolithic kitchen dispatch backends."
        ),
        "tradeoffs": [
            "Bounded-context Spring Boot services isolate menu reads from transactional order writes.",
            "Dockerized service mesh ensures reproducible local and staging orchestration.",
        ],
        "metrics": [
            "Spring Boot service fleet",
            "Containerized Docker topology",
            "Zero-app QR table ordering",
        ],
        "diagram_type": "microservices",
        "arch_nodes": [
            {"id": "qr", "label": "QR Table Client", "role": "client", "tier": 0},
            {"id": "gw", "label": "API Gateway", "role": "gateway", "tier": 1},
            {"id": "orders", "label": "Order & Menu Services", "role": "compute", "tier": 1},
            {"id": "dock", "label": "Docker Mesh", "role": "infra", "tier": 2},
        ],
        "arch_edges": [
            ("qr", "gw", "HTTPS"),
            ("gw", "orders", "Route"),
            ("orders", "dock", "Deploy"),
        ],
    },
    {
        "id": "shifha",
        "code": "SYS-04",
        "title": "Shifha",
        "tagline": "Clinical AI protocol & clinician decision support",
        "category": "AI & Data Lab",
        "status": "CONCEPT",
        "accent": "accent_indigo",
        "stack": ["React Native", "Python", "Medical NLP"],
        "plate_pills": ["React Native", "Python", "Medical NLP"],
        "plate_desc_lines": [
            "Clinical AI protocol engine &",
            "structured clinician decision aid.",
        ],
        "plate_metric": "DOMAIN: MEDICAL NLP · MOBILE APP",
        "url": "https://www.linkedin.com/in/kerem-kalyoncu/",
        "repo_url": None,
        "sub_repos": [],
        "summary": (
            "Collaborative clinical AI protocol for structured medical information routing "
            "and automated clinician decision support across mobile workflows."
        ),
        "problem": (
            "Unstructured clinical notes slow down triage handoffs and obscure protocol "
            "checklists at point of care."
        ),
        "tradeoffs": [
            "Python Medical NLP extraction pipeline paired with mobile-first React Native UX.",
            "Human-in-the-loop protocol routing surfaces confidence rather than black-box verdicts.",
        ],
        "metrics": [
            "Cross-platform mobile client",
            "Structured NLP triage routing",
            "Clinician-in-the-loop design",
        ],
        "diagram_type": "mobile-ai",
        "arch_nodes": [
            {"id": "app", "label": "React Native Client", "role": "client", "tier": 0},
            {"id": "nlp", "label": "Python Medical NLP", "role": "compute", "tier": 1},
            {"id": "proto", "label": "Clinical Protocol Router", "role": "output", "tier": 2},
        ],
        "arch_edges": [
            ("app", "nlp", "Clinical Note"),
            ("nlp", "proto", "Structured Aid"),
        ],
    },
    {
        "id": "kriptoparatakip",
        "code": "SYS-05",
        "title": "KriptoParaTakip",
        "tagline": "Real-time financial market tracker & alert engine",
        "category": "Backend & Microservices",
        "status": "RELEASED",
        "accent": "accent_emerald",
        "stack": ["Java", "REST APIs", "Desktop GUI", "JSON Pipelines"],
        "plate_pills": ["Java", "REST APIs", "Desktop GUI", "JSON"],
        "plate_desc_lines": [
            "Real-time crypto market tracker &",
            "automated volatility alert engine.",
        ],
        "plate_metric": "PIPELINE: REST APIS · JSON STREAM",
        "url": "https://github.com/KeremKalyoncu/KriptoParaTakip",
        "repo_url": "https://github.com/KeremKalyoncu/KriptoParaTakip",
        "sub_repos": [],
        "summary": (
            "Financial market tracking engine streaming live cryptocurrency telemetry, "
            "price feeds, and automated volatility alerts in a Java desktop suite."
        ),
        "problem": (
            "Browser dashboards consume heavy memory and lack lightweight threshold-based "
            "volatility alerting."
        ),
        "tradeoffs": [
            "Direct Java HTTP/JSON ingestion pipeline avoids heavyweight browser runtime overhead.",
            "Stateful delta evaluator triggers immediate desktop alerts on configurable swings.",
        ],
        "metrics": [
            "Live REST market telemetry",
            "Low-footprint Java GUI",
            "Automated threshold alerts",
        ],
        "diagram_type": "stream",
        "arch_nodes": [
            {"id": "feed", "label": "Market REST Feeds", "role": "ingest", "tier": 0},
            {"id": "pipe", "label": "JSON Parser & Rules", "role": "compute", "tier": 1},
            {"id": "gui", "label": "Java Desktop Alerts", "role": "output", "tier": 2},
        ],
        "arch_edges": [
            ("feed", "pipe", "JSON Tick"),
            ("pipe", "gui", "Alert Delta"),
        ],
    },
    {
        "id": "ml-data-lab",
        "code": "SYS-06",
        "title": "ML & Data Lab",
        "tagline": "Predictive modeling, feature engineering & EDA studies",
        "category": "AI & Data Lab",
        "status": "RESEARCH",
        "accent": "accent_indigo",
        "stack": ["Python", "Scikit-Learn", "Pandas", "NumPy"],
        "plate_pills": ["Python", "Scikit-Learn", "Pandas", "EDA"],
        "plate_desc_lines": [
            "Predictive modeling, feature pipelines",
            "& supervised classification studies.",
        ],
        "plate_metric": "REPOS: ML-FINAL · ML-ARA · TITANIC",
        "url": "https://github.com/KeremKalyoncu/ml-final-odev",
        "repo_url": "https://github.com/KeremKalyoncu/ml-final-odev",
        "sub_repos": [
            {
                "name": "ml-final-odev (Housing Regression)",
                "url": "https://github.com/KeremKalyoncu/ml-final-odev",
            },
            {
                "name": "ml-ara-odev (Churn Classification)",
                "url": "https://github.com/KeremKalyoncu/ml-ara-odev",
            },
            {
                "name": "Titanic_Veri_Analizi (EDA)",
                "url": "https://github.com/KeremKalyoncu/Titanic_Veri_Analizi",
            },
        ],
        "summary": (
            "Predictive modeling and EDA pipelines covering California Housing regression "
            "with GridSearchCV, Customer Churn classification benchmarking LR/KNN/DT, and "
            "survival pattern analysis."
        ),
        "problem": (
            "Raw tabular datasets suffer from leakage, skew, and class imbalance without "
            "reproducible preprocessing and cross-validation pipelines."
        ),
        "tradeoffs": [
            "Scikit-Learn Pipeline + ColumnTransformer prevents train/test feature leakage.",
            "Benchmarks interpretable baselines (LR, KNN, Decision Trees) before complexity.",
        ],
        "metrics": [
            "3 open ML repositories",
            "Cross-validated GridSearch",
            "Class-imbalance benchmarking",
        ],
        "diagram_type": "ml-dag",
        "arch_nodes": [
            {"id": "data", "label": "Raw Tabular Datasets", "role": "ingest", "tier": 0},
            {"id": "fe", "label": "Pandas Feature Pipeline", "role": "compute", "tier": 1},
            {"id": "cv", "label": "GridSearch & LR/KNN/DT", "role": "output", "tier": 2},
        ],
        "arch_edges": [
            ("data", "fe", "Clean/Scale"),
            ("fe", "cv", "K-Fold CV"),
        ],
    },
]

SUPPORTING_REPOS: list[dict] = [
    {
        "id": "gelismis-kutuphane",
        "title": "Gelismis_Kutuphane_Sistemi",
        "url": "https://github.com/KeremKalyoncu/Gelismis_Kutuphane_Sistemi",
        "visibility": "public",
        "stack": ["Python", "SQLite", "Data Architecture", "Logging"],
        "summary": "Relational SQLite library system with transactional borrowing workflows and audit logging.",
    },
    {
        "id": "benzin-istasyonu",
        "title": "Benzin_Istasyonu_Otamasyon",
        "url": "https://github.com/KeremKalyoncu/Benzin_Istasyonu_Otamasyon",
        "visibility": "public",
        "stack": ["C#", ".NET", "Enterprise Automation", "Workflows"],
        "summary": "Enterprise domain automation modeling pump inventory, daily transactions, and station logic.",
    },
    {
        "id": "envanter-stok",
        "title": "Envanter-Stok-Takibi",
        "url": "https://github.com/KeremKalyoncu/Envanter-Stok-Takibi",
        "visibility": "public",
        "stack": ["Python", "Inventory", "Automation"],
        "summary": "Inventory and stock tracking application tailored for small-business operations.",
    },
    {
        "id": "dinamik-css-portfolyo",
        "title": "Dinamik-Css-Portfolyo",
        "url": "https://github.com/KeremKalyoncu/Dinamik-Css-Portfolyo",
        "visibility": "public",
        "stack": ["JavaScript", "CSS3", "UI/UX", "Interactive Design"],
        "summary": "Interactive frontend showcase exploring responsive layouts, CSS motion, and vanilla JS state.",
    },
    {
        "id": "fondedektifi",
        "title": "FonDedektifi",
        "url": None,
        "visibility": "private",
        "stack": ["Python", "FastAPI", "DuckDB", "Financial Forensics"],
        "summary": "Financial intelligence platform for TEFAS funds & BIST equities: liquidity risk (DTL), HHI concentration, and anomaly detection.",
    },
]

TIMELINE: list[dict] = [
    {
        "id": "dogus-bsc",
        "period": "2023–2027",
        "organization": "Doğuş University",
        "role": "Software Engineering, BSc",
        "category": "education",
        "summary": "Undergraduate software engineering curriculum covering algorithms, databases, distributed systems, and applied AI.",
        "url": None,
        "accent": "accent_amber",
        "plate_period": "2023–2027",
        "plate_org": "Doğuş University",
        "plate_lines": ["BSc Software Eng.", "ISTANBUL · DEGREE"],
    },
    {
        "id": "gdg-dogus",
        "period": "2025–2026",
        "organization": "GDG on Campus Doğuş",
        "role": "Design & Social Media Team Lead",
        "category": "community",
        "summary": "Leading visual identity, technical event design, and campus developer community outreach at Doğuş University.",
        "url": "https://tr.linkedin.com/company/gdg-on-campus-dogus",
        "accent": "accent_indigo",
        "plate_period": "2025–2026",
        "plate_org": "GDG on Campus Doğuş",
        "plate_lines": ["Design & Social", "Media Team Lead"],
    },
    {
        "id": "huawei-ai",
        "period": "2026",
        "organization": "Huawei × AI Academy",
        "role": "Data Science & Machine Learning",
        "category": "training",
        "summary": "Intensive data science, supervised learning, and applied machine learning engineering program.",
        "url": None,
        "accent": "accent_orange",
        "plate_period": "2026",
        "plate_org": "Huawei × AI Academy",
        "plate_lines": ["Data Science & ML", "APPLIED AI TRACK"],
    },
    {
        "id": "btk-ai",
        "period": "2025–2026",
        "organization": "BTK AI Fundamentals",
        "role": "AI Fundamentals & Applied ML",
        "category": "training",
        "summary": "Certified foundation in artificial intelligence principles, data analysis, and model evaluation.",
        "url": None,
        "accent": "accent_emerald",
        "plate_period": "FOUNDATION",
        "plate_org": "BTK AI Fundamentals",
        "plate_lines": ["AI & ML Basics", "CERTIFIED STUDY"],
    },
    {
        "id": "vollsign",
        "period": "Experience",
        "organization": "VollSign",
        "role": "Software Engineer · Dev / QA / Testing",
        "category": "experience",
        "summary": "Software development, quality assurance, and automated verification workflows for production systems.",
        "url": "https://vollsign.com",
        "accent": "accent_amber",
        "plate_period": "EXPERIENCE",
        "plate_org": "VollSign",
        "plate_lines": ["Dev / QA & Testing", "VOLLSIGN.COM"],
    },
]

TECH_PILLARS: list[dict] = [
    {
        "id": "systems-backend",
        "code": "01",
        "title": "Systems & Backend",
        "accent": "accent_orange",
        "items": [
            "Java",
            "Spring Boot",
            "C#",
            "ASP.NET Core",
            "Python",
            "FastAPI",
            "REST APIs",
            "Microservices",
        ],
        "plate_lines": [
            "Java · Spring Boot",
            "C# · ASP.NET Core",
            "Python · Microservices",
            "PostgreSQL · REST APIs",
        ],
    },
    {
        "id": "web-interface",
        "code": "02",
        "title": "Web & Interface",
        "accent": "accent_amber",
        "items": [
            "TypeScript",
            "React",
            "Next.js",
            "Material UI",
            "Leaflet.js",
            "HTML5 / CSS3",
            "PWA",
            "Vector SVG",
        ],
        "plate_lines": [
            "React · TypeScript",
            "React Native · PWA",
            "Leaflet.js · Material UI",
            "SVG · Canvas2D Systems",
        ],
    },
    {
        "id": "ai-data-lab",
        "code": "03",
        "title": "AI & Data Lab",
        "accent": "accent_indigo",
        "items": [
            "Python",
            "Pandas",
            "NumPy",
            "Scikit-Learn",
            "SQLite",
            "DuckDB",
            "Medical NLP",
            "Feature Engineering",
        ],
        "plate_lines": [
            "Scikit-Learn · Pandas",
            "Medical NLP Pipelines",
            "Feature Engineering",
            "Predictive Modeling",
        ],
    },
    {
        "id": "cloud-edge",
        "code": "04",
        "title": "Cloud & Edge",
        "accent": "accent_emerald",
        "items": [
            "Docker",
            "PostgreSQL",
            "GitHub Actions",
            "Linux / Bash",
            "CI/CD",
            "Edge Node (~1.2W)",
            "Cron Telemetry",
        ],
        "plate_lines": [
            "Docker · GitHub Actions",
            "Edge Nodes (~1.2W IoT)",
            "Open-Meteo · AIS Feeds",
            "QA & Test Automation",
        ],
    },
]
