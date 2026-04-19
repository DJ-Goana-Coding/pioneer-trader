---
title: Pioneer Trader
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 10000
pinned: false
---

# 🚀 Pioneer Trader — CGAL Omega Trading System

**Pioneer Trader** is a FastAPI-based algorithmic trading backend for the Citadel Omega ecosystem. It connects to the MEXC exchange, provides a JWT-secured REST API for trade execution, exposes a cockpit for system monitoring via T.I.A. (Tactical Intelligence Agent), and mirrors to the central Mapping & Inventory Hub.

## 📋 Project Overview

| Item | Detail |
|------|--------|
| **Type** | FastAPI trading backend |
| **Exchange** | MEXC (spot) |
| **Auth** | JWT (HS256) via `/auth/login` |
| **HF Space** | `DJ-Goana-Coding/pioneer-trader` |
| **GitHub** | `DJ-Goana-Coding/pioneer-trader` |
| **Hub Link** | `DJ-Goana-Coding/mapping-and-inventory` |
| **Default Port** | 10000 |
| **Default Mode** | PAPER (safe, no real trades) |

## 🏗️ Architecture

```
pioneer-trader/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── config.py        # Pydantic settings (env vars)
│   │   ├── security.py      # JWT auth (get_current_admin / get_current_user)
│   │   ├── logging_config.py
│   │   ├── personas.py      # T.I.A., DJ Goanna, Void, Hippy persona registry
│   │   ├── iso20022_parser.py  # ISO 20022 structural parser (stub)
│   │   └── yield_engine.py  # Remote-area yield calculator
│   ├── routers/
│   │   ├── auth.py          # POST /auth/login, GET /auth/me
│   │   ├── telemetry.py     # GET /telemetry/health, /telemetry/status
│   │   ├── cockpit.py       # T.I.A. + Admiral command endpoints
│   │   ├── security.py      # Red Flag Scanner + Shadow Archive
│   │   ├── finance.py       # ISO 20022 + Yield Engine (JWT-guarded)
│   │   ├── hub_router.py    # /v1/ingest, /v1/query → Mapping Hub
│   │   ├── brain.py         # GET /brain/knowledge
│   │   ├── trade.py         # POST /trade/order (needs app.state.oms)
│   │   └── strategy.py      # GET /strategy/analyze/{symbol}
│   └── services/
│       ├── vortex.py        # VortexOmega — lightweight MEXC wrapper
│       ├── exchange.py      # ExchangeService (async MEXC, paper/live modes)
│       ├── strategy_engine.py  # StrategyEngine (Frankfurt)
│       ├── tia_agent.py     # TIAAgent — risk analysis
│       ├── admiral_engine.py   # AdmiralEngine — capability gating
│       ├── tia_admiral_bridge.py  # Authorization bridge
│       ├── garage_manager.py   # Genesis Garage strategy loader
│       ├── brain.py         # SkinWalkerBrain — persona + knowledge
│       ├── knowledge.py     # KnowledgeBase (JSON file store)
│       ├── malware_protection.py  # RedFlagScanner
│       ├── archival.py      # Shadow Archive (JSONL trade logs)
│       ├── redis_cache.py   # RedisCache (graceful fallback)
│       ├── oms.py           # OMS — order management
│       └── admiral_engine.py
├── src/                     # UI Stencil Pack (web components)
├── tests/                   # Test suite
├── config/
│   └── ato_coefficients.json  # ATO yield engine coefficients (empty stub)
├── Dockerfile               # Docker build (python:3.12-slim, port 10000)
├── requirements.txt         # Python deps
└── .github/workflows/
    └── hf_sync.yml          # Syncs repo → HF Space on push to main
```

## 🔑 Required Environment Variables

Set these in your `.env` file or as HuggingFace Space secrets:

| Variable | Required | Description |
|----------|----------|-------------|
| `MEXC_API_KEY` | For LIVE mode | MEXC exchange API key |
| `MEXC_SECRET` | For LIVE mode | MEXC exchange secret |
| `ADMIN_USERNAME` | Yes | Login username (default: `admin`) |
| `ADMIN_PASSWORD` | Yes | Login password |
| `SECRET_KEY` | Yes | JWT signing key (min 32 chars) |
| `EXECUTION_MODE` | No | `PAPER` (default) or `LIVE` |
| `ALLOWED_ORIGINS` | No | Extra CORS origins (comma-separated) |
| `REDIS_URL` | No | Redis URL (default: `redis://localhost:6379`) |
| `REDIS_ENABLED` | No | `True`/`False` (default: `True`) |
| `MAX_ORDER_NOTIONAL` | No | Max USDT per order (default: `50.0`) |
| `MAPPING_HUB_URL` | No | Hub URL (default: HF Space URL) |

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in environment variables
cp .env.example .env

# Run locally
uvicorn backend.main:app --host 0.0.0.0 --port 10000

# Or via Docker
docker build -t pioneer-trader .
docker run -p 10000:10000 --env-file .env pioneer-trader
```

## 🔌 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Process liveness probe |
| GET | `/ready` | None | Deep probe (touches exchange) |
| POST | `/auth/login` | None | Get JWT token |
| GET | `/auth/me` | JWT | Current user info |
| GET | `/telemetry/health` | None | Telemetry health |
| GET | `/telemetry/status` | JWT | System status |
| GET | `/cockpit/status` | None | T.I.A. + Admiral + Vortex status |
| GET | `/cockpit/health` | None | Cockpit component health |
| POST | `/cockpit/authorize` | None | T.I.A. authorizes Admiral |
| GET | `/cockpit/tia/summary` | None | T.I.A. risk assessment |
| GET | `/security/status` | None | Red Flag Scanner status |
| POST | `/security/scan` | None | Scan code for threats |
| GET | `/v1/hub/health` | None | Hub connection status |
| POST | `/v1/ingest` | None | Forward data to Mapping Hub |
| POST | `/v1/query` | None | Query Mapping Hub RAG |
| POST | `/v1/finance/analyze` | JWT | ISO 20022 + Yield analysis |
| POST | `/strike` | JWT | Manual trade execution |
| POST | `/start/{symbol}` | JWT | Start market monitoring |

## 🤝 Contributing

See [AGENT_BLUEPRINT.md](./AGENT_BLUEPRINT.md) for agent architecture, and [PIONEER_TRADER_KNOWLEDGE.md](./PIONEER_TRADER_KNOWLEDGE.md) for comprehensive system documentation.

## 🔗 Links

- [GitHub Repository](https://github.com/DJ-Goana-Coding/pioneer-trader)
- [HuggingFace Space](https://huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader)
- [Mapping & Inventory Hub](https://github.com/DJ-Goana-Coding/mapping-and-inventory)
- [API Docs](https://dj-goana-coding-pioneer-trader.hf.space/docs)

