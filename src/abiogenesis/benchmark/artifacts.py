"""Safe artifact writing and hashing for benchmark runs."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from abiogenesis.benchmark.models import ScenarioDefinition, SuiteDefinition


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def format_utc(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_run_id(
    scenario: ScenarioDefinition,
    suite: SuiteDefinition,
    *,
    now: datetime | None = None,
    suffix: str | None = None,
) -> str:
    timestamp = (now or utc_now()).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    collision_suffix = suffix or secrets.token_hex(2)
    if len(collision_suffix) != 4 or any(
        character not in "0123456789abcdef" for character in collision_suffix
    ):
        raise ValueError("Run ID suffix must be four lowercase hexadecimal characters.")
    return f"{timestamp}_{scenario.scenario_id}_{suite.suite_id}_{collision_suffix}"


def create_run_directory(output_root: Path, run_id: str) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    run_directory = output_root / run_id
    try:
        run_directory.mkdir()
    except FileExistsError as error:
        raise FileExistsError(f"Run directory already exists: {run_directory}") from error
    return run_directory


def atomic_write_json(path: Path, payload: object) -> None:
    text = json.dumps(payload, indent=2, sort_keys=False, allow_nan=False) + "\n"
    atomic_write_text(path, text)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_declaration(path: Path, *, run_directory: Path, media_type: str) -> dict[str, object]:
    return {
        "path": path.relative_to(run_directory).as_posix(),
        "media_type": media_type,
        "sha256": sha256_file(path),
    }
