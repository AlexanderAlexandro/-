from __future__ import annotations

from data.ui_texts import (
    ABOUT_TEXT,
    CALCULATORS_SECTION_TEXT,
    HELP_TEXT,
    KIT_SECTION_TEXT,
    MAIN_MENU_TEXT,
    STOP_FLOW_TEXT,
    TEMPLATES_SECTION_TEXT,
    UNKNOWN_MESSAGE_TEXT,
    USEFUL_SECTION_TEXT,
    WELCOME_TEXT,
)
from data.useful import USEFUL_BLOCKS
from utils.formatting import render_screen
from utils.text import escape_html


def get_welcome_text() -> str:
    return WELCOME_TEXT


def get_main_menu_text() -> str:
    return MAIN_MENU_TEXT


def get_kit_text() -> str:
    return KIT_SECTION_TEXT


def get_help_text() -> str:
    return HELP_TEXT


def get_templates_section_text() -> str:
    return TEMPLATES_SECTION_TEXT


def get_calculators_section_text() -> str:
    return CALCULATORS_SECTION_TEXT


def get_useful_section_text() -> str:
    return USEFUL_SECTION_TEXT


def get_about_text() -> str:
    return ABOUT_TEXT


def get_unknown_message_text() -> str:
    return UNKNOWN_MESSAGE_TEXT


def get_stop_flow_text() -> str:
    return STOP_FLOW_TEXT


def list_useful_blocks():
    return tuple(USEFUL_BLOCKS.values())


def get_useful_block(block_id: str):
    return USEFUL_BLOCKS.get(block_id)


def render_useful_block(block_id: str) -> str:
    block = get_useful_block(block_id)
    if block is None:
        return "Блок не найден."

    return render_screen(
        block.title,
        [escape_html(block.content)],
        emoji="📎",
    )
