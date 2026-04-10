from __future__ import annotations

from collections.abc import Callable

from data.template_scenarios import TEMPLATE_SCENARIOS
from data.templates import TEMPLATE_CATEGORIES, TEMPLATES
from utils.formatting import (
    render_copy_block,
    render_hint,
    render_label_block,
    render_screen,
)
from utils.text import escape_html


def list_categories():
    return TEMPLATE_CATEGORIES


def get_category(category_id: str):
    return next(
        (category for category in TEMPLATE_CATEGORIES if category.id == category_id),
        None,
    )


def list_templates_by_category(category_id: str):
    return tuple(
        template for template in TEMPLATES.values() if template.category_id == category_id
    )


def get_template(template_id: str):
    return TEMPLATES.get(template_id)


def get_scenario(template_id: str):
    return TEMPLATE_SCENARIOS.get(template_id, ())


def get_question(template_id: str, step_index: int):
    scenario = get_scenario(template_id)
    if 0 <= step_index < len(scenario):
        return scenario[step_index]
    return None


def get_question_keys(template_id: str) -> tuple[str, ...]:
    return tuple(question.key for question in get_scenario(template_id))


def render_category_card(category_id: str) -> str:
    category = get_category(category_id)
    title = category.title if category else "Шаблоны"
    return render_screen(
        title,
        ["Выберите шаблон из списка ниже."],
        emoji="🗂️",
    )


def render_template_card(template_id: str) -> str:
    template = get_template(template_id)
    if template is None:
        return "Шаблон не найден."

    return render_screen(
        template.title,
        [
            render_label_block("Когда использовать", template.use_case),
            "Если хотите, могу просто показать заготовку. Если удобнее, задам несколько вопросов и соберу готовый текст.",
        ],
        emoji="📝",
    )


def render_blank_template(template_id: str) -> str:
    template = get_template(template_id)
    if template is None:
        return "Шаблон не найден."

    return render_screen(
        template.title,
        [
            render_label_block("Когда использовать", template.use_case),
            render_copy_block("Пустой шаблон", template.empty_template),
        ],
        emoji="📝",
    )


def render_build_intro(template_id: str) -> str:
    template = get_template(template_id)
    scenario = get_scenario(template_id)

    if template is None:
        return "Шаблон не найден."

    return render_screen(
        template.title,
        [
            "Сейчас коротко пройдемся по вопросам. На выходе я соберу готовый текст, который можно сразу отправить, и отдельно покажу структуру по блокам.",
            render_hint(
                f"Шагов: {len(scenario)}. Можно отвечать коротко или развернуто: чем точнее ответы, тем сильнее получится итоговый текст."
            ),
        ],
        emoji="⚙️",
    )


def render_question(template_id: str, step_index: int) -> str:
    template = get_template(template_id)
    question = get_question(template_id, step_index)
    total_steps = len(get_scenario(template_id))

    if template is None or question is None:
        return "Шаг не найден."

    answer_hint = "Можно нажать кнопку или просто написать Да / Нет."
    if not question.choices:
        answer_hint = "Ответ можно прислать в свободной форме. Длинный текст тоже подойдет."

    return render_screen(
        template.title,
        [
            f"<b>Шаг {step_index + 1} из {total_steps}</b>",
            escape_html(question.question),
            render_hint(answer_hint),
        ],
        emoji="🧩",
    )


def render_result(template_id: str, answers: dict[str, str]) -> str:
    template = get_template(template_id)
    if template is None:
        return "Шаблон не найден."

    ready_text = build_ready_text(template_id, answers)
    sections = [
        render_hint(
            "Ниже сначала идет готовое сообщение, которое можно сразу отправить или вставить в документ. После него оставил структуру по полям."
        ),
        render_copy_block("Готовое сообщение", ready_text),
        "<b>Структурированная версия</b>",
    ]
    sections.extend(
        render_label_block(section.title, answers.get(section.key, "—"))
        for section in template.sections
    )

    return render_screen(template.title, sections, emoji="✅")


