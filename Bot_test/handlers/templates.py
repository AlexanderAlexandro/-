from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from data.ui_texts import EMPTY_INPUT_TEXT
from keyboards.common import flow_keyboard, result_keyboard
from keyboards.templates import (
    template_actions_keyboard,
    template_build_intro_keyboard,
    template_categories_keyboard,
    template_list_keyboard,
    template_preview_keyboard,
)
from services.report_service import send_owner_report
from services.static_service import get_templates_section_text
from services.template_service import (
    get_question,
    get_question_keys,
    get_template,
    list_templates_by_category,
    render_blank_template,
    render_build_intro,
    render_category_card,
    render_question,
    render_result,
    render_template_card,
    resolve_choice_label,
    resolve_typed_choice,
)
from utils.flow import trim_answers
from utils.messages import safe_edit_text
from utils.states import TemplateBuilderState


router = Router()


def _template_result_keyboard(template_id: str) -> InlineKeyboardMarkup:
    return result_keyboard(
        retry_callback=f"taction:{template_id}:build",
        section_callback="menu:templates",
        section_label="В шаблоны",
    )


def _template_flow_keyboard(template_id: str, step_index: int) -> InlineKeyboardMarkup:
    question = get_question(template_id, step_index)
    choice_buttons = None
    if question is not None and question.choices:
        choice_buttons = [(choice.value, choice.label) for choice in question.choices]

    return flow_keyboard(
        section_callback="menu:templates",
        section_label="В шаблоны",
        show_back=True,
        choice_buttons=choice_buttons,
    )


async def _show_template_step(
    *,
    callback: CallbackQuery | None = None,
    message: Message | None = None,
    template_id: str,
    step_index: int,
) -> None:
    text = render_question(template_id, step_index)
    reply_markup = _template_flow_keyboard(template_id, step_index)

    if callback is not None:
        await safe_edit_text(callback, text, reply_markup=reply_markup)
        return

    if message is not None:
        await message.answer(text, reply_markup=reply_markup)


async def _show_template_result(
    *,
    result_text: str,
    template_id: str,
    callback: CallbackQuery | None = None,
    message: Message | None = None,
) -> None:
    reply_markup = _template_result_keyboard(template_id)

    if callback is not None:
        await safe_edit_text(callback, result_text, reply_markup=reply_markup)
        return

    if message is not None:
        await message.answer(result_text, reply_markup=reply_markup)


async def _start_template_build(
    state: FSMContext,
    *,
    template_id: str,
) -> None:
    # Состояние живет только в памяти процесса и очищается после завершения сценария.
    await state.set_state(TemplateBuilderState.awaiting_answer)
    await state.set_data(
        {
            "template_id": template_id,
            "step_index": 0,
            "answers": {},
        }
    )


async def _process_template_answer(
    *,
    state: FSMContext,
    template_id: str,
    step_index: int,
    answers: dict[str, str],
    answer_value: str,
    callback: CallbackQuery | None = None,
    message: Message | None = None,
) -> None:
    question = get_question(template_id, step_index)
    if question is None:
        await state.clear()
        return

    answers[question.key] = answer_value
    next_step_index = step_index + 1

    if get_question(template_id, next_step_index) is None:
        await state.clear()
        result_text = render_result(template_id, answers)
        await _show_template_result(
            result_text=result_text,
            template_id=template_id,
            callback=callback,
            message=message,
        )
        template = get_template(template_id)
        if callback is not None:
            await send_owner_report(
                bot=callback.bot,
                section_title="Шаблоны",
                scenario_title=template.title if template else template_id,
                result_text=result_text,
                user=callback.from_user,
            )
        elif message is not None:
            await send_owner_report(
                bot=message.bot,
                section_title="Шаблоны",
                scenario_title=template.title if template else template_id,
                result_text=result_text,
                user=message.from_user,
            )
        return

    await state.update_data(step_index=next_step_index, answers=answers)
    await _show_template_step(
        callback=callback,
        message=message,
        template_id=template_id,
        step_index=next_step_index,
    )


