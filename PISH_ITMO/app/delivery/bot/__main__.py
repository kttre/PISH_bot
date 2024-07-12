import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.apps.pish.bot.menu.expert.router import router as expert_router
from app.apps.pish.bot.menu.manager.router import router as manager_router
from app.apps.pish.bot.menu.router import router as menu_router
from app.apps.pish.bot.menu.user.router import router as user_router
from app.apps.pish.bot.registration.router import router as reg_router
from app.apps.pish.bot.start_command.router import router as start_router
from app.apps.pish.bot.storage import DjangoStorage
from app.apps.pish.bot.utils import Notification, Utils
from app.config.bot import TG_TOKEN

bot = Bot(token=TG_TOKEN, parse_mode="HTML")
dispatcher = Dispatcher(storage=DjangoStorage())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _register_routers() -> None:
    dispatcher.include_router(start_router)
    dispatcher.include_router(menu_router)
    dispatcher.include_router(user_router)
    dispatcher.include_router(expert_router)
    dispatcher.include_router(manager_router)
    dispatcher.include_router(reg_router)


@dispatcher.startup()
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    _register_routers()

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(Notification.send_notifs, trigger="cron", hour=20,
                      minute=5, start_date=datetime.now(),
                      kwargs={"notif_type": "transfer", "bot": bot})
    scheduler.add_job(Notification.send_notifs, trigger="cron", hour=20,
                      minute=10, start_date=datetime.now(),
                      kwargs={"notif_type": "living", "bot": bot})
    scheduler.add_job(Notification.send_notifs, trigger="cron", hour=21,
                      minute=0, start_date=datetime.now(),
                      kwargs={"notif_type": "activity", "bot": bot})
    scheduler.add_job(Notification.send_notifs, trigger="cron", hour=8,
                      minute=0, start_date=datetime.now(),
                      kwargs={"notif_type": "schedule", "bot": bot})
    scheduler.add_job(Notification.send_notifs, trigger="cron", hour=16,
                      minute=0, start_date=datetime.now(),
                      kwargs={"notif_type": "consultation", "bot": bot})
    scheduler.add_job(Utils.delete_messages, trigger="cron", hour=23,
                      minute=55, start_date=datetime.now(),
                      kwargs={"bot": bot, "next_day": True, "types": ["transfer", "living"]})
    scheduler.add_job(Utils.delete_messages, trigger="cron", hour=17,
                      minute=0, start_date=datetime.now(),
                      kwargs={"bot": bot, "next_day": True, "types": ["activity"]})
    scheduler.add_job(Utils.delete_messages, trigger="cron", hour=19,
                      minute=0, start_date=datetime.now(),
                      kwargs={"bot": bot, "types": ["consultation"]})
    scheduler.add_job(Utils.delete_messages, trigger="cron", hour=23,
                      minute=59, start_date=datetime.now(),
                      kwargs={"bot": bot, "types": ["imenu", "notif", "feedback", "general", "schedule"]})
    scheduler.start()


def run_polling() -> None:
    dispatcher.run_polling(bot)


if __name__ == "__main__":
    run_polling()
