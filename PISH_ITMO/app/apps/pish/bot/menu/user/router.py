from aiogram import Router, types
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import keyboards as kb
from . import text
from ..keyboards import user_menu as kb_user_menu
from ..router import Menu
from ..text import user_menu as text_user_menu
from ...utils import ConsultationInterval, Consultation, ConsultationRecord

# Router Start
router = Router()


@router.callback_query(Text(text="back"), Menu.User())
async def back(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    match current_state.split(":")[1]:
        case "register_interval":
            await register(callback=callback, state=state)
        case "register_confirm":
            is_group = (await state.get_data()).get("is_group")
            if is_group:
                await register_types(callback=callback, state=state)
            else:
                await expert_choose(callback=callback, state=state)
        case "register_personal_date":
            await register_types(callback=callback, state=state)
        case "register_final":
            is_group = (await state.get_data()).get("is_group")
            if is_group:
                await expert_choose(callback=callback, state=state)
            else:
                await date_choose(callback=callback, state=state)
        case "deregister_confirm":
            await deregister(callback=callback, state=state)
        case "deregister_final":
            await deregister_types(callback=callback, state=state)


@router.callback_query(Text(text="register"), Menu.User.general)
async def register(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Menu.User.register)
    await callback.message.edit_text(text=text.register, reply_markup=kb.register_types)


@router.callback_query(Text(text=["group", "personal"]), Menu.User.register)
async def register_types(callback: types.CallbackQuery, state: FSMContext) -> None:
    current_state = (await state.get_state()).split(":")[1]
    if current_state == "register":
        is_group = True if callback.data == "group" else False
    else:
        is_group = (await state.get_data()).get("is_group")

    intervals = await ConsultationInterval.get_by_user(tg_id=callback.from_user.id, is_group=is_group)

    if intervals:
        text_intervals = f"{text.intervals} в <b>каждом</b> временном слоте" if is_group else text.intervals
        await state.set_state(Menu.User.register_interval)
        await state.update_data({"is_group": is_group})
        kb_builder = InlineKeyboardBuilder()

        for interval in intervals:
            new_button = types.InlineKeyboardButton(text=f"{interval['date']}", 
                                                    callback_data=f"interval_{interval['pk']}")
            kb_builder.add(new_button)

        kb_builder.add(kb.back_button)
        kb_builder.adjust(1)
        await callback.message.edit_text(text=text_intervals, reply_markup=kb_builder.as_markup())
    else:
        await callback.answer(text=text.register_unavailable, show_alert=True)


@router.callback_query(Text(startswith="interval_"), Menu.User.register_interval)
async def expert_choose(callback: types.CallbackQuery, state: FSMContext) -> None:
    current_state = (await state.get_state()).split(":")[1]
    if current_state == "register_interval":
        interval_pk = int(callback.data.split("_")[1])
    else:
        interval_pk = (await state.get_data()).get("interval_pk")
    is_group = (await state.get_data()).get("is_group")
    experts = await Consultation.get_experts(tg_id=callback.from_user.id, interval_pk=interval_pk, is_group=is_group)

    if experts:
        await state.update_data({"interval_pk": interval_pk})
        kb_builder = InlineKeyboardBuilder()

        if is_group:
            await state.set_state(Menu.User.register_confirm)
            key = "consultation_"
        else:
            await state.set_state(Menu.User.register_personal_date)
            key = "expert_"

        for expert in experts:
            new_button = types.InlineKeyboardButton(text=f"{expert['full_name']}", callback_data=f"{key}{expert['pk']}")
            kb_builder.add(new_button)

        kb_builder.add(kb.back_button)
        kb_builder.adjust(1)

        await callback.message.edit_text(text=text.experts(is_group), reply_markup=kb_builder.as_markup())
    else:
        await callback.answer(text=text.experts_none, show_alert=True)


@router.callback_query(Text(startswith="expert_"), Menu.User.register_personal_date)
async def date_choose(callback: types.CallbackQuery, state: FSMContext) -> None:
    current_state = (await state.get_state()).split(":")[1]
    state_data = await state.get_data()
    interval_pk = state_data.get("interval_pk")
    is_group = state_data.get("is_group")

    if current_state == "register_personal_date":
        expert_pk = int(callback.data.split("_")[1])
    else:
        expert_pk = state_data.get("expert_pk")

    dates = await Consultation.get_dates_by_expert(
        tg_id=callback.from_user.id, expert_pk=expert_pk, interval_pk=interval_pk, is_group=is_group
    )

    if dates:
        await state.set_state(Menu.User.register_confirm)
        await state.update_data({"expert_pk": expert_pk})
        kb_builder = InlineKeyboardBuilder()
        for date in dates:
            new_button = types.InlineKeyboardButton(text=f"{date['date']}", callback_data=f"consultation_{date['pk']}")
            kb_builder.add(new_button)
        kb_builder.add(kb.back_button)
        kb_builder.adjust(1)
        await callback.message.edit_text(text=text.dates_choose, reply_markup=kb_builder.as_markup())
    else:
        await callback.answer(text=text.dates_none, show_alert=True)


@router.callback_query(Text(startswith="consultation_"), Menu.User.register_confirm)
async def register_confirm(callback: types.CallbackQuery, state: FSMContext) -> None:
    consultation_pk = int(callback.data.split("_")[1])
    await state.update_data({"consultation_pk": consultation_pk})
    await state.set_state(Menu.User.register_final)

    consultation = await Consultation.get(pk=consultation_pk)

    expert = consultation.get("full_name")
    start_time = consultation.get("start_time")
    end_time = consultation.get("end_time")

    text_message = f"{text.register_confirm} <b>{expert} c {start_time}</b>"

    if end_time:
        text_message += f"<b> до {end_time}</b>?"
    else:
        text_message += "?"

    await callback.message.edit_text(text=text_message, reply_markup=kb.register_confrim)


@router.callback_query(Text(text="confirm"), Menu.User.register_final)
async def register_end(callback: types.CallbackQuery, state: FSMContext) -> None:
    consultation_pk = (await state.get_data()).get("consultation_pk")
    status = await ConsultationRecord.create(tg_id=callback.from_user.id, consultation_pk=consultation_pk)

    await state.set_state(Menu.User.general)
    await state.update_data({"consultation_pk": None, "expert_pk": None, "interval_pk": None, "is_group": None})
    await callback.message.edit_text(text=text_user_menu, reply_markup=kb_user_menu)

    text_answer = text.register_end if status else text.register_error

    await callback.answer(text=text_answer, show_alert=True)


@router.callback_query(Text(text="deregister"), Menu.User.general)
async def deregister(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Menu.User.deregister)
    await callback.message.edit_text(text=text.deregister, reply_markup=kb.deregister_types)


@router.callback_query(Text(text=["group", "personal"]), Menu.User.deregister)
async def deregister_types(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data != "back":
        is_group = True if callback.data == "group" else False
        await state.update_data({"is_group": is_group})
        callback_data = callback.data
    else:
        is_group = (await state.get_data()).get("is_group", False)
        callback_data = "group" if is_group else "personal"

    consultation_records = await ConsultationRecord.get_by_user(
        tg_id=callback.from_user.id, deregister=True, is_group=is_group
    )

    records = consultation_records.get(callback_data)
    if records:
        kb_builder = InlineKeyboardBuilder()
        for record in records:
            new_button = types.InlineKeyboardButton(
                text=f"{record['full_name']} ({record['date']})",
                callback_data=f"consultation_{record['pk']}"
            )
            kb_builder.row(new_button)
        kb_builder.row(kb.back_button)

        await callback.message.edit_text(text=text.deregister_choose, reply_markup=kb_builder.as_markup())
        await state.set_state(Menu.User.deregister_confirm)

    else:
        consultation_type = "групповые" if callback.data == "group" else "индивидуальные"
        await callback.answer(
            text=text.deregister_unavailable.format(consultation_type=consultation_type), show_alert=True
        )


@router.callback_query(Text(startswith="consultation_"), Menu.User.deregister_confirm)
async def deregister_confirm(callback: types.CallbackQuery, state: FSMContext) -> None:
    consultation_pk = int(callback.data.split("_")[1])
    await state.update_data({"consultation_pk": consultation_pk})
    await state.set_state(Menu.User.deregister_final)

    consultation = await Consultation.get(pk=consultation_pk)

    expert = consultation.get("full_name")
    start_time = consultation.get("start_time")
    end_time = consultation.get("end_time")

    text_message = f"{text.deregister_confirm} <b>{expert} c {start_time}</b>"

    if end_time:
        text_message += f"<b> до {end_time}</b>?"
    else:
        text_message += "?"

    await callback.message.edit_text(text=text_message, reply_markup=kb.register_confrim)


@router.callback_query(Text(text="confirm"), Menu.User.deregister_final)
async def deregister_end(callback: types.CallbackQuery, state: FSMContext) -> None:
    consultation_pk = (await state.get_data()).get("consultation_pk")
    status = await ConsultationRecord.delete(tg_id=callback.from_user.id, consultation_pk=consultation_pk)

    await state.set_state(Menu.User.general)
    await state.update_data({"consultation_pk": None})
    await callback.message.edit_text(text=text_user_menu, reply_markup=kb_user_menu)

    text_answer = text.deregister_end if status else text.deregister_error

    await callback.answer(text=text_answer, show_alert=True)


@router.callback_query(Text(text="diary"), Menu.User.general)
async def diary(callback: types.CallbackQuery, state: FSMContext) -> None:
    diary_data = await ConsultationRecord.get_by_user(tg_id=callback.from_user.id)

    if diary_data:
        await state.set_state(Menu.User.diary)
        await callback.message.edit_text(text=text.diary(diary_data))
    else:
        await callback.answer(text=text.diary_none, show_alert=True)
