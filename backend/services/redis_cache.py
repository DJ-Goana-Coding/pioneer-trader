# ================================================================
# 🔴 REDIS CACHE SERVICE - State Persistence Layer
# ================================================================
import os
import json
import redis
from typing import Optional, Any, Dict
from datetime import datetime, timezone
from backend.core.logging_config import setup_logging

logger = setup_logging("redis_cache")

class RedisCache:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.enabled = os.getenv("REDIS_ENABLED", "True").lower() == "true"
        self.client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        """Initialize Redis connection"""
        if not self.enabled:
            logger.info("📴 REDIS: Disabled via REDIS_ENABLED=False")
            return
            
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            # Log connection without exposing full URL
            host_info = self.redis_url.split('@')[-1] if '@' in self.redis_url else 'localhost:6379'
            logger.info(f"🔴 REDIS: Connected to {host_info}")
        except Exception as e:
            logger.warning(f"⚠️ REDIS: Connection failed - {e}. Running in memory-only mode.")
            self.client = None

    def is_connected(self) -> bool:
        """Check if Redis is available"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    # ═══════════════════════════════════════════════════════════
    # 💰 PORTFOLIO STATE
    # ═══════════════════════════════════════════════════════════
    
    def save_portfolio_state(self, state: Dict[str, Any]):
        """Persist portfolio state to Redis"""
        if not self.client:
            return False
        try:
            state['last_updated'] = datetime.now(timezone.utc).isoformat()
            self.client.hset("vortex:portfolio", mapping={
                k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in state.items()
            })
            self.client.expire("vortex:portfolio", 3600)  # 1 hour TTL
            return True
        except Exception as e:
            logger.warning(f"⚠️ REDIS: Failed to save portfolio - {e}")
            return False

    def get_portfolio_state(self) -> Optional[Dict[str, Any]]:
        """Retrieve portfolio state from Redis"""
        if not self.client:
            return None
        try:
            data = self.client.hgetall("vortex:portfolio")
            if not data:
                return None
            result = {}
            for k, v in data.items():
                try:
                    # Try to parse as JSON
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, ValueError):
                    # Keep as string if not valid JSON
                    result[k] = v
            return result
        except Exception as e:
            logger.warning(f"⚠️ REDIS: Failed to get portfolio - {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # 📈 PEAK PRICE TRACKING (For Trailing Take Profit)
    # ═══════════════════════════════════════════════════════════
    
    def set_peak_price(self, symbol: str, price: float):
        """Store peak price for trailing stop logic"""
        if not self.client:
            return
        try:
            self.client.hset("vortex:peaks", symbol, str(price))
        except Exception as e:
            logger.warning(f"⚠️ REDIS: Failed to set peak price - {e}")
            pass

    def get_peak_price(self, symbol: str) -> Optional[float]:
        """Get stored peak price"""
        if not self.client:
            return None
        try:
            val = self.client.hget("vortex:peaks", symbol)
            return float(val) if val else None
        except Exception:
            return None

    def get_all_peaks(self) -> Dict[str, float]:
        """Get all peak prices"""
        if not self.client:
            return {}
        try:
            data = self.client.hgetall("vortex:peaks")
            return {k: float(v) for k, v in data.items()}
        except Exception:
            return {}

    def clear_peak(self, symbol: str):
        """Clear peak price after sell"""
        if not self.client:
            return
        try:
            self.client.hdel("vortex:peaks", symbol)
        except Exception as e:
            logger.warning(f"⚠️ REDIS: Failed to clear peak - {e}")
            pass

    # ═══════════════════════════════════════════════════════════
    # 📝 TRADE HISTORY
    # ═══════════════════════════════════════════════════════════
    
    def log_trade(self, trade: Dict[str, Any]):
        """Append trade to history list"""
        if not self.client:
            return
        try:
            trade['timestamp'] = datetime.now(timezone.utc).isoformat()
            self.client.lpush("vortex:trades", json.dumps(trade))
            self.client.ltrim("vortex:trades", 0, 99)  # Keep last 100 trades
        except Exception as e:
            logger.warning(f"⚠️ REDIS: Failed to log trade - {e}")
            pass

    def get_trade_history(self, limit: int = 20) -> list:
        """Get recent trade history"""
        if not self.client:
            return []
        try:
            trades = self.client.lrange("vortex:trades", 0, limit - 1)
            return [json.loads(t) for t in trades]
        except Exception:
            return []

    # ═══════════════════════════════════════════════════════════
    # 🎯 TICKER CACHE (Reduce API calls)
    # ═══════════════════════════════════════════════════════════
    
    def cache_ticker(self, symbol: str, data: Dict[str, Any], ttl: int = 10):
        """Cache ticker data with short TTL"""
        if not self.client:
            return
        try:
            self.client.setex(f"ticker:{symbol}", ttl, json.dumps(data))
        except Exception as e:
            logger.warning(f"⚠️ REDIS: Failed to cache ticker - {e}")
            pass

    def get_cached_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached ticker if available"""
        if not self.client:
            return None
        try:
            data = self.client.get(f"ticker:{symbol}")
            return json.loads(data) if data else None
        except Exception:
            return None


# Singleton instance
redis_cache = RedisCache()
