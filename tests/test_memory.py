from abiogenesis.agents.memory import (
    DirectionalNoveltyTracker,
    LoopMemoryTracker,
    LoopScentEncoder,
    NOVELTY_BLOCKED,
    NOVELTY_UNVISITED,
    NOVELTY_VISITED,
    NO_PREVIOUS_ACTION,
    MemoryScentEncoder,
    NoveltyScentEncoder,
    TinyMemoryTracker,
    VisitMemoryTracker,
    VisitScentEncoder,
    encode_loop_scent_observation,
    encode_memory_scent_observation,
    encode_novelty_scent_observation,
    encode_visit_scent_observation,
)
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import Action, BacteriaWorldEnv


def make_memory_env() -> BacteriaWorldEnv:
    env = BacteriaWorldEnv(BacteriaWorldConfig(width=5, height=5, food_count=0, poison_count=0))
    env.reset(seed=1)
    env.organism = (2, 2)
    return env


def test_memory_reset_clears_episode_state() -> None:
    env = make_memory_env()
    tracker = TinyMemoryTracker(previous_action=Action.NORTH, same_position=True)
    tracker.repeat_count = 2

    tracker.reset(env._observation())

    assert tracker.previous_action == NO_PREVIOUS_ACTION
    assert tracker.previous_position == (2, 2)
    assert not tracker.same_position
    assert tracker.repeat_count == 0
    assert tracker.repeat_bucket == 0


def test_memory_tracks_previous_action() -> None:
    env = make_memory_env()
    tracker = TinyMemoryTracker()
    tracker.reset(env._observation())
    env.organism = (2, 1)

    tracker.update_after_step(
        action=Action.NORTH,
        observation=env._observation(),
    )

    assert tracker.previous_action == Action.NORTH
    assert tracker.previous_position == (2, 1)


def test_memory_tracks_repeated_position_bucket() -> None:
    env = make_memory_env()
    tracker = TinyMemoryTracker()
    tracker.reset(env._observation())

    tracker.update_after_step(action=Action.WAIT, observation=env._observation())
    assert tracker.same_position
    assert tracker.repeat_bucket == 1

    tracker.update_after_step(action=Action.WAIT, observation=env._observation())
    assert tracker.same_position
    assert tracker.repeat_bucket == 2


def test_memory_scent_encoding_appends_memory_fields() -> None:
    env = make_memory_env()
    env.food[0, 2] = 1
    memory = TinyMemoryTracker()
    memory.reset(env._observation())
    memory.update_after_step(action=Action.WAIT, observation=env._observation())

    state = encode_memory_scent_observation(env._observation(), memory=memory)

    assert state[-3:] == (Action.WAIT, 1, 1)
    assert state[4] == 1


def test_memory_scent_encoder_resets_and_updates() -> None:
    env = make_memory_env()
    encoder = MemoryScentEncoder()

    encoder.reset(env._observation())
    encoder.update_after_step(action=Action.EAST, observation=env._observation())
    state = encoder(env._observation())

    assert state[-3:] == (Action.EAST, 1, 1)


def test_visit_memory_reset_marks_start_tile() -> None:
    env = make_memory_env()
    tracker = VisitMemoryTracker()

    tracker.reset(env._observation())

    assert tracker.current_position == (2, 2)
    assert tracker.visited_positions == {(2, 2)}
    assert not tracker.current_tile_visited_before
    assert tracker.unique_tiles_visited == 1


def test_visit_memory_tracks_current_tile_revisit() -> None:
    env = make_memory_env()
    tracker = VisitMemoryTracker()
    tracker.reset(env._observation())

    tracker.update_after_step(action=Action.WAIT, observation=env._observation())

    assert tracker.current_tile_visited_before
    assert tracker.unique_tiles_visited == 1


def test_visit_memory_adjacent_encoding() -> None:
    env = make_memory_env()
    tracker = VisitMemoryTracker()
    tracker.reset(env._observation())
    env.organism = (2, 1)
    tracker.update_after_step(action=Action.NORTH, observation=env._observation())

    assert tracker.adjacent_visited_flags() == (0, 1, 0, 0)


def test_visit_scent_state_shape_and_content() -> None:
    env = make_memory_env()
    env.food[0, 2] = 1
    tracker = VisitMemoryTracker()
    tracker.reset(env._observation())
    tracker.update_after_step(action=Action.WAIT, observation=env._observation())

    state = encode_visit_scent_observation(env._observation(), memory=tracker)

    assert len(state) == 14
    assert state[4] == 1
    assert state[-5:] == (1, 0, 0, 0, 0)


def test_visit_scent_encoder_resets_and_updates() -> None:
    env = make_memory_env()
    encoder = VisitScentEncoder()
    encoder.reset(env._observation())
    env.organism = (3, 2)

    encoder.update_after_step(action=Action.EAST, observation=env._observation())
    state = encoder(env._observation())

    assert state[-5:] == (0, 0, 0, 0, 1)


