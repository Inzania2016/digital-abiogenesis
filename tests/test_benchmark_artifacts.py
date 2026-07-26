import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from abiogenesis.benchmark.artifacts import (
    atomic_write_json,
    create_run_directory,
    generate_run_id,
)
from abiogenesis.benchmark.catalog import resolve_policies, resolve_scenario, resolve_suite
from abiogenesis.benchmark.runner import _base_manifest


def test_atomic_json_write_is_parseable(tmp_path: Path) -> None:
    path = tmp_path / "artifact.json"

    atomic_write_json(path, {"b": [1, 2], "a": "microbe"})

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "b": [1, 2],
        "a": "microbe",
    }
    assert not list(tmp_path.glob("*.tmp"))


def test_run_directory_rejects_collision(tmp_path: Path) -> None:
    run_id = generate_run_id(
        resolve_scenario("stable-default-v1"),
        resolve_suite("b0-quick-v1"),
        now=datetime(2026, 7, 26, tzinfo=UTC),
        suffix="0001",
    )
    created = create_run_directory(tmp_path, run_id)

    assert created.is_dir()
    with pytest.raises(FileExistsError, match="already exists"):
        create_run_directory(tmp_path, run_id)


def test_base_manifest_starts_running_without_terminal_hashes() -> None:
    scenario = resolve_scenario("stable-default-v1")
    suite = resolve_suite("b0-quick-v1")

    manifest = _base_manifest(
        run_id="20260726T000000Z_stable-default-v1_b0-quick-v1_0001",
        scenario=scenario,
        suite=suite,
        policies=resolve_policies(),
        source={
            "kind": "git",
            "repository_url": "https://example.invalid/repo",
            "commit": "0" * 40,
            "dirty": False,
        },
        command="python -m abiogenesis.benchmark.runner",
        started_at="2026-07-26T00:00:00Z",
        deviations=(),
        keep_policies=False,
    )

    assert manifest["status"] == "running"
    assert manifest["completed_at"] is None
    assert manifest["artifacts"]["metrics"]["sha256"] is None
    assert manifest["artifacts"]["summary"]["sha256"] is None
    assert manifest["artifacts"]["policies"] == []
