from asyncio import sleep
from contextlib import suppress

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.logic import invert_f
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import QuerySet

from . import keyboards as kb
from . import text
from ..utils import User, Utils, SpamFilter, Transfer, Living, or_f_list, Notification
from ... import models

router = Router()


class Menu(StatesGroup):
    main = State()
    transfer_choose = State()
    transfer_info = State()
    living_info = State()
    contacts_info = State()
    support_links = State()

    class User(StatesGroup):
        general = State()

        register = State()
        register_interval = State()
        register_personal_date = State()
        register_confirm = State()
        register_final = State()

        deregister = State()
        deregister_confirm = State()
        deregister_final = State()

        diary = State()

    class Listener(StatesGroup):
        general = State()

    class Expert(StatesGroup):
        general = State()
        consultations = State()

    class Manager(StatesGroup):
        general = State()
        notif_recipient = State()
        notif_person_confirm = State()
        notif_type_check = State()
        notif_message = State()
        notif_confirm = State()
        notif_send = State()


# User Menu
@router.message(Text(text=text.menu_button), SpamFilter(), Menu())
async def user_menu(message: types.Message, state: FSMContext, bot: Bot):
    await message.delete()
    await Utils.delete_message_by_type(chat_id=message.chat.id, message_types=["imenu"], bot=bot)
    user_status = await User.get_user_status(tg_id=message.from_user.id)

    if user_status == "user":
        await state.set_state(Menu.User.general)
        bot_msg = await message.answer(text=text.user_menu, reply_markup=kb.user_menu)
        await Utils.add_message_to_delete(message_id=bot_msg.message_id, chat_id=bot_msg.chat.id, message_type="imenu")

    elif user_status == "listener":
        await state.set_state(Menu.Listener.general)
        bot_msg = await message.answer(text=text.listener_menu, reply_markup=kb.listener_menu)
        await Utils.add_message_to_delete(message_id=bot_msg.message_id, chat_id=bot_msg.chat.id, message_type="imenu")

    elif user_status == "expert":
        await state.set_state(Menu.Expert.general)
        bot_msg = await message.answer(text=text.expert_menu, reply_markup=kb.expert_menu)
        await Utils.add_message_to_delete(message_id=bot_msg.message_id, chat_id=bot_msg.chat.id, message_type="imenu")

    elif user_status == "manager":
        await state.set_state(Menu.Manager.general)
        bot_msg = await message.answer(text=text.manager_menu, reply_markup=kb.manager_menu)
        await Utils.add_message_to_delete(message_id=bot_msg.message_id, chat_id=bot_msg.chat.id, message_type="imenu")


@router.callback_query(Text(text="back"), Menu.transfer_info)
async def transfer_back(callback: types.CallbackQuery, state: FSMContext):
    await transfer(callback=callback, state=state)


@router.callback_query(Text(text="transfer"), or_f_list(Menu.User.general, 
                                                        Menu.Listener.general, 
                                                        Menu.Expert.general, 
                                                        Menu.Manager.general
                                                        ))
async def transfer(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=text.transfer_choose, reply_markup=kb.transfer_choose)
    await state.set_state(Menu.transfer_choose)


@router.callback_query(Text(startswith="transfer_"), Menu.transfer_choose)
async def transfer_choose(callback: types.CallbackQuery, state: FSMContext):
    direction = callback.data.split("_")[1]
    info = await Transfer.get_info(tg_id=callback.from_user.id, direction=direction)

    if info:
        await state.set_state(Menu.transfer_info)
        message_text = text.transfer_info.format(
            date=info['date'], place=info['place'], car_num=info['car_num'], driver_num=info['driver_num']
        )

        companions = info.get("companions")
        if isinstance(companions, QuerySet):
            if await companions.aexists():
                companions_list = []
                async for companion in companions:
                    companions_list.append(f"{companion.get('user__last_name')} "
                                           f"{companion.get('user__first_name')} "
                                           f"(@{companion.get('user__username')})")
                message_text += "\n\nВместе с вами едут:\n" + "\n".join(companions_list)

        await callback.message.edit_text(
            text=message_text,
            reply_markup=kb.back
        )
    else:
        await callback.answer(text=text.transfer_none, show_alert=True)


@router.callback_query(Text(text="living"), or_f_list(Menu.User.general, 
                                                      Menu.Listener.general, 
                                                      Menu.Expert.general,
                                                      Menu.Manager.general
                                                      ))
