---
title: Pioneer Trader - V19 Fleet Command
emoji: 🛸
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Pioneer Trader - V19 Fleet Command

**T.I.A. Citadel - The Infinite Cockpit**

A distributed trading bot system with advanced AI swarm intelligence, security protection, and dual-mode UI.

## 🏛️ V19 Master Fleet Architecture

The V19 Distributed Hive is a multi-node trading system utilizing:

### Fleet Nodes

| Hub Location | V19 Node | System Role | CPU/Resource Logic |
|--------------|----------|-------------|-------------------|
| tias-citadel | Node 01 | The Infinite Cockpit | 8 vCPU (Pro). Runs Streamlit with Zen/Overkill modes |
| tias-pioneer-trader | Node 02 | Jules Execution | 8 vCPU (Pro). Direct USD Spot Pipeline to Binance |
| tias-sentinel-scout | Node 04-07 | The Ant Swarm | 6 vCPU total. 6x Phi-3.5 drones for trading & malware defense |
| tias-soul-vault | Node 09 | Shadow Archive | 1TB Persistent storage for trade logs |

## 🚀 Features

### 1. The Infinite Cockpit (UI)
Two distinct UI modes for different trading mindsets:

#### Overkill Mode 🔥
- Monstrous charts with enhanced metrics
- 5-line rolling win/loss logs with live status
- Mathematical indicator boxes (RSI, SMA, etc.)
- Cyberpunk-inspired neon aesthetics
- Real-time swarm and security status

#### Zen Mode 🌸
- Minimalist, peaceful interface
- Soft backgrounds and gradients
- AI yarning with philosophical trading wisdom
- Radio media player integration
- Mindful trading approach

### 2. Safety Modulator 🎚️
- 0-10 scale for trade aggression control
- 0 = Maximum Safety (Paper Trading)
- 10 = Full Aggression (Live Trading)
- Dynamic risk adjustment based on modulator setting

### 3. Swarm Intelligence 🛸
- 6x Phi-3.5 Mini (INT4) drones
- Distributed market analysis
- Consensus-based trading signals
- Real-time drone status monitoring

### 4. Security Shield 🛡️
- Red Flag Malware Hunter
- Zero-Trust AI Airlock
- Automatic threat isolation
- Real-time security scanning

### 5. Archival System 📦
- Shadow Archive with persistent storage
- Auto-sync trade logs
- GitHub Pages export support
- Session statistics and analytics

### 6. Authentication 🔐
- Standard JWT-based login
- GitHub Device Code Flow support
- Node 08 Bridge integration

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/DJ-Goana-Coding/pioneer-trader.git
cd pioneer-trader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run the backend:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

5. Run the Streamlit UI:
```bash
streamlit run streamlit_app/app.py
```

## ⚙️ Configuration

Key environment variables:

```env
# Security
SECRET_KEY=your_secret_key_here

# Trading
EXECUTION_MODE=PAPER  # PAPER, TESTNET, or LIVE
BINANCE_API_KEY=
BINANCE_SECRET_KEY=

# V19 Fleet Configuration
UI_THEME=OVERKILL  # OVERKILL or ZEN
SAFETY_MODULATOR=5  # 0-10 scale
PHI_DRONE_COUNT=6

# Security
ENABLE_MALWARE_PROTECTION=true

# Archival
SHADOW_ARCHIVE_PATH=/tmp/shadow_archive
ENABLE_GITHUB_PAGES_EXPORT=false

# GitHub Auth (optional)
ENABLE_GITHUB_AUTH=false
GITHUB_CLIENT_ID=
```

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - Standard login
- `POST /auth/github/device-code` - Initiate GitHub Device Flow
- `POST /auth/github/poll-token` - Poll for GitHub token

### Trading
- `POST /trade/order` - Place a trade order
- `GET /strategy/analyze/{symbol}` - Analyze market
- `GET /strategy/swarm-analyze/{symbol}` - Swarm consensus analysis

### Telemetry
- `GET /telemetry/health` - Health check
- `GET /telemetry/status` - Full system status
- `GET /telemetry/swarm` - Swarm status
- `GET /telemetry/security` - Security status
- `GET /telemetry/archival` - Archival statistics

### Brain
- `GET /brain/knowledge` - Knowledge base
- `GET /brain/fleet-status` - V19 Fleet status

## 🔒 Security

The system includes multiple security layers:

1. **Malware Protection**: Scans all code and request data for malicious patterns
2. **Risk Management**: Safety modulator controls trade aggression
3. **Trade Limits**: Configurable notional value limits
4. **Isolated Execution**: Paper/Testnet/Live mode separation

## 📈 Trading Modes

- **PAPER**: Simulated trading with mock data (no real funds)
- **TESTNET**: Binance testnet API integration
- **LIVE**: Real trading on Binance (use with caution)

## 🎵 Media Integration

Both UI modes support ambient audio:
- **Overkill Mode**: Radio stations with trading beats
- **Zen Mode**: Meditation music and nature sounds

## 📝 License

This is a demonstration project. Use at your own risk. Not financial advice.

## 🛸 Contributing

Contributions welcome! Please open an issue or PR.

## ⚠️ Disclaimer

This software is for educational purposes only. Cryptocurrency trading carries significant risks. Never trade with funds you cannot afford to lose.
