from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

back_button = InlineKeyboardButton(
    text="Назад ◀️", callback_data="back"
)

confirm_button = InlineKeyboardButton(
    text="Подтвердить", callback_data="confirm"
)

register_confrim: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[confirm_button, back_button]]
)