async def living(callback: types.CallbackQuery, state: FSMContext):
    info = await Living.get_info(tg_id=callback.from_user.id)
    if info:
        await state.set_state(Menu.living_info)
        await callback.message.edit_text(text=text.living_info.format(room=info["room"], build=info["build"]),
                                         disable_web_page_preview=True)
    else:
        await callback.answer(text=text.living_none, show_alert=True)


@router.callback_query(
    Text(text="support_links"),
    or_f_list(
        Menu.User.general,
        Menu.Listener.general,
        Menu.Expert.general,
        Menu.Manager.general
    )
)
async def support_links(callback: types.CallbackQuery, state: FSMContext):
    statuses = models.User.Status
    info = await User.get_status_and_map(tg_id=callback.from_user.id)
    if (
        info and info.get("status") not in [statuses.USER, statuses.LISTENER, statuses.EXPERT, statuses.MANAGER]
    ) or not info:
        await callback.answer(text=text.support_links_none, show_alert=True)
        return

    user_status = info.get("status")

    kb_builder = InlineKeyboardBuilder()

    if user_status in [statuses.USER, statuses.LISTENER]:
        map_url = info.get("self_determination_map")

        if map_url and user_status == "user":
            map_button = kb.map_button
            map_button.url = map_url
            kb_builder.add(map_button)

        kb_builder.add(
            kb.business_card_button,
            kb.expert_presentation_button,
            kb.images_button,
            kb.contacts_button
        )

    elif user_status in (statuses.EXPERT, statuses.MANAGER):
        kb_builder.add(
            kb.business_card_button,
            kb.images_button,
            kb.contacts_button
        )

    kb_builder.adjust(1)

    await callback.message.edit_text(text=text.support_links, reply_markup=kb_builder.as_markup())
    await state.set_state(Menu.support_links)


@router.callback_query(Text(text="contacts"), Menu.support_links)
async def contacts(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Menu.contacts_info)
    await callback.message.edit_text(text=text.contacts_info)


@router.callback_query(Text(startswith="feedbackstart_"), invert_f(Menu.Manager()))
async def feedback_start(callback: types.CallbackQuery, state: FSMContext):
    event_pk = callback.data.split("_")[1]
    feedback_list = (await state.get_data()).get("feedback_list")
    if feedback_list is None:
        feedback_list = {f"{event_pk}": {"step": 1}}
    else:
        feedback_list.update({f"{event_pk}": {"step": 1}})
    await state.update_data({"feedback_list": feedback_list})
    # feedbackbutton_{pk}:{step}:{grade}
    kb_builder = InlineKeyboardBuilder()
    buttons = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(1, 6):
        new_button = types.InlineKeyboardButton(text=f"{buttons[i]}", callback_data=f"feedbackbutton_{event_pk}:1:{i}")
        kb_builder.add(new_button)
    await callback.message.edit_text(text=text.feedback_answer["1"], reply_markup=kb_builder.as_markup())


@router.callback_query(Text(startswith="feedbackbutton_"), invert_f(Menu.Manager()))
async def feedback_step(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data.split("_")[1].split(":")
    feedback_list = (await state.get_data()).get("feedback_list")
    feedback_by_pk_data = feedback_list.get(callback_data[0])
    feedback_by_pk_data.update({"step": int(callback_data[1]) + 1, f"grade_{callback_data[1]}": int(callback_data[2])})
    if callback_data[1] != "4":
        await state.update_data({"feedback_list": feedback_list})
        kb_builder = InlineKeyboardBuilder()
        buttons = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for i in range(1, 6):
            new_button = types.InlineKeyboardButton(text=f"{buttons[i]}",
                                                    callback_data=(
                                                        f"feedbackbutton_"
                                                        f"{callback_data[0]}:{int(callback_data[1]) + 1}:{i}"))
            kb_builder.add(new_button)
        await callback.message.edit_text(text=text.feedback_answer[str(int(callback_data[1]) + 1)],
                                         reply_markup=kb_builder.as_markup())
    else:
        await Notification.feedback_send(tg_id=callback.from_user.id, pk=int(callback_data[0]),
                                         feedback_dict=feedback_by_pk_data)
        await callback.message.edit_text(text=text.feedback_final)
        feedback_list.update({f"{callback_data[0]}": None})
        await state.update_data({"feedback_list": feedback_list})
        await state.update_data()
        await sleep(5)
        await callback.message.delete()


@router.message(invert_f(or_f_list(Menu.Manager.notif_person_confirm, Menu.Manager.notif_message)))
async def message_delete(message: types.Message) -> None:
    with suppress(TelegramBadRequest):
        await message.delete()
