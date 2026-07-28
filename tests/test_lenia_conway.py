import numpy as np
import pytest

from abiogenesis.lenia.conway import conway_step


def test_stable_block_remains_stable_and_input_is_not_mutated() -> None:
    field = np.zeros((6, 6), dtype=np.uint8)
    field[2:4, 2:4] = 1
    original = field.copy()

    result = conway_step(field)

    assert np.array_equal(result, original)
    assert np.array_equal(field, original)
    assert result is not field
    assert result.dtype == np.uint8
    assert result.flags.c_contiguous


def test_blinker_has_period_two_under_synchronous_updates() -> None:
    field = np.zeros((5, 5), dtype=np.bool_)
    field[2, 1:4] = True
    expected_vertical = np.zeros_like(field)
    expected_vertical[1:4, 2] = True

    first = conway_step(field)
    second = conway_step(first)

    assert np.array_equal(first, expected_vertical)
    assert np.array_equal(second, field)


def test_periodic_edge_blinker_wraps_across_both_sides() -> None:
    field = np.zeros((5, 5), dtype=np.uint8)
    field[0, [4, 0, 1]] = 1
    expected = np.zeros_like(field)
    expected[[4, 0, 1], 0] = 1

    assert np.array_equal(conway_step(field), expected)


@pytest.mark.parametrize(
    "field",
    [
        np.zeros(5, dtype=np.uint8),
        np.zeros((5, 5), dtype=np.float32),
        np.full((5, 5), 2, dtype=np.uint8),
    ],
)
def test_invalid_conway_fields_fail(field: np.ndarray) -> None:
    with pytest.raises(ValueError):
        conway_step(field)
