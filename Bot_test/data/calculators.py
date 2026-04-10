from __future__ import annotations

from data.models import CalculatorDefinition, CalculatorQuestion


CALCULATORS: dict[str, CalculatorDefinition] = {
    "pct_of": CalculatorDefinition(
        id="pct_of",
        title="Процент от числа",
        description="Показывает, сколько составляет указанный процент от числа.",
        formula_hint="Формула: число × процент / 100",
        questions=(
            CalculatorQuestion(key="base_value", question="Введите число."),
            CalculatorQuestion(key="percent", question="Введите процент."),
        ),
    ),
    "growth": CalculatorDefinition(
        id="growth",
        title="Рост между двумя числами",
        description="Считает абсолютное изменение и рост или падение в процентах.",
        formula_hint="Формула: (новое - старое) / старое × 100%",
        questions=(
            CalculatorQuestion(
                key="start_value",
                question="Введите начальное значение.",
            ),
            CalculatorQuestion(
                key="end_value",
                question="Введите конечное значение.",
            ),
        ),
    ),
    "discount": CalculatorDefinition(
        id="discount",
        title="Скидка",
        description="Считает размер скидки и итоговую цену после нее.",
        formula_hint="Формула: цена - (цена × скидка / 100)",
        questions=(
            CalculatorQuestion(
                key="original_price",
                question="Введите исходную цену.",
            ),
            CalculatorQuestion(
                key="discount_percent",
                question="Введите размер скидки в процентах.",
            ),
        ),
    ),
    "conversion": CalculatorDefinition(
        id="conversion",
        title="Конверсия",
        description="Считает долю целевых действий от общего количества.",
        formula_hint="Формула: целевые действия / общее количество × 100%",
        questions=(
            CalculatorQuestion(
                key="total_count",
                question="Введите общее количество.",
            ),
            CalculatorQuestion(
                key="target_count",
                question="Введите количество целевых действий.",
            ),
        ),
    ),
    "ctr": CalculatorDefinition(
        id="ctr",
        title="CTR",
        description="Считает кликабельность по количеству показов и кликов.",
        formula_hint="Формула: клики / показы × 100%",
        questions=(
            CalculatorQuestion(
                key="impressions",
                question="Введите количество показов.",
            ),
            CalculatorQuestion(
                key="clicks",
                question="Введите количество кликов.",
            ),
        ),
    ),
    "cpl": CalculatorDefinition(
        id="cpl",
        title="CPL",
        description="Считает стоимость одного лида по расходам и количеству лидов.",
        formula_hint="Формула: расходы / количество лидов",
        questions=(
            CalculatorQuestion(
                key="spend",
                question="Введите рекламные расходы.",
            ),
            CalculatorQuestion(
                key="leads",
                question="Введите количество лидов.",
            ),
        ),
    ),
    "roi": CalculatorDefinition(
        id="roi",
        title="ROI",
        description="Считает возврат инвестиций по доходу и затратам.",
        formula_hint="Формула: (доход - затраты) / затраты × 100%",
        questions=(
            CalculatorQuestion(key="revenue", question="Введите доход."),
            CalculatorQuestion(key="costs", question="Введите затраты."),
        ),
    ),
    "retention": CalculatorDefinition(
        id="retention",
        title="Retention",
        description="Считает долю пользователей, которые вернулись в выбранный период.",
        formula_hint="Формула: вернувшиеся пользователи / база периода × 100%",
        questions=(
            CalculatorQuestion(
                key="base_users",
                question="Введите размер базы пользователей в начале периода.",
            ),
            CalculatorQuestion(
                key="retained_users",
                question="Введите количество пользователей, которые вернулись.",
            ),
        ),
    ),
    "churn": CalculatorDefinition(
        id="churn",
        title="Churn rate",
        description="Считает долю пользователей, которые перестали пользоваться продуктом.",
        formula_hint="Формула: ушедшие пользователи / база периода × 100%",
        questions=(
            CalculatorQuestion(
                key="base_users",
                question="Введите размер базы пользователей в начале периода.",
            ),
            CalculatorQuestion(
                key="lost_users",
                question="Введите количество ушедших пользователей.",
            ),
        ),
    ),
    "stickiness": CalculatorDefinition(
        id="stickiness",
        title="Stickiness DAU/MAU",
        description="Считает липкость продукта по соотношению DAU к MAU.",
        formula_hint="Формула: DAU / MAU × 100%",
        questions=(
            CalculatorQuestion(key="dau", question="Введите DAU."),
            CalculatorQuestion(key="mau", question="Введите MAU."),
        ),
    ),
    "arpu": CalculatorDefinition(
        id="arpu",
        title="ARPU",
        description="Считает средний доход на одного активного пользователя.",
        formula_hint="Формула: доход / количество пользователей",
        questions=(
            CalculatorQuestion(
                key="revenue",
                question="Введите суммарный доход за период.",
            ),
            CalculatorQuestion(
                key="users_count",
                question="Введите количество активных пользователей за период.",
            ),
        ),
    ),
    "arppu": CalculatorDefinition(
        id="arppu",
        title="ARPPU",
        description="Считает средний доход на одного платящего пользователя.",
        formula_hint="Формула: доход / количество платящих пользователей",
        questions=(
            CalculatorQuestion(
                key="revenue",
                question="Введите суммарный доход за период.",
            ),
            CalculatorQuestion(
                key="paying_users",
                question="Введите количество платящих пользователей.",
            ),
        ),
    ),
    "ltv": CalculatorDefinition(
        id="ltv",
        title="LTV",
        description="Считает lifetime value по ARPU и среднему сроку жизни пользователя.",
        formula_hint="Формула: ARPU × средний срок жизни",
        questions=(
            CalculatorQuestion(
                key="arpu_value",
                question="Введите ARPU за период.",
            ),
            CalculatorQuestion(
                key="lifetime",
                question="Введите средний срок жизни пользователя в периодах.",
            ),
        ),
    ),
    "cac": CalculatorDefinition(
        id="cac",
        title="CAC",
        description="Считает стоимость привлечения одного пользователя.",
        formula_hint="Формула: расходы на привлечение / количество привлеченных пользователей",
        questions=(
            CalculatorQuestion(
                key="acquisition_costs",
                question="Введите расходы на привлечение.",
            ),
            CalculatorQuestion(
                key="acquired_users",
                question="Введите количество привлеченных пользователей.",
            ),
        ),
    ),
    "aov": CalculatorDefinition(
        id="aov",
        title="AOV",
        description="Считает средний чек по выручке и количеству заказов.",
        formula_hint="Формула: выручка / количество заказов",
        questions=(
            CalculatorQuestion(
                key="revenue",
                question="Введите общую выручку.",
            ),
            CalculatorQuestion(
                key="orders_count",
                question="Введите количество заказов.",
            ),
        ),
    ),
    "payback": CalculatorDefinition(
        id="payback",
        title="Payback CAC",
        description="Считает срок окупаемости привлечения по CAC и ежемесячной марже на клиента.",
        formula_hint="Формула: CAC / ежемесячная маржа на клиента",
        questions=(
            CalculatorQuestion(
                key="cac_value",
                question="Введите CAC.",
            ),
            CalculatorQuestion(
                key="monthly_margin",
                question="Введите ежемесячную маржу с одного клиента.",
            ),
        ),
    ),
    "runway": CalculatorDefinition(
        id="runway",
        title="Runway",
        description="Считает, на сколько месяцев хватит текущего денежного запаса.",
        formula_hint="Формула: денежный запас / ежемесячный burn",
        questions=(
            CalculatorQuestion(
                key="cash_reserve",
                question="Введите текущий денежный запас.",
            ),
            CalculatorQuestion(
                key="monthly_burn",
                question="Введите ежемесячный burn.",
            ),
        ),
    ),
}
