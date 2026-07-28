"""Deterministic analytic fixture recipes and manifest helpers."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np

from abiogenesis.lenia.config import CANONICAL_DTYPE_STRING, LeniaConfig
from abiogenesis.lenia.kernel import build_kernel
from abiogenesis.lenia.reference import save_field, step_many, validate_field

CANONICAL_DTYPE = np.dtype(CANONICAL_DTYPE_STRING)
FIXTURE_CONTRACT = "lenia-cpu-fixtures-1.0"
FIXTURE_FILES = (
    ("field_32_initial.npy", "initial", "analytic-gaussian-pair-v1", 32, 0),
    ("field_32_step1.npy", "expected-output", "analytic-gaussian-pair-v1", 32, 1),
    ("field_64_initial.npy", "initial", "analytic-annulus-lobe-v1", 64, 0),
    ("field_64_step10.npy", "expected-output", "analytic-annulus-lobe-v1", 64, 10),
)


def analytic_field(size: int) -> np.ndarray:
    """Create one of the two project-authored canonical fixture fields."""

    coordinates = np.arange(size, dtype=np.float64)
    rows, columns = np.meshgrid(coordinates, coordinates, indexing="ij")
    if size == 32:
        primary = 0.78 * np.exp(-((columns - 15.5) ** 2 + (rows - 15.5) ** 2) / (2.0 * 3.2**2))
        offset = 0.32 * np.exp(-((columns - 21.0) ** 2 + (rows - 11.0) ** 2) / (2.0 * 1.8**2))
        field = primary + offset
    elif size == 64:
        distance = np.sqrt((columns - 31.5) ** 2 + (rows - 31.5) ** 2)
        annulus = 0.68 * np.exp(-((distance - 11.0) ** 2) / (2.0 * 2.2**2))
        lobe = 0.24 * np.exp(-((columns - 43.0) ** 2 + (rows - 27.0) ** 2) / (2.0 * 3.0**2))
        field = annulus + lobe
    else:
        raise ValueError("analytic fixtures are defined only for sizes 32 and 64")
    result = np.asarray(np.clip(field, 0.0, 1.0), dtype=CANONICAL_DTYPE, order="C")
    validate_field(result)
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_fixture_payloads(config: LeniaConfig) -> dict[str, np.ndarray]:
    """Generate all canonical fields in memory."""

    kernel = build_kernel(config)
    field_32 = analytic_field(32)
    field_64 = analytic_field(64)
    return {
        "field_32_initial.npy": field_32,
        "field_32_step1.npy": step_many(
            field_32,
            kernel=kernel,
            config=config,
            steps=1,
        ),
        "field_64_initial.npy": field_64,
        "field_64_step10.npy": step_many(
            field_64,
            kernel=kernel,
            config=config,
            steps=10,
        ),
    }


def write_fixtures(directory: Path, config: LeniaConfig) -> dict[str, object]:
    """Write fields and a deterministic manifest, returning the manifest."""

    directory.mkdir(parents=True, exist_ok=True)
    payloads = generate_fixture_payloads(config)
    entries = []
    metadata = {
        filename: (role, recipe, size, steps)
        for filename, role, recipe, size, steps in FIXTURE_FILES
    }
    for filename, field in payloads.items():
        path = directory / filename
        save_field(path, field)
        role, recipe, size, steps = metadata[filename]
        entries.append(
            {
                "path": filename,
                "role": role,
                "recipe_id": recipe,
                "step_count": steps,
                "shape": [size, size],
                "dtype": field.dtype.str,
                "sha256": sha256_file(path),
            }
        )
    manifest = {
        "fixture_contract": FIXTURE_CONTRACT,
        "config_id": config.config_id,
        "boundary": config.boundary,
        "dtype": config.dtype,
        "convolution": config.convolution,
        "files": entries,
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def check_fixtures(directory: Path, config: LeniaConfig) -> None:
    """Regenerate elsewhere and require byte-identical committed fixtures and manifest."""

    with tempfile.TemporaryDirectory(prefix="abiogenesis-lenia-fixtures-") as temporary:
        generated = Path(temporary)
        write_fixtures(generated, config)
        expected_names = {"manifest.json", *(item[0] for item in FIXTURE_FILES)}
        actual_names = {path.name for path in directory.iterdir() if path.is_file()}
        if actual_names != expected_names:
            raise ValueError(
                f"fixture inventory mismatch: expected {sorted(expected_names)}, "
                f"found {sorted(actual_names)}"
            )
        for name in sorted(expected_names):
            if (generated / name).read_bytes() != (directory / name).read_bytes():
                raise ValueError(f"fixture drift detected: {name}")
