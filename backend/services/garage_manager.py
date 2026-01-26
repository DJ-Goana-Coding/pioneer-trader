# ================================================================
# 🏁 GARAGE MANAGER - Multi-Ferrari Strategy Selector
# ================================================================
# The "Hangar" that holds T.I.A.'s fleet of strategy engines
# Selects the best Ferrari for the current market weather
# ================================================================

import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

from backend.services.tia_agent import tia_agent, RiskLevel
from backend.core.logging_config import setup_logging

logger = setup_logging("garage_manager")


class GarageBay(str, Enum):
    """Available Ferrari bays in the Genesis Garage"""
    ELITE = "01_ELITE"          # Precision Logic - LOW risk
    ATOMIC = "02_ATOMIC"        # Warfare Logic - HIGH/CRITICAL risk
    CLOCKWORK = "03_CLOCKWORK"  # Cycle Logic - MEDIUM risk
    FUSION = "04_FUSION"        # T.I.A. + Scavenged Math - Special


class GarageManager:
    """
    Genesis Garage Manager - Multi-Ferrari Strategy Selector
    
    T.I.A. is the gatekeeper. The Garage provides the cars.
    Based on T.I.A.'s risk assessment, the manager selects
    which Ferrari (strategy engine) to activate.
    """
    
    GARAGE_PATH = Path(__file__).parent.parent.parent / "GENESIS_GARAGE"
    
    # Risk level to Ferrari bay mapping
    RISK_TO_BAY = {
        RiskLevel.LOW: GarageBay.ELITE,
        RiskLevel.MEDIUM: GarageBay.CLOCKWORK,
        RiskLevel.HIGH: GarageBay.ATOMIC,
    }
    
    def __init__(self):
        self.current_bay: Optional[GarageBay] = None
        self.current_engine = None
        self.engines_cache: Dict[GarageBay, Any] = {}
        
        logger.info("🏁 GARAGE MANAGER: Initialized")
        logger.info(f"   Garage Path: {self.GARAGE_PATH}")
        
        # Verify garage structure exists
        if not self.GARAGE_PATH.exists():
            logger.warning(f"⚠️ GARAGE: Genesis Garage not found at {self.GARAGE_PATH}")
    
    def _load_engine(self, bay: GarageBay) -> Optional[Any]:
        """
        Load a Ferrari engine from the specified bay
        
        Args:
            bay: The garage bay to load from
            
        Returns:
            The loaded engine module or None if not available
        """
        if bay in self.engines_cache:
            logger.info(f"🏎️ GARAGE: Using cached {bay.value} Ferrari")
            return self.engines_cache[bay]
        
        bay_path = self.GARAGE_PATH / bay.value / "main.py"
        
        if not bay_path.exists():
            logger.warning(f"⚠️ GARAGE: {bay.value} Ferrari not found at {bay_path}")
            return None
        
        try:
            # Dynamically import the engine module
            spec = importlib.util.spec_from_file_location(
                f"garage.{bay.value}",
                bay_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                
                # Cache the loaded engine
                self.engines_cache[bay] = module
                
                logger.info(f"✅ GARAGE: Loaded {bay.value} Ferrari from {bay_path}")
                return module
            else:
                logger.error(f"❌ GARAGE: Failed to load spec for {bay.value}")
                return None
                
        except Exception as e:
            logger.error(f"❌ GARAGE: Error loading {bay.value} Ferrari: {e}")
            return None
    
    def select_ferrari(self, force_bay: Optional[GarageBay] = None) -> Optional[Any]:
        """
        Select the appropriate Ferrari based on T.I.A.'s risk assessment
        
        Args:
            force_bay: Optional bay to force selection (overrides T.I.A.)
            
        Returns:
            The selected engine module or None
        """
        if force_bay:
            logger.info(f"🏁 GARAGE: Force selecting {force_bay.value} Ferrari")
            selected_bay = force_bay
        else:
            # Get T.I.A.'s current risk assessment
            tia_status = tia_agent.get_status()
            risk_level = RiskLevel(tia_status['risk_level'])
            
            # Select Ferrari based on risk
            selected_bay = self.RISK_TO_BAY.get(risk_level, GarageBay.CLOCKWORK)
            
            logger.info(f"🦎 T.I.A. RISK: {risk_level.value} → Selecting {selected_bay.value} Ferrari")
        
        # Load the selected engine
        engine = self._load_engine(selected_bay)
        
        if engine:
            self.current_bay = selected_bay
            self.current_engine = engine
            logger.info(f"🏎️ GARAGE: {selected_bay.value} Ferrari ACTIVE")
        else:
            logger.warning(f"⚠️ GARAGE: Failed to activate {selected_bay.value} Ferrari")
        
        return engine
    
    def execute_current_strategy(self, market_data: dict, config: dict = None) -> dict:
        """
        Execute the currently selected Ferrari's strategy
        
        Args:
            market_data: Current market data and indicators
            config: Optional configuration parameters
            
        Returns:
            Trading signals and recommendations
        """
        if not self.current_engine:
            logger.warning("⚠️ GARAGE: No Ferrari currently active. Selecting...")
            self.select_ferrari()
        
        if not self.current_engine:
            return {
                "error": "NO_FERRARI_ACTIVE",
                "message": "No strategy engine available",
                "status": "FAILED"
            }
        
        try:
            # Execute the strategy
            result = self.current_engine.execute_strategy(market_data, config)
            result['active_bay'] = self.current_bay.value if self.current_bay else None
            return result
            
        except Exception as e:
            logger.error(f"❌ GARAGE: Strategy execution error: {e}")
            return {
                "error": "EXECUTION_FAILED",
                "message": str(e),
                "status": "FAILED",
                "active_bay": self.current_bay.value if self.current_bay else None
            }
    
    def get_garage_status(self) -> Dict[str, Any]:
        """
        Get complete garage status
        
        Returns:
            Status dict with active bay, available bays, and engine states
        """
        # Check which bays have engines loaded
        available_bays = []
        for bay in GarageBay:
            bay_path = self.GARAGE_PATH / bay.value / "main.py"
            if bay_path.exists():
                available_bays.append(bay.value)
        
        # Get current engine status if active
        engine_status = None
        if self.current_engine and hasattr(self.current_engine, 'get_status'):
            try:
                engine_status = self.current_engine.get_status()
            except Exception as e:
                logger.warning(f"⚠️ Could not get engine status: {e}")
        
        return {
            "garage_path": str(self.GARAGE_PATH),
            "current_bay": self.current_bay.value if self.current_bay else None,
            "available_bays": available_bays,
            "total_bays": len(GarageBay),
            "engines_cached": len(self.engines_cache),
            "current_engine_status": engine_status,
            "tia_integration": "ACTIVE"
        }
    
    def reload_engines(self):
        """
        Clear the engine cache and force reload on next selection
        Useful after manually updating Ferrari code
        """
        logger.info("🔄 GARAGE: Clearing engine cache")
        self.engines_cache.clear()
        self.current_engine = None
        self.current_bay = None
        logger.info("✅ GARAGE: Cache cleared. Engines will reload on next selection.")
    
    def get_bay_for_risk(self, risk_level: RiskLevel) -> GarageBay:
        """
        Get the recommended bay for a given risk level
        
        Args:
            risk_level: T.I.A. risk level
            
        Returns:
            Recommended garage bay
        """
        return self.RISK_TO_BAY.get(risk_level, GarageBay.CLOCKWORK)


# Singleton instance
garage_manager = GarageManager()
