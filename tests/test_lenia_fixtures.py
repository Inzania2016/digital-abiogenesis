import json
from pathlib import Path

import numpy as np

from abiogenesis.lenia.config import load_config
from abiogenesis.lenia.fixtures import (
    FIXTURE_CONTRACT,
    check_fixtures,
    generate_fixture_payloads,
    sha256_file,
)

CONFIG = load_config(Path("configs/lenia/lenia-single-channel-cpu-v1.json"))
FIXTURE_DIRECTORY = Path("tests/fixtures/lenia")


def test_fixture_manifest_inventory_hashes_and_array_contracts() -> None:
    manifest = json.loads((FIXTURE_DIRECTORY / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["fixture_contract"] == FIXTURE_CONTRACT
    assert manifest["config_id"] == CONFIG.config_id
    assert manifest["boundary"] == "periodic"
    assert manifest["dtype"] == "<f4"
    assert manifest["convolution"] == "direct-row-major"
    assert len(manifest["files"]) == 4
    for declaration in manifest["files"]:
        path = FIXTURE_DIRECTORY / declaration["path"]
        field = np.load(path, allow_pickle=False)
        assert path.is_file()
        assert sha256_file(path) == declaration["sha256"]
        assert list(field.shape) == declaration["shape"]
        assert field.dtype.str == declaration["dtype"] == "<f4"
        assert field.flags.c_contiguous
        assert np.all(np.isfinite(field))
        assert np.all((field >= 0.0) & (field <= 1.0))


def test_fixture_generation_is_bitwise_reproducible() -> None:
    generated_once = generate_fixture_payloads(CONFIG)
    generated_twice = generate_fixture_payloads(CONFIG)

    for filename, first in generated_once.items():
        committed = np.load(FIXTURE_DIRECTORY / filename, allow_pickle=False)
        assert np.array_equal(first, generated_twice[filename])
        assert np.array_equal(first, committed)
        assert np.allclose(first, committed, rtol=0.0, atol=1e-6)


def test_committed_fixture_files_and_manifest_are_byte_identical_on_regeneration() -> None:
    check_fixtures(FIXTURE_DIRECTORY, CONFIG)
