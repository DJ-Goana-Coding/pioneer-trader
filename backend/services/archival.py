"""
Archival & Logging Service - V19 Shadow Archive
Auto-sync to GitHub Pages and persistent storage
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from backend.core.config import settings
from backend.core.logging_config import setup_logging

logger = setup_logging("archival")

class ArchivalService:
    """Manages trade logs and archival to GitHub Pages and Shadow Archive"""
    
    def __init__(self):
        self.shadow_archive_path = Path(getattr(settings, 'SHADOW_ARCHIVE_PATH', '/tmp/shadow_archive'))
        self.trade_logs: List[Dict] = []
        self.session_start = datetime.now()
        
        # Ensure archive directory exists
        if not self.shadow_archive_path.exists():
            self.shadow_archive_path.mkdir(parents=True, exist_ok=True)
    
    def log_trade(self, trade_data: Dict):
        """Log a trade to memory and archive"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_time": (datetime.now() - self.session_start).total_seconds(),
            **trade_data
        }
        
        self.trade_logs.append(log_entry)
        self._archive_to_shadow(log_entry)
        
        return log_entry
    
    def _archive_to_shadow(self, log_entry: Dict):
        """Archive log entry to shadow storage"""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = self.shadow_archive_path / f"trades_{date_str}.jsonl"
            
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            logger.warning(f"Failed to archive to shadow: {e}")
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent trade logs"""
        return self.trade_logs[-limit:]
    
    def get_session_stats(self) -> Dict:
        """Get statistics for current session"""
        if not self.trade_logs:
            return {
                "session_duration": (datetime.now() - self.session_start).total_seconds(),
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0
            }
        
        wins = sum(1 for log in self.trade_logs if log.get("status") == "WIN")
        losses = sum(1 for log in self.trade_logs if log.get("status") == "LOSS")
        
        return {
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "session_start": self.session_start.isoformat(),
            "total_trades": len(self.trade_logs),
            "wins": wins,
            "losses": losses,
            "win_rate": (wins / len(self.trade_logs) * 100) if self.trade_logs else 0.0
        }
    
    def export_for_github_pages(self) -> Dict:
        """Export trade logs in format suitable for GitHub Pages"""
        if not getattr(settings, 'ENABLE_GITHUB_PAGES_EXPORT', False):
            return {"error": "GitHub Pages export not enabled"}
        
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "session_stats": self.get_session_stats(),
            "recent_trades": self.get_recent_logs(50),
            "version": "V19",
            "node": "Node 08 - Pioneer Trader"
        }
        
        try:
            export_file = self.shadow_archive_path / "github_pages_export.json"
            with open(export_file, "w") as f:
                json.dump(export_data, f, indent=2)
            
            return {
                "status": "success",
                "file": str(export_file),
                "trades_exported": len(export_data["recent_trades"])
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_archive_stats(self) -> Dict:
        """Get archive statistics"""
        try:
            files = list(self.shadow_archive_path.glob("trades_*.jsonl"))
            total_size = sum(f.stat().st_size for f in files)
            
            return {
                "archive_path": str(self.shadow_archive_path),
                "log_files": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "oldest_log": min((f.stat().st_mtime for f in files), default=0) if files else 0,
                "newest_log": max((f.stat().st_mtime for f in files), default=0) if files else 0
            }
        except Exception as e:
            return {"error": str(e)}

# Global archival service instance
archival_service = ArchivalService()
