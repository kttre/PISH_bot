from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

reg_button = InlineKeyboardButton(text="Перейти к регистрации ➡️", callback_data="start_reg")
start_reg = InlineKeyboardMarkup(inline_keyboard=[[reg_button]])

send_button = InlineKeyboardButton(text="Отправить ✉️", callback_data="send")
send = InlineKeyboardMarkup(inline_keyboard=[[send_button]])

try_again_button = InlineKeyboardButton(text="Попробовать еще раз 🔄", callback_data="send")
try_again = InlineKeyboardMarkup(inline_keyboard=[[try_again_button]])
