"""Yield Engine — Geospatial remote-area yield scaffolding.

This module intentionally does NOT hardcode any ATO tax offsets.
Coefficients are loaded from a configuration file (default:
``config/ato_coefficients.json``) so that compliance-reviewed values can
be supplied without code changes.

Returned values are structural only until coefficients are populated;
when any required coefficient is ``None`` the engine reports
``status = "PENDING_COEFFICIENTS"`` and does not fabricate a number.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = os.path.join("config", "ato_coefficients.json")


class YieldResult(BaseModel):
    postcode: str
    zone: Optional[str] = None
    status: str
    yield_value: Optional[float] = None
    inputs: Dict[str, Any] = {}
    notes: Optional[str] = None


class YieldEngineError(RuntimeError):
    """Raised for unrecoverable engine configuration failures."""


class YieldEngine:
    """Geospatial yield calculator driven by external coefficients."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config_path = config_path or os.environ.get(
            "ATO_COEFFICIENTS_PATH", DEFAULT_CONFIG_PATH
        )
        self._coefficients: Dict[str, Any] = {}
        self.reload()

    # ------------------------------------------------------------------ #
    # Config management
    # ------------------------------------------------------------------ #
    def reload(self) -> None:
        """Load coefficients from disk. Missing file is non-fatal."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as fh:
                self._coefficients = json.load(fh)
        except FileNotFoundError:
            logger.warning(
                "ATO coefficients file not found at %s; engine will "
                "report PENDING_COEFFICIENTS.",
                self.config_path,
            )
            self._coefficients = {}
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to load coefficients: %s", exc)
            self._coefficients = {}

    def _zone_for(self, postcode: str) -> Dict[str, Any]:
        zones = self._coefficients.get("zones", {}) or {}
        defaults = self._coefficients.get("defaults", {}) or {}
        zone = zones.get(str(postcode))
        if zone is None:
            return {**defaults, "zone": None, "description": None}
        return {**defaults, **zone}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def calculate_remote_area_yield(
        self,
        postcode: str,
        latency_ms: float = 0.0,
    ) -> YieldResult:
        """Compute the Remote Area Yield for a postcode.

        The formula is deliberately simple and driven entirely by config:
            yield_value = base_offset - (latency_weight * latency_ms)

        If either coefficient is missing the engine refuses to fabricate
        a result.
        """
        if postcode is None or str(postcode).strip() == "":
            raise ValueError("postcode is required")

        try:
            latency_ms = float(latency_ms)
        except (TypeError, ValueError) as exc:
            raise ValueError("latency_ms must be numeric") from exc

        zone = self._zone_for(postcode)
        base_offset = zone.get("base_offset")
        latency_weight = zone.get("latency_weight")

        inputs = {
            "postcode": str(postcode),
            "latency_ms": latency_ms,
            "base_offset": base_offset,
            "latency_weight": latency_weight,
        }

        if base_offset is None or latency_weight is None:
            return YieldResult(
                postcode=str(postcode),
                zone=zone.get("zone"),
                status="PENDING_COEFFICIENTS",
                yield_value=None,
                inputs=inputs,
                notes=(
                    "ATO coefficients not yet populated. "
                    "Populate config/ato_coefficients.json to enable."
                ),
            )

        try:
            value = float(base_offset) - float(latency_weight) * latency_ms
        except (TypeError, ValueError) as exc:
            raise YieldEngineError(
                f"Invalid coefficient types for postcode {postcode}: {exc}"
            ) from exc

        return YieldResult(
            postcode=str(postcode),
            zone=zone.get("zone"),
            status="OK",
            yield_value=value,
            inputs=inputs,
        )


__all__ = ["YieldEngine", "YieldResult", "YieldEngineError"]
