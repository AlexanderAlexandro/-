from __future__ import annotations

from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from data.ui_texts import INVALID_NUMBER_TEXT
from keyboards.calculators import calculator_card_keyboard, calculators_keyboard
from keyboards.common import flow_keyboard, result_keyboard
from services.calculator_service import (
    get_calculator,
    get_question,
    get_question_keys,
    render_calculator_card,
    render_question,
    render_result,
    validate_answer,
)
from services.report_service import send_owner_report
from services.static_service import get_calculators_section_text
from utils.flow import trim_answers
from utils.messages import safe_edit_text
from utils.states import CalculatorState


router = Router()


def _calculator_flow_keyboard() -> InlineKeyboardMarkup:
    return flow_keyboard(
        section_callback="menu:calculators",
        section_label="В калькуляторы",
    )


def _calculator_result_keyboard(calculator_id: str) -> InlineKeyboardMarkup:
    return result_keyboard(
        retry_callback=f"calcstart:{calculator_id}",
        section_callback="menu:calculators",
        section_label="В калькуляторы",
    )


async def _show_calculator_step(
    *,
    callback: CallbackQuery | None = None,
    message: Message | None = None,
    calculator_id: str,
    step_index: int,
) -> None:
    text = render_question(calculator_id, step_index)
    reply_markup = _calculator_flow_keyboard()

    if callback is not None:
        await safe_edit_text(callback, text, reply_markup=reply_markup)
        return

    if message is not None:
        await message.answer(text, reply_markup=reply_markup)


async def _show_calculator_result(
    *,
    calculator_id: str,
    result_text: str,
    message: Message,
) -> None:
    await message.answer(
        result_text,
        reply_markup=_calculator_result_keyboard(calculator_id),
    )


async def _process_calculator_answer(
    *,
    state: FSMContext,
    calculator_id: str,
    step_index: int,
    answers: dict[str, Decimal],
    value: Decimal,
    message: Message,
) -> None:
    question = get_question(calculator_id, step_index)
    if question is None:
        await state.clear()
        return

    answers[question.key] = value
    next_step_index = step_index + 1

    if get_question(calculator_id, next_step_index) is None:
        await state.clear()
        result_text = render_result(calculator_id, answers)
        await _show_calculator_result(
            calculator_id=calculator_id,
            result_text=result_text,
            message=message,
        )
        calculator = get_calculator(calculator_id)
        await send_owner_report(
            bot=message.bot,
            section_title="Калькуляторы",
            scenario_title=calculator.title if calculator else calculator_id,
            result_text=result_text,
            user=message.from_user,
        )
        return

    await state.update_data(step_index=next_step_index, answers=answers)
    await _show_calculator_step(
        message=message,
        calculator_id=calculator_id,
        step_index=next_step_index,
    )


@router.callback_query(F.data == "menu:calculators")
async def open_calculators_section(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit_text(
        callback,
        get_calculators_section_text(),
        reply_markup=calculators_keyboard(),
    )


@router.callback_query(F.data.startswith("calc:"))
async def open_calculator(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    calculator_id = callback.data.split(":", maxsplit=1)[1]
    calculator = get_calculator(calculator_id)

    if calculator is None:
        await safe_edit_text(
            callback,
            "Калькулятор не найден.",
            reply_markup=calculators_keyboard(),
        )
        return

    await safe_edit_text(
        callback,
        render_calculator_card(calculator_id),
        reply_markup=calculator_card_keyboard(calculator_id),
    )


@router.callback_query(F.data.startswith("calcstart:"))
async def start_calculator(callback: CallbackQuery, state: FSMContext) -> None:
    calculator_id = callback.data.split(":", maxsplit=1)[1]
    calculator = get_calculator(calculator_id)

    if calculator is None:
        await safe_edit_text(
            callback,
            "Калькулятор не найден.",
            reply_markup=calculators_keyboard(),
        )
        return

    await state.set_state(CalculatorState.awaiting_answer)
    await state.set_data(
        {
            "calculator_id": calculator_id,
            "step_index": 0,
            "answers": {},
        }
    )
    await _show_calculator_step(
        callback=callback,
        calculator_id=calculator_id,
        step_index=0,
    )


@router.callback_query(CalculatorState.awaiting_answer, F.data == "flow:back")
async def calculator_back(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    calculator_id = data["calculator_id"]
    step_index = data.get("step_index", 0)
    answers = data.get("answers", {})

    if step_index <= 0:
        await state.clear()
        await safe_edit_text(
            callback,
            render_calculator_card(calculator_id),
            reply_markup=calculator_card_keyboard(calculator_id),
        )
        return

    new_step_index = step_index - 1
    trimmed_answers = trim_answers(
        get_question_keys(calculator_id),
        new_step_index,
        answers,
    )
    await state.update_data(step_index=new_step_index, answers=trimmed_answers)
    await _show_calculator_step(
        callback=callback,
        calculator_id=calculator_id,
        step_index=new_step_index,
    )


@router.message(CalculatorState.awaiting_answer)
async def calculator_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    calculator_id = data["calculator_id"]
    step_index = data["step_index"]
    answers = data.get("answers", {})
    question = get_question(calculator_id, step_index)

    if question is None:
        await state.clear()
        await message.answer(
            get_calculators_section_text(),
            reply_markup=calculators_keyboard(),
        )
        return

    if not message.text or not message.text.strip():
        await message.answer(
            INVALID_NUMBER_TEXT,
            reply_markup=_calculator_flow_keyboard(),
        )
        return

    try:
        validated_value = validate_answer(
            calculator_id,
            question.key,
            message.text.strip(),
            answers,
        )
    except ValueError as error:
        error_text = str(error)
        if error_text == "invalid_number":
            error_text = INVALID_NUMBER_TEXT
        await message.answer(
            error_text,
            reply_markup=_calculator_flow_keyboard(),
        )
        return

    await _process_calculator_answer(
        state=state,
        calculator_id=calculator_id,
        step_index=step_index,
        answers=answers,
        value=validated_value,
        message=message,
    )
