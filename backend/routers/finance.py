"""Finance router — links ISO 20022 parser and Yield Engine.

The endpoint is intentionally a scaffolded node: it wires the parser
and engine together behind the existing JWT guard. Finance logic
verification is deferred to a later sweep.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.core.iso20022_parser import (
    ISO20022ParseError,
    ISO20022Parser,
)
from backend.core.security import get_current_admin
from backend.core.yield_engine import YieldEngine, YieldEngineError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/finance", tags=["finance"])

# Singletons — cheap to construct, safe to share across requests.
_parser = ISO20022Parser()
_engine = YieldEngine()


class AnalyzeRequest(BaseModel):
    payload: Any = Field(
        ...,
        description="ISO 20022 payload (dict, JSON string, or XML string).",
    )
    postcode: str = Field(
        default="4874",
        description="Operational-zone postcode for the yield calculation.",
    )
    latency_ms: float = Field(
        default=0.0,
        description="Observed latency for the operational zone, in ms.",
    )


class AnalyzeResponse(BaseModel):
    parsed: dict
    yield_result: dict
    warnings: Optional[list] = None


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    req: AnalyzeRequest,
    _admin: str = Depends(get_current_admin),
) -> AnalyzeResponse:
    """Parse an ISO 20022 payload and return the computed remote-area yield."""
    warnings: list = []

    try:
        message = _parser.parse(req.payload)
    except ISO20022ParseError as exc:
        raise HTTPException(status_code=400, detail=f"Parse error: {exc}")
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected parser failure")
        raise HTTPException(status_code=500, detail="Parser failure") from exc

    # Validation is a stub today; surface that honestly.
    try:
        _parser.validate(message)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Validator raised: %s", exc)
        warnings.append(f"validator_warning: {exc}")

    try:
        result = _engine.calculate_remote_area_yield(
            postcode=req.postcode,
            latency_ms=req.latency_ms,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except YieldEngineError as exc:
        logger.error("Yield engine error: %s", exc)
        raise HTTPException(status_code=500, detail="Yield engine error")
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected yield engine failure")
        raise HTTPException(status_code=500, detail="Yield engine failure") from exc

    if result.status == "PENDING_COEFFICIENTS":
        warnings.append(
            "ATO coefficients not populated; yield_value is None by design."
        )

    return AnalyzeResponse(
        parsed=message.model_dump(),
        yield_result=result.model_dump(),
        warnings=warnings or None,
    )
