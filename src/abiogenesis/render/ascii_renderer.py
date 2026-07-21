"""ASCII rendering for the first Petri dish."""

from typing import Any

from abiogenesis.core.types import Position


def render_ascii(
    *,
    width: int,
    height: int,
    organism: Position,
    food,
    poison,
    energy: int,
    steps: int,
    max_steps: int,
    last_reward: float = 0.0,
    total_reward: float = 0.0,
    food_eaten: int = 0,
    poison_collisions: int = 0,
) -> str:
    """Return a compact text view of the grid and episode state."""

    rows: list[str] = []
    border = "+" + ("-" * width) + "+"
    for y in range(height):
        cells: list[str] = []
        for x in range(width):
            if (x, y) == organism:
                cells.append("B")
            elif food[y, x]:
                cells.append("F")
            elif poison[y, x]:
                cells.append("P")
            else:
                cells.append(" ")
        rows.append("|" + "".join(cells) + "|")

    status = format_status_line(
        step=steps,
        max_steps=max_steps,
        energy=energy,
        last_reward=last_reward,
        total_reward=total_reward,
        food_eaten=food_eaten,
        poison_collisions=poison_collisions,
    )
    return "\n".join([status, border, *rows, border])


def format_status_line(
    *,
    step: int,
    max_steps: int,
    energy: int,
    last_reward: float,
    total_reward: float,
    food_eaten: int,
    poison_collisions: int,
) -> str:
    """Format the playback status line used by text renderers."""

    return (
        f"step={step}/{max_steps} "
        f"energy={energy} "
        f"last_reward={last_reward:.2f} "
        f"total_reward={total_reward:.2f} "
        f"food={food_eaten} "
        f"poison={poison_collisions}"
    )


def render_observation_ascii(
    *,
    observation: dict[str, Any],
    max_steps: int,
    last_reward: float = 0.0,
    total_reward: float = 0.0,
    food_eaten: int = 0,
    poison_collisions: int = 0,
) -> str:
    """Render an observation dict without reaching into the environment object."""

    food = observation["food"]
    height, width = food.shape
    organism = tuple(int(value) for value in observation["organism"])
    return render_ascii(
        width=width,
        height=height,
        organism=organism,
        food=food,
        poison=observation["poison"],
        energy=int(observation["energy"][0]),
        steps=int(observation["steps"][0]),
        max_steps=max_steps,
        last_reward=last_reward,
        total_reward=total_reward,
        food_eaten=food_eaten,
        poison_collisions=poison_collisions,
    )
