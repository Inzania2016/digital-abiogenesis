from pathlib import Path

from abiogenesis.render.pygame_controls import (
    ViewerControls,
    apply_key,
    consume_transient_flags,
    screenshot_path,
)


def test_apply_key_toggles_pause_and_overlays() -> None:
    controls = ViewerControls()

    controls = apply_key(controls, "space")
    controls = apply_key(controls, "t")
    controls = apply_key(controls, "s")
    controls = apply_key(controls, "h")

    assert controls.paused
    assert controls.show_trail
    assert controls.show_scent
    assert not controls.show_hud


def test_apply_key_adjusts_speed() -> None:
    controls = ViewerControls(delay=0.4)

    faster = apply_key(controls, "up")
    slower = apply_key(faster, "down")

    assert faster.delay < controls.delay
    assert slower.delay > faster.delay


def test_transient_flags_are_consumed() -> None:
    controls = apply_key(ViewerControls(), "r")
    controls = apply_key(controls, "p")

    consumed = consume_transient_flags(controls)

    assert controls.should_reset
    assert controls.should_screenshot
    assert not consumed.should_reset
    assert not consumed.should_screenshot


def test_screenshot_path_is_predictable() -> None:
    path = screenshot_path(directory=Path("artifacts/screenshots"), seed=7, step=12)

    assert path == Path("artifacts/screenshots/bacterium-0-seed-7-step-12.png")
