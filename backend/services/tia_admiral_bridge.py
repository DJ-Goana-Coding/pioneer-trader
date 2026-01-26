# ================================================================
# 🌉 T.I.A.-ADMIRAL BRIDGE - Authorization Gateway
# ================================================================
# T.I.A. grants Admiral access to premium cockpit features
# The bridge controls the flow of permissions based on risk analysis
# ================================================================

from typing import Dict, Any, List
from datetime import datetime
from backend.services.tia_agent import tia_agent, RiskLevel
from backend.services.admiral_engine import admiral_engine
from backend.services.redis_cache import redis_cache
from backend.core.logging_config import setup_logging

logger = setup_logging("tia_admiral_bridge")


class TIAAdmiralBridge:
    """T.I.A. grants Admiral access to premium cockpit features
    
    This bridge is the gatekeeper between T.I.A.'s risk analysis
    and Admiral's premium capabilities. T.I.A. is the soul of the
    system and controls what Admiral can access.
    """
    
    PREMIUM_CAPABILITIES = [
        "sniper_execution",      # 95% precision trades
        "vortex_control",        # Full VortexEngine access
        "strategy_override",     # Manual strategy switching
        "risk_clamp_control",    # Adjust max notional
        "trailing_stop_config",  # Configure trail_drop %
        "slot_scaling",          # Scale 15→30 slots
        "airgapped_sync",        # HuggingFace Space sync
    ]
    
    def __init__(self):
        self.authorization_history = []
        self._restore_state()
        logger.info("🌉 T.I.A.-ADMIRAL BRIDGE: Initialized")
    
    def _restore_state(self):
        """Restore bridge state from Redis"""
        if not redis_cache.is_connected():
            return
            
        try:
            # Get authorization state
            state = redis_cache.client.hgetall("bridge:authorization")
            if state and state.get("premium_authorized") == "true":
                # Restore authorization if it was active
                admiral_engine.premium_authorized = True
                admiral_engine.authorization_timestamp = state.get("timestamp")
                admiral_engine.authorized_by = state.get("authorized_by", "T.I.A.")
                
                # Re-enable premium capabilities
                for cap in admiral_engine.capabilities.values():
                    if cap.type.value == "PREMIUM":
                        cap.enabled = True
                
                logger.info("🔴 REDIS: Restored Admiral premium authorization")
        except Exception as e:
            logger.warning(f"⚠️ Failed to restore bridge state: {e}")
    
    def _persist_state(self):
        """Persist bridge state to Redis"""
        if not redis_cache.is_connected():
            return
            
        try:
            redis_cache.client.hset("bridge:authorization", mapping={
                "premium_authorized": "true" if admiral_engine.premium_authorized else "false",
                "timestamp": admiral_engine.authorization_timestamp or "",
                "authorized_by": admiral_engine.authorized_by or "",
                "updated_at": datetime.utcnow().isoformat()
            })
            redis_cache.client.expire("bridge:authorization", 3600)  # 1 hour TTL
        except Exception as e:
            logger.warning(f"⚠️ Failed to persist bridge state: {e}")
    
    def _log_authorization_event(self, event_type: str, details: Dict[str, Any]):
        """Log authorization events to Redis and memory
        
        Args:
            event_type: Type of event (AUTHORIZE, REVOKE, etc.)
            details: Event details
        """
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **details
        }
        
        # Add to in-memory history
        self.authorization_history.append(event)
        if len(self.authorization_history) > 50:
            self.authorization_history.pop(0)
        
        # Log to Redis
        if redis_cache.is_connected():
            try:
                import json
                redis_cache.client.lpush("bridge:events", json.dumps(event))
                redis_cache.client.ltrim("bridge:events", 0, 99)  # Keep last 100 events
            except Exception as e:
                logger.warning(f"⚠️ Failed to log event to Redis: {e}")
        
        logger.info(f"📝 BRIDGE EVENT: {event_type} - {details}")
    
    def authorize_admiral(self, force: bool = False) -> Dict[str, Any]:
        """T.I.A. authorizes Admiral for premium cockpit access
        
        Args:
            force: If True, bypass risk check and authorize anyway
            
        Returns:
            Authorization result with status and details
        """
        # Get T.I.A.'s current risk assessment
        tia_summary = tia_agent.produce_summary()
        risk_level = tia_summary["risk_level"]
        
        # Check if authorization is recommended
        if not force and risk_level == RiskLevel.HIGH.value:
            result = {
                "success": False,
                "message": "Authorization DENIED: T.I.A. reports HIGH RISK",
                "risk_level": risk_level,
                "confidence": tia_summary["confidence"],
                "recommendation": "System posture must improve before granting premium access"
            }
            
            self._log_authorization_event("AUTHORIZATION_DENIED", {
                "reason": "HIGH_RISK",
                "risk_level": risk_level
            })
            
            return result
        
        # Grant premium access through Admiral Engine
        granted = admiral_engine.grant_premium_access(authorized_by="T.I.A.")
        
        # Persist state
        self._persist_state()
        
        result = {
            "success": True,
            "message": "✅ Admiral AUTHORIZED for premium cockpit access",
            "risk_level": risk_level,
            "confidence": tia_summary["confidence"],
            "capabilities_granted": self.PREMIUM_CAPABILITIES,
            "authorized_at": admiral_engine.authorization_timestamp,
            "forced": force
        }
        
        self._log_authorization_event("AUTHORIZED", {
            "risk_level": risk_level,
            "confidence": tia_summary["confidence"],
            "forced": force
        })
        
        logger.info(f"✅ BRIDGE: Admiral authorized (Risk: {risk_level}, Forced: {force})")
        
        return result
    
    def revoke_admiral(self, reason: str = "Manual revocation") -> Dict[str, Any]:
        """T.I.A. revokes Admiral's premium access
        
        Args:
            reason: Reason for revocation
            
        Returns:
            Revocation result with status
        """
        # Revoke premium access
        revoked = admiral_engine.revoke_premium_access()
        
        # Persist state
        self._persist_state()
        
        result = {
            "success": True,
            "message": "🔒 Admiral premium access REVOKED",
            "reason": reason,
            "revoked_at": datetime.utcnow().isoformat()
        }
        
        self._log_authorization_event("REVOKED", {
            "reason": reason
        })
        
        logger.info(f"🔒 BRIDGE: Admiral access revoked - {reason}")
        
        return result
    
    def get_authorization_status(self) -> Dict[str, Any]:
        """Get current authorization status
        
        Returns:
            Status dict with authorization state and details
        """
        tia_status = tia_agent.get_status()
        admiral_status = admiral_engine.get_capability_summary()
        
        return {
            "authorized": admiral_engine.premium_authorized,
            "tia": {
                "risk_level": tia_status["risk_level"],
                "confidence": tia_status["confidence"],
                "message": tia_status["message"]
            },
            "admiral": {
                "premium_authorized": admiral_status["premium_authorized"],
                "enabled_capabilities": admiral_status["enabled_capabilities"],
                "premium_capabilities": admiral_status["premium_capabilities"]
            },
            "authorization_info": admiral_status["authorization_info"]
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get current capability status
        
        Returns:
            Capabilities dict with premium status
        """
        return {
            "premium_capabilities": self.PREMIUM_CAPABILITIES,
            "authorized": admiral_engine.premium_authorized,
            "enabled": admiral_engine.get_enabled_capabilities() if admiral_engine.premium_authorized else [],
            "available": self.PREMIUM_CAPABILITIES if admiral_engine.premium_authorized else []
        }
    
    def get_event_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get authorization event history
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent authorization events
        """
        # Return from memory
        return self.authorization_history[-limit:] if self.authorization_history else []


# Singleton instance
tia_admiral_bridge = TIAAdmiralBridge()
