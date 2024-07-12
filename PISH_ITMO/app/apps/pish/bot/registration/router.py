from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..menu.keyboards import menu as kb_menu
from ..utils import User, Utils
from ..start_command.text import start as text_start
from . import keyboards as kb
from . import text

router = Router()


class Registration(StatesGroup):
    start = State()
    confirmation = State()


@router.callback_query(Text(text="start_reg"), Registration.start)
async def confirm_message(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        text=text.agreement,
        reply_markup=kb.send
    )
    await state.set_state(Registration.confirmation)


@router.callback_query(Text(text="send"), Registration.confirmation)
async def confirm_reg(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    from ..menu.router import Menu

    status = await User.register_user(tg_id=callback.from_user.id, username=callback.from_user.username)
    if status:
        await callback.answer(text=text.success_reg, show_alert=True)
        bot_msg = await bot.send_message(chat_id=callback.from_user.id, text=text_start, reply_markup=kb_menu)
        await callback.message.delete()
        await state.set_state(Menu.main)
        await Utils.add_message_to_delete(message_id=bot_msg.message_id, chat_id=bot_msg.chat.id, message_type="rmenu")
    else:
        try:
            await callback.message.edit_text(text=text.failed_reg, reply_markup=kb.try_again)
        except TelegramBadRequest:
            await callback.answer(text=text.still_failed_reg, show_alert=True)
