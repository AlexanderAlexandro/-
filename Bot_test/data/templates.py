from __future__ import annotations

from data.models import TemplateCategory, TemplateDefinition, TemplateSection


TEMPLATE_CATEGORIES: tuple[TemplateCategory, ...] = (
    TemplateCategory(id="product", title="Продуктовые"),
    TemplateCategory(id="communication", title="Коммуникация"),
    TemplateCategory(id="work", title="Рабочие"),
)


TEMPLATES: dict[str, TemplateDefinition] = {
    "hypothesis": TemplateDefinition(
        id="hypothesis",
        category_id="product",
        title="Шаблон гипотезы",
        use_case=(
            "Когда нужно описать ожидаемое влияние изменения на поведение "
            "пользователя и метрики."
        ),
        empty_template=(
            "Если мы сделаем:\n"
            "[изменение]\n\n"
            "То:\n"
            "[целевой сегмент пользователей]\n\n"
            "Будет:\n"
            "[ожидаемое изменение поведения]\n\n"
            "Потому что:\n"
            "[причина]\n\n"
            "В результате изменятся:\n"
            "[основные метрики]\n"
            "[вторичные метрики]\n\n"
            "Риски:\n"
            "[риски и ограничения]"
        ),
        sections=(
            TemplateSection(key="change", title="Если мы сделаем"),
            TemplateSection(key="segment", title="То"),
            TemplateSection(key="behavior", title="Будет"),
            TemplateSection(key="reason", title="Потому что"),
            TemplateSection(key="primary_metrics", title="Основные метрики"),
            TemplateSection(key="secondary_metrics", title="Вторичные метрики"),
            TemplateSection(key="risks", title="Риски"),
        ),
    ),
    "feature_draft": TemplateDefinition(
        id="feature_draft",
        category_id="product",
        title="Шаблон короткого драфта фичи",
        use_case="Когда нужно быстро зафиксировать идею фичи и рабочий контекст.",
        empty_template=(
            "Название фичи:\n"
            "[название]\n\n"
            "Проблема:\n"
            "[в чем проблема]\n\n"
            "Почему это важно:\n"
            "[бизнес-контекст]\n\n"
            "Предлагаемое решение:\n"
            "[что хотим сделать]\n\n"
            "Изменение пути пользователя:\n"
            "[что изменится для пользователя]\n\n"
            "Целевые метрики:\n"
            "[какие метрики должны измениться]\n\n"
            "Риски и ограничения:\n"
            "[что может помешать]\n\n"
            "Открытые вопросы:\n"
            "[что нужно уточнить]"
        ),
        sections=(
            TemplateSection(key="feature_name", title="Название фичи"),
            TemplateSection(key="problem", title="Проблема"),
            TemplateSection(key="importance", title="Почему это важно"),
            TemplateSection(key="solution", title="Предлагаемое решение"),
            TemplateSection(key="user_path_change", title="Изменение пути пользователя"),
            TemplateSection(key="target_metrics", title="Целевые метрики"),
            TemplateSection(key="risks", title="Риски и ограничения"),
            TemplateSection(key="open_questions", title="Открытые вопросы"),
        ),
    ),
    "feature_goals": TemplateDefinition(
        id="feature_goals",
        category_id="product",
        title="Шаблон целей фичи",
        use_case="Когда нужно коротко сформулировать цель изменения и критерий успеха.",
        empty_template=(
            "Что меняем:\n"
            "[изменение]\n\n"
            "Для кого:\n"
            "[сегмент]\n\n"
            "Какое поведение хотим изменить:\n"
            "[новое поведение]\n\n"
            "Почему это должно сработать:\n"
            "[обоснование]\n\n"
            "На какие метрики повлияет:\n"
            "[метрики]\n\n"
            "Критерий успеха:\n"
            "[как поймем, что гипотеза сработала]"
        ),
        sections=(
            TemplateSection(key="change", title="Что меняем"),
            TemplateSection(key="segment", title="Для кого"),
            TemplateSection(key="behavior", title="Какое поведение хотим изменить"),
            TemplateSection(key="reason", title="Почему это должно сработать"),
            TemplateSection(key="metrics", title="На какие метрики повлияет"),
            TemplateSection(key="success_criteria", title="Критерий успеха"),
        ),
    ),
    "analytic_conclusion": TemplateDefinition(
        id="analytic_conclusion",
        category_id="product",
        title="Шаблон аналитического вывода",
        use_case="Когда нужно быстро оформить вывод по данным и следующий шаг.",
        empty_template=(
            "Основной вывод:\n"
            "[главная мысль]\n\n"
            "Что видно в данных:\n"
            "[факт]\n\n"
            "Почему это важно:\n"
            "[значимость]\n\n"
            "Что это значит для продукта:\n"
            "[интерпретация]\n\n"
            "Следующий шаг:\n"
            "[рекомендуемое действие]"
        ),
        sections=(
            TemplateSection(key="main_conclusion", title="Основной вывод"),
            TemplateSection(key="data_fact", title="Что видно в данных"),
            TemplateSection(key="importance", title="Почему это важно"),
            TemplateSection(key="product_meaning", title="Что это значит для продукта"),
            TemplateSection(key="next_step", title="Следующий шаг"),
        ),
    ),
    "dev_task": TemplateDefinition(
        id="dev_task",
        category_id="product",
        title="Шаблон задачи разработчику",
        use_case="Когда нужно поставить понятную задачу разработчику без лишних уточнений.",
        empty_template=(
            "Что нужно сделать:\n"
            "[задача]\n\n"
            "Зачем это нужно:\n"
            "[цель]\n\n"
            "Текущее поведение:\n"
            "[как работает сейчас]\n\n"
            "Ожидаемое поведение:\n"
            "[как должно работать]\n\n"
            "Критерии готовности:\n"
            "[definition of done]\n\n"
            "Ограничения:\n"
            "[важные условия]\n\n"
            "Открытые вопросы:\n"
            "[неясности]"
        ),
        sections=(
            TemplateSection(key="task", title="Что нужно сделать"),
            TemplateSection(key="goal", title="Зачем это нужно"),
            TemplateSection(key="current_behavior", title="Текущее поведение"),
            TemplateSection(key="expected_behavior", title="Ожидаемое поведение"),
            TemplateSection(key="done_criteria", title="Критерии готовности"),
            TemplateSection(key="constraints", title="Ограничения"),
            TemplateSection(key="open_questions", title="Открытые вопросы"),
        ),
    ),
    "design_task": TemplateDefinition(
        id="design_task",
        category_id="product",
        title="Шаблон задачи дизайнеру",
        use_case="Когда нужно кратко описать задачу дизайнеру и ожидаемый эффект.",
        empty_template=(
            "Контекст:\n"
            "[где и в каком сценарии проблема]\n\n"
            "Проблема:\n"
            "[что неудобно или не работает]\n\n"
            "Что нужно изменить:\n"
            "[суть изменений]\n\n"
            "Экран или блок:\n"
            "[где именно]\n\n"
            "Что важно сохранить:\n"
            "[ограничения]\n\n"
            "Что хотим улучшить:\n"
            "[ожидаемый эффект]\n\n"
            "Ожидаемый результат:\n"
            "[как поймем, что стало лучше]"
        ),
        sections=(
            TemplateSection(key="context", title="Контекст"),
            TemplateSection(key="problem", title="Проблема"),
            TemplateSection(key="change_needed", title="Что нужно изменить"),
            TemplateSection(key="screen_or_block", title="Экран или блок"),
            TemplateSection(key="keep_constraints", title="Что важно сохранить"),
            TemplateSection(key="improvement_goal", title="Что хотим улучшить"),
            TemplateSection(key="expected_result", title="Ожидаемый результат"),
        ),
    ),
    "landing_brief": TemplateDefinition(
        id="landing_brief",
        category_id="product",
        title="Бриф лендинга",
        use_case="Когда нужно быстро собрать рабочий бриф для лендинга перед дизайном, генерацией или копирайтингом.",
        empty_template=(
            "Продукт или предложение:\n"
            "[что продвигаем]\n\n"
            "Для кого:\n"
            "[целевая аудитория]\n\n"
            "Главная проблема:\n"
            "[основная боль]\n\n"
            "Ключевое обещание:\n"
            "[что обещаем пользователю]\n\n"
            "Доказательства:\n"
            "[кейсы, цифры, отзывы, траст-блоки]\n\n"
            "Основные блоки страницы:\n"
            "[какие блоки должны быть]\n\n"
            "Целевое действие:\n"
            "[что должен сделать пользователь]\n\n"
            "Тон и стиль:\n"
            "[каким должен быть текст]"
        ),
        sections=(
            TemplateSection(key="product", title="Продукт или предложение"),
            TemplateSection(key="audience", title="Для кого"),
            TemplateSection(key="problem", title="Главная проблема"),
            TemplateSection(key="promise", title="Ключевое обещание"),
            TemplateSection(key="proof", title="Доказательства"),
            TemplateSection(key="sections_plan", title="Основные блоки страницы"),
            TemplateSection(key="cta", title="Целевое действие"),
            TemplateSection(key="tone", title="Тон и стиль"),
        ),
    ),
    "offer_message": TemplateDefinition(
        id="offer_message",
        category_id="product",
        title="Формулировка оффера",
        use_case="Когда нужно быстро собрать понятный оффер для лендинга, рекламы или обсуждения в команде.",
        empty_template=(
            "Для кого:\n"
            "[сегмент]\n\n"
            "Какая проблема:\n"
            "[боль]\n\n"
            "Что предлагаем:\n"
            "[решение]\n\n"
            "Какой результат обещаем:\n"
            "[ценность]\n\n"
            "Почему нам можно верить:\n"
            "[доказательства]\n\n"
            "Целевое действие:\n"
            "[что просим сделать]"
        ),
        sections=(
            TemplateSection(key="audience", title="Для кого"),
            TemplateSection(key="problem", title="Какая проблема"),
            TemplateSection(key="solution", title="Что предлагаем"),
            TemplateSection(key="result", title="Какой результат обещаем"),
            TemplateSection(key="proof", title="Почему нам можно верить"),
            TemplateSection(key="cta", title="Целевое действие"),
        ),
    ),
    "icp_profile": TemplateDefinition(
        id="icp_profile",
        category_id="product",
        title="Портрет ICP",
        use_case="Когда нужно зафиксировать, для кого делаем продукт, лендинг или предложение.",
        empty_template=(
            "Сегмент:\n"
            "[кто это]\n\n"
            "Роль или лицо, принимающее решение:\n"
            "[кто выбирает или покупает]\n\n"
            "Контекст использования:\n"
            "[в какой ситуации возникает задача]\n\n"
            "Главная боль:\n"
            "[что мешает сейчас]\n\n"
            "Что считается успехом:\n"
            "[какой результат нужен]\n\n"
            "Основные возражения:\n"
            "[что мешает купить или попробовать]\n\n"
            "Триггер интереса:\n"
            "[что запускает поиск решения]"
        ),
        sections=(
            TemplateSection(key="segment", title="Сегмент"),
            TemplateSection(key="decision_maker", title="Роль или лицо, принимающее решение"),
            TemplateSection(key="context", title="Контекст использования"),
            TemplateSection(key="pain", title="Главная боль"),
            TemplateSection(key="success", title="Что считается успехом"),
            TemplateSection(key="objections", title="Основные возражения"),
            TemplateSection(key="trigger", title="Триггер интереса"),
        ),
    ),
    "business_message": TemplateDefinition(
        id="business_message",
        category_id="communication",
        title="Шаблон делового сообщения",
        use_case="Когда нужно быстро собрать короткое деловое сообщение.",
        empty_template=(
            "Привет:\n"
            "[обращение]\n\n"
            "Контекст:\n"
            "[почему пишу]\n\n"
            "Основная мысль или просьба:\n"
            "[суть]\n\n"
            "Ожидание или срок:\n"
            "[что и когда нужно]\n\n"
            "Завершение:\n"
            "[финальная фраза]"
        ),
        sections=(
            TemplateSection(key="greeting", title="Привет"),
            TemplateSection(key="context", title="Контекст"),
            TemplateSection(key="request", title="Основная мысль или просьба"),
            TemplateSection(key="expectation", title="Ожидание или срок"),
            TemplateSection(key="closing", title="Завершение"),
        ),
    ),
    "soft_reminder": TemplateDefinition(
        id="soft_reminder",
        category_id="communication",
        title="Шаблон мягкого напоминания",
        use_case="Когда нужно напомнить без давления и лишней жесткости.",
        empty_template=(
            "Привет:\n"
            "[обращение]\n\n"
            "Напоминание:\n"
            "[о чем идет речь]\n\n"
            "Что нужно сейчас:\n"
            "[запрос]\n\n"
            "Завершение:\n"
            "[мягкое завершение]"
        ),
        sections=(
            TemplateSection(key="greeting", title="Привет"),
            TemplateSection(key="reminder", title="Напоминание"),
            TemplateSection(key="current_need", title="Что нужно сейчас"),
            TemplateSection(key="closing", title="Завершение"),
        ),
    ),
    "short_feedback": TemplateDefinition(
        id="short_feedback",
        category_id="communication",
        title="Шаблон короткого фидбэка",
        use_case="Когда нужно дать короткий, конструктивный и понятный фидбэк.",
        empty_template=(
            "Что хорошо:\n"
            "[сильная сторона]\n\n"
            "Что стоит улучшить:\n"
            "[слабая сторона]\n\n"
            "Почему это важно:\n"
            "[обоснование]\n\n"
            "Что предлагаю:\n"
            "[следующий шаг]"
        ),
        sections=(
            TemplateSection(key="good", title="Что хорошо"),
            TemplateSection(key="improve", title="Что стоит улучшить"),
            TemplateSection(key="importance", title="Почему это важно"),
            TemplateSection(key="next_step", title="Что предлагаю"),
        ),
    ),
    "polite_decline": TemplateDefinition(
        id="polite_decline",
        category_id="communication",
        title="Шаблон вежливого отказа",
        use_case="Когда нужно отказать коротко, уважительно и без лишнего напряжения.",
        empty_template=(
            "Благодарность:\n"
            "[спасибо за предложение]\n\n"
            "Позиция:\n"
            "[не могу / не подхожу]\n\n"
            "Короткая причина:\n"
            "[почему]\n\n"
            "Завершение:\n"
            "[вежливая финальная фраза]"
        ),
        sections=(
            TemplateSection(key="gratitude", title="Благодарность"),
            TemplateSection(key="position", title="Позиция"),
            TemplateSection(key="reason", title="Короткая причина"),
            TemplateSection(key="closing", title="Завершение"),
        ),
    ),
    "meeting_summary": TemplateDefinition(
        id="meeting_summary",
        category_id="work",
        title="Шаблон саммари встречи",
        use_case="Когда нужно быстро оформить итоги встречи и следующие шаги.",
        empty_template=(
            "Тема:\n"
            "[тема]\n\n"
            "Что обсудили:\n"
            "[основные вопросы]\n\n"
            "К каким выводам пришли:\n"
            "[выводы]\n\n"
            "Какие решения приняты:\n"
            "[решения]\n\n"
            "Следующие шаги:\n"
            "[action items]"
        ),
        sections=(
            TemplateSection(key="topic", title="Тема"),
            TemplateSection(key="discussion", title="Что обсудили"),
            TemplateSection(key="conclusions", title="К каким выводам пришли"),
            TemplateSection(key="decisions", title="Какие решения приняты"),
            TemplateSection(key="next_steps", title="Следующие шаги"),
        ),
    ),
    "action_items": TemplateDefinition(
        id="action_items",
        category_id="work",
        title="Шаблон action items",
        use_case="Когда нужно быстро собрать одну рабочую задачу в понятной форме.",
        empty_template=(
            "Задача:\n"
            "[что сделать]\n\n"
            "Ответственный:\n"
            "[кто делает]\n\n"
            "Срок:\n"
            "[когда]\n\n"
            "Статус:\n"
            "[статус]\n\n"
            "Комментарий:\n"
            "[дополнение]"
        ),
        sections=(
            TemplateSection(key="task", title="Задача"),
            TemplateSection(key="owner", title="Ответственный"),
            TemplateSection(key="deadline", title="Срок"),
            TemplateSection(key="status", title="Статус"),
            TemplateSection(key="comment", title="Комментарий"),
        ),
    ),
    "startup_update": TemplateDefinition(
        id="startup_update",
        category_id="work",
        title="Апдейт по запуску стартапа",
        use_case="Когда нужно быстро отправить в чат понятный апдейт по запуску без длинного пересказа.",
        empty_template=(
            "Период:\n"
            "[за какой период апдейт]\n\n"
            "Главный фокус:\n"
            "[на чем была основная работа]\n\n"
            "Что удалось:\n"
            "[главный результат]\n\n"
            "Метрики:\n"
            "[цифры за период]\n\n"
            "Блокеры:\n"
            "[что мешает]\n\n"
            "Что нужно решить:\n"
            "[где нужна обратная связь или решение]\n\n"
            "Следующие шаги:\n"
            "[что делаем дальше]\n\n"
            "Запрос к команде:\n"
            "[какая помощь нужна]"
        ),
        sections=(
            TemplateSection(key="period", title="Период"),
            TemplateSection(key="focus", title="Главный фокус"),
            TemplateSection(key="wins", title="Что удалось"),
            TemplateSection(key="metrics", title="Метрики"),
            TemplateSection(key="blockers", title="Блокеры"),
            TemplateSection(key="decisions_needed", title="Что нужно решить"),
            TemplateSection(key="next_steps", title="Следующие шаги"),
            TemplateSection(key="ask", title="Запрос к команде"),
        ),
    ),
    "doc_review_checklist": TemplateDefinition(
        id="doc_review_checklist",
        category_id="work",
        title="Шаблон чек-листа ревью документа",
        use_case="Когда нужно быстро проверить, хватает ли базовых блоков в документе.",
        empty_template=(
            "Есть ли понятная цель?\n"
            "[да / нет]\n\n"
            "Есть ли проблема?\n"
            "[да / нет]\n\n"
            "Есть ли решение?\n"
            "[да / нет]\n\n"
            "Есть ли влияние на метрики?\n"
            "[да / нет]\n\n"
            "Есть ли риски?\n"
            "[да / нет]\n\n"
            "Есть ли открытые вопросы?\n"
            "[да / нет]"
        ),
        sections=(
            TemplateSection(key="goal", title="Есть ли понятная цель"),
            TemplateSection(key="problem", title="Есть ли проблема"),
            TemplateSection(key="solution", title="Есть ли решение"),
            TemplateSection(key="metrics", title="Есть ли влияние на метрики"),
            TemplateSection(key="risks", title="Есть ли риски"),
            TemplateSection(key="open_questions", title="Есть ли открытые вопросы"),
        ),
    ),
}
