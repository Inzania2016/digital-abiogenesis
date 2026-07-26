"""Artifact primitives for the provisional NEAT research contract."""

from __future__ import annotations

import os
import secrets
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from abiogenesis.benchmark.artifacts import (
    artifact_declaration,
    atomic_write_json,
    atomic_write_text,
    create_run_directory,
    format_utc,
    sha256_file,
    utc_now,
)

ARTIFACT_TYPE = "neuroevolution-research"
ARTIFACT_CONTRACT = "neat-research-0.1"
RUN_PREFIX = "neat-feedforward-experimental"


def generate_run_id(
    *,
    now: datetime | None = None,
    suffix: str | None = None,
) -> str:
    """Generate a UTC-based collision-resistant experimental run identifier."""

    timestamp = (now or utc_now()).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    collision_suffix = suffix or secrets.token_hex(2)
    if len(collision_suffix) != 4 or any(
        character not in "0123456789abcdef" for character in collision_suffix
    ):
        raise ValueError("Run ID suffix must be four lowercase hexadecimal characters.")
    return f"{timestamp}_{RUN_PREFIX}_{collision_suffix}"


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    """Atomically persist a binary artifact without exposing a partial file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


__all__ = [
    "ARTIFACT_CONTRACT",
    "ARTIFACT_TYPE",
    "artifact_declaration",
    "atomic_write_bytes",
    "atomic_write_json",
    "atomic_write_text",
    "create_run_directory",
    "format_utc",
    "generate_run_id",
    "sha256_file",
    "utc_now",
]
