
from typing import Dict, Type
# Mocking settings to avoid another import error
class Settings:
    PROJECT_NAME = "Citadel"
settings = Settings()

from registry.registry import Registry, StrategySpec

# --- Placeholder Strategy Classes ---
class BaseStrategy:
    def __init__(self, spec: StrategySpec):
        self.spec = spec
        print(f"   🔧 Initialized Logic: {spec.name} [{spec.id}]")

    def run(self, market_data):
        print(f"   🚀 Executing {self.spec.id} with data: {market_data}")

class EMATrendStrategy(BaseStrategy): pass
class RSIReversionStrategy(BaseStrategy): pass

class RuntimeBinder:
    def __init__(self, codex_path="registry/codex.json"):
        self.registry = Registry.load(codex_path)
        self.strategy_map = {
            "trend_ema_01": EMATrendStrategy,
            "mr_rsi_01": RSIReversionStrategy,
        }
        self.active_instances = {}

    def bind_and_load(self):
        print("\n🔌 BINDING CODEX TO RUNTIME...")
        loaded_count = 0
        for strat_id, spec in self.registry.strategies.items():
            if not spec.enabled: continue
            
            strat_class = self.strategy_map.get(strat_id)
            if strat_class:
                self.active_instances[strat_id] = strat_class(spec)
                loaded_count += 1
            else:
                print(f"   ⚠️ WARNING: No code mapped for {strat_id}")
        
        print(f"✅ BINDER COMPLETE. {loaded_count} Strategies Ready.\n")
        return self.active_instances
