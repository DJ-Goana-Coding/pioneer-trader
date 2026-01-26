# ================================================================
# 🛡️ SECURITY ROUTER - V19 Security & Archival API
# ================================================================
# API endpoints for Red Flag Scanner and Shadow Archive
# Provides malware protection and trade logging capabilities
# ================================================================

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, List
from pydantic import BaseModel

from backend.services.malware_protection import scanner
from backend.services.archival import archival_service

router = APIRouter(prefix="/security", tags=["security"])


# ═══════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════

class ScanCodeRequest(BaseModel):
    """Request to scan code for malicious patterns"""
    code: str
    source: str = "api"


class ScanDataRequest(BaseModel):
    """Request to scan data for malicious content"""
    data: Dict
    source: str = "api"


class TradeLogRequest(BaseModel):
    """Request to log a trade"""
    symbol: str
    action: str
    price: float
    quantity: float
    status: Optional[str] = None
    metadata: Optional[Dict] = None


# ═══════════════════════════════════════════════════════════
# SECURITY ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/status")
async def get_security_status():
    """Get malware scanner status
    
    Returns:
        Scanner status including scan count and threats detected
    """
    return scanner.get_status()


@router.post("/scan")
async def scan_content(request: ScanCodeRequest):
    """Scan provided code or content for malicious patterns
    
    Args:
        request: ScanCodeRequest with code to scan
        
    Returns:
        Scan results with any threats detected
    """
    result = scanner.scan_code(request.code, request.source)
    
    if result["status"] == "threat_detected":
        # Return 200 but with threat information
        return {
            **result,
            "warning": "Malicious patterns detected and isolated"
        }
    
    return result


@router.post("/scan-data")
async def scan_data(request: ScanDataRequest):
    """Scan API request data for malicious content
    
    Args:
        request: ScanDataRequest with data to scan
        
    Returns:
        Scan results with any threats detected
    """
    result = scanner.scan_request_data(request.data, request.source)
    
    if result["status"] == "threat_detected":
        return {
            **result,
            "warning": "Malicious patterns detected and isolated"
        }
    
    return result


@router.get("/isolated")
async def get_isolated_threats(limit: int = 10):
    """Get list of isolated threats
    
    Args:
        limit: Maximum number of items to return (default: 10)
        
    Returns:
        List of isolated threats
    """
    return {
        "items": scanner.get_isolated_items(limit),
        "total_isolated": len(scanner.isolated_items)
    }


@router.delete("/isolated")
async def clear_isolated_threats():
    """Clear all isolated threats (admin function)
    
    Returns:
        Number of items cleared
    """
    return scanner.clear_isolated()


# ═══════════════════════════════════════════════════════════
# ARCHIVAL ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/archival/stats")
async def get_archive_stats():
    """Get archive statistics
    
    Returns:
        Archive statistics including file count and size
    """
    return archival_service.get_archive_stats()


@router.get("/archival/logs")
async def get_trade_logs(limit: int = 100):
    """Get recent trade logs
    
    Args:
        limit: Maximum number of logs to return (default: 100)
        
    Returns:
        List of recent trade logs
    """
    logs = archival_service.get_recent_logs(limit)
    return {
        "logs": logs,
        "count": len(logs)
    }


@router.get("/archival/session")
async def get_session_stats():
    """Get session statistics
    
    Returns:
        Session statistics including wins, losses, and win rate
    """
    return archival_service.get_session_stats()


@router.post("/archival/log-trade")
async def log_trade(request: TradeLogRequest):
    """Log a trade to the archive
    
    Args:
        request: TradeLogRequest with trade details
        
    Returns:
        Logged trade entry
    """
    trade_data = {
        "symbol": request.symbol,
        "action": request.action,
        "price": request.price,
        "quantity": request.quantity,
        "status": request.status,
        "metadata": request.metadata or {}
    }
    
    log_entry = archival_service.log_trade(trade_data)
    return {
        "success": True,
        "log_entry": log_entry
    }


@router.post("/archival/export-github-pages")
async def export_to_github_pages():
    """Export trade logs for GitHub Pages
    
    Returns:
        Export status and file location
    """
    result = archival_service.export_for_github_pages()
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
