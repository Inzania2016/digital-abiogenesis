"""Color and sizing defaults for the pygame Petri dish."""

from __future__ import annotations

from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass(frozen=True)
class PygameTheme:
    """Visual style for the lab dish."""

    background: Color = (10, 13, 16)
    panel: Color = (18, 22, 26)
    panel_edge: Color = (52, 61, 68)
    grid: Color = (52, 61, 66)
    empty: Color = (24, 30, 34)
    empty_alt: Color = (28, 35, 39)
    food: Color = (86, 210, 118)
    food_glow: Color = (178, 255, 190)
    poison: Color = (205, 63, 91)
    poison_glow: Color = (255, 136, 157)
    organism: Color = (93, 190, 255)
    organism_core: Color = (218, 246, 255)
    trail: Color = (76, 112, 136)
    text: Color = (230, 238, 240)
    muted_text: Color = (142, 155, 164)
    warning_text: Color = (255, 174, 96)
    scent_food: Color = (118, 238, 143)
    scent_poison: Color = (255, 112, 139)
    scent_conflict: Color = (255, 205, 94)


DEFAULT_THEME = PygameTheme()
