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
    "monograph": "KEREM KALYONCU // ISTANBUL SYSTEMS, QA, AI & SECURITY",
    "revision": "VOLLSIGN · X-ETC · SHIFHA · DOĞUŞ UNIV.",
    "plate_code": "SOFTWARE ENGINEER @VOLLSIGN",
    "topo_label": "BOSPHORUS STRAIT",
    "topo_datum": "BEYOĞLU × PENDİK",
}

PROFILE: dict = {
    "name": "Kerem Kalyoncu",
    "handle": "KeremKalyoncu",
    "email": "keremkalyoncu.dev@gmail.com",
    "email_secondary": "gskerem200553@outlook.com",
    "title": "Software Engineer @VollSign · Full-Stack, QA/Test, AI & Cybersecurity",
    "role_short": "SOFTWARE ENGINEER @VOLLSIGN",
    "location": "İstanbul, Türkiye",
    "location_upper": "BEYOĞLU, İSTANBUL",
    "coordinates": "41.0082° N, 28.9784° E",
    "coordinates_compact": "41.0082° N · 28.9784° E",
    "lat": "41.0082° N",
    "lon": "28.9784° E",
    "sector_code": "IST // TR-34",
    "university": "Doğuş University",
    "degree": "Software Engineering, BSc",
    "graduation_years": "2023–2027",
    "degree_badge": "DOĞUŞ BSc '23–'27",
    "lead": "Full-Stack Dev (Python, React, ASP.NET Core) · QA & Test · AI & Cybersecurity",
    "bio_lines": [
        "Software Engineer @VollSign (Beyoğlu Teknopark) & BSc Software Eng. at Doğuş University.",
        "Full-stack enterprise systems, clinical AI assistants, QA/API testing & SMB cybersecurity.",
    ],
    "kpi_line": "CYBERSECURITY & PENTESTING  ·  GDG ON CAMPUS DOĞUŞ  ·  keremkalyoncu.dev@gmail.com",
    "summary": (
        "Software Engineer at VollSign in İstanbul working across full-stack development "
        "(ASP.NET Core, React.js, Python), systematic UI/API QA testing, clinical AI, "
        "and independent SMB cybersecurity & penetration testing."
    ),
    "principles": [
        "Build products that solve real physical & operational problems — from enterprise warehouses to family AC service shops.",
        "Test UI, API integrations, and user flows systematically; uncover weak points through security assessments & pentesting.",
        "Design statistically rigorous backtesting and deterministic safety engines (0 LLM in critical marine safety loops).",
        "Combine full-stack engineering with active developer community leadership at GDG on Campus Doğuş University.",
    ],
    "links": {
        "github": "https://github.com/KeremKalyoncu",
        "linkedin": "https://www.linkedin.com/in/kerem-kalyoncu/",
        "site": "https://keremkalyoncu.github.io/KeremKalyoncu/",
        "email": "mailto:keremkalyoncu.dev@gmail.com",
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
        "tagline": "AI-powered doctor assistant & clinical decision support",
        "category": "AI & Data Lab",
        "status": "ACTIVE",
        "accent": "accent_indigo",
        "stack": ["Python", "React Native", "Medical NLP", "Clinical AI"],
        "plate_pills": ["Python", "React Native", "Medical NLP", "AI"],
        "plate_desc_lines": [
            "AI-powered doctor assistant in Python",
            "& clinical decision-support workflow.",
        ],
        "plate_metric": "FEB–AUG 2026 · PYTHON CLINICAL AI",
        "url": "https://www.linkedin.com/in/kerem-kalyoncu/",
        "repo_url": None,
        "sub_repos": [],
        "summary": (
            "Built AI-driven healthcare features in Python for an AI-powered doctor assistant, "
            "structuring medical information routing and clinician decision support."
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
            "7 mos Software Engineer @Shifha",
            "Python AI doctor assistant",
            "Clinician-in-the-loop NLP",
        ],
        "diagram_type": "mobile-ai",
        "arch_nodes": [
            {"id": "app", "label": "React Native Client", "role": "client", "tier": 0},
            {"id": "nlp", "label": "Python AI Doctor Aid", "role": "compute", "tier": 1},
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
        "tagline": "Statistical crypto strategy backtester & live market tracker",
        "category": "Backend & Microservices",
        "status": "RELEASED",
        "accent": "accent_emerald",
        "stack": ["Java", "Python", "REST APIs", "Desktop GUI", "JSON Pipelines"],
        "plate_pills": ["Java", "Backtest", "REST APIs", "JSON"],
        "plate_desc_lines": [
            "Crypto strategy backtesting research",
            "& live market volatility alert engine.",
        ],
        "plate_metric": "STATISTICAL BACKTEST · LIVE REST",
        "url": "https://github.com/KeremKalyoncu/KriptoParaTakip",
        "repo_url": "https://github.com/KeremKalyoncu/KriptoParaTakip",
        "sub_repos": [],
        "summary": (
            "Cryptocurrency market tracking suite and statistically rigorous strategy backtesting "
            "research platform focused on out-of-sample robustness and live volatility alerts."
        ),
        "problem": (
            "Retail crypto strategies overfit historical noise while browser dashboards consume "
            "heavy memory without deterministic threshold alerting."
        ),
        "tradeoffs": [
            "Direct Java HTTP/JSON ingestion pipeline avoids heavyweight browser runtime overhead.",
            "Statistical robustness backtesting evaluates strategy drawdowns and regime shifts.",
        ],
        "metrics": [
            "Statistically rigorous backtests",
            "Live REST market telemetry",
            "Automated volatility alerts",
        ],
        "diagram_type": "stream",
        "arch_nodes": [
            {"id": "feed", "label": "Market REST Feeds", "role": "ingest", "tier": 0},
            {"id": "pipe", "label": "Backtest & Delta Rules", "role": "compute", "tier": 1},
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

SPECIALIST_PRACTICES: list[dict] = [
    {
        "id": "klima-gaz-defteri",
        "code": "FIELD-01",
        "title": "Klima Gaz Defteri",
        "subtitle": "Family Automotive AC Service Digital Suite",
        "desc": "Custom digital operations, vehicle service ledger & refrigerant tracking tools built for family automotive AC business.",
        "metric": "AUTOMOTIVE AC OPS · PRODUCTION TOOL",
        "accent": "accent_emerald",
    },
    {
        "id": "cybersecurity-practice",
        "code": "SEC-02",
        "title": "Cybersecurity & Pentesting",
        "subtitle": "Independent SMB Security Consulting",
        "desc": "Security assessments, penetration testing, and UI/API vulnerability analysis uncovering weak points for small businesses.",
        "metric": "PENTESTING · QA & API HARDENING",
        "accent": "accent_orange",
    },
    {
        "id": "fondedektifi-forensics",
        "code": "FIN-03",
        "title": "FonDedektifi & Strategy Lab",
        "subtitle": "TEFAS / BIST Forensics & Crypto Backtesting",
        "desc": "FastAPI + DuckDB financial forensics (DTL liquidity risk, HHI concentration) & statistically rigorous strategy backtests.",
        "metric": "FASTAPI · DUCKDB · QUANT BACKTEST",
        "accent": "accent_amber",
    },
]

SUPPORTING_REPOS: list[dict] = [
    {
        "id": "klima-gaz-defteri",
        "title": "Klima Gaz Defteri",
        "url": "https://www.linkedin.com/in/kerem-kalyoncu/",
        "visibility": "production",
        "stack": ["Full-Stack", "Digital Operations", "Automotive AC", "Ledger"],
        "summary": "Digital service ledger, refrigerant tracking, and workshop operations tool built for my family's automotive AC service business.",
    },
    {
        "id": "cybersecurity-consulting",
        "title": "SMB Cybersecurity & Pentesting",
        "url": "https://www.linkedin.com/in/kerem-kalyoncu/",
        "visibility": "consulting",
        "stack": ["Penetration Testing", "Security Assessments", "API QA", "OWASP"],
        "summary": "Independent cybersecurity consulting practice offering security assessments, vulnerability discovery, and penetration testing to small businesses.",
    },
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
        "id": "vollsign",
        "period": "Aug 2026–Present",
        "organization": "VollSign",
        "role": "Software Engineer · Dev, QA & Functional Testing",
        "category": "experience",
        "summary": "Software Engineer at VollSign (Beyoğlu Teknopark, İstanbul). Developing features and systematically testing UI, API integrations, and end-to-end user flows.",
        "url": "https://vollsign.com",
        "accent": "accent_emerald",
        "plate_period": "AUG 2026–PRESENT",
        "plate_org": "VollSign (Teknopark)",
        "plate_lines": ["Software Engineer & QA", "BEYOĞLU · UI & API TEST"],
    },
    {
        "id": "x-etc",
        "period": "Feb 2026–Aug 2026",
        "organization": "X-ETC.",
        "role": "Full-Stack Software Engineer · ASP.NET Core & React",
        "category": "experience",
        "summary": "End-to-end full-stack engineering in Pendik, İstanbul — building an enterprise-scale multi-warehouse inventory & workforce platform with ASP.NET Core and React.js.",
        "url": "https://x-etc.online",
        "accent": "accent_orange",
        "plate_period": "FEB–AUG 2026 (7M)",
        "plate_org": "X-ETC. (Pendik)",
        "plate_lines": ["Full-Stack Engineer", "ASP.NET CORE & REACT.JS"],
    },
    {
        "id": "shifha-exp",
        "period": "Feb 2026–Aug 2026",
        "organization": "Clinical AI Venture",
        "role": "Software Engineer · Python AI Doctor Assistant",
        "category": "experience",
        "summary": "Built AI-driven healthcare features in Python for an AI-powered doctor assistant supporting clinical triage and medical workflows in İstanbul.",
        "url": "https://www.linkedin.com/in/kerem-kalyoncu/",
        "accent": "accent_indigo",
        "plate_period": "FEB–AUG 2026 (7M)",
        "plate_org": "Clinical AI R&D",
        "plate_lines": ["Software Engineer (AI)", "PYTHON DOCTOR ASSISTANT"],
    },
    {
        "id": "gdg-dogus",
        "period": "Sep 2025–Sep 2026",
        "organization": "GDG on Campus Doğuş",
        "role": "Social Media Coordinator · Design & Social Media Team Lead",
        "category": "community",
        "summary": "Coordinated the social media & design team for 1 yr 1 mo at GDG on Campus Doğuş University, producing technical content and growing campus developer community engagement.",
        "url": "https://tr.linkedin.com/company/gdg-on-campus-dogus",
        "accent": "accent_amber",
        "plate_period": "SEP 2025–SEP 2026",
        "plate_org": "GDG on Campus Doğuş",
        "plate_lines": ["Social Media Coord.", "DESIGN & COMMUNITY LEAD"],
    },
    {
        "id": "eryaz",
        "period": "Aug 2024–Sep 2024",
        "organization": "Eryaz Bilgi Teknolojileri A.Ş.",
        "role": "Software Developer Intern · C#, ASP.NET, JS & SQL",
        "category": "experience",
        "summary": "Worked with C#, ASP.NET, JavaScript, HTML, CSS, and SQL across enterprise software development lifecycles and team project delivery in İstanbul.",
        "url": "https://www.linkedin.com/in/kerem-kalyoncu/",
        "accent": "accent_orange",
        "plate_period": "AUG–SEP 2024",
        "plate_org": "Eryaz Bilgi Teknolojileri",
        "plate_lines": ["Software Developer", "C# · ASP.NET · JS · SQL"],
    },
    {
        "id": "dogus-bsc",
        "period": "2023–2027",
        "organization": "Doğuş University",
        "role": "Software Engineering, BSc",
        "category": "education",
        "summary": "Undergraduate BSc Software Engineering at Doğuş University (İstanbul) covering algorithms, relational databases, distributed systems, QA, and applied AI.",
        "url": None,
        "accent": "accent_amber",
        "plate_period": "2023–2027 · BSc",
        "plate_org": "Doğuş University",
        "plate_lines": ["BSc Software Eng.", "İSTANBUL · UNDERGRAD"],
    },
    {
        "id": "huawei-ai",
        "period": "2026",
        "organization": "Huawei × AI Academy",
        "role": "Huawei Student Developers · Data Science & ML",
        "category": "training",
        "summary": "Huawei Student Developers Data Science & Machine Learning certification covering supervised learning, feature engineering, and model evaluation.",
        "url": None,
        "accent": "accent_indigo",
        "plate_period": "CERTIFIED · 2026",
        "plate_org": "Huawei × AI Academy",
        "plate_lines": ["HSD Data Science & ML", "MACHINE LEARNING CERT"],
    },
    {
        "id": "btk-ai",
        "period": "2025–2026",
        "organization": "BTK AI Fundamentals",
        "role": "Yapay Zekaya Giriş & GDG Core Team Certs",
        "category": "training",
        "summary": "Certified in AI Fundamentals (Yapay Zekaya Giriş) and GDG On Campus Core Team Certificate of Completion.",
        "url": None,
        "accent": "accent_emerald",
        "plate_period": "CERTIFICATIONS",
        "plate_org": "BTK AI & GDG Core",
        "plate_lines": ["AI Fundamentals Cert", "GDG CORE TEAM CERT"],
    },
]

TECH_PILLARS: list[dict] = [
    {
        "id": "systems-backend",
        "code": "01",
        "title": "Full-Stack & Enterprise",
        "accent": "accent_orange",
        "items": [
            "Python",
            "C#",
            "ASP.NET Core",
            "React",
            "TypeScript",
            "Java",
            "Spring Boot",
            "FastAPI",
            "PostgreSQL",
            "REST APIs",
            "Microservices",
        ],
        "plate_lines": [
            "Python · C# · ASP.NET Core",
            "React.js · TypeScript · MUI",
            "Java · Spring Boot · SQL",
            "PostgreSQL · REST APIs",
        ],
    },
    {
        "id": "web-interface",
        "code": "02",
        "title": "QA, Testing & Security",
        "accent": "accent_emerald",
        "items": [
            "QA & Functional Testing",
            "API Integration Testing",
            "Penetration Testing",
            "Security Assessments",
            "Docker",
            "GitHub Actions",
            "Linux / Bash",
            "CI/CD",
        ],
        "plate_lines": [
            "UI & API Functional QA",
            "SMB Penetration Testing",
            "Security Assessments",
            "Docker · CI/CD Pipelines",
        ],
    },
    {
        "id": "ai-data-lab",
        "code": "03",
        "title": "AI, Data & Backtesting",
        "accent": "accent_indigo",
        "items": [
            "Python",
            "Scikit-Learn",
            "Pandas",
            "NumPy",
            "Medical NLP",
            "Crypto Backtesting",
            "SQLite",
            "DuckDB",
            "Feature Engineering",
        ],
        "plate_lines": [
            "Python AI Doctor Assistant",
            "Statistical Crypto Backtest",
            "Scikit-Learn · Pandas · EDA",
            "FastAPI · DuckDB Forensics",
        ],
    },
    {
        "id": "cloud-edge",
        "code": "04",
        "title": "Geospatial, Edge & Ops",
        "accent": "accent_amber",
        "items": [
            "Leaflet.js",
            "AIS Telemetry",
            "PWA",
            "Edge Node (~1.2W)",
            "HTML5 / CSS3",
            "Vector SVG",
            "Team Management",
            "Community Leadership",
        ],
        "plate_lines": [
            "Leaflet.js · AIS · Open-Meteo",
            "~1.2W Recycled Edge Node",
            "Klima Gaz Defteri AC Ops",
            "Team & Community Lead",
        ],
    },
]