def resolve_choice_label(template_id: str, step_index: int, value: str) -> str | None:
    question = get_question(template_id, step_index)
    if question is None:
        return None

    for choice in question.choices:
        if choice.value == value:
            return choice.label
    return None


def resolve_typed_choice(template_id: str, step_index: int, raw_value: str) -> str | None:
    normalized = raw_value.strip().lower()
    question = get_question(template_id, step_index)
    if question is None:
        return None

    for choice in question.choices:
        if normalized == choice.label.lower():
            return choice.label

    if normalized in {"да", "yes", "y"}:
        return resolve_choice_label(template_id, step_index, "yes")
    if normalized in {"нет", "no", "n"}:
        return resolve_choice_label(template_id, step_index, "no")
    return None


def build_ready_text(template_id: str, answers: dict[str, str]) -> str:
    builder = READY_TEXT_BUILDERS.get(template_id)
    if builder is None:
        return _build_generic_structured_text(template_id, answers)
    return builder(answers)


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def _strip_terminal_punctuation(value: str) -> str:
    return _normalize_text(value).rstrip(".!?")


def _finish_sentence(value: str) -> str:
    normalized = _normalize_text(value)
    if not normalized:
        return ""
    if normalized.endswith((".", "!", "?")):
        return normalized
    return f"{normalized}."


def _quoted_value(value: str) -> str:
    normalized = _strip_terminal_punctuation(value)
    if not normalized:
        return ""
    return f"«{normalized}»"


def _statement(prefix: str, value: str, *, quoted: bool = False) -> str:
    normalized = _quoted_value(value) if quoted else _normalize_text(value)
    if not normalized:
        return ""
    return _finish_sentence(f"{prefix}{normalized}")


def _paragraph(*sentences: str) -> str:
    return " ".join(sentence for sentence in sentences if sentence)


def _plain_section(title: str, body: str) -> str:
    return f"{title}\n{_normalize_text(body)}"


def _plain_sections(*sections: str) -> str:
    return "\n\n".join(section for section in sections if section)


def _build_generic_structured_text(template_id: str, answers: dict[str, str]) -> str:
    template = get_template(template_id)
    if template is None:
        return "Шаблон не найден."

    sentences = [
        _statement(f"{section.title}: ", answers.get(section.key, "—"))
        for section in template.sections
    ]
    return _plain_sections(
        _finish_sentence(f"Подготовил сообщение по шаблону «{template.title}»"),
        _paragraph(*sentences),
    )


def _build_hypothesis_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _finish_sentence("Коллеги, предлагаю проверить следующую гипотезу"),
        _paragraph(
            _statement("Суть изменения — ", answers["change"], quoted=True),
            _statement("Целевой сегмент — ", answers["segment"], quoted=True),
            _statement("Ожидаемое изменение поведения — ", answers["behavior"], quoted=True),
        ),
        _paragraph(
            _statement("Считаем, что гипотеза может сработать, потому что ", answers["reason"], quoted=True),
            _statement("Основные метрики, на которые смотрим, — ", answers["primary_metrics"], quoted=True),
        ),
        _paragraph(
            _statement("Дополнительно будем смотреть на следующие вторичные эффекты и метрики: ", answers["secondary_metrics"], quoted=True),
            _statement("Из рисков важно учитывать ", answers["risks"], quoted=True),
        ),
    )


