"""Immutable configuration for the bounded single-channel Lenia CPU reference."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

CANONICAL_CONFIG_ID = "lenia-single-channel-cpu-v1"
CANONICAL_DTYPE_STRING = "<f4"
SUPPORTED_BOUNDARY = "periodic"
SUPPORTED_CONVOLUTION = "direct-row-major"
SUPPORTED_BETA = (1.0,)


@dataclass(frozen=True)
class LeniaConfig:
    """Complete versioned parameters for RS-02."""

    config_id: str
    kernel_radius: int
    kernel_alpha: int
    kernel_beta: tuple[float, ...]
    growth_mu: float
    growth_sigma: float
    time_scale_T: int
    dt: float
    boundary: str
    dtype: str
    convolution: str

    def __post_init__(self) -> None:
        if self.config_id != CANONICAL_CONFIG_ID:
            raise ValueError(f"unsupported config_id: {self.config_id!r}")
        if type(self.kernel_radius) is not int or self.kernel_radius <= 0:
            raise ValueError("kernel_radius must be a positive integer")
        if type(self.kernel_alpha) is not int or self.kernel_alpha <= 0:
            raise ValueError("kernel_alpha must be a positive integer")
        if tuple(self.kernel_beta) != SUPPORTED_BETA:
            raise ValueError(f"kernel_beta must be exactly {SUPPORTED_BETA}")
        if (
            not isinstance(self.growth_mu, (int, float))
            or isinstance(self.growth_mu, bool)
            or not math.isfinite(self.growth_mu)
            or not 0.0 <= self.growth_mu <= 1.0
        ):
            raise ValueError("growth_mu must be finite and within [0, 1]")
        if (
            not isinstance(self.growth_sigma, (int, float))
            or isinstance(self.growth_sigma, bool)
            or not math.isfinite(self.growth_sigma)
            or self.growth_sigma <= 0.0
        ):
            raise ValueError("growth_sigma must be finite and strictly positive")
        if type(self.time_scale_T) is not int or self.time_scale_T <= 0:
            raise ValueError("time_scale_T must be a positive integer")
        if (
            not isinstance(self.dt, (int, float))
            or isinstance(self.dt, bool)
            or not math.isfinite(self.dt)
            or self.dt <= 0.0
        ):
            raise ValueError("dt must be finite and strictly positive")
        if self.dt != 1.0 / self.time_scale_T:
            raise ValueError("dt must agree exactly with 1 / time_scale_T")
        if self.boundary != SUPPORTED_BOUNDARY:
            raise ValueError(f"boundary must be {SUPPORTED_BOUNDARY!r}")
        if self.dtype != CANONICAL_DTYPE_STRING:
            raise ValueError(f"dtype must be {CANONICAL_DTYPE_STRING!r}")
        if self.convolution != SUPPORTED_CONVOLUTION:
            raise ValueError(f"convolution must be {SUPPORTED_CONVOLUTION!r}")

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "LeniaConfig":
        """Build a config while rejecting missing or unknown contract fields."""

        expected = set(cls.__dataclass_fields__)
        actual = set(payload)
        missing = expected - actual
        unknown = actual - expected
        if missing:
            raise ValueError(f"missing configuration fields: {sorted(missing)}")
        if unknown:
            raise ValueError(f"unknown configuration fields: {sorted(unknown)}")
        values = dict(payload)
        beta = values["kernel_beta"]
        if not isinstance(beta, (list, tuple)):
            raise ValueError("kernel_beta must be an array")
        values["kernel_beta"] = tuple(beta)
        try:
            return cls(**values)
        except TypeError as error:
            raise ValueError(f"invalid configuration values: {error}") from error

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["kernel_beta"] = list(self.kernel_beta)
        return payload

    def to_json(self) -> str:
        """Return canonical deterministic JSON with one terminal newline."""

        return (
            json.dumps(
                self.as_dict(),
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n"
        )


def load_config(path: str | Path) -> LeniaConfig:
    """Load and validate one JSON configuration."""

    config_path = Path(path)
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load Lenia configuration {config_path}: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError("Lenia configuration must contain a JSON object")
    return LeniaConfig.from_mapping(payload)
