"""Keyboard control state for pygame replay."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ViewerControls:
    """Small immutable control state for replay."""

    paused: bool = False
    show_trail: bool = False
    show_scent: bool = False
    show_hud: bool = True
    delay: float = 0.2
    should_quit: bool = False
    should_reset: bool = False
    should_screenshot: bool = False


def apply_key(control: ViewerControls, key_name: str) -> ViewerControls:
    """Return updated controls for a normalized key name."""

    key = key_name.lower()
    if key in {"escape", "q"}:
        return _replace(control, should_quit=True)
    if key == "space":
        return _replace(control, paused=not control.paused)
    if key == "r":
        return _replace(control, should_reset=True)
    if key in {"up", "+", "plus", "equals"}:
        return _replace(control, delay=max(0.02, control.delay * 0.75))
    if key in {"down", "-", "minus"}:
        return _replace(control, delay=min(2.0, control.delay / 0.75))
    if key == "t":
        return _replace(control, show_trail=not control.show_trail)
    if key == "s":
        return _replace(control, show_scent=not control.show_scent)
    if key == "h":
        return _replace(control, show_hud=not control.show_hud)
    if key in {"f12", "p"}:
        return _replace(control, should_screenshot=True)
    return control


def consume_transient_flags(control: ViewerControls) -> ViewerControls:
    """Clear one-frame action flags after the caller handles them."""

    return _replace(
        control,
        should_reset=False,
        should_screenshot=False,
    )


def screenshot_path(*, directory: Path, seed: int, step: int) -> Path:
    """Return a predictable screenshot path."""

    return directory / f"bacterium-0-seed-{seed}-step-{step}.png"


def _replace(control: ViewerControls, **changes) -> ViewerControls:
    values = {
        "paused": control.paused,
        "show_trail": control.show_trail,
        "show_scent": control.show_scent,
        "show_hud": control.show_hud,
        "delay": control.delay,
        "should_quit": control.should_quit,
        "should_reset": control.should_reset,
        "should_screenshot": control.should_screenshot,
    }
    values.update(changes)
    return ViewerControls(**values)
