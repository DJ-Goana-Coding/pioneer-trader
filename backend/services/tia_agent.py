# ================================================================
# 🦎 T.I.A. AGENT - Tactical Intelligence Agent
# ================================================================
# Risk analysis & posture tracking
# Pattern adapted from perimeter-scout architecture
# ================================================================

import time
from enum import Enum
from typing import Dict, Optional, Any
from datetime import datetime
from backend.services.redis_cache import redis_cache
from backend.core.logging_config import setup_logging

logger = setup_logging("tia_agent")


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TIAAgent:
    """T.I.A. - Tactical Intelligence Agent
    
    The soul of the system - analyzes risk and controls access
    to premium features based on system posture.
    """
    
    def __init__(self):
        self.current_risk = RiskLevel.LOW
        self.confidence = 1.0  # 0.0 to 1.0
        self.last_assessment = None
        self.aegis_snapshots = []
        
        # Restore state from Redis
        self._restore_state()
        
        logger.info("🦎 T.I.A. AGENT: Initialized")
    
    def _restore_state(self):
        """Restore T.I.A. state from Redis"""
        if not redis_cache.is_connected():
            return
            
        try:
            state = redis_cache.client.hgetall("tia:state")
            if state:
                self.current_risk = RiskLevel(state.get("risk_level", "LOW"))
                self.confidence = float(state.get("confidence", 1.0))
                self.last_assessment = state.get("last_assessment")
                logger.info(f"🔴 REDIS: Restored T.I.A. state - Risk: {self.current_risk}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to restore T.I.A. state: {e}")
    
    def _persist_state(self):
        """Persist T.I.A. state to Redis"""
        if not redis_cache.is_connected():
            return
            
        try:
            redis_cache.client.hset("tia:state", mapping={
                "risk_level": self.current_risk.value,
                "confidence": str(self.confidence),
                "last_assessment": self.last_assessment or "",
                "updated_at": datetime.utcnow().isoformat()
            })
            redis_cache.client.expire("tia:state", 3600)  # 1 hour TTL
        except Exception as e:
            logger.warning(f"⚠️ Failed to persist T.I.A. state: {e}")
    
    def consume_aegis(self, snapshot: Dict[str, Any]) -> None:
        """Consume security/posture snapshot from the system
        
        Args:
            snapshot: System status snapshot with metrics like:
                - wallet_balance: Current USDT balance
                - total_equity: Total portfolio value
                - active_slots: Number of active positions
                - recent_trades: Recent trade history
                - market_volatility: Optional volatility indicator
        """
        snapshot["timestamp"] = datetime.utcnow().isoformat()
        self.aegis_snapshots.append(snapshot)
        
        # Keep last 10 snapshots
        if len(self.aegis_snapshots) > 10:
            self.aegis_snapshots.pop(0)
        
        logger.info(f"🦎 T.I.A.: Consumed AEGIS snapshot - {len(self.aegis_snapshots)} in buffer")
    
    def analyze_risk(self, snapshot: Optional[Dict[str, Any]] = None) -> RiskLevel:
        """Analyze current risk level based on system metrics
        
        Args:
            snapshot: Optional snapshot to analyze. If None, uses last consumed snapshot.
            
        Returns:
            RiskLevel: LOW, MEDIUM, or HIGH
        """
        if snapshot:
            data = snapshot
        elif self.aegis_snapshots:
            data = self.aegis_snapshots[-1]
        else:
            # No data - assume LOW risk for initial state
            return RiskLevel.LOW
        
        risk_score = 0.0
        
        # Factor 1: Wallet balance (lower balance = higher risk)
        wallet_balance = data.get("wallet_balance", 100.0)
        if wallet_balance < 10:
            risk_score += 0.4
        elif wallet_balance < 25:
            risk_score += 0.2
        
        # Factor 2: Active slots (too many slots = higher risk)
        active_slots = data.get("active_slots", 0)
        if active_slots > 12:
            risk_score += 0.3
        elif active_slots > 8:
            risk_score += 0.15
        
        # Factor 3: Total equity vs starting capital
        total_equity = data.get("total_equity", 100.0)
        starting_capital = data.get("starting_capital", 94.50)
        if total_equity < starting_capital * 0.7:  # Down 30%+
            risk_score += 0.5
        elif total_equity < starting_capital * 0.85:  # Down 15%+
            risk_score += 0.25
        
        # Determine risk level from score
        if risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def produce_summary(self) -> Dict[str, Any]:
        """Generate risk assessment summary
        
        Returns:
            Dict with risk level, confidence, and analysis details
        """
        # Analyze current risk
        new_risk = self.analyze_risk()
        
        # Update confidence based on data availability
        if len(self.aegis_snapshots) >= 3:
            self.confidence = 1.0
        elif len(self.aegis_snapshots) >= 1:
            self.confidence = 0.7
        else:
            self.confidence = 0.5
        
        # Update state
        self.current_risk = new_risk
        self.last_assessment = datetime.utcnow().isoformat()
        
        # Persist to Redis
        self._persist_state()
        
        summary = {
            "risk_level": self.current_risk.value,
            "confidence": self.confidence,
            "last_assessment": self.last_assessment,
            "snapshots_analyzed": len(self.aegis_snapshots),
            "authorization_recommended": self.current_risk != RiskLevel.HIGH,
            "message": self._get_risk_message()
        }
        
        logger.info(f"🦎 T.I.A. ASSESSMENT: Risk={self.current_risk} Confidence={self.confidence:.0%}")
        
        return summary
    
    def _get_risk_message(self) -> str:
        """Get human-readable risk message"""
        if self.current_risk == RiskLevel.LOW:
            return "System posture excellent. All systems green."
        elif self.current_risk == RiskLevel.MEDIUM:
            return "Elevated risk detected. Monitor closely."
        else:
            return "HIGH RISK: Recommend defensive posture. Premium access should be restricted."
    
    def get_status(self) -> Dict[str, Any]:
        """Get current T.I.A. status without re-analyzing
        
        Returns:
            Current status including risk level and confidence
        """
        return {
            "risk_level": self.current_risk.value,
            "confidence": self.confidence,
            "last_assessment": self.last_assessment,
            "status": "ACTIVE",
            "message": self._get_risk_message()
        }
    
    def should_authorize_admiral(self) -> bool:
        """Determine if Admiral should be authorized for premium access
        
        Returns:
            True if risk level is not HIGH, False otherwise
        """
        return self.current_risk != RiskLevel.HIGH


# Singleton instance
tia_agent = TIAAgent()
