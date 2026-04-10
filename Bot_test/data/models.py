from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TemplateCategory:
    id: str
    title: str


@dataclass(frozen=True)
class TemplateSection:
    key: str
    title: str


@dataclass(frozen=True)
class TemplateDefinition:
    id: str
    category_id: str
    title: str
    use_case: str
    empty_template: str
    sections: tuple[TemplateSection, ...]


@dataclass(frozen=True)
class ChoiceOption:
    value: str
    label: str


@dataclass(frozen=True)
class TemplateQuestion:
    key: str
    question: str
    choices: tuple[ChoiceOption, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CalculatorQuestion:
    key: str
    question: str


@dataclass(frozen=True)
class CalculatorDefinition:
    id: str
    title: str
    description: str
    formula_hint: str
    questions: tuple[CalculatorQuestion, ...]


@dataclass(frozen=True)
class UsefulBlock:
    id: str
    title: str
    content: str

