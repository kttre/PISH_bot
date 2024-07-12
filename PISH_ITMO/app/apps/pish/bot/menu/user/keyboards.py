from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

back_button = InlineKeyboardButton(
    text="Назад ◀️", callback_data="back"
)

register_group_button = InlineKeyboardButton(
    text="Групповая 👥", callback_data="group"
)

register_personal_button = InlineKeyboardButton(
    text="Индивидуальная 👤", callback_data="personal"
)

confirm_button = InlineKeyboardButton(
    text="Подтвердить ✅", callback_data="confirm"
)

register_types: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[register_group_button, register_personal_button]]
)

register_confrim: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[confirm_button], [back_button]]
)

deregister_group_button = InlineKeyboardButton(
    text="Групповые 👥", callback_data="group"
)

deregister_personal_button = InlineKeyboardButton(
    text="Индивидуальные 👤", callback_data="personal"
)

deregister_types = InlineKeyboardMarkup(
    inline_keyboard=[[deregister_group_button, deregister_personal_button]]
)