def test_loop_tracker_reset_clears_episode_state() -> None:
    env = make_memory_env()
    tracker = LoopMemoryTracker()
    tracker.reset(env._observation())
    env.organism = (3, 2)
    tracker.update_after_step(action=Action.EAST, observation=env._observation())

    tracker.reset(env._observation())

    assert tracker.previous_action == NO_PREVIOUS_ACTION
    assert tracker.recent_history() == ((3, 2),)
    assert not tracker.loop_detected
    assert tracker.loop_bucket == 0
    assert tracker.loop_detections == 0


def test_loop_tracker_ignores_simple_non_loop_movement() -> None:
    env = make_memory_env()
    tracker = LoopMemoryTracker()
    tracker.reset(env._observation())
    for action, position in (
        (Action.EAST, (3, 2)),
        (Action.EAST, (4, 2)),
        (Action.NORTH, (4, 1)),
    ):
        env.organism = position
        tracker.update_after_step(action=action, observation=env._observation())

    assert not tracker.loop_detected
    assert tracker.loop_bucket == 0


def test_loop_tracker_detects_two_position_loop() -> None:
    env = make_memory_env()
    tracker = LoopMemoryTracker()
    tracker.reset(env._observation())
    for action, position in (
        (Action.EAST, (3, 2)),
        (Action.WEST, (2, 2)),
        (Action.EAST, (3, 2)),
    ):
        env.organism = position
        tracker.update_after_step(action=action, observation=env._observation())

    assert tracker.loop_detected
    assert tracker.loop_length == 2
    assert tracker.loop_bucket == 1
    assert tracker.short_loops == 1


def test_loop_tracker_detects_three_position_loop() -> None:
    env = make_memory_env()
    tracker = LoopMemoryTracker()
    tracker.reset(env._observation())
    for action, position in (
        (Action.EAST, (3, 2)),
        (Action.NORTH, (3, 1)),
        (Action.WEST, (2, 2)),
        (Action.EAST, (3, 2)),
        (Action.NORTH, (3, 1)),
    ):
        env.organism = position
        tracker.update_after_step(action=action, observation=env._observation())

    assert tracker.loop_detected
    assert tracker.loop_length == 3
    assert tracker.loop_bucket == 2
    assert tracker.medium_loops == 1


def test_loop_scent_encoding_appends_loop_state() -> None:
    env = make_memory_env()
    tracker = LoopMemoryTracker()
    tracker.reset(env._observation())
    for action, position in (
        (Action.EAST, (3, 2)),
        (Action.WEST, (2, 2)),
        (Action.EAST, (3, 2)),
    ):
        env.organism = position
        tracker.update_after_step(action=action, observation=env._observation())

    state = encode_loop_scent_observation(env._observation(), memory=tracker)

    assert len(state) == 11
    assert state[-2:] == (Action.EAST, 1)


def test_loop_scent_encoder_resets_and_updates() -> None:
    env = make_memory_env()
    encoder = LoopScentEncoder()
    encoder.reset(env._observation())
    env.organism = (3, 2)
    encoder.update_after_step(action=Action.EAST, observation=env._observation())

    state = encoder(env._observation())

    assert state[-2:] == (Action.EAST, 0)


def test_directional_novelty_reset_marks_start_tile() -> None:
    env = make_memory_env()
    tracker = DirectionalNoveltyTracker()

    tracker.reset(env._observation())

    assert tracker.current_position == (2, 2)
    assert tracker.visited_positions == {(2, 2)}
    assert tracker.unique_tiles_visited == 1


def test_directional_novelty_reports_unvisited_visited_and_blocked() -> None:
    env = make_memory_env()
    tracker = DirectionalNoveltyTracker()
    tracker.reset(env._observation())
    env.organism = (2, 1)
    tracker.update_after_step(action=Action.NORTH, observation=env._observation())
    env.organism = (2, 0)
    tracker.update_after_step(action=Action.NORTH, observation=env._observation())

    assert tracker.directional_novelty(env._observation()) == (
        NOVELTY_BLOCKED,
        NOVELTY_VISITED,
        NOVELTY_UNVISITED,
        NOVELTY_UNVISITED,
    )


def test_novelty_scent_encoding_appends_directional_novelty() -> None:
    env = make_memory_env()
    tracker = DirectionalNoveltyTracker()
    tracker.reset(env._observation())
    env.organism = (2, 1)
    tracker.update_after_step(action=Action.NORTH, observation=env._observation())

    state = encode_novelty_scent_observation(env._observation(), memory=tracker)

    assert len(state) == 13
    assert state[-4:] == (
        NOVELTY_UNVISITED,
        NOVELTY_VISITED,
        NOVELTY_UNVISITED,
        NOVELTY_UNVISITED,
    )


def test_novelty_scent_encoder_resets_and_updates() -> None:
    env = make_memory_env()
    encoder = NoveltyScentEncoder()
    encoder.reset(env._observation())
    env.organism = (3, 2)

    encoder.update_after_step(action=Action.EAST, observation=env._observation())
    state = encoder(env._observation())

    assert state[-4:] == (
        NOVELTY_UNVISITED,
        NOVELTY_UNVISITED,
        NOVELTY_UNVISITED,
        NOVELTY_VISITED,
    )
