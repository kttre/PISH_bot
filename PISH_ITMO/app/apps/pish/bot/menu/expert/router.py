from aiogram import Router, types
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext

from ..router import Menu
from ...utils import Consultation
from . import text

# Router Start
router = Router()


@router.callback_query(Text(text="consultations"), Menu.Expert.general)
async def consultations_view(callback: types.CallbackQuery, state: FSMContext):
    consultations = await Consultation.get_by_expert(tg_id=callback.from_user.id)

    if consultations:
        await state.set_state(Menu.Expert.consultations)
        await callback.message.edit_text(text=text.consultations(consultations))
    else:
        await callback.answer(text=text.consultations_none, show_alert=True)
