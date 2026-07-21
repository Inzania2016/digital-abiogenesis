"""Minimal episode metric recording."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EpisodeRecord:
    """Summary of one organism episode."""

    total_reward: float
    steps: int
    final_energy: int
    food_eaten: int = 0
    poison_collisions: int = 0
    wasted_moves: int = 0
    repeated_positions: int = 0
    unique_tiles_visited: int = 0
    loop_detections: int = 0
    short_loops: int = 0
    medium_loops: int = 0
    long_loops: int = 0
    novelty_bonuses: int = 0
    novelty_reward_total: float = 0.0

    @property
    def revisit_ratio(self) -> float:
        """Return the fraction of steps that revisited known tiles."""

        if self.steps <= 0:
            return 0.0
        revisits = max(0, self.steps + 1 - self.unique_tiles_visited)
        return revisits / self.steps


@dataclass(frozen=True)
class RunSummary:
    """Aggregate metrics for a batch of episodes."""

    episodes: int
    seed: int
    grid_size: int
    average_reward: float
    average_lifespan: float
    food_eaten: int
    poison_collisions: int
    wasted_moves: int
    repeated_positions: int
    unique_tiles_visited: int
    loop_detections: int
    short_loops: int
    medium_loops: int
    long_loops: int
    novelty_bonuses: int
    novelty_reward_total: float
    revisit_ratio: float

    @classmethod
    def from_records(
        cls,
        *,
        records: list[EpisodeRecord],
        seed: int,
        grid_size: int,
    ) -> "RunSummary":
        if not records:
            raise ValueError("Cannot summarize an empty run.")

        return cls(
            episodes=len(records),
            seed=seed,
            grid_size=grid_size,
            average_reward=sum(record.total_reward for record in records) / len(records),
            average_lifespan=sum(record.steps for record in records) / len(records),
            food_eaten=sum(record.food_eaten for record in records),
            poison_collisions=sum(record.poison_collisions for record in records),
            wasted_moves=sum(record.wasted_moves for record in records),
            repeated_positions=sum(record.repeated_positions for record in records),
            unique_tiles_visited=sum(record.unique_tiles_visited for record in records),
            loop_detections=sum(record.loop_detections for record in records),
            short_loops=sum(record.short_loops for record in records),
            medium_loops=sum(record.medium_loops for record in records),
            long_loops=sum(record.long_loops for record in records),
            novelty_bonuses=sum(record.novelty_bonuses for record in records),
            novelty_reward_total=sum(record.novelty_reward_total for record in records),
            revisit_ratio=sum(record.revisit_ratio for record in records) / len(records),
        )
