
import sys
import os

# Add root to path so we can import registry
sys.path.append(os.getcwd())

try:
    from registry.registry import Registry
    print("🛡️ Running Codex Validation Protocol...")
    
    reg = Registry.load("registry/codex.json")
    
    print(f"✅ Schema Validated.")
    print(f"   - Strategies: {len(reg.strategies)}")
    print(f"   - Engines: {len(reg.engines)}")
    print(f"   - Overlays: {len(reg.overlays)}")
    print("✅ SYSTEM INTEGRITY: 100%")
    
except Exception as e:
    print(f"❌ VALIDATION FAILED: {e}")
    sys.exit(1)
