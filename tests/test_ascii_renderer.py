import numpy as np

from abiogenesis.render.ascii_renderer import format_status_line, render_ascii


def test_ascii_renderer_draws_bordered_grid_and_entities() -> None:
    food = np.zeros((2, 3), dtype=np.int8)
    poison = np.zeros((2, 3), dtype=np.int8)
    food[0, 1] = 1
    poison[1, 2] = 1

    rendered = render_ascii(
        width=3,
        height=2,
        organism=(0, 0),
        food=food,
        poison=poison,
        energy=9,
        steps=4,
        max_steps=20,
    )

    assert "+---+" in rendered
    assert "|BF |" in rendered
    assert "|  P|" in rendered


def test_status_line_includes_episode_metrics() -> None:
    status = format_status_line(
        step=3,
        max_steps=10,
        energy=7,
        last_reward=0.5,
        total_reward=1.25,
        food_eaten=2,
        poison_collisions=1,
    )

    assert status == ("step=3/10 energy=7 last_reward=0.50 total_reward=1.25 food=2 poison=1")
