"""Configuration for the first Petri dish."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BacteriaWorldConfig:
    """Small, explicit rules for Bacterium-0's world."""

    width: int = 10
    height: int = 10
    food_count: int = 8
    poison_count: int = 6
    initial_energy: int = 20
    max_steps: int = 100
    step_energy_cost: int = 1
    food_energy: int = 5
    poison_energy_cost: int = 8
    food_reward: float = 1.0
    poison_penalty: float = -1.0
    step_penalty: float = -0.01
