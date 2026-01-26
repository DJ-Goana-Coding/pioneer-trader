# 🏁 GENESIS GARAGE - Multi-Ferrari Strategy System

## Overview

The Genesis Garage is T.I.A.'s "hangar" for strategy engines. It's a Multi-Ferrari Garage where T.I.A. selects the best car for the market weather based on her risk assessment.

## Architecture

```
GENESIS_GARAGE/
├── 01_ELITE/          # 🏎️ Precision Logic Ferrari
│   └── main.py        #    Activated: Risk = LOW
├── 02_ATOMIC/         # ⚔️ Warfare Logic Ferrari  
│   └── main.py        #    Activated: Risk = HIGH/CRITICAL
├── 03_CLOCKWORK/      # ⚙️ Cycle Logic Ferrari
│   └── main.py        #    Activated: Risk = MEDIUM
└── 04_FUSION/         # 🌟 T.I.A. + Scavenged Math Ferrari
    └── main.py        #    Activated: Special conditions
```

## How It Works

### 1. T.I.A. Analyzes Risk
T.I.A. continuously monitors system metrics and calculates risk level:
- **LOW** (score < 0.3)
- **MEDIUM** (0.3-0.6)
- **HIGH** (≥ 0.6)

### 2. Garage Manager Selects Ferrari
Based on T.I.A.'s risk assessment, the Garage Manager selects the appropriate strategy:

| Risk Level | Selected Ferrari | Strategy Type |
|------------|-----------------|---------------|
| LOW        | 01_ELITE        | Precision Logic |
| MEDIUM     | 03_CLOCKWORK    | Cycle Logic |
| HIGH       | 02_ATOMIC       | Warfare Logic |
| Special    | 04_FUSION       | T.I.A. + Scavenged Math |

### 3. Strategy Execution
The active Ferrari executes its strategy based on market data.

## Usage

### API Endpoints

```bash
# Get garage status
curl http://localhost:8000/cockpit/garage/status

# Select a specific Ferrari (force)
curl -X POST "http://localhost:8000/cockpit/garage/select?bay=01_ELITE"

# Auto-select based on T.I.A. risk
curl -X POST http://localhost:8000/cockpit/garage/select

# Execute current strategy
curl -X POST http://localhost:8000/cockpit/garage/execute \
  -H "Content-Type: application/json" \
  -d '{"market_data": {"price": 65000, "volume": 1000000}}'

# Reload engines (after updating code)
curl -X POST http://localhost:8000/cockpit/garage/reload
```

### Python API

```python
from backend.services.garage_manager import garage_manager, GarageBay

# Get garage status
status = garage_manager.get_garage_status()

# Auto-select Ferrari based on T.I.A. risk
engine = garage_manager.select_ferrari()

# Force select a specific Ferrari
engine = garage_manager.select_ferrari(force_bay=GarageBay.ELITE)

# Execute strategy
result = garage_manager.execute_current_strategy(
    market_data={"price": 65000, "volume": 1000000},
    config={"risk_limit": 0.02}
)

# Reload engines after updating code
garage_manager.reload_engines()
```

## Adding Your Ferrari Code

### Current Status
Each bay contains a **placeholder** `main.py` file. The structure is ready for your strategy code.

### How to Add Code

#### Option 1: Direct Edit (Mobile-Friendly)
1. Navigate to the bay on GitHub (e.g., `GENESIS_GARAGE/01_ELITE/main.py`)
2. Click "Edit" (works on mobile browser)
3. Paste your Ferrari code
4. Commit directly to the branch

#### Option 2: Local Development
```bash
# Edit the main.py file locally
nano GENESIS_GARAGE/01_ELITE/main.py

# Commit and push
git add GENESIS_GARAGE/01_ELITE/main.py
git commit -m "Add ELITE Ferrari strategy code"
git push
```

### Required Interface

Each Ferrari's `main.py` must implement:

```python
def execute_strategy(market_data: dict, config: dict = None) -> dict:
    """
    Execute the strategy
    
    Args:
        market_data: Current market data and indicators
        config: Optional configuration parameters
        
    Returns:
        Trading signals and recommendations
    """
    return {
        "strategy": "YOUR_STRATEGY_NAME",
        "signal": "BUY" | "SELL" | "HOLD",
        "confidence": 0.95,  # 0.0 to 1.0
        "price_target": 66000,
        "stop_loss": 64000,
        "position_size": 0.1
    }

def get_status() -> dict:
    """Get engine status"""
    return {
        "engine": "01_ELITE",
        "name": "Your Ferrari Name",
        "status": "READY",
        "ready": True
    }
```

## Ferrari Descriptions

### 🏎️ 01_ELITE - Precision Logic
**Activation:** LOW risk conditions  
**Purpose:** High-precision trades in stable markets  
**Characteristics:** 
- Conservative position sizing
- Tight stop losses
- High win rate focus

### ⚔️ 02_ATOMIC - Warfare Logic
**Activation:** HIGH/CRITICAL risk conditions  
**Purpose:** Aggressive defensive trading in volatile markets  
**Characteristics:**
- Dynamic position sizing
- Wide stop losses
- Volatility exploitation

### ⚙️ 03_CLOCKWORK - Cycle Logic
**Activation:** MEDIUM risk conditions  
**Purpose:** Balanced strategy for normal market cycles  
**Characteristics:**
- Pattern recognition
- Cycle-based entries/exits
- Moderate risk/reward

### 🌟 04_FUSION - T.I.A. + Scavenged Math
**Activation:** Special conditions / T.I.A. override  
**Purpose:** Advanced hybrid strategy combining T.I.A.'s intelligence with mathematical models  
**Characteristics:**
- AI-enhanced decision making
- Dynamic strategy blending
- Adaptive to market regime

## Integration with T.I.A. Cockpit

The Garage Manager is fully integrated with the T.I.A. Cockpit:

1. **Automatic Selection:** T.I.A.'s risk level automatically determines which Ferrari to use
2. **Manual Override:** Admiral can force-select a specific Ferrari
3. **Real-time Monitoring:** Cockpit displays active Ferrari and its status
4. **Hot Reload:** Update Ferrari code without restarting the system

## Testing

```python
# Test garage initialization
from backend.services.garage_manager import garage_manager

status = garage_manager.get_garage_status()
print(f"Available bays: {status['available_bays']}")

# Test Ferrari loading
engine = garage_manager.select_ferrari()
print(f"Active bay: {garage_manager.current_bay}")

# Test strategy execution
result = garage_manager.execute_current_strategy({"test": "data"})
print(f"Result: {result}")
```

## Why Now?

**Context is Fresh:** The agent just finished the T.I.A. Bridge and knows exactly how T.I.A. thinks.

**One Clean PR:** By adding the Garage to this branch, everything arrives as one big, beautiful upgrade.

**Mobile Friendly:** The `main.py` files are ready in the repo. Just navigate on your phone, hit "Edit," and paste your code.

## Commander's Vision 🦎⚔️

> "T.I.A. is the gatekeeper. The Garage provides the cars."

T.I.A. analyzes the market weather and selects the perfect Ferrari for the conditions. Each strategy engine is a precision tool, and the Garage Manager ensures the right tool is always active.

**The hangar is built. The bays are ready. Time to drop in the cool shit.** 🏁
