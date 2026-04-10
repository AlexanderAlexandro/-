from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypeVar


ValueT = TypeVar("ValueT")


def trim_answers(
    question_keys: Sequence[str],
    step_index: int,
    answers: Mapping[str, ValueT],
) -> dict[str, ValueT]:
    allowed_keys = set(question_keys[:step_index])
    return {key: value for key, value in answers.items() if key in allowed_keys}

