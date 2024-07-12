from asyncio import sleep

from aiogram import Router, types, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import or_f
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.apps.pish import models
from . import keyboards as kb
from . import text
from ..keyboards import manager_menu as kb_manager_menu
from ..router import Menu
from ..text import manager_menu as text_manager_menu
from ...utils import Notification, User

# Router Start
router = Router()


@router.callback_query(Text(text="back"), Menu.Manager())
async def back(callback: types.CallbackQuery, state: FSMContext):
    current_state = (await state.get_state()).split(":")[1]
    state_data = await state.get_data()
    selection = state_data.get("selection", "")
    notif_data = state_data.get("notif_data", ":")
    if not isinstance(notif_data, list):
        notif_data = notif_data.split(":")[0]

    match current_state, selection, notif_data:
        case "notif_person_confirm", "person", notif_data:
            await get_notif_type(callback=callback, state=state)
        case "notif_type_check", "feedback" | "activity" | "consultation" | "roles", notif_data:
            await get_notif_type(callback=callback, state=state)
        case "notif_type_check" | "notif_send", "person", notif_data:
            await notif_recipient(callback=callback, state=state)
        case "notif_send", "feedback", "feedback":
            await notif_recipient(callback=callback, state=state)
        case "notif_send", selection, notif_data:
            await notif_type_check(callback=callback, state=state)
        case "notif_send", "activity" | "consultation", "activity" | "consultation":
            await notif_type_check(callback=callback, state=state)
        case "notif_message", selection, notif_data:
            await notif_type_check(callback=callback, state=state)


