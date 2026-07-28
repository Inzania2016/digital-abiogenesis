import json
from dataclasses import replace
from pathlib import Path

import pytest

from abiogenesis.lenia.config import LeniaConfig, load_config

CONFIG_PATH = Path("configs/lenia/lenia-single-channel-cpu-v1.json")


def test_canonical_config_loads_and_round_trips_deterministically() -> None:
    config = load_config(CONFIG_PATH)

    assert config == LeniaConfig(
        config_id="lenia-single-channel-cpu-v1",
        kernel_radius=5,
        kernel_alpha=4,
        kernel_beta=(1.0,),
        growth_mu=0.15,
        growth_sigma=0.015,
        time_scale_T=10,
        dt=0.1,
        boundary="periodic",
        dtype="<f4",
        convolution="direct-row-major",
    )
    assert config.to_json() == CONFIG_PATH.read_text(encoding="utf-8")
    assert json.loads(config.to_json()) == config.as_dict()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("kernel_radius", 0, "kernel_radius"),
        ("kernel_radius", 1.5, "kernel_radius"),
        ("kernel_alpha", 0, "kernel_alpha"),
        ("kernel_beta", (0.5,), "kernel_beta"),
        ("kernel_beta", (1.0, 1.0), "kernel_beta"),
        ("growth_mu", float("nan"), "growth_mu"),
        ("growth_mu", 1.1, "growth_mu"),
        ("growth_sigma", 0.0, "growth_sigma"),
        ("growth_sigma", float("inf"), "growth_sigma"),
        ("time_scale_T", 0, "time_scale_T"),
        ("dt", 0.2, "agree"),
        ("boundary", "reflect", "boundary"),
        ("dtype", ">f4", "dtype"),
        ("dtype", "<f8", "dtype"),
        ("convolution", "fft", "convolution"),
    ],
)
def test_invalid_configuration_values_fail(field: str, value, message: str) -> None:
    config = load_config(CONFIG_PATH)

    with pytest.raises(ValueError, match=message):
        replace(config, **{field: value})


def test_missing_and_unknown_configuration_fields_fail() -> None:
    payload = load_config(CONFIG_PATH).as_dict()
    del payload["boundary"]
    with pytest.raises(ValueError, match="missing"):
        LeniaConfig.from_mapping(payload)

    payload = load_config(CONFIG_PATH).as_dict()
    payload["backend"] = "surprise"
    with pytest.raises(ValueError, match="unknown"):
        LeniaConfig.from_mapping(payload)
