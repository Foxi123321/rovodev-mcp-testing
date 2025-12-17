"""Schemas package - Mental models for website intelligence."""

from .website_state_schema import (
    WEBSITE_STATE_SCHEMA,
    validate_website_state,
    create_empty_website_state
)

from .exploration_goal_schema import (
    EXPLORATION_GOAL_SCHEMA,
    validate_exploration_goal,
    create_exploration_goal
)

__all__ = [
    "WEBSITE_STATE_SCHEMA",
    "validate_website_state",
    "create_empty_website_state",
    "EXPLORATION_GOAL_SCHEMA",
    "validate_exploration_goal",
    "create_exploration_goal"
]
