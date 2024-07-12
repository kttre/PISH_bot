from contextlib import suppress

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from ..menu.keyboards import menu as kb_menu
from ..menu.router import Menu
from ..registration.keyboards import start_reg as kb_start_reg
from ..registration.router import Registration
from ..registration.text import new_user as text_new_user
from ..utils import User, Utils, SpamFilter
from .text import start as text_start

router = Router()


@router.message(Command(commands=["start"]), SpamFilter())
async def start(message: types.Message, state: FSMContext, bot: Bot):
    user_id = await User.get_user_id(tg_id=message.from_user.id)

    if not user_id:
        reg_message = (await state.get_data()).get("reg_message")
        if reg_message:
            with suppress(TelegramBadRequest):
                await bot.delete_message(chat_id=message.chat.id, message_id=reg_message)

        bot_msg = await message.answer(
            text=text_new_user,
            reply_markup=kb_start_reg,
        )
        await message.delete()
        await state.set_state(Registration.start)
        await state.update_data({"reg_message": bot_msg.message_id})

    else:
        await state.set_state(Menu.main)
        await Utils.delete_message_by_type(chat_id=message.chat.id, message_types=["rmenu", "imenu"], bot=bot)
        bot_msg = await message.answer(text=text_start, reply_markup=kb_menu)
        await message.delete()
        await Utils.add_message_to_delete(message_id=bot_msg.message_id, chat_id=bot_msg.chat.id, message_type="rmenu")