@router.callback_query(Text(text="send_notifs"), Menu.Manager.general)
async def get_notif_type(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.update_data({"notif_data": "", "notif_text": "", "manager_msg_id": "", "selection": ""})
    await state.set_state(Menu.Manager.notif_recipient)
    await callback.message.edit_text(text=text.notif_type, reply_markup=kb.notif_types)


@router.callback_query(Text(startswith="choose_"), Menu.Manager.notif_recipient)
async def notif_recipient(callback: types.CallbackQuery, state: FSMContext) -> None:
    current_state = (await state.get_state()).split(":")[1]
    if current_state == "notif_recipient":
        selection = callback.data.split("_")[1]
        await state.update_data({"selection": selection})
    else:
        selection = (await state.get_data()).get("selection")

    if selection != "person":
        choices = await Notification.get_choices(notif_type=selection)
        if choices:
            await state.set_state(Menu.Manager.notif_type_check)
            kb_builder = InlineKeyboardBuilder()

            for choice in choices:
                new_button = types.InlineKeyboardButton(text=f"{choice['name']}",
                                                        callback_data=f"notif_{selection}:{choice['pk']}")
                kb_builder.add(new_button)
            kb_builder.add(kb.back_button)
            kb_builder.adjust(1)
            await callback.message.edit_text(text=text.notif_recipient[selection], reply_markup=kb_builder.as_markup())
        else:
            await callback.answer(text=text.choices_none, show_alert=True)
    else:
        await state.set_state(Menu.Manager.notif_person_confirm)
        await callback.message.edit_text(text=text.choose_person, reply_markup=kb.back)
        await state.update_data({"manager_msg_id": callback.message.message_id})


@router.message(Menu.Manager.notif_person_confirm)
async def notif_person_confirm(message: types.Message, state: FSMContext, bot: Bot) -> None:
    await message.delete()
    message_id = (await state.get_data()).get("manager_msg_id")
    first_symbol = ord((message.text.lower())[0])

    if 97 <= first_symbol <= 122 or first_symbol == 64:
        person = await User.get_by_info(info=message.text.replace('@', ''), info_type="username")
    elif 1072 <= first_symbol <= 1105 and len(message.text.split(" ")) == 2:
        person = await User.get_by_info(info=message.text)
    else:
        person = None

    if person:
        await state.set_state(Menu.Manager.notif_type_check)
        kb_builder = InlineKeyboardBuilder()
        kb_builder.add(types.InlineKeyboardButton(text="Подтвердить", callback_data=f"notif_person:{person['pk']}"))
        kb_builder.add(kb.back_button)     
        await bot.edit_message_text(
            text=text.person_found.format(full_name=person["full_name"], username=person["username"]),
            reply_markup=kb_builder.as_markup(),
            chat_id=message.chat.id,
            message_id=message_id
        )        
    else:
        await bot.edit_message_text(
            text=text.person_none.format(person=message.text),
            reply_markup=kb.back,
            chat_id=message.chat.id,
            message_id=message_id
        )         


@router.callback_query(Text(startswith="notif_roles"), Menu.Manager.notif_type_check)
async def notif_roles_mark(callback: types.CallbackQuery, state: FSMContext) -> None:
    action = callback.data.split(":")[1]
    keyboard = callback.message.reply_markup.inline_keyboard
    if action != "continue":
        for row in keyboard:
            if row[0].callback_data == f"notif_roles:{action}":
                if "❌" in row[0].text:
                    row[0].text = f"{models.User.Status(action).label} ✅"
                else:
                    row[0].text = f"{models.User.Status(action).label} ❌"

        await callback.message.edit_text(
            text=callback.message.text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

    else:
        choices = []
        for row in keyboard:
            if "✅" in row[0].text:
                choices.append(row[0].callback_data.split(":")[1])
        await callback.message.edit_text(text=text.write_msg)
        await state.update_data({"manager_msg_id": callback.message.message_id, "notif_data": choices})
        await state.set_state(Menu.Manager.notif_message)


@router.callback_query(Text(startswith="notif_"), or_f(Menu.Manager.notif_type_check, Menu.Manager.notif_recipient))
async def notif_type_check(callback: types.CallbackQuery, state: FSMContext) -> None:
    current_state = (await state.get_state()).split(":")[1]
    if current_state == "notif_type_check" or current_state == "notif_recipient":
        notif_data = callback.data.split("_")[1]
        await state.update_data({"notif_data": notif_data})
    else:
        notif_data = (await state.get_data()).get("notif_data")

    if not isinstance(notif_data, list):
        notif_type = notif_data.split(":")[0]
    else:
        notif_type = "roles"

    if notif_type != "feedback":
        await callback.message.edit_text(text=text.write_msg)
        await state.update_data({"manager_msg_id": callback.message.message_id})
        await state.set_state(Menu.Manager.notif_message)
    else:
        event_name = await Notification.get_name(pk=int(notif_data.split(":")[1]), notif_type=notif_type)
        await state.set_state(Menu.Manager.notif_send)
        await callback.message.edit_text(text=text.feedback_confirm.format(name=event_name),
                                         reply_markup=kb.send_confirm)


@router.message(Menu.Manager.notif_message)
async def notif_message(message: types.Message, state: FSMContext, bot: Bot) -> None:
    await message.delete()
    state_data = await state.get_data()
    message_id = state_data.get("manager_msg_id")
    notif_data = state_data.get("notif_data", ":")
    if not isinstance(notif_data, list):
        notif_data = notif_data.split(":")

    if len(message.text) <= 4000:
        if notif_data[0] and notif_data[0] not in models.User.Status.values:
            name = await Notification.get_name(pk=int(notif_data[1]), notif_type=notif_data[0])
        else:
            names = []
            for role in notif_data:
                names.append(f"{text.type_names[role]}")
            name = ", ".join(names)

        await bot.edit_message_text(text=f"{text.send_confirm.format(name=name)}{message.text}", 
                                    reply_markup=kb.send_confirm, 
                                    chat_id=message.chat.id, 
                                    message_id=message_id
                                    )
        await state.set_state(Menu.Manager.notif_send)
        await state.update_data({"notif_text": message.text})
    else:
        await bot.edit_message_text(
            text=text.too_long_msg,
            reply_markup=kb.back,
            chat_id=message.chat.id,
            message_id=message_id
        )


@router.callback_query(Text(text="confirm"), Menu.Manager.notif_send)
async def notif_send(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    state_data = await state.get_data()
    notif_data = state_data.get("notif_data", ":")
    if not isinstance(notif_data, list):
        notif_data = notif_data.split(":")
        notif_type = notif_data[0]
        notif_pk = notif_data[1] if len(notif_data) == 2 else None
    else:
        notif_type = "roles"
        notif_pk = notif_data

    if notif_type != "feedback":
        notif_text = state_data.get("notif_text")
    else:
        notif_text = text.feedback_message

    await callback.message.edit_text(text=text.sending_in_process)
    send_count = await Notification.send_notifs_by_manager(notif_type=notif_type, bot=bot,
                                                           pk=notif_pk, notif_text=notif_text)
    await callback.message.edit_text(
        text=text.sending_success.format(send_count=send_count)
    )
    await sleep(5)

    await state.update_data({"notif_data": "", "notif_text": "", "manager_msg_id": "", "selection": ""})
    await state.set_state(Menu.Manager.general)
    try:
        await callback.message.edit_text(text=text_manager_menu, reply_markup=kb_manager_menu)
    except TelegramBadRequest:
        pass
