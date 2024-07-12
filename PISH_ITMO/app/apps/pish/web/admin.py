import locale

from django.contrib import admin
from django.db.models import Avg
from django.urls import reverse
from django.utils.safestring import mark_safe

from app.apps.pish.models import *

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
date_format = "%d.%m (%a) %H:%M"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ("tg_id", "username", "first_name", "last_name", "self_determination_map", "status", "get_consultations")
    list_display = ["tg_id", "username", "get_name", "status"]
    list_filter = ["status"]
    search_fields = ("username", "tg_id", "last_name", "first_name")
    list_editable = ["status"]
    readonly_fields = ("get_consultations",)

    @admin.display(ordering="last_name", description="Фамилия и имя")
    def get_name(self, object):
        return object

    @admin.display(description="Записи на консультации")
    def get_consultations(self, object):
        records = object.consultation_records.all().select_related()
        records_list = ""
        for record in records:
            records_list += "<a href='{url}'>{consultation} – {date}</a><br>".format(
                url=reverse("admin:{}_{}_change".format(record._meta.app_label, record._meta.model_name),
                            args=(record.pk,)),
                consultation=f"{record.consultation.expert.last_name} {record.consultation.expert.first_name}",
                date=f"{record.consultation.interval.date.strftime('%d %B')} "
                     f"{record.consultation.start_time.strftime('%H:%M')}"
            )
        return mark_safe(records_list)


@admin.register(ConsultationInterval)
class ConsultationIntervalAdmin(admin.ModelAdmin):
    list_display = ["date", "start_time", "end_time"]


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = [
        "expert", "get_date", "get_time", "registered_count", "is_group", "has_template", "status", "is_active"
    ]
    list_filter = ["expert", "is_group", "status", "is_active"]
    list_editable = ["is_active"]
    readonly_fields = ("users_list",)
    ordering = ("-created_at",)

    @admin.display(ordering="interval__date", description="Дата")
    def get_date(self, object):
        return object.interval.date

    @admin.display(ordering="start_time", description="Время начала")
    def get_time(self, object):
        return object.start_time

    @admin.display(ordering="count", description="Записей")
    def registered_count(self, object):
        return f"{object.count}/{object.max_count}"

    @admin.display(description="Есть шаблон?", boolean=True)
    def has_template(self, object):
        if object.template:
            return True
        else:
            return False

    @admin.display(description="Список участников")
    def users_list(self, object):
        users = object.records.all().select_related()
        users_list = ""
        for user in users:
            users_list += "<a href='{url}'>{user}</a><br>".format(
                url=reverse("admin:{}_{}_change".format(user._meta.app_label, user._meta.model_name),
                            args=(user.pk,)),
                user=user.user)
        return mark_safe(users_list)


@admin.register(ConsultationRecord)
class ConsultationRecordAdmin(admin.ModelAdmin):
    list_display = ["get_user", "consultation", "get_is_group", "get_date", "get_time", "created_at"]
    list_display_links = ("get_user",)
    list_filter = ["consultation"]

    @admin.display(ordering="user__last_name", description="Фамилия и имя")
    def get_user(self, object):
        return object.user

    @admin.display(ordering="consultation__interval__date", description="Дата")
    def get_date(self, object):
        return object.consultation.interval.date

    @admin.display(ordering="consultation__start_time", description="Время начала")
    def get_time(self, object):
        return object.consultation.start_time

    @admin.display(description="Групповая?", boolean=True)
    def get_is_group(self, object):
        if object.consultation.is_group:
            return True
        else:
            return False


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "has_template", "status"]
    list_filter = ["name", "status"]
    search_fields = ("name",)
    ordering = ("-created_at",)

    @admin.display(description="Есть шаблон?", boolean=True)
    def has_template(self, object):
        if object.template:
            return True
        else:
            return False


@admin.register(ActivityRecord)
class ActivityRecordAdmin(admin.ModelAdmin):
    list_display = ["get_user", "activity", "get_date", "created_at"]
    list_display_links = ("get_user",)
    list_filter = ["activity"]

    @admin.display(ordering="user__last_name", description="Фамилия и имя")
    def get_user(self, object):
        return object.user

    @admin.display(ordering="activity__date", description="Дата и время")
    def get_date(self, object):
        return object.activity.date


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "get_avg_impression", "get_avg_liked",
                    "get_avg_useful", "get_avg_relevant",  "status"]
    list_filter = ["name", "status"]
    search_fields = ("name",)

    @admin.display(description="Впечатление")
    def get_avg_impression(self, object):
        feedbacks = object.feedbacks.all().aggregate(Avg("impression"))
        if feedbacks.get("impression__avg"):
            return round(feedbacks.get("impression__avg", 0), 2)

    @admin.display(description="Понравился спикер")
    def get_avg_liked(self, object):
        feedbacks = object.feedbacks.all().aggregate(Avg("liked"))
        if feedbacks.get("liked__avg"):
            return round(feedbacks.get("liked__avg", 0), 2)

    @admin.display(description="Полезность")
    def get_avg_useful(self, object):
        feedbacks = object.feedbacks.all().aggregate(Avg("useful"))
        if feedbacks.get("useful__avg"):
            return round(feedbacks.get("useful__avg", 0), 2)

    @admin.display(description="Применимость")
    def get_avg_relevant(self, object):
        feedbacks = object.feedbacks.all().aggregate(Avg("relevant"))
        if feedbacks.get("relevant__avg"):
            return round(feedbacks.get("relevant__avg", 0), 2)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["get_user", "event", "impression", "liked", "useful", "relevant", "created_at"]
    list_filter = ["event"]

    @admin.display(ordering="user__last_name", description="Фамилия и имя")
    def get_user(self, object):
        return object.user


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ["get_user", "direction", "date", "place", "car_num", "driver_num", "status"]

    @admin.display(ordering="user__last_name", description="Фамилия и имя")
    def get_user(self, object):
        return object.user


@admin.register(Living)
class LivingAdmin(admin.ModelAdmin):
    list_display = ["get_user", "room", "build", "date", "status"]

    @admin.display(ordering="user__last_name", description="Фамилия и имя")
    def get_user(self, object):
        return object.user


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ["date", "has_template", "status"]
    list_filter = ["status"]
    search_fields = ("date",)

    @admin.display(description="Есть шаблон?", boolean=True)
    def has_template(self, object):
        if object.template:
            return True
        else:
            return False


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    search_fields = ("key", "data")
    list_display = ["key", "data", "state"]


@admin.register(MessageToDelete)
class MessageToDeleteAdmin(admin.ModelAdmin):
    list_display = ["id", "chat_id", "type", "created_at"]
    search_fields = ("chat_id",)
    list_filter = ["type"]


admin.site.site_title = 'Админ-панель «ПИШ»'
admin.site.site_header = 'Админ-панель «ПИШ»'
