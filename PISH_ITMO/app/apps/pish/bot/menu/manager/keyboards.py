from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

back_button = InlineKeyboardButton(
    text="Назад ◀️", callback_data="back"
)

confirm_button = InlineKeyboardButton(
    text="Подтвердить ✅", callback_data="confirm"
)

continue_button = InlineKeyboardButton(
    text="Продолжить ➡️", callback_data="notif_person"
)

feedback_choose_button = InlineKeyboardButton(
    text="Отправить оценку мероприятия 💛", callback_data="choose_feedback"
)

activity_choose_button = InlineKeyboardButton(
    text="Участники активности 🧘", callback_data="choose_activity"
)

consultation_choose_button = InlineKeyboardButton(
    text="Участники консультации 🗣", callback_data="choose_consultation"
)

roles_choose_button = InlineKeyboardButton(
    text="По ролям 🚻", callback_data="choose_roles"
)

person_choose_button = InlineKeyboardButton(
    text="Конкретному пользователю 🖍", callback_data="choose_person"
)

back: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[back_button]]
)
notif_types: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[feedback_choose_button],
                     [activity_choose_button], 
                     [consultation_choose_button],
                     [roles_choose_button],
                     [person_choose_button]]
)

person_confirm: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[continue_button], [back_button]]
)

send_confirm: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[confirm_button], [back_button]]
)
