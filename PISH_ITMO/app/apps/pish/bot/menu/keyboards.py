from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from .text import menu_button

menu_button = KeyboardButton(text=menu_button)
menu = ReplyKeyboardMarkup(keyboard=[[menu_button]], resize_keyboard=True)
support_links_button = InlineKeyboardButton(text="Полезные ссылки 🔗", callback_data="support_links")
back_button = InlineKeyboardButton(text="Назад ◀️", callback_data="back")

transfer_button = InlineKeyboardButton(text="Трансфер 🚘", callback_data="transfer")
transfer_to_button = InlineKeyboardButton(text="В Альметьевск ✈️", callback_data="transfer_to")
transfer_from_button = InlineKeyboardButton(text="Из Альметьевска 🏘", callback_data="transfer_from")
living_button = InlineKeyboardButton(text="Проживание 🏘", callback_data="living")

schedule_button = InlineKeyboardButton(text="Расписание 📌", url="https://clck.ru/34GAYJ")
register_button = InlineKeyboardButton(text="Записаться ✏️", callback_data="register")
diary_button = InlineKeyboardButton(text="Мои записи 📅", callback_data="diary")
consultations_button = InlineKeyboardButton(text="Консультации 📅", callback_data="consultations")
send_notifs_button = InlineKeyboardButton(text="Отправить рассылку", callback_data="send_notifs")
db_link_button = InlineKeyboardButton(text="База данных ℹ️", url="http://178.170.195.124:8080/admin/")
deregister_button = InlineKeyboardButton(text="Перезаписаться ♻️", callback_data="deregister")

map_button = InlineKeyboardButton(text="Карта 🗺")
business_card_button = InlineKeyboardButton(
    text="Визитки экспертов и участников 📹",
    url="https://meadow-class-77f.notion.site/I-23-13bcc8c6aa784ee18384377058dcad8b?pvs=4"
)
expert_presentation_button = InlineKeyboardButton(
    text="Презентации экспертов 💻️", url="https://drive.google.com/drive/folders/1lKzuNtkS8ckfQ-NuimJ2_7vy-_XWSmTe"
)
images_button = InlineKeyboardButton(
    text="Фотографии 📷", url="https://drive.google.com/drive/folders/1nBIqHxuJytWVHA9mNbxhMMyqR_jsPd5V"
)
contacts_button = InlineKeyboardButton(text="Контакты ☎️", callback_data="contacts")

back: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[back_button]]
)

user_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [transfer_button],
        [living_button],
        [register_button],
        [deregister_button],
        [diary_button],
        [support_links_button],
        [schedule_button],
    ]
)

listener_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[transfer_button], [living_button], [support_links_button], [schedule_button]]
)

expert_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [transfer_button],
        [living_button],
        [consultations_button],
        [support_links_button],
        [schedule_button]
    ]
)

manager_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [transfer_button],
        [living_button],
        [send_notifs_button],
        [db_link_button],
        [support_links_button],
        [schedule_button]
    ]
)

transfer_choose: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[transfer_to_button, transfer_from_button]]
)
