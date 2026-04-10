from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal, InvalidOperation

from data.calculators import CALCULATORS
from utils.formatting import render_hint, render_label_block, render_screen
from utils.text import escape_html, format_number


def list_calculators():
    return tuple(CALCULATORS.values())


def get_calculator(calculator_id: str):
    return CALCULATORS.get(calculator_id)


def get_question(calculator_id: str, step_index: int):
    calculator = get_calculator(calculator_id)
    if calculator is None:
        return None
    if 0 <= step_index < len(calculator.questions):
        return calculator.questions[step_index]
    return None


def get_question_keys(calculator_id: str) -> tuple[str, ...]:
    calculator = get_calculator(calculator_id)
    if calculator is None:
        return ()
    return tuple(question.key for question in calculator.questions)


def render_calculator_card(calculator_id: str) -> str:
    calculator = get_calculator(calculator_id)
    if calculator is None:
        return "Калькулятор не найден."

    return render_screen(
        calculator.title,
        [
            escape_html(calculator.description),
            render_label_block("Как считается", calculator.formula_hint),
            render_hint("Нажмите «Начать расчет». Я по шагам спрошу данные и сразу покажу итог."),
        ],
        emoji="🧮",
    )


def render_question(calculator_id: str, step_index: int) -> str:
    calculator = get_calculator(calculator_id)
    question = get_question(calculator_id, step_index)

    if calculator is None or question is None:
        return "Шаг не найден."

    return render_screen(
        calculator.title,
        [
            f"<b>Шаг {step_index + 1} из {len(calculator.questions)}</b>",
            escape_html(question.question),
            render_hint("Можно использовать целые числа, точку или запятую."),
        ],
        emoji="🧮",
    )


def parse_number(raw_value: str) -> Decimal:
    normalized = raw_value.strip().replace(" ", "").replace(",", ".")
    try:
        return Decimal(normalized)
    except InvalidOperation as error:
        raise ValueError("invalid_number") from error


def validate_answer(
    calculator_id: str,
    question_key: str,
    raw_value: str,
    answers: dict[str, Decimal],
) -> Decimal:
    value = parse_number(raw_value)
    validator = VALIDATORS.get(calculator_id)
    if validator is None:
        return value
    return validator(question_key, value, answers)


def render_result(calculator_id: str, answers: dict[str, Decimal]) -> str:
    calculator = get_calculator(calculator_id)
    if calculator is None:
        return "Калькулятор не найден."

    renderer = RESULT_RENDERERS.get(calculator_id)
    if renderer is None:
        return "Результат не найден."

    return renderer(calculator.title, answers)


def _render_result_screen(
    title: str,
    input_blocks: list[str],
    result_blocks: list[str],
) -> str:
    sections = [
        render_hint("Ниже собрал исходные данные и готовый расчет."),
        "<b>Что взяли в расчет</b>",
        *input_blocks,
        "<b>Что получилось</b>",
        *result_blocks,
    ]
    return render_screen(title, sections, emoji="✅")


def _require_positive(value: Decimal, text: str) -> Decimal:
    if value <= 0:
        raise ValueError(text)
    return value


def _require_non_negative(value: Decimal, text: str) -> Decimal:
    if value < 0:
        raise ValueError(text)
    return value