def _build_feature_draft_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _statement("Коллеги, подготовил короткий драфт по фиче ", answers["feature_name"], quoted=True),
        _paragraph(
            _statement("Сейчас видим следующую проблему: ", answers["problem"], quoted=True),
            _statement("Для продукта и бизнеса это важно, потому что ", answers["importance"], quoted=True),
        ),
        _paragraph(
            _statement("Предлагаемое решение — ", answers["solution"], quoted=True),
            _statement("Для пользователя изменение будет выглядеть так: ", answers["user_path_change"], quoted=True),
        ),
        _paragraph(
            _statement("Ожидаем влияние на следующие метрики: ", answers["target_metrics"], quoted=True),
            _statement("Из ограничений важно учитывать ", answers["risks"], quoted=True),
            _statement("До старта реализации отдельно нужно уточнить ", answers["open_questions"], quoted=True),
        ),
    )


def _build_feature_goals_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _finish_sentence("Коллеги, фиксирую цель изменения"),
        _paragraph(
            _statement("Что меняем — ", answers["change"], quoted=True),
            _statement("Для кого делаем — ", answers["segment"], quoted=True),
        ),
        _paragraph(
            _statement("Хотим изменить следующее поведение: ", answers["behavior"], quoted=True),
            _statement("Ожидаем, что это сработает, потому что ", answers["reason"], quoted=True),
        ),
        _paragraph(
            _statement("Метрики, на которые ориентируемся, — ", answers["metrics"], quoted=True),
            _statement("Решение будем считать успешным, если ", answers["success_criteria"], quoted=True),
        ),
    )


def _build_analytic_conclusion_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _paragraph(
            _statement("Коллеги, по итогам анализа основной вывод такой: ", answers["main_conclusion"], quoted=True),
            _statement("В данных видно следующее: ", answers["data_fact"], quoted=True),
        ),
        _paragraph(
            _statement("Это важно, потому что ", answers["importance"], quoted=True),
            _statement("Для продукта это означает ", answers["product_meaning"], quoted=True),
        ),
        _paragraph(
            _statement("Следующим шагом предлагаю ", answers["next_step"], quoted=True),
        ),
    )


def _build_dev_task_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _finish_sentence("Привет. Нужна помощь с задачей"),
        _paragraph(
            _statement("Что нужно сделать: ", answers["task"], quoted=True),
            _statement("Это нужно для того, чтобы ", answers["goal"], quoted=True),
        ),
        _paragraph(
            _statement("Сейчас поведение такое: ", answers["current_behavior"], quoted=True),
            _statement("После изменения ожидаем: ", answers["expected_behavior"], quoted=True),
        ),
        _paragraph(
            _statement("Критерии готовности: ", answers["done_criteria"], quoted=True),
            _statement("Ограничения, которые важно учесть: ", answers["constraints"], quoted=True),
            _statement("Отдельно нужно уточнить: ", answers["open_questions"], quoted=True),
        ),
    )


def _build_design_task_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _finish_sentence("Привет. Нужна помощь с задачей по дизайну"),
        _paragraph(
            _statement("Контекст: ", answers["context"], quoted=True),
            _statement("Проблема сейчас такая: ", answers["problem"], quoted=True),
        ),
        _paragraph(
            _statement("Нужно изменить ", answers["change_needed"], quoted=True),
            _statement("Это относится к экрану или блоку ", answers["screen_or_block"], quoted=True),
            _statement("Важно сохранить ", answers["keep_constraints"], quoted=True),
        ),
        _paragraph(
            _statement("Улучшить хотим ", answers["improvement_goal"], quoted=True),
            _statement("Хорошим результатом считаем ситуацию, когда ", answers["expected_result"], quoted=True),
        ),
    )


def _build_landing_brief_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _statement("Коллеги, собрал бриф лендинга для ", answers["product"], quoted=True),
        _paragraph(
            _statement("Целевая аудитория — ", answers["audience"], quoted=True),
            _statement("Главная проблема этой аудитории — ", answers["problem"], quoted=True),
        ),
        _paragraph(
            _statement("Ключевое обещание страницы: ", answers["promise"], quoted=True),
            _statement("Доверие и доказательства усиливаем через ", answers["proof"], quoted=True),
        ),
        _paragraph(
            _statement("По структуре страницы предлагаю следующие блоки: ", answers["sections_plan"], quoted=True),
            _statement("Целевое действие на странице — ", answers["cta"], quoted=True),
            _statement("Тон и стиль текста — ", answers["tone"], quoted=True),
        ),
    )


