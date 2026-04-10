from __future__ import annotations

from data.models import ChoiceOption, TemplateQuestion


YES_NO_CHOICES = (
    ChoiceOption(value="yes", label="Да"),
    ChoiceOption(value="no", label="Нет"),
)


TEMPLATE_SCENARIOS: dict[str, tuple[TemplateQuestion, ...]] = {
    "hypothesis": (
        TemplateQuestion(key="change", question="Что мы хотим изменить?"),
        TemplateQuestion(key="segment", question="Для какого сегмента пользователей?"),
        TemplateQuestion(key="behavior", question="Какое поведение должно измениться?"),
        TemplateQuestion(key="reason", question="Почему это должно произойти?"),
        TemplateQuestion(
            key="primary_metrics",
            question="На какие основные метрики это должно повлиять?",
        ),
        TemplateQuestion(
            key="secondary_metrics",
            question="Какие вторичные метрики или эффекты ожидаются?",
        ),
        TemplateQuestion(
            key="risks",
            question="Какие есть риски или ограничения?",
        ),
    ),
    "feature_draft": (
        TemplateQuestion(key="feature_name", question="Как называется фича?"),
        TemplateQuestion(key="problem", question="В чем основная проблема?"),
        TemplateQuestion(
            key="importance",
            question="Почему это важно для бизнеса или продукта?",
        ),
        TemplateQuestion(key="solution", question="Какое решение предлагается?"),
        TemplateQuestion(
            key="user_path_change",
            question="Что изменится в пути пользователя?",
        ),
        TemplateQuestion(
            key="target_metrics",
            question="На какие метрики хотим повлиять?",
        ),
        TemplateQuestion(
            key="risks",
            question="Какие есть риски и ограничения?",
        ),
        TemplateQuestion(
            key="open_questions",
            question="Какие есть открытые вопросы?",
        ),
    ),
    "feature_goals": (
        TemplateQuestion(key="change", question="Что именно меняем?"),
        TemplateQuestion(
            key="segment",
            question="Для какого сегмента это изменение?",
        ),
        TemplateQuestion(
            key="behavior",
            question="Какое поведение хотим изменить?",
        ),
        TemplateQuestion(
            key="reason",
            question="Почему это должно сработать?",
        ),
        TemplateQuestion(
            key="metrics",
            question="На какие метрики хотим повлиять?",
        ),
        TemplateQuestion(
            key="success_criteria",
            question="Как поймем, что решение сработало?",
        ),
    ),
    "analytic_conclusion": (
        TemplateQuestion(key="main_conclusion", question="Какой основной вывод?"),
        TemplateQuestion(key="data_fact", question="Что именно видно в данных?"),
        TemplateQuestion(key="importance", question="Почему это важно?"),
        TemplateQuestion(
            key="product_meaning",
            question="Что это значит для продукта?",
        ),
        TemplateQuestion(
            key="next_step",
            question="Какой следующий шаг логичен?",
        ),
    ),
    "dev_task": (
        TemplateQuestion(key="task", question="Что нужно сделать?"),
        TemplateQuestion(key="goal", question="Зачем это нужно?"),
        TemplateQuestion(
            key="current_behavior",
            question="Как это работает сейчас?",
        ),
        TemplateQuestion(
            key="expected_behavior",
            question="Как должно работать после изменения?",
        ),
        TemplateQuestion(
            key="done_criteria",
            question="Какие критерии готовности?",
        ),
        TemplateQuestion(
            key="constraints",
            question="Какие есть ограничения?",
        ),
        TemplateQuestion(
            key="open_questions",
            question="Какие есть открытые вопросы?",
        ),
    ),
    "design_task": (
        TemplateQuestion(
            key="context",
            question="В каком контексте возникла задача?",
        ),
        TemplateQuestion(key="problem", question="В чем проблема?"),
        TemplateQuestion(
            key="change_needed",
            question="Что нужно изменить?",
        ),
        TemplateQuestion(
            key="screen_or_block",
            question="На каком экране или в каком блоке?",
        ),
        TemplateQuestion(
            key="keep_constraints",
            question="Что важно сохранить?",
        ),
        TemplateQuestion(
            key="improvement_goal",
            question="Что хотим улучшить?",
        ),
        TemplateQuestion(
            key="expected_result",
            question="Какой ожидаемый результат?",
        ),
    ),
    "landing_brief": (
        TemplateQuestion(key="product", question="Что именно продвигаем или продаем?"),
        TemplateQuestion(key="audience", question="Для кого этот лендинг?"),
        TemplateQuestion(key="problem", question="Какая главная проблема или боль у этой аудитории?"),
        TemplateQuestion(key="promise", question="Какое ключевое обещание хотим донести?"),
        TemplateQuestion(key="proof", question="Какие есть кейсы, цифры, отзывы или траст-блоки?"),
        TemplateQuestion(key="sections_plan", question="Какие основные блоки должны быть на странице?"),
        TemplateQuestion(key="cta", question="Какое целевое действие должен сделать пользователь?"),
        TemplateQuestion(key="tone", question="Каким должен быть тон и стиль текста?"),
    ),
    "offer_message": (
        TemplateQuestion(key="audience", question="Для кого этот оффер?"),
        TemplateQuestion(key="problem", question="Какую проблему пользователя он должен закрывать?"),
        TemplateQuestion(key="solution", question="Что именно предлагаем?"),
        TemplateQuestion(key="result", question="Какой результат обещаем пользователю?"),
        TemplateQuestion(key="proof", question="Почему этому предложению можно верить?"),
        TemplateQuestion(key="cta", question="Какое целевое действие хотим получить?"),
    ),
    "icp_profile": (
        TemplateQuestion(key="segment", question="Какой это сегмент или тип клиента?"),
        TemplateQuestion(key="decision_maker", question="Кто принимает решение или выбирает продукт?"),
        TemplateQuestion(key="context", question="В каком контексте возникает потребность?"),
        TemplateQuestion(key="pain", question="Какая главная боль у этого сегмента?"),
        TemplateQuestion(key="success", question="Что для этого клиента считается хорошим результатом?"),
        TemplateQuestion(key="objections", question="Какие основные возражения могут быть?"),
        TemplateQuestion(key="trigger", question="Что обычно запускает интерес к решению?"),
    ),
    "business_message": (
        TemplateQuestion(
            key="greeting",
            question="Кому пишем или как обращаемся?",
        ),
        TemplateQuestion(key="context", question="Какой контекст?"),
        TemplateQuestion(
            key="request",
            question="В чем основная мысль или просьба?",
        ),
        TemplateQuestion(
            key="expectation",
            question="Есть ли срок или ожидание?",
        ),
        TemplateQuestion(
            key="closing",
            question="Как завершить сообщение?",
        ),
    ),
    "soft_reminder": (
        TemplateQuestion(key="greeting", question="Как обратиться?"),
        TemplateQuestion(
            key="reminder",
            question="О чем нужно напомнить?",
        ),
        TemplateQuestion(
            key="current_need",
            question="Что нужно сейчас?",
        ),
        TemplateQuestion(
            key="closing",
            question="Как мягко завершить сообщение?",
        ),
    ),
    "short_feedback": (
        TemplateQuestion(key="good", question="Что хорошо?"),
        TemplateQuestion(
            key="improve",
            question="Что стоит улучшить?",
        ),
        TemplateQuestion(
            key="importance",
            question="Почему это важно?",
        ),
        TemplateQuestion(
            key="next_step",
            question="Что предлагаешь дальше?",
        ),
    ),
    "polite_decline": (
        TemplateQuestion(key="gratitude", question="За что благодарим?"),
        TemplateQuestion(
            key="position",
            question="Как формулируем отказ?",
        ),
        TemplateQuestion(
            key="reason",
            question="Какая короткая причина?",
        ),
        TemplateQuestion(
            key="closing",
            question="Как вежливо завершить?",
        ),
    ),
    "meeting_summary": (
        TemplateQuestion(key="topic", question="Какая тема встречи?"),
        TemplateQuestion(key="discussion", question="Что обсудили?"),
        TemplateQuestion(
            key="conclusions",
            question="К каким выводам пришли?",
        ),
        TemplateQuestion(
            key="decisions",
            question="Какие решения приняты?",
        ),
        TemplateQuestion(
            key="next_steps",
            question="Какие следующие шаги?",
        ),
    ),
    "action_items": (
        TemplateQuestion(key="task", question="Какая задача?"),
        TemplateQuestion(key="owner", question="Кто ответственный?"),
        TemplateQuestion(key="deadline", question="Какой срок?"),
        TemplateQuestion(key="status", question="Какой статус?"),
        TemplateQuestion(
            key="comment",
            question="Нужен ли комментарий?",
        ),
    ),
    "startup_update": (
        TemplateQuestion(key="period", question="За какой период делаем апдейт?"),
        TemplateQuestion(key="focus", question="На чем был главный фокус?"),
        TemplateQuestion(key="wins", question="Что удалось сделать или получить за этот период?"),
        TemplateQuestion(key="metrics", question="Какие цифры или метрики важно показать?"),
        TemplateQuestion(key="blockers", question="Какие есть блокеры или ограничения?"),
        TemplateQuestion(key="decisions_needed", question="Какие решения или комментарии сейчас нужны?"),
        TemplateQuestion(key="next_steps", question="Какие следующие шаги?"),
        TemplateQuestion(key="ask", question="Какой запрос или просьба к команде?"),
    ),
    "doc_review_checklist": (
        TemplateQuestion(
            key="goal",
            question="Есть ли понятная цель?",
            choices=YES_NO_CHOICES,
        ),
        TemplateQuestion(
            key="problem",
            question="Есть ли проблема?",
            choices=YES_NO_CHOICES,
        ),
        TemplateQuestion(
            key="solution",
            question="Есть ли решение?",
            choices=YES_NO_CHOICES,
        ),
        TemplateQuestion(
            key="metrics",
            question="Есть ли влияние на метрики?",
            choices=YES_NO_CHOICES,
        ),
        TemplateQuestion(
            key="risks",
            question="Есть ли риски?",
            choices=YES_NO_CHOICES,
        ),
        TemplateQuestion(
            key="open_questions",
            question="Есть ли открытые вопросы?",
            choices=YES_NO_CHOICES,
        ),
    ),
}
