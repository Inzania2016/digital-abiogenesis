"""Auditable direct periodic Lenia update and headless command-line interface."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np

from abiogenesis.lenia.config import CANONICAL_DTYPE_STRING, LeniaConfig, load_config
from abiogenesis.lenia.kernel import build_kernel

CANONICAL_DTYPE = np.dtype(CANONICAL_DTYPE_STRING)


def validate_field(field: np.ndarray) -> None:
    """Validate the canonical finite two-dimensional state contract."""

    if not isinstance(field, np.ndarray) or field.ndim != 2:
        raise ValueError("Lenia field must be a two-dimensional NumPy array")
    if field.dtype != CANONICAL_DTYPE:
        raise ValueError(f"Lenia field dtype must be {CANONICAL_DTYPE_STRING}")
    if not field.flags.c_contiguous:
        raise ValueError("Lenia field must be C-contiguous")
    if not np.all(np.isfinite(field)):
        raise ValueError("Lenia field values must be finite")
    if np.any(field < 0.0) or np.any(field > 1.0):
        raise ValueError("Lenia field values must be within [0, 1]")


def direct_periodic_convolution(field: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Convolve in deterministic row-major offset order with a float32 accumulator."""

    validate_field(field)
    if (
        not isinstance(kernel, np.ndarray)
        or kernel.ndim != 2
        or kernel.shape[0] != kernel.shape[1]
        or kernel.shape[0] % 2 != 1
    ):
        raise ValueError("kernel must be an odd square two-dimensional array")
    if kernel.dtype != CANONICAL_DTYPE or not kernel.flags.c_contiguous:
        raise ValueError(f"kernel must be C-contiguous {CANONICAL_DTYPE_STRING}")
    if not np.all(np.isfinite(kernel)) or np.any(kernel < 0.0):
        raise ValueError("kernel must be finite and nonnegative")
    if abs(float(np.sum(kernel, dtype=np.float64)) - 1.0) > 1e-6:
        raise ValueError("kernel must have a normalized discrete sum")

    center = kernel.shape[0] // 2
    accumulator = np.zeros_like(field, dtype=CANONICAL_DTYPE, order="C")
    for row_index in range(kernel.shape[0]):
        for column_index in range(kernel.shape[1]):
            weight = kernel[row_index, column_index]
            if weight == 0.0:
                continue
            row_offset = row_index - center
            column_offset = column_index - center
            rolled = np.roll(
                field,
                shift=(-row_offset, -column_offset),
                axis=(0, 1),
            )
            np.add(accumulator, weight * rolled, out=accumulator)
    return accumulator


def growth_mapping(potential: np.ndarray, *, mu: float, sigma: float) -> np.ndarray:
    """Apply the paper's exponential growth map as canonical float32 arithmetic."""

    if not isinstance(potential, np.ndarray) or potential.ndim != 2:
        raise ValueError("potential must be a two-dimensional NumPy array")
    if potential.dtype != CANONICAL_DTYPE or not potential.flags.c_contiguous:
        raise ValueError(f"potential must be C-contiguous {CANONICAL_DTYPE_STRING}")
    if not np.all(np.isfinite(potential)):
        raise ValueError("potential must be finite")
    if isinstance(mu, (bool, np.bool_)):
        raise ValueError("mu must be finite and within [0, 1]")
    if isinstance(sigma, (bool, np.bool_)):
        raise ValueError("sigma must be finite and strictly positive")
    try:
        mu_value = float(mu)
        sigma_value = float(sigma)
    except (TypeError, ValueError) as error:
        raise ValueError("mu and sigma must be numeric scalars") from error
    if not np.isfinite(mu_value) or not 0.0 <= mu_value <= 1.0:
        raise ValueError("mu must be finite and within [0, 1]")
    if not np.isfinite(sigma_value) or sigma_value <= 0.0:
        raise ValueError("sigma must be finite and strictly positive")

    mu32 = np.float32(mu_value)
    sigma32 = np.float32(sigma_value)
    exponent = -((potential - mu32) ** 2) / (np.float32(2.0) * sigma32**2)
    growth = np.float32(2.0) * np.exp(exponent) - np.float32(1.0)
    if not np.all(np.isfinite(growth)):
        raise ValueError("growth output must be finite")
    return np.ascontiguousarray(growth, dtype=CANONICAL_DTYPE)