@router.callback_query(F.data == "menu:templates")
async def open_templates_section(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit_text(
        callback,
        get_templates_section_text(),
        reply_markup=template_categories_keyboard(),
    )


@router.callback_query(F.data.startswith("tmplcat:"))
async def open_template_category(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    category_id = callback.data.split(":", maxsplit=1)[1]
    templates = list_templates_by_category(category_id)

    if not templates:
        await safe_edit_text(
            callback,
            "В этой категории пока нет шаблонов.",
            reply_markup=template_categories_keyboard(),
        )
        return

    await safe_edit_text(
        callback,
        render_category_card(category_id),
        reply_markup=template_list_keyboard(category_id),
    )


@router.callback_query(F.data.startswith("tmpl:"))
async def open_template(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    template_id = callback.data.split(":", maxsplit=1)[1]
    template = get_template(template_id)

    if template is None:
        await safe_edit_text(
            callback,
            "Шаблон не найден.",
            reply_markup=template_categories_keyboard(),
        )
        return

    await safe_edit_text(
        callback,
        render_template_card(template_id),
        reply_markup=template_actions_keyboard(template_id, template.category_id),
    )


@router.callback_query(F.data.startswith("taction:"))
async def handle_template_action(callback: CallbackQuery, state: FSMContext) -> None:
    _, template_id, action = callback.data.split(":", maxsplit=2)
    template = get_template(template_id)

    if template is None:
        await safe_edit_text(
            callback,
            "Шаблон не найден.",
            reply_markup=template_categories_keyboard(),
        )
        return

    if action == "show":
        await state.clear()
        await safe_edit_text(
            callback,
            render_blank_template(template_id),
            reply_markup=template_preview_keyboard(template_id),
        )
        return

    if action == "build":
        await state.clear()
        await safe_edit_text(
            callback,
            render_build_intro(template_id),
            reply_markup=template_build_intro_keyboard(template_id),
        )
        return

    if action == "start":
        await _start_template_build(
            state,
            template_id=template_id,
        )
        await _show_template_step(
            callback=callback,
            template_id=template_id,
            step_index=0,
        )


@router.callback_query(TemplateBuilderState.awaiting_answer, F.data == "flow:back")
async def template_build_back(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    template_id = data["template_id"]
    step_index = data.get("step_index", 0)
    answers = data.get("answers", {})

    if step_index <= 0:
        await state.clear()
        template = get_template(template_id)
        if template is None:
            await safe_edit_text(
                callback,
                get_templates_section_text(),
                reply_markup=template_categories_keyboard(),
            )
            return

        await safe_edit_text(
            callback,
            render_build_intro(template_id),
            reply_markup=template_build_intro_keyboard(template_id),
        )
        return

    new_step_index = step_index - 1
    trimmed_answers = trim_answers(
        get_question_keys(template_id),
        new_step_index,
        answers,
    )
    await state.update_data(step_index=new_step_index, answers=trimmed_answers)
    await _show_template_step(
        callback=callback,
        template_id=template_id,
        step_index=new_step_index,
    )


@router.callback_query(TemplateBuilderState.awaiting_answer, F.data.startswith("flowans:"))
async def template_choice_answer(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    template_id = data["template_id"]
    step_index = data["step_index"]
    answers = data.get("answers", {})
    choice_value = callback.data.split(":", maxsplit=1)[1]

    resolved_value = resolve_choice_label(template_id, step_index, choice_value)
    if resolved_value is None:
        await callback.answer("Не удалось обработать ответ.", show_alert=True)
        return

    await _process_template_answer(
        state=state,
        template_id=template_id,
        step_index=step_index,
        answers=answers,
        answer_value=resolved_value,
        callback=callback,
    )


@router.message(TemplateBuilderState.awaiting_answer)
async def template_text_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    template_id = data["template_id"]
    step_index = data["step_index"]
    answers = data.get("answers", {})
    question = get_question(template_id, step_index)

    if question is None:
        await state.clear()
        await message.answer(
            get_templates_section_text(),
            reply_markup=template_categories_keyboard(),
        )
        return

    if not message.text or not message.text.strip():
        await message.answer(
            EMPTY_INPUT_TEXT,
            reply_markup=_template_flow_keyboard(template_id, step_index),
        )
        return

    answer_text = message.text.strip()
    if question.choices:
        resolved_value = resolve_typed_choice(template_id, step_index, answer_text)
        if resolved_value is None:
            await message.answer(
                "Нужно выбрать один из вариантов: Да или Нет.",
                reply_markup=_template_flow_keyboard(template_id, step_index),
            )
            return
        answer_text = resolved_value

    await _process_template_answer(
        state=state,
        template_id=template_id,
        step_index=step_index,
        answers=answers,
        answer_value=answer_text,
        message=message,
    )
