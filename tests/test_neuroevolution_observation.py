import numpy as np
import pytest

from abiogenesis.envs import Action
from abiogenesis.neuroevolution.observation import FEATURE_NAMES, ObservationAdapter


def observation_at(position: tuple[int, int] = (2, 2)) -> dict[str, np.ndarray]:
    food = np.zeros((5, 5), dtype=np.int8)
    poison = np.zeros((5, 5), dtype=np.int8)
    food[1, 2] = 1
    poison[2, 3] = 1
    return {
        "organism": np.array(position, dtype=np.int64),
        "food": food,
        "poison": poison,
        "energy": np.array([20], dtype=np.int32),
        "steps": np.array([0], dtype=np.int32),
    }


def test_feature_order_and_known_normalized_values() -> None:
    adapter = ObservationAdapter()
    observation = observation_at()
    adapter.reset(observation)

    assert FEATURE_NAMES == (
        "north_tile",
        "south_tile",
        "east_tile",
        "west_tile",
        "north_conflict_scent",
        "south_conflict_scent",
        "east_conflict_scent",
        "west_conflict_scent",
        "energy_bucket",
        "north_novelty",
        "south_novelty",
        "east_novelty",
        "west_novelty",
    )
    assert adapter.vector(observation) == (
        1 / 3,
        0.0,
        2 / 3,
        0.0,
        1 / 4,
        0.0,
        1.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    )


def test_conversion_is_fixed_length_deterministic_and_ignores_extra_fields() -> None:
    adapter = ObservationAdapter()
    observation = observation_at()
    observation["not_an_environment_sensor"] = np.array([999])
    adapter.reset(observation)

    first = adapter.vector(observation)
    second = adapter.vector(observation)

    assert len(first) == 13
    assert first == second


def test_adapter_requires_reset_and_tracks_existing_encoder_memory() -> None:
    adapter = ObservationAdapter()
    observation = observation_at()
    with pytest.raises(RuntimeError, match="reset"):
        adapter.vector(observation)

    adapter.reset(observation)
    moved = observation_at((2, 1))
    adapter.update(action=Action.NORTH, observation=moved)

    assert adapter.vector(moved)[10] == 0.5