def _validate_growth(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "start_value":
        return _require_positive(value, "Начальное значение должно быть больше нуля.")
    return value


def _validate_discount(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "original_price":
        return _require_non_negative(value, "Цена не может быть отрицательной.")
    if question_key == "discount_percent" and not Decimal("0") <= value <= Decimal("100"):
        raise ValueError("Скидка должна быть в диапазоне от 0 до 100.")
    return value


def _validate_conversion(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "total_count":
        return _require_positive(value, "Общее количество должно быть больше нуля.")
    if question_key == "target_count":
        _require_non_negative(value, "Количество целевых действий не может быть отрицательным.")
        total = answers.get("total_count")
        if total is not None and value > total:
            raise ValueError("Целевых действий не может быть больше общего количества.")
    return value


def _validate_ctr(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "impressions":
        return _require_positive(value, "Показы должны быть больше нуля.")
    if question_key == "clicks":
        _require_non_negative(value, "Клики не могут быть отрицательными.")
        impressions = answers.get("impressions")
        if impressions is not None and value > impressions:
            raise ValueError("Кликов не может быть больше показов.")
    return value


def _validate_cpl(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "spend":
        return _require_non_negative(value, "Расходы не могут быть отрицательными.")
    if question_key == "leads":
        return _require_positive(value, "Количество лидов должно быть больше нуля.")
    return value


def _validate_roi(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "revenue":
        return _require_non_negative(value, "Доход не может быть отрицательным.")
    if question_key == "costs":
        return _require_positive(value, "Затраты должны быть больше нуля.")
    return value


def _validate_retention(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "base_users":
        return _require_positive(value, "База пользователей должна быть больше нуля.")
    if question_key == "retained_users":
        _require_non_negative(value, "Количество вернувшихся пользователей не может быть отрицательным.")
        base_users = answers.get("base_users")
        if base_users is not None and value > base_users:
            raise ValueError("Вернувшихся пользователей не может быть больше базы периода.")
    return value


def _validate_churn(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "base_users":
        return _require_positive(value, "База пользователей должна быть больше нуля.")
    if question_key == "lost_users":
        _require_non_negative(value, "Количество ушедших пользователей не может быть отрицательным.")
        base_users = answers.get("base_users")
        if base_users is not None and value > base_users:
            raise ValueError("Ушедших пользователей не может быть больше базы периода.")
    return value


def _validate_stickiness(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "dau":
        return _require_non_negative(value, "DAU не может быть отрицательным.")
    if question_key == "mau":
        _require_positive(value, "MAU должен быть больше нуля.")
        dau = answers.get("dau")
        if dau is not None and dau > value:
            raise ValueError("DAU не может быть больше MAU.")
    return value


def _validate_arpu(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "revenue":
        return _require_non_negative(value, "Доход не может быть отрицательным.")
    if question_key == "users_count":
        return _require_positive(value, "Количество пользователей должно быть больше нуля.")
    return value


def _validate_arppu(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "revenue":
        return _require_non_negative(value, "Доход не может быть отрицательным.")
    if question_key == "paying_users":
        return _require_positive(value, "Количество платящих пользователей должно быть больше нуля.")
    return value


def _validate_ltv(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "arpu_value":
        return _require_non_negative(value, "ARPU не может быть отрицательным.")
    if question_key == "lifetime":
        return _require_positive(value, "Срок жизни пользователя должен быть больше нуля.")
    return value


def _validate_cac(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "acquisition_costs":
        return _require_non_negative(value, "Расходы на привлечение не могут быть отрицательными.")
    if question_key == "acquired_users":
        return _require_positive(value, "Количество привлеченных пользователей должно быть больше нуля.")
    return value


def _validate_aov(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "revenue":
        return _require_non_negative(value, "Выручка не может быть отрицательной.")
    if question_key == "orders_count":
        return _require_positive(value, "Количество заказов должно быть больше нуля.")
    return value


def _validate_payback(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "cac_value":
        return _require_non_negative(value, "CAC не может быть отрицательным.")
    if question_key == "monthly_margin":
        return _require_positive(value, "Ежемесячная маржа должна быть больше нуля.")
    return value


def _validate_runway(
    question_key: str,
    value: Decimal,
    answers: dict[str, Decimal],
) -> Decimal:
    if question_key == "cash_reserve":
        return _require_non_negative(value, "Денежный запас не может быть отрицательным.")
    if question_key == "monthly_burn":
        return _require_positive(value, "Ежемесячный burn должен быть больше нуля.")
    return value


def _render_pct_of_result(title: str, answers: dict[str, Decimal]) -> str:
    base_value = answers["base_value"]
    percent = answers["percent"]
    result = base_value * percent / Decimal("100")
    return _render_result_screen(
        title,
        [
            render_label_block("Число", format_number(base_value)),
            render_label_block("Процент", f"{format_number(percent)}%"),
        ],
        [render_label_block("Результат", format_number(result))],
    )


def _render_growth_result(title: str, answers: dict[str, Decimal]) -> str:
    start_value = answers["start_value"]
    end_value = answers["end_value"]
    delta = end_value - start_value
    growth_percent = delta / start_value * Decimal("100")
    return _render_result_screen(
        title,
        [
            render_label_block("Начальное значение", format_number(start_value)),
            render_label_block("Конечное значение", format_number(end_value)),
        ],
        [
            render_label_block("Изменение", format_number(delta)),
            render_label_block("Рост", f"{format_number(growth_percent)}%"),
        ],
    )


def _render_discount_result(title: str, answers: dict[str, Decimal]) -> str:
    original_price = answers["original_price"]
    discount_percent = answers["discount_percent"]
    discount_amount = original_price * discount_percent / Decimal("100")
    final_price = original_price - discount_amount
    return _render_result_screen(
        title,
        [
            render_label_block("Исходная цена", format_number(original_price)),
            render_label_block("Скидка", f"{format_number(discount_percent)}%"),
        ],
        [
            render_label_block("Экономия", format_number(discount_amount)),
            render_label_block("Итоговая цена", format_number(final_price)),
        ],
    )


def _render_conversion_result(title: str, answers: dict[str, Decimal]) -> str:
    total_count = answers["total_count"]
    target_count = answers["target_count"]
    conversion = target_count / total_count * Decimal("100")
    return _render_result_screen(
        title,
        [
            render_label_block("Общее количество", format_number(total_count)),
            render_label_block("Целевые действия", format_number(target_count)),
        ],
        [render_label_block("Конверсия", f"{format_number(conversion)}%")],
    )


def _render_ctr_result(title: str, answers: dict[str, Decimal]) -> str:
    impressions = answers["impressions"]
    clicks = answers["clicks"]
    ctr = clicks / impressions * Decimal("100")
    return _render_result_screen(
        title,
        [
            render_label_block("Показы", format_number(impressions)),
            render_label_block("Клики", format_number(clicks)),
        ],
        [render_label_block("CTR", f"{format_number(ctr)}%")],
    )


def _render_cpl_result(title: str, answers: dict[str, Decimal]) -> str:
    spend = answers["spend"]
    leads = answers["leads"]
    cpl = spend / leads
    return _render_result_screen(
        title,
        [
            render_label_block("Расходы", format_number(spend)),
            render_label_block("Лиды", format_number(leads)),
        ],
        [render_label_block("CPL", format_number(cpl))],
    )


def _render_roi_result(title: str, answers: dict[str, Decimal]) -> str:
    revenue = answers["revenue"]
    costs = answers["costs"]
    profit = revenue - costs
    roi = profit / costs * Decimal("100")
    return _render_result_screen(
        title,
        [
            render_label_block("Доход", format_number(revenue)),
            render_label_block("Затраты", format_number(costs)),
        ],
        [
            render_label_block("Прибыль", format_number(profit)),
            render_label_block("ROI", f"{format_number(roi)}%"),
        ],
    )


def _render_retention_result(title: str, answers: dict[str, Decimal]) -> str:
    base_users = answers["base_users"]
    retained_users = answers["retained_users"]
    retention = retained_users / base_users * Decimal("100")
    lost_users = base_users - retained_users
    return _render_result_screen(
        title,
        [
            render_label_block("База периода", format_number(base_users)),
            render_label_block("Вернувшиеся пользователи", format_number(retained_users)),
        ],
        [
            render_label_block("Retention", f"{format_number(retention)}%"),
            render_label_block("Не вернулись", format_number(lost_users)),
        ],
    )


def _render_churn_result(title: str, answers: dict[str, Decimal]) -> str:
    base_users = answers["base_users"]
    lost_users = answers["lost_users"]
    churn = lost_users / base_users * Decimal("100")
    retained_users = base_users - lost_users
    return _render_result_screen(
        title,
        [
            render_label_block("База периода", format_number(base_users)),
            render_label_block("Ушедшие пользователи", format_number(lost_users)),
        ],
        [
            render_label_block("Churn", f"{format_number(churn)}%"),
            render_label_block("Остались активными", format_number(retained_users)),
        ],
    )


def _render_stickiness_result(title: str, answers: dict[str, Decimal]) -> str:
    dau = answers["dau"]
    mau = answers["mau"]
    stickiness = dau / mau * Decimal("100")
    return _render_result_screen(
        title,
        [
            render_label_block("DAU", format_number(dau)),
            render_label_block("MAU", format_number(mau)),
        ],
        [render_label_block("Stickiness", f"{format_number(stickiness)}%")],
    )


def _render_arpu_result(title: str, answers: dict[str, Decimal]) -> str:
    revenue = answers["revenue"]
    users_count = answers["users_count"]
    arpu = revenue / users_count
    return _render_result_screen(
        title,
        [
            render_label_block("Доход", format_number(revenue)),
            render_label_block("Активные пользователи", format_number(users_count)),
        ],
        [render_label_block("ARPU", format_number(arpu))],
    )


def _render_arppu_result(title: str, answers: dict[str, Decimal]) -> str:
    revenue = answers["revenue"]
    paying_users = answers["paying_users"]
    arppu = revenue / paying_users
    return _render_result_screen(
        title,
        [
            render_label_block("Доход", format_number(revenue)),
            render_label_block("Платящие пользователи", format_number(paying_users)),
        ],
        [render_label_block("ARPPU", format_number(arppu))],
    )


def _render_ltv_result(title: str, answers: dict[str, Decimal]) -> str:
    arpu_value = answers["arpu_value"]
    lifetime = answers["lifetime"]
    ltv = arpu_value * lifetime
    return _render_result_screen(
        title,
        [
            render_label_block("ARPU", format_number(arpu_value)),
            render_label_block("Средний срок жизни", format_number(lifetime)),
        ],
        [render_label_block("LTV", format_number(ltv))],
    )


def _render_cac_result(title: str, answers: dict[str, Decimal]) -> str:
    acquisition_costs = answers["acquisition_costs"]
    acquired_users = answers["acquired_users"]
    cac = acquisition_costs / acquired_users
    return _render_result_screen(
        title,
        [
            render_label_block("Расходы на привлечение", format_number(acquisition_costs)),
            render_label_block("Привлеченные пользователи", format_number(acquired_users)),
        ],
        [render_label_block("CAC", format_number(cac))],
    )


def _render_aov_result(title: str, answers: dict[str, Decimal]) -> str:
    revenue = answers["revenue"]
    orders_count = answers["orders_count"]
    aov = revenue / orders_count
    return _render_result_screen(
        title,
        [
            render_label_block("Выручка", format_number(revenue)),
            render_label_block("Заказы", format_number(orders_count)),
        ],
        [render_label_block("AOV", format_number(aov))],
    )


def _render_payback_result(title: str, answers: dict[str, Decimal]) -> str:
    cac_value = answers["cac_value"]
    monthly_margin = answers["monthly_margin"]
    payback_months = cac_value / monthly_margin
    payback_days = payback_months * Decimal("30")
    return _render_result_screen(
        title,
        [
            render_label_block("CAC", format_number(cac_value)),
            render_label_block("Ежемесячная маржа", format_number(monthly_margin)),
        ],
        [
            render_label_block("Окупаемость", f"{format_number(payback_months)} мес."),
            render_label_block("Примерно в днях", f"{format_number(payback_days, precision=0)} дн."),
        ],
    )


def _render_runway_result(title: str, answers: dict[str, Decimal]) -> str:
    cash_reserve = answers["cash_reserve"]
    monthly_burn = answers["monthly_burn"]
    runway_months = cash_reserve / monthly_burn
    runway_days = runway_months * Decimal("30")
    return _render_result_screen(
        title,
        [
            render_label_block("Денежный запас", format_number(cash_reserve)),
            render_label_block("Ежемесячный burn", format_number(monthly_burn)),
        ],
        [
            render_label_block("Runway", f"{format_number(runway_months)} мес."),
            render_label_block("Примерно в днях", f"{format_number(runway_days, precision=0)} дн."),
        ],
    )


VALIDATORS: dict[str, Callable[[str, Decimal, dict[str, Decimal]], Decimal]] = {
    "growth": _validate_growth,
    "discount": _validate_discount,
    "conversion": _validate_conversion,
    "ctr": _validate_ctr,
    "cpl": _validate_cpl,
    "roi": _validate_roi,
    "retention": _validate_retention,
    "churn": _validate_churn,
    "stickiness": _validate_stickiness,
    "arpu": _validate_arpu,
    "arppu": _validate_arppu,
    "ltv": _validate_ltv,
    "cac": _validate_cac,
    "aov": _validate_aov,
    "payback": _validate_payback,
    "runway": _validate_runway,
}


RESULT_RENDERERS: dict[str, Callable[[str, dict[str, Decimal]], str]] = {
    "pct_of": _render_pct_of_result,
    "growth": _render_growth_result,
    "discount": _render_discount_result,
    "conversion": _render_conversion_result,
    "ctr": _render_ctr_result,
    "cpl": _render_cpl_result,
    "roi": _render_roi_result,
    "retention": _render_retention_result,
    "churn": _render_churn_result,
    "stickiness": _render_stickiness_result,
    "arpu": _render_arpu_result,
    "arppu": _render_arppu_result,
    "ltv": _render_ltv_result,
    "cac": _render_cac_result,
    "aov": _render_aov_result,
    "payback": _render_payback_result,
    "runway": _render_runway_result,
}