def _build_offer_message_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _statement("Предлагаю такой оффер для ", answers["audience"], quoted=True),
        _paragraph(
            _statement("Проблема, которую закрываем: ", answers["problem"], quoted=True),
            _statement("Что предлагаем: ", answers["solution"], quoted=True),
        ),
        _paragraph(
            _statement("Ключевой результат, который обещаем: ", answers["result"], quoted=True),
            _statement("Поверить предложению помогает следующее: ", answers["proof"], quoted=True),
        ),
        _paragraph(
            _statement("Целевое действие, которое хотим получить, — ", answers["cta"], quoted=True),
        ),
    )


def _build_icp_profile_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _finish_sentence("Коллеги, фиксирую рабочий портрет ICP"),
        _paragraph(
            _statement("Сегмент — ", answers["segment"], quoted=True),
            _statement("Роль или лицо, принимающее решение, — ", answers["decision_maker"], quoted=True),
        ),
        _paragraph(
            _statement("Контекст, в котором возникает потребность: ", answers["context"], quoted=True),
            _statement("Главная боль этого сегмента: ", answers["pain"], quoted=True),
        ),
        _paragraph(
            _statement("Хорошим результатом для них считается ", answers["success"], quoted=True),
            _statement("Основные возражения: ", answers["objections"], quoted=True),
            _statement("Типичный триггер интереса — ", answers["trigger"], quoted=True),
        ),
    )


def _build_business_message_text(answers: dict[str, str]) -> str:
    parts = [
        _normalize_text(answers["greeting"]),
        _paragraph(
            _statement("Пишу по такому вопросу: ", answers["context"]),
            _statement("Основная просьба: ", answers["request"]),
        ),
        _statement("По сроку или ожиданию ориентир такой: ", answers["expectation"]),
        _finish_sentence(answers["closing"]),
    ]
    return "\n\n".join(part for part in parts if part)


def _build_soft_reminder_text(answers: dict[str, str]) -> str:
    parts = [
        _normalize_text(answers["greeting"]),
        _statement("Хочу мягко напомнить о следующем: ", answers["reminder"]),
        _statement("Сейчас нужен такой следующий шаг: ", answers["current_need"]),
        _finish_sentence(answers["closing"]),
    ]
    return "\n\n".join(part for part in parts if part)


def _build_short_feedback_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _finish_sentence("Спасибо за работу. Ниже коротко собрал фидбэк"),
        _paragraph(
            _statement("Что особенно хорошо: ", answers["good"]),
            _statement("То, что стоит улучшить в первую очередь: ", answers["improve"]),
        ),
        _paragraph(
            _statement("Это важно, потому что ", answers["importance"]),
            _statement("Предлагаю следующий шаг: ", answers["next_step"]),
        ),
    )


def _build_polite_decline_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _finish_sentence(answers["gratitude"]),
        _paragraph(
            _statement("Моя позиция такая: ", answers["position"]),
            _statement("Короткая причина: ", answers["reason"]),
        ),
        _paragraph(
            _finish_sentence(answers["closing"]),
        ),
    )


def _build_meeting_summary_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _statement("Коллеги, отправляю краткое саммари встречи по теме ", answers["topic"], quoted=True),
        _paragraph(
            _statement("Обсудили: ", answers["discussion"], quoted=True),
            _statement("По итогам пришли к следующим выводам: ", answers["conclusions"], quoted=True),
        ),
        _paragraph(
            _statement("Принятые решения: ", answers["decisions"], quoted=True),
            _statement("Следующие шаги: ", answers["next_steps"], quoted=True),
        ),
    )


