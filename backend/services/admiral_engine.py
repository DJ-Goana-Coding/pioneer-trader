# ================================================================
# ⚔️ ADMIRAL ENGINE - Trading Module Interface
# ================================================================
# Manages base and premium capabilities for the trading system
# Premium access granted by T.I.A. through the bridge
# ================================================================

from enum import Enum
from typing import List, Dict, Any
from datetime import datetime
from backend.core.logging_config import setup_logging

logger = setup_logging("admiral_engine")


class CapabilityType(str, Enum):
    """Capability types"""
    BASE = "BASE"
    PREMIUM = "PREMIUM"


class Capability:
    """Trading capability definition"""
    def __init__(self, name: str, description: str, capability_type: CapabilityType):
        self.name = name
        self.description = description
        self.type = capability_type
        self.enabled = capability_type == CapabilityType.BASE  # Base always enabled


class AdmiralEngine:
    """Admiral Engine - Trading Module Interface
    
    Manages trading capabilities and premium features.
    Premium access is controlled by T.I.A. through the bridge.
    """
    
    # Base capabilities - always available
    BASE_CAPABILITIES = [
        ("basic_trading", "Execute standard buy/sell trades"),
        ("telemetry", "Monitor system metrics and status"),
        ("portfolio_view", "View portfolio and holdings"),
    ]
    
    # Premium capabilities - granted by T.I.A.
    PREMIUM_CAPABILITIES = [
        ("sniper_execution", "95% precision trades with advanced timing"),
        ("vortex_control", "Full VortexEngine access and control"),
        ("strategy_override", "Manual strategy switching and configuration"),
        ("risk_clamp_control", "Adjust maximum notional and risk limits"),
        ("trailing_stop_config", "Configure trail_drop % for positions"),
        ("slot_scaling", "Scale from 15 to 30 trading slots"),
        ("airgapped_sync", "HuggingFace Space synchronization"),
    ]
    
    def __init__(self):
        self.capabilities: Dict[str, Capability] = {}
        self.premium_authorized = False
        self.authorization_timestamp = None
        self.authorized_by = None
        
        # Initialize base capabilities
        for name, desc in self.BASE_CAPABILITIES:
            self.capabilities[name] = Capability(name, desc, CapabilityType.BASE)
        
        # Initialize premium capabilities (disabled by default)
        for name, desc in self.PREMIUM_CAPABILITIES:
            self.capabilities[name] = Capability(name, desc, CapabilityType.PREMIUM)
        
        logger.info(f"⚔️ ADMIRAL ENGINE: Initialized with {len(self.BASE_CAPABILITIES)} base capabilities")
    
    def grant_premium_access(self, authorized_by: str = "T.I.A.") -> bool:
        """Grant premium capabilities to Admiral
        
        Args:
            authorized_by: Who authorized the access (default: T.I.A.)
            
        Returns:
            True if access was granted, False if already granted
        """
        if self.premium_authorized:
            logger.info("⚔️ ADMIRAL: Premium access already granted")
            return False
        
        self.premium_authorized = True
        self.authorization_timestamp = datetime.utcnow().isoformat()
        self.authorized_by = authorized_by
        
        # Enable all premium capabilities
        for cap in self.capabilities.values():
            if cap.type == CapabilityType.PREMIUM:
                cap.enabled = True
        
        logger.info(f"✅ ADMIRAL: Premium access GRANTED by {authorized_by}")
        return True
    
    def revoke_premium_access(self) -> bool:
        """Revoke premium capabilities from Admiral
        
        Returns:
            True if access was revoked, False if already revoked
        """
        if not self.premium_authorized:
            logger.info("⚔️ ADMIRAL: Premium access already revoked")
            return False
        
        self.premium_authorized = False
        self.authorization_timestamp = None
        self.authorized_by = None
        
        # Disable all premium capabilities
        for cap in self.capabilities.values():
            if cap.type == CapabilityType.PREMIUM:
                cap.enabled = False
        
        logger.info("🔒 ADMIRAL: Premium access REVOKED")
        return True
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if a specific capability is enabled
        
        Args:
            capability_name: Name of the capability to check
            
        Returns:
            True if capability exists and is enabled
        """
        cap = self.capabilities.get(capability_name)
        return cap.enabled if cap else False
    
    def get_enabled_capabilities(self) -> List[str]:
        """Get list of currently enabled capabilities
        
        Returns:
            List of enabled capability names
        """
        return [
            name for name, cap in self.capabilities.items()
            if cap.enabled
        ]
    
    def get_premium_capabilities(self) -> List[str]:
        """Get list of premium capabilities (regardless of enabled state)
        
        Returns:
            List of premium capability names
        """
        return [
            name for name, cap in self.capabilities.items()
            if cap.type == CapabilityType.PREMIUM
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get Admiral Engine status for cockpit display
        
        Returns:
            Status dict with capabilities and authorization info
        """
        enabled_caps = self.get_enabled_capabilities()
        premium_caps = self.get_premium_capabilities()
        
        status = {
            "status": "ACTIVE",
            "premium_authorized": self.premium_authorized,
            "authorization_timestamp": self.authorization_timestamp,
            "authorized_by": self.authorized_by,
            "total_capabilities": len(self.capabilities),
            "enabled_capabilities": len(enabled_caps),
            "premium_capabilities": len(premium_caps),
            "capabilities": {
                "base": [
                    {"name": name, "description": cap.description, "enabled": cap.enabled}
                    for name, cap in self.capabilities.items()
                    if cap.type == CapabilityType.BASE
                ],
                "premium": [
                    {"name": name, "description": cap.description, "enabled": cap.enabled}
                    for name, cap in self.capabilities.items()
                    if cap.type == CapabilityType.PREMIUM
                ]
            }
        }
        
        return status
    
    def get_capability_summary(self) -> Dict[str, Any]:
        """Get summary of capabilities for quick display
        
        Returns:
            Simplified capability summary
        """
        return {
            "premium_authorized": self.premium_authorized,
            "enabled_capabilities": self.get_enabled_capabilities(),
            "premium_capabilities": self.get_premium_capabilities(),
            "authorization_info": {
                "authorized_by": self.authorized_by,
                "timestamp": self.authorization_timestamp
            } if self.premium_authorized else None
        }


# Singleton instance
admiral_engine = AdmiralEngine()