def step(field: np.ndarray, *, kernel: np.ndarray, config: LeniaConfig) -> np.ndarray:
    """Return one clipped synchronous update from the unchanged current field."""

    validate_field(field)
    expected_kernel_shape = (2 * config.kernel_radius + 1,) * 2
    if kernel.shape != expected_kernel_shape:
        raise ValueError(
            f"kernel shape {kernel.shape} does not match config radius "
            f"{config.kernel_radius}: expected {expected_kernel_shape}"
        )
    potential = direct_periodic_convolution(field, kernel)
    growth = growth_mapping(
        potential,
        mu=config.growth_mu,
        sigma=config.growth_sigma,
    )
    updated = field + np.float32(config.dt) * growth
    clipped = np.clip(updated, np.float32(0.0), np.float32(1.0))
    result = np.ascontiguousarray(clipped, dtype=CANONICAL_DTYPE)
    validate_field(result)
    return result


def step_many(
    field: np.ndarray,
    *,
    kernel: np.ndarray,
    config: LeniaConfig,
    steps: int,
) -> np.ndarray:
    """Execute a fixed positive number of synchronous steps."""

    if type(steps) is not int or steps < 0:
        raise ValueError("steps must be a non-negative integer")
    validate_field(field)
    current = field.copy(order="C")
    for _ in range(steps):
        current = step(current, kernel=kernel, config=config)
    return current


def load_field(path: str | Path) -> np.ndarray:
    """Load a canonical field with pickle explicitly disabled."""

    field = np.load(Path(path), allow_pickle=False)
    validate_field(field)
    return field


def save_field(path: str | Path, field: np.ndarray) -> None:
    """Save one canonical field as deterministic NumPy ``.npy`` data."""

    validate_field(field)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, field, allow_pickle=False)


def _runtime_summary(config: LeniaConfig, field: np.ndarray) -> dict[str, object]:
    from abiogenesis.lenia.metrics import field_mass, toroidal_centroid

    return {
        "config_id": config.config_id,
        "shape": list(field.shape),
        "dtype": field.dtype.str,
        "mass": field_mass(field),
        "toroidal_centroid": toroidal_centroid(field),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "operating_system": platform.system(),
        "architecture": platform.machine(),
    }


def _benchmark(
    *,
    config: LeniaConfig,
    sizes: list[int],
    warmup: int,
    steps: int,
) -> dict[str, object]:
    from abiogenesis.lenia.fixtures import analytic_field

    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if steps < 1:
        raise ValueError("benchmark steps must be at least 1")
    kernel = build_kernel(config)
    results = []
    for size in sizes:
        field = analytic_field(size)
        current = step_many(field, kernel=kernel, config=config, steps=warmup)
        started = time.perf_counter()
        step_many(current, kernel=kernel, config=config, steps=steps)
        elapsed = time.perf_counter() - started
        results.append(
            {
                "size": size,
                "shape": [size, size],
                "warmup_steps": warmup,
                "measured_steps": steps,
                "total_seconds": elapsed,
                "seconds_per_step": elapsed / steps,
            }
        )
    return {
        "mode": "serial-wall-clock-benchmark",
        "config_id": config.config_id,
        "dtype": CANONICAL_DTYPE_STRING,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "operating_system": platform.system(),
        "architecture": platform.machine(),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--steps", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--sizes", type=int, nargs="+", default=[32, 64])
    parser.add_argument("--warmup", type=int, default=5)
    args = parser.parse_args()
    config = load_config(args.config)

    if args.benchmark:
        if args.input is not None or args.output is not None:
            parser.error("--benchmark cannot be combined with --input or --output")
        summary = _benchmark(
            config=config,
            sizes=args.sizes,
            warmup=args.warmup,
            steps=args.steps,
        )
    else:
        if args.input is None:
            parser.error("--input is required unless --benchmark is used")
        field = load_field(args.input)
        result = step_many(
            field,
            kernel=build_kernel(config),
            config=config,
            steps=args.steps,
        )
        if args.output is not None:
            save_field(args.output, result)
        summary = {
            "mode": "fixed-step-run",
            "input": str(args.input),
            "output": None if args.output is None else str(args.output),
            "steps": args.steps,
            **_runtime_summary(config, result),
        }
    print(json.dumps(summary, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
