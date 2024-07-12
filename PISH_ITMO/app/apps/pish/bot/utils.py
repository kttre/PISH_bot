import asyncio
import datetime
import time
from contextlib import suppress
from typing import Union, Dict, Any

import pytz
from aiogram import Bot
from aiogram.dispatcher.event.handler import CallbackType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import BaseFilter
from aiogram.filters.logic import _OrFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Count
from django.utils import timezone

from .menu.manager import text as manager_text
from .. import models


class User:
    @staticmethod
    async def get_user_id(tg_id: int) -> int | None:
        try:
            return await models.User.objects.values_list("tg_id", flat=True).aget(tg_id=tg_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    async def register_user(tg_id: int, username: str):
        user = await models.User.objects.filter(username=username).aupdate(tg_id=tg_id)

        if user != 0:
            return True
        else:
            return False

    @staticmethod
    async def get_user_status(tg_id: int) -> str | None:
        try:
            return await models.User.objects.values_list("status", flat=True).aget(tg_id=tg_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    async def get_by_info(info: str, info_type: str = None):
        try:
            if info_type == "username":
                user = await models.User.objects.aget(username=info)
            else:
                name = info.split(" ")
                last_name = name[0]
                first_name = name[1]
                user = await models.User.objects.aget(
                    first_name=first_name,
                    last_name=last_name)

            user_info = {
                "pk": user.pk,
                "full_name": f"{user.last_name} {user.first_name}",
                "username": user.username
            }
            return user_info

        except ObjectDoesNotExist:
            return None

    @staticmethod
    async def get_status_and_map(tg_id: int) -> dict[str, str | None] | None:
        try:
            return await models.User.objects.values("status", "self_determination_map").aget(tg_id=tg_id)
        except ObjectDoesNotExist:
            return None


class Transfer:
    @staticmethod
    async def get_info(tg_id: int, direction: str):
        try:
            info = await models.Transfer.objects.values("pk", "date", "place", "car_num", "driver_num").aget(
                user__tg_id=tg_id, direction=direction
            )

            companions = models.Transfer.objects.filter(
                date=info.get("date"),
                place=info.get("place"),
                car_num=info.get("car_num")
            ).exclude(pk=info.get("pk")).values("user__first_name", "user__last_name", "user__username")
            if await companions.aexists():
                info["companions"] = companions

            info["date"] = info["date"].astimezone(pytz.timezone("Europe/Moscow")).strftime("%d %B в %H:%M")

            return info

        except ObjectDoesNotExist:
            return None


class Living:
    @staticmethod
    async def get_info(tg_id: int):
        try:
            return await models.Living.objects.values("room", "build").aget(
                user__tg_id=tg_id
            )
        except ObjectDoesNotExist:
            return None


class Consultation:
    @staticmethod
    async def get_experts(tg_id: int, interval_pk: int, is_group: bool):
        user_registrations = models.ConsultationRecord.objects.filter(
            user__tg_id=tg_id,
            consultation__interval_id=interval_pk,
            consultation__is_group=is_group,
            consultation__is_active=True
        ).values_list("consultation__start_time", flat=True)

        consultations = models.Consultation.objects.select_related().filter(
            is_active=True,
            interval_id=interval_pk,
            is_group=is_group,
            count__lt=F("max_count")
        ).exclude(start_time__in=user_registrations)

        experts = []
        if is_group:
            async for consultation in consultations:
                experts.append({
                    "pk": consultation.pk,
                    "full_name": f"{consultation.expert.last_name} {consultation.expert.first_name}"
                })
        else:
            async for consultation in consultations:
                expert = {
                    "pk": consultation.expert.pk,
                    "full_name": f"{consultation.expert.last_name} {consultation.expert.first_name}",
                }
                if expert not in experts:
                    experts.append(expert)

        return experts

    @staticmethod
    async def get_dates_by_expert(tg_id: int, expert_pk: int, interval_pk: int, is_group: bool):
        user_registrations = models.ConsultationRecord.objects.filter(
            user__tg_id=tg_id,
            consultation__interval_id=interval_pk,
            consultation__is_group=is_group,
            consultation__is_active=True
        ).values_list("consultation__start_time", flat=True)

        consultations = models.Consultation.objects.filter(
            expert_id=expert_pk,
            interval_id=interval_pk,
            is_group=is_group,
            is_active=True,
            count__lt=F("max_count")
        ).exclude(start_time__in=user_registrations)

        dates = []
        async for consultation in consultations:
            dates.append({
                "pk": consultation.pk,
                "date": consultation.start_time.strftime("%H:%M")
            })

        return dates

    @staticmethod
    async def get(pk: int):
        consultation = await models.Consultation.objects.select_related().aget(pk=pk)

        if consultation.is_group:
            consultation_info = {
                "full_name": f"{consultation.expert.last_name} {consultation.expert.first_name}",
                "start_time": f"{consultation.start_time.strftime('%H:%M')}",
                "end_time": f"{consultation.interval.end_time.strftime('%H:%M')}"
            }
        else:
            consultation_info = {
                "full_name": f"{consultation.expert.last_name} {consultation.expert.first_name}",
                "start_time": consultation.start_time.strftime("%H:%M")
            }

        return consultation_info

    @staticmethod
    async def get_by_expert(tg_id: int):
        consultations = models.Consultation.objects.select_related().filter(
            expert__tg_id=tg_id,
            is_active=True,
            count__gt=0
        )

        consultations_info = []
        async for consultation in consultations:
            date = (
                f"{consultation.interval.date.strftime('%d %B')} "
                f"{consultation.start_time.strftime('%H:%M')}"
            )

            records = models.ConsultationRecord.objects.select_related().filter(consultation=consultation)

            users = []
            async for record in records:
                users.append((f"{record.user.last_name} {record.user.first_name}", record.user.self_determination_map))

            consultations_info.append({
                "date": date,
                "users": users
            })

        return consultations_info


class ConsultationRecord:
    @staticmethod
    async def create(tg_id: int, consultation_pk: int):
        consultation = await models.Consultation.objects.aget(pk=consultation_pk)
        if consultation.count < consultation.max_count:
            consultation.count = F('count') + 1
            await sync_to_async(consultation.save)(update_fields=["count", "updated_at"])
            user_id = await models.User.objects.values_list("pk", flat=True).aget(tg_id=tg_id)
            user_record = await models.ConsultationRecord.objects.acreate(
                user_id=user_id,
                consultation_id=consultation.id
            )
            if user_record:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    async def delete(tg_id: int, consultation_pk: int):
        date = timezone.now().astimezone(pytz.timezone("Europe/Moscow"))
        record = models.ConsultationRecord.objects.select_related().filter(
            (Q(consultation__interval__date__day=date.day) & Q(consultation__start_time__gt=date.time())) |
            Q(consultation__interval__date__day=(date + datetime.timedelta(days=1)).day),
            consultation__pk=consultation_pk,
            user__tg_id=tg_id
        )
        if not await record.aexists():
            return False

        deleted_count, _ = await record.adelete()
        if not deleted_count:
            return False

        await models.Consultation.objects.filter(pk=consultation_pk).aupdate(count=F('count') - 1)
        return True

    @staticmethod
    async def get_by_user(tg_id: int, *, deregister: bool = False, is_group: bool = False):
        date = timezone.now().astimezone(pytz.timezone("Europe/Moscow"))

        if not deregister:
            records = models.ConsultationRecord.objects.select_related().filter(
                Q(consultation__interval__date__day=date.day) |
                Q(consultation__interval__date__day=(date + datetime.timedelta(days=1)).day),
                consultation__is_active=True,
                user__tg_id=tg_id,
            )
        else:
            records = models.ConsultationRecord.objects.select_related().filter(
                (Q(consultation__interval__date__day=date.day) & Q(consultation__start_time__gt=date.time())) |
                Q(consultation__interval__date__day=(date + datetime.timedelta(days=1)).day),
                consultation__is_active=True,
                consultation__is_group=is_group,
                user__tg_id=tg_id
            )

        consultations_info = {"group": [], "personal": []}
        async for record in records:
            if not deregister:
                date = (
                    f"<b>{record.consultation.interval.date.strftime('%d %B')}</b> в "
                    f"<b>{record.consultation.start_time.strftime('%H:%M')}</b>"
                )
            else:
                date = (
                    f"{record.consultation.interval.date.strftime('%d.%m')} "
                    f"{record.consultation.start_time.strftime('%H:%M')}"
                )

            new_record = {
                "pk": record.consultation.pk,
                "full_name": (
                    f"{record.consultation.expert.last_name} {record.consultation.expert.first_name}"
                ),
                "date": date,
            }
            if record.consultation.is_group:
                consultations_info["group"].append(new_record)
            else:
                consultations_info["personal"].append(new_record)

        return consultations_info


class ConsultationInterval:
    @staticmethod
    async def get_by_user(tg_id: int, is_group: bool):
        date = timezone.now().astimezone(pytz.timezone("Europe/Moscow"))

        user_intervals = models.ConsultationRecord.objects.filter(
            user__tg_id=tg_id,
            consultation__is_group=is_group
        ).values("consultation__interval__pk").annotate(count=Count("consultation__interval__pk")).order_by()

        unavailable_intervals = []
        async for interval in user_intervals:
            if interval.get("count", 2) >= 2:
                interval_pk = interval.get("consultation__interval__pk")
                if interval_pk:
                    unavailable_intervals.append(interval_pk)

        intervals = models.ConsultationInterval.objects.filter(
            (Q(date__day=date.day) & Q(start_time__gt=(date + datetime.timedelta(minutes=5)).time())) |
            (Q(date__day=(date + datetime.timedelta(days=1)).day) & Q(start_time__lt=date.time()))
        ).exclude(pk__in=unavailable_intervals)

        intervals_list = []
        async for interval in intervals:
            if await interval.consultations.filter(is_active=True, is_group=is_group).aexists():
                intervals_list.append({
                    "pk": interval.pk,
                    "date": (
                        f"{interval.date.strftime('%d %B')} "
                        f"{interval.start_time.strftime('%H:%M')}-{interval.end_time.strftime('%H:%M')}"
                    )
                })

        return intervals_list


class Utils:
    @staticmethod
    async def add_message_to_delete(message_id: int, chat_id: int, message_type: str):
        await models.MessageToDelete.objects.acreate(
            id=message_id,
            chat_id=chat_id,
            type=message_type
        )

    @staticmethod
    async def delete_message_by_type(chat_id: int, message_types: list, bot: Bot):
        messages = models.MessageToDelete.objects.filter(chat_id=chat_id, type__in=message_types)
        async for message in messages:
            with suppress(TelegramBadRequest):
                await bot.delete_message(message_id=message.id, chat_id=message.chat_id)
        await messages.adelete()

    @staticmethod
    async def delete_messages(bot: Bot, types: list, next_day: bool = False):
        messages = models.MessageToDelete.objects.filter(type__in=types)
        if next_day:
            date = timezone.now().astimezone(pytz.timezone("Europe/Moscow"))
            messages = messages.filter(created_at__date=(date - datetime.timedelta(days=1)).date())
        async for message in messages:
            with suppress(TelegramBadRequest):
                await bot.delete_message(message_id=message.id, chat_id=message.chat_id)
            await asyncio.sleep(1)
        await messages.adelete()


class Notification:
    @staticmethod
    async def get_choices(notif_type: str):
        date = timezone.now().astimezone(pytz.timezone("Europe/Moscow"))

        choices_list = []
        match notif_type:
            case "feedback":
                events = models.Event.objects.filter(status="not_send",
                                                     date__date=date.date())
                async for event in events:
                    choices_list.append({
                        "pk": event.pk,
                        "name": event.name
                    })
            case "activity":
                activities = models.Activity.objects.filter()
                choices_names = []
                async for activity in activities:
                    if activity.name not in choices_names:
                        choices_names.append(activity.name)
                        choices_list.append({
                            "pk": activity.pk,
                            "name": activity.name
                        })
            case "consultation":
                consultations = models.Consultation.objects.select_related().order_by(
                    "interval__date", "start_time"
                ).filter(is_active=True)
                async for consultation in consultations:
                    choices_list.append({
                        "pk": consultation.pk,
                        "name": (
                            f"{consultation.expert.last_name} {consultation.expert.first_name} "
                            f"({consultation.interval.date.strftime('%d %B')} "
                            f"{consultation.start_time.strftime('%H:%M')})"
                        )
                    })
            case "roles":
                roles = models.User.Status.choices
                for role in roles:
                    choices_list.append({
                        "pk": role[0],
                        "name": f"{role[1]} ❌"
                    })
                choices_list.append({
                    "pk": "continue",
                    "name": "Продолжить ➡️"
                })

        return choices_list

    @staticmethod
    async def get_name(pk: int, notif_type: str):
        name = ""
        try:
            match notif_type:
                case "person":
                    user = await models.User.objects.aget(pk=pk)
                    name = f"{user.last_name} {user.first_name} (@{user.username})"
                case "feedback":
                    name = await models.Event.objects.values_list("name", flat=True).aget(pk=pk)
                case "activity":
                    name = await models.Activity.objects.values_list("name", flat=True).aget(pk=pk)
                case "consultation":
                    consultation = await models.Consultation.objects.select_related().aget(pk=pk)
                    name = (
                        f"{consultation.expert.last_name} {consultation.expert.first_name} "
                        f"({consultation.start_time.strftime('%H:%M')})"
                    )
            return name

        except ObjectDoesNotExist:
            return None

    @staticmethod
    async def get_tg_id(obj: (models.ActivityRecord | models.ConsultationRecord
                              | models.User | models.Transfer | models.Living)):
        if isinstance(obj, models.User):
            tg_id = obj.tg_id
        else:
            tg_id = obj.user.tg_id

        return tg_id

    @staticmethod
    async def send_notifs_by_manager(notif_type: str, bot: Bot, pk: int | list = None, notif_text: str = None):
        send_count = 0

        objects = []
        reply_markup = None
        bot_msg = None

        match notif_type:
            case "activity":
                activity = await models.Activity.objects.aget(pk=pk)
                objects = models.ActivityRecord.objects.select_related().filter(activity=activity)

            case "consultation":
                consultation = await models.Consultation.objects.aget(pk=pk)
                objects = models.ConsultationRecord.objects.select_related().filter(consultation=consultation)

            case "roles":
                objects = models.User.objects.filter(status__in=pk)

            case "person":
                objects = models.User.objects.filter(pk=pk)

            case "feedback":
                event = await models.Event.objects.aget(pk=pk)
                objects = models.User.objects.filter(~Q(status="manager"))
                notif_text = notif_text.format(name=event.name)
                kb_builder = InlineKeyboardBuilder()
                new_button = InlineKeyboardButton(text="Оценить",
                                                  callback_data=f"feedbackstart_{event.pk}")
                kb_builder.add(new_button)
                reply_markup = kb_builder.as_markup()

        async for obj in objects:
            try:
                bot_msg = await bot.send_message(chat_id=await Notification.get_tg_id(obj=obj),
                                                 text=notif_text,
                                                 reply_markup=reply_markup)
                await Utils.add_message_to_delete(
                    message_id=bot_msg.message_id,
                    chat_id=bot_msg.chat.id,
                    message_type="notif"
                )
                if bot_msg:
                    send_count += 1
                await asyncio.sleep(0.034)
            except Exception as e:
                await sync_to_async(print)(e)

        if notif_type == "feedback":
            if bot_msg:
                await models.Event.objects.filter(pk=pk).aupdate(status="send")
            else:
                await models.Event.objects.filter(pk=pk).aupdate(status="failed")

        return send_count

    @staticmethod
    async def send_notifs(notif_type: str, bot: Bot):
        date = timezone.now().astimezone(pytz.timezone("Europe/Moscow"))

        match notif_type:
            case "transfer":
                transfers = models.Transfer.objects.select_related().filter(
                    date__date=(date + datetime.timedelta(days=1)).date())
                async for transfer in transfers:
                    try:
                        bot_msg = await bot.send_message(
                            chat_id=transfer.user.tg_id,
                            text=manager_text.transfer_notif.format(
                                time=transfer.date.astimezone(pytz.timezone("Europe/Moscow")).time().strftime("%H:%M"),
                                place=transfer.place,
                                car_num=transfer.car_num,
                                driver_num=transfer.driver_num
                            )
                        )
                        await Utils.add_message_to_delete(
                            message_id=bot_msg.message_id,
                            chat_id=bot_msg.chat.id,
                            message_type="transfer"
                        )
                        await models.Transfer.objects.filter(pk=transfer.id).aupdate(status="send")
                    except Exception as e:
                        await sync_to_async(print)(e)
                        await models.Transfer.objects.filter(pk=transfer.id).aupdate(status="failed")
                    await asyncio.sleep(1)
            case "living":
                livings = models.Living.objects.select_related().filter(date=(date + datetime.timedelta(days=1)).date())
                async for living in livings:
                    try:
                        bot_msg = await bot.send_message(
                            chat_id=living.user.tg_id,
                            text=manager_text.living_notif.format(
                                room=living.room,
                                build=living.build
                            )
                        )
                        await Utils.add_message_to_delete(
                            message_id=bot_msg.message_id,
                            chat_id=bot_msg.chat.id,
                            message_type="living"
                        )
                        await models.Living.objects.filter(pk=living.id).aupdate(status="send")
                    except Exception as e:
                        await sync_to_async(print)(e)
                        await models.Living.objects.filter(pk=living.id).aupdate(status="failed")
                    await asyncio.sleep(1)
            case "activity":
                activities = models.Activity.objects.filter(date__date=(date + datetime.timedelta(days=1)).date())
                async for activity in activities:
                    records = models.ActivityRecord.objects.select_related().filter(activity=activity)
                    notif_text = activity.template
                    failed = None
                    async for record in records:
                        try:
                            bot_msg = await bot.send_message(
                                chat_id=record.user.tg_id,
                                text=notif_text
                            )
                            await Utils.add_message_to_delete(
                                message_id=bot_msg.message_id,
                                chat_id=bot_msg.chat.id,
                                message_type="activity"
                            )
                        except Exception as e:
                            await sync_to_async(print)(e)
                            failed = True
                        await asyncio.sleep(1)
                    if not failed:
                        await models.Activity.objects.filter(pk=activity.id).aupdate(status="send")
                    else:
                        await models.Activity.objects.filter(pk=activity.id).aupdate(status="failed")

            case "schedule":
                schedules = models.Schedule.objects.filter(date=date.date())
                users = models.User.objects.filter(~Q(status="manager"))
                async for schedule in schedules:
                    async for user in users:
                        try:
                            bot_msg = await bot.send_message(
                                chat_id=user.tg_id,
                                text=schedule.template
                            )
                            await Utils.add_message_to_delete(
                                message_id=bot_msg.message_id,
                                chat_id=bot_msg.chat.id,
                                message_type="schedule"
                            )
                            await models.Schedule.objects.filter(pk=schedule.id).aupdate(status="send")
                        except Exception as e:
                            await sync_to_async(print)(e)
                            await models.Schedule.objects.filter(pk=schedule.id).aupdate(status="failed")
                        await asyncio.sleep(1)
            case "consultation":
                consultations = models.Consultation.objects.select_related().filter(
                    interval__date=date.date())
                async for consultation in consultations:
                    records = models.ConsultationRecord.objects.select_related().filter(consultation=consultation)
                    notif_text = manager_text.consultation_notif.format(
                        expert=f"{consultation.expert.last_name} {consultation.expert.first_name}",
                        date=f"{consultation.interval.date.strftime('%d %B')} "
                             f"в {consultation.start_time.strftime('%H:%M')}")
                    failed = None
                    async for record in records:
                        try:
                            bot_msg = await bot.send_message(
                                chat_id=record.user.tg_id,
                                text=notif_text
                            )
                            await Utils.add_message_to_delete(
                                message_id=bot_msg.message_id,
                                chat_id=bot_msg.chat.id,
                                message_type="consultation"
                            )
                        except Exception as e:
                            await sync_to_async(print)(e)
                            failed = True
                        await asyncio.sleep(1)
                    if not failed:
                        await models.Consultation.objects.filter(pk=consultation.id).aupdate(status="send")
                    else:
                        await models.Consultation.objects.filter(pk=consultation.id).aupdate(status="failed")

    @staticmethod
    async def feedback_send(tg_id: int, pk: int, feedback_dict: dict):
        user_id = await models.User.objects.values_list("pk", flat=True).aget(tg_id=tg_id)
        status = await models.Feedback.objects.acreate(
            event_id=pk,
            user_id=user_id,
            impression=feedback_dict["grade_1"],
            liked=feedback_dict["grade_2"],
            useful=feedback_dict["grade_3"],
            relevant=feedback_dict["grade_4"]
        )

        return status


class SpamFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext, bot: Bot) -> Union[bool, Dict[str, Any]]:
        data = await state.get_data()
        new_message = int(time.time())
        old_message = data.get("old_message")
        spam_count = data.get("spam_count")
        if not spam_count:
            spam_count = 0

        if old_message and new_message - old_message >= 60:
            await Utils.delete_message_by_type(chat_id=message.chat.id, message_types=["flood"], bot=bot)
            await state.update_data({"old_message": new_message, "spam_count": 0, "is_banned": False})
            return True

        elif spam_count >= 8:
            await message.delete()
            is_banned = data.get("is_banned")
            if not is_banned:
                flood_msg = await message.answer(
                    "Антифлуд система!\n"
                    "Подождите 60 секунд."
                )
                await Utils.add_message_to_delete(
                    message_id=flood_msg.message_id,
                    chat_id=flood_msg.chat.id,
                    message_type="flood"
                )
            await state.update_data(
                {
                    "old_message": new_message,
                    "is_banned": True
                }
            )
            return False

        elif old_message and new_message - old_message <= 5:
            await state.update_data({"spam_count": int(spam_count + 1)})

        await state.update_data({"old_message": new_message})
        return True


def or_f_list(*targets: "CallbackType") -> _OrFilter:
    from aiogram.dispatcher.event.handler import FilterObject
    target_list = []
    for target in targets:
        target_list.append(FilterObject(target))
    return _OrFilter(*target_list)
