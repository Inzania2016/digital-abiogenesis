import json
import shutil
from pathlib import Path

import pytest

import abiogenesis.benchmark.runner as benchmark_runner
import abiogenesis.benchmark.validation as benchmark_validation
from abiogenesis.benchmark.artifacts import atomic_write_json, sha256_file
from abiogenesis.benchmark.catalog import CANONICAL_POLICY_IDS
from abiogenesis.benchmark.models import SuiteDefinition
from abiogenesis.benchmark.runner import main, run_benchmark
from abiogenesis.benchmark.validation import ArtifactValidationError, validate_run


@pytest.fixture(scope="module")
def valid_run(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output_root = tmp_path_factory.mktemp("benchmark-runs")
    return run_benchmark(
        output_root=output_root,
        run_id="20260726T010101Z_stable-default-v1_b0-quick-v1_1001",
        test_smoke=True,
        keep_policies=True,
        command="python -m abiogenesis.benchmark.runner --test-smoke",
    )


def _copy_run(source: Path, tmp_path: Path) -> Path:
    destination = tmp_path / source.name
    shutil.copytree(source, destination)
    return destination


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    atomic_write_json(path, payload)


def _refresh_metrics_hash(run_directory: Path) -> None:
    manifest_path = run_directory / "manifest.json"
    manifest = _read_json(manifest_path)
    manifest["artifacts"]["metrics"]["sha256"] = sha256_file(run_directory / "metrics.json")
    _write_json(manifest_path, manifest)


def test_tiny_integration_run_validates_and_retains_policies(valid_run: Path) -> None:
    validate_run(valid_run)
    manifest = _read_json(valid_run / "manifest.json")
    metrics = _read_json(valid_run / "metrics.json")

    assert manifest["status"] == "partial"
    assert "test-smoke-profile" in {item["code"] for item in manifest["deviations"]}
    assert tuple(record["policy_id"] for record in metrics["policies"]) == CANONICAL_POLICY_IDS
    assert len(manifest["artifacts"]["policies"]) == 4
    assert len(list((valid_run / "policy").glob("*.json"))) == 4
    assert all(record["status"] == "completed" for record in metrics["policies"])


def test_tiny_run_without_policy_retention_has_no_policy_directory(tmp_path: Path) -> None:
    run_directory = run_benchmark(
        output_root=tmp_path,
        run_id="20260726T020202Z_stable-default-v1_b0-quick-v1_1002",
        test_smoke=True,
    )

    assert not (run_directory / "policy").exists()
    assert _read_json(run_directory / "manifest.json")["artifacts"]["policies"] == []
    validate_run(run_directory)


def test_tiny_clean_canonical_harness_writes_completed_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tiny_suite = SuiteDefinition(
        suite_id="b0-quick-v1",
        replicate_roots=(21,),
        training_episodes=2,
        evaluation_episodes=2,
        evidence_label="test-only canonical lifecycle harness",
    )
    monkeypatch.setattr(benchmark_runner, "resolve_suite", lambda _suite_id: tiny_suite)
    monkeypatch.setattr(benchmark_validation, "resolve_suite", lambda _suite_id: tiny_suite)
    monkeypatch.setattr(
        benchmark_runner,
        "source_identity",
        lambda: {
            "kind": "git",
            "repository_url": "https://example.invalid/digital-abiogenesis.git",
            "commit": "0" * 40,
            "dirty": False,
        },
    )

    run_directory = benchmark_runner.run_benchmark(
        output_root=tmp_path,
        run_id="20260726T025252Z_stable-default-v1_b0-quick-v1_1004",
    )
    manifest = _read_json(run_directory / "manifest.json")

    assert manifest["status"] == "completed"
    assert manifest["completed_at"] is not None
    assert manifest["deviations"] == []
    benchmark_validation.validate_run(run_directory)


def test_resource_shift_uses_separate_configs_without_continued_learning(
    tmp_path: Path,
) -> None:
    run_directory = run_benchmark(
        scenario_id="resource-shift-v1",
        output_root=tmp_path,
        policy_ids=("local-q",),
        run_id="20260726T030303Z_resource-shift-v1_b0-quick-v1_1003",
        test_smoke=True,
    )
    manifest = _read_json(run_directory / "manifest.json")
    metrics = _read_json(run_directory / "metrics.json")

    assert manifest["environment"]["training"]["food_count"] == 8
    assert manifest["environment"]["evaluation"]["food_count"] == 4
    assert metrics["policies"][0]["policy_id"] == "local-q"
    assert metrics["policies"][0]["status"] == "completed"
    validate_run(run_directory)


def test_validation_rejects_mismatched_run_id(valid_run: Path, tmp_path: Path) -> None:
    run_directory = _copy_run(valid_run, tmp_path)
    manifest_path = run_directory / "manifest.json"
    manifest = _read_json(manifest_path)
    manifest["run_id"] = "20260726T010101Z_stable-default-v1_b0-quick-v1_dead"
    _write_json(manifest_path, manifest)

    with pytest.raises(ArtifactValidationError, match="does not match directory"):
        validate_run(run_directory)


def test_validation_rejects_missing_required_file(valid_run: Path, tmp_path: Path) -> None:
    run_directory = _copy_run(valid_run, tmp_path)
    (run_directory / "summary.md").unlink()

    with pytest.raises(ArtifactValidationError, match="Missing required file: summary.md"):
        validate_run(run_directory)


def test_validation_rejects_invalid_status(valid_run: Path, tmp_path: Path) -> None:
    run_directory = _copy_run(valid_run, tmp_path)
    manifest_path = run_directory / "manifest.json"
    manifest = _read_json(manifest_path)
    manifest["status"] = "victorious"
    _write_json(manifest_path, manifest)

    with pytest.raises(ArtifactValidationError, match="Invalid manifest status"):
        validate_run(run_directory)


def test_validation_rejects_wrong_seed_order(valid_run: Path, tmp_path: Path) -> None:
    run_directory = _copy_run(valid_run, tmp_path)
    manifest_path = run_directory / "manifest.json"
    manifest = _read_json(manifest_path)
    manifest["seeds"]["replicate_roots"] = [999]
    _write_json(manifest_path, manifest)

    with pytest.raises(ArtifactValidationError, match="replicate order"):
        validate_run(run_directory)


def test_validation_rejects_missing_policy_for_completed_run(
    valid_run: Path, tmp_path: Path
) -> None:
    run_directory = _copy_run(valid_run, tmp_path)
    manifest_path = run_directory / "manifest.json"
    manifest = _read_json(manifest_path)
    manifest["status"] = "completed"
    manifest["completed_at"] = "2026-07-26T01:01:02Z"
    manifest["source"]["dirty"] = False
    manifest["deviations"] = []
    manifest["policies"] = manifest["policies"][:-1]
    _write_json(manifest_path, manifest)

    with pytest.raises(ArtifactValidationError, match="every canonical policy"):
        validate_run(run_directory)


def test_validation_rejects_aggregate_arithmetic_mismatch(valid_run: Path, tmp_path: Path) -> None:
    run_directory = _copy_run(valid_run, tmp_path)
    metrics_path = run_directory / "metrics.json"
    metrics = _read_json(metrics_path)
    metrics["policies"][0]["aggregate"]["average_reward"]["mean"] += 1.0
    _write_json(metrics_path, metrics)
    _refresh_metrics_hash(run_directory)

    with pytest.raises(ArtifactValidationError, match="does not match per-seed values"):
        validate_run(run_directory)


def test_validation_rejects_artifact_hash_mismatch(valid_run: Path, tmp_path: Path) -> None:
    run_directory = _copy_run(valid_run, tmp_path)
    metrics_path = run_directory / "metrics.json"
    metrics_path.write_text(metrics_path.read_text(encoding="utf-8") + " ", encoding="utf-8")

    with pytest.raises(ArtifactValidationError, match="Artifact hash mismatch"):
        validate_run(run_directory)


def test_validation_rejects_completed_run_without_completion_time(
    valid_run: Path, tmp_path: Path
) -> None:
    run_directory = _copy_run(valid_run, tmp_path)
    manifest_path = run_directory / "manifest.json"
    manifest = _read_json(manifest_path)
    manifest["status"] = "completed"
    manifest["completed_at"] = None
    _write_json(manifest_path, manifest)

    with pytest.raises(ArtifactValidationError, match="requires completed_at"):
        validate_run(run_directory)


def test_summary_is_deterministic_and_contains_claim_boundaries(valid_run: Path) -> None:
    first = (valid_run / "summary.md").read_text(encoding="utf-8")
    second = (valid_run / "summary.md").read_text(encoding="utf-8")

    assert first == second
    assert "## Claims Supported" in first
    assert "## Claims Not Supported" in first
    assert "## Failures and Deviations" in first
    assert "conscious" in first


def test_dry_run_creates_no_artifacts(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    exit_code = main(
        [
            "--dry-run",
            "--test-smoke",
            "--output-root",
            str(tmp_path),
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["dry_run"] is True
    assert output["replicate_roots"] == [21]
    assert not list(tmp_path.iterdir())


def test_validate_only_returns_nonzero_for_invalid_run(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    invalid = tmp_path / "missing"

    exit_code = main(["--validate-only", str(invalid)])

    assert exit_code == 1
    assert "does not exist" in capsys.readouterr().err