def _build_action_items_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _finish_sentence("Фиксирую action item по итогам обсуждения"),
        _paragraph(
            _statement("Задача: ", answers["task"], quoted=True),
            _statement("Ответственный: ", answers["owner"], quoted=True),
        ),
        _paragraph(
            _statement("Срок: ", answers["deadline"], quoted=True),
            _statement("Текущий статус: ", answers["status"], quoted=True),
        ),
        _paragraph(
            _statement("Комментарий: ", answers["comment"], quoted=True),
        ),
    )


def _build_startup_update_text(answers: dict[str, str]) -> str:
    return _plain_sections(
        _statement("Коллеги, короткий апдейт по запуску за ", answers["period"], quoted=True),
        _paragraph(
            _statement("Главный фокус периода — ", answers["focus"], quoted=True),
            _statement("Что удалось за это время: ", answers["wins"], quoted=True),
        ),
        _paragraph(
            _statement("По цифрам и метрикам видим следующее: ", answers["metrics"], quoted=True),
            _statement("Основные блокеры сейчас — ", answers["blockers"], quoted=True),
        ),
        _paragraph(
            _statement("Что нужно решить или обсудить: ", answers["decisions_needed"], quoted=True),
            _statement("Следующие шаги: ", answers["next_steps"], quoted=True),
            _statement("Отдельный запрос к команде: ", answers["ask"], quoted=True),
        ),
    )


def _build_doc_review_checklist_text(answers: dict[str, str]) -> str:
    labels = {
        "goal": "Понятная цель",
        "problem": "Сформулированная проблема",
        "solution": "Понятное решение",
        "metrics": "Влияние на метрики",
        "risks": "Риски",
        "open_questions": "Открытые вопросы",
    }

    completed_items = [
        title for key, title in labels.items() if answers.get(key, "").lower() == "да"
    ]
    missing_items = [
        title for key, title in labels.items() if answers.get(key, "").lower() != "да"
    ]

    recommendation = (
        "Документ выглядит собранным по базовому чек-листу."
        if not missing_items
        else "Перед дальнейшим согласованием документ стоит дополнить."
    )

    completed_text = ", ".join(completed_items) or "пока ничего"
    missing_text = ", ".join(missing_items) or "ничего не пропущено"
    follow_up_text = (
        _finish_sentence("Все ключевые блоки на месте")
        if not missing_items
        else _finish_sentence(
            f"Перед дальнейшим согласованием стоит обратить внимание на следующие пункты: {missing_text}"
        )
    )

    return _plain_sections(
        _finish_sentence("Проверил документ по базовому чек-листу"),
        _paragraph(
            _finish_sentence(
                f"Сейчас в документе уже есть следующие ключевые блоки: {completed_text}"
            ),
        ),
        _paragraph(
            follow_up_text,
            _finish_sentence(
                f"Итоговое покрытие чек-листа составляет {len(completed_items)} из {len(labels)} пунктов"
            ),
        ),
        _paragraph(_finish_sentence(recommendation)),
    )


READY_TEXT_BUILDERS: dict[str, Callable[[dict[str, str]], str]] = {
    "hypothesis": _build_hypothesis_text,
    "feature_draft": _build_feature_draft_text,
    "feature_goals": _build_feature_goals_text,
    "analytic_conclusion": _build_analytic_conclusion_text,
    "dev_task": _build_dev_task_text,
    "design_task": _build_design_task_text,
    "landing_brief": _build_landing_brief_text,
    "offer_message": _build_offer_message_text,
    "icp_profile": _build_icp_profile_text,
    "business_message": _build_business_message_text,
    "soft_reminder": _build_soft_reminder_text,
    "short_feedback": _build_short_feedback_text,
    "polite_decline": _build_polite_decline_text,
    "meeting_summary": _build_meeting_summary_text,
    "action_items": _build_action_items_text,
    "startup_update": _build_startup_update_text,
    "doc_review_checklist": _build_doc_review_checklist_text,
}
