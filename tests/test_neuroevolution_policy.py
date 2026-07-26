import math

import pytest

from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import BacteriaWorldEnv
from abiogenesis.neuroevolution.policy import NeatPolicy


class FixedNetwork:
    def __init__(self, outputs) -> None:
        self.outputs = outputs

    def activate(self, inputs):
        assert len(inputs) == 13
        return self.outputs


def initial_observation():
    env = BacteriaWorldEnv(BacteriaWorldConfig(food_count=0, poison_count=0))
    return env.reset(seed=4)[0]


def test_argmax_uses_five_outputs_and_first_max_tie_behavior() -> None:
    observation = initial_observation()
    policy = NeatPolicy(FixedNetwork((0.0, 3.0, 3.0, -1.0, 0.0)))
    policy.reset(observation)

    assert policy.act(observation) == 1
    assert policy.last_scores == (0.0, 3.0, 3.0, -1.0, 0.0)


@pytest.mark.parametrize("outputs", [(0.0,) * 4, (0.0,) * 6])
def test_invalid_output_length_is_rejected(outputs) -> None:
    observation = initial_observation()
    policy = NeatPolicy(FixedNetwork(outputs))
    policy.reset(observation)

    with pytest.raises(ValueError, match="outputs"):
        policy.act(observation)


@pytest.mark.parametrize("bad_value", [math.nan, math.inf, -math.inf])
def test_nonfinite_outputs_are_rejected(bad_value: float) -> None:
    observation = initial_observation()
    policy = NeatPolicy(FixedNetwork((0.0, 0.0, bad_value, 0.0, 0.0)))
    policy.reset(observation)

    with pytest.raises(ValueError, match="finite"):
        policy.act(observation)
