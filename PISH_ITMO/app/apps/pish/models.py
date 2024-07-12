from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class CreateUpdateTracker(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        abstract = True


class User(CreateUpdateTracker):
    class Meta:
        db_table = "user"
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ("last_name", "first_name")

    class Status(models.TextChoices):
        USER = "user", "Участник"
        LISTENER = "listener", "Слушатель"
        EXPERT = "expert", "Эксперт"
        MANAGER = "manager", "Организатор"

    tg_id = models.BigIntegerField(blank=True, null=True, verbose_name="TG ID")
    username = models.CharField(max_length=64, verbose_name="Username")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    self_determination_map = models.URLField(blank=True, verbose_name="Карта самоопределения")

    status = models.CharField(max_length=8, choices=Status.choices, default=Status.USER, verbose_name="Роль")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class ConsultationInterval(CreateUpdateTracker):
    class Meta:
        db_table = "consult_interval"
        verbose_name = "интервал консультаций"
        verbose_name_plural = "интервалы консультаций"

    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время конца")

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time}"


class Consultation(CreateUpdateTracker):
    class Meta:
        db_table = "consultation"
        verbose_name = "консультация"
        verbose_name_plural = "консультации"

    class Status(models.TextChoices):
        SEND = "send", "Отправлено"
        FAILED = "failed", "Ошибка"
        NOT_SEND = "not_send", "Не отправлено"

    expert = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name="Эксперт",
        limit_choices_to=Q(status="expert"),
        related_name="consultations",
    )
    interval = models.ForeignKey(
        "ConsultationInterval", on_delete=models.PROTECT, related_name="consultations", verbose_name="Интервал"
    )
    start_time = models.TimeField(verbose_name="Время начала", help_text=(
        "Для групповых должно совпадать с началом интервала.<br>"
        "Для индивидуальных должно быть в пределах интервала."
    ))
    count = models.PositiveSmallIntegerField(default=0, verbose_name="Записей")
    max_count = models.PositiveSmallIntegerField(default=1, verbose_name="Лимит записей")
    is_group = models.BooleanField(default=False, verbose_name="Групповая?")
    is_active = models.BooleanField(default=False, verbose_name="Активен?")
    template = models.TextField(blank=True, verbose_name="Шаблон рассылки")

    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.NOT_SEND, verbose_name="Статус рассылки"
    )

    def __str__(self):
        return f"{self.expert}"

    def clean(self) -> None:
        if self.is_group:
            if self.start_time != self.interval.start_time:
                raise ValidationError({
                    "start_time": "Время начала групповой консультации должно совпадать с началом выбранного интервала"
                })
        else:
            if not self.interval.start_time <= self.start_time <= self.interval.end_time:
                raise ValidationError({
                    "start_time": "Время начала индивидуальной консультации должно входить в выбранный интервал"
                })


class ConsultationRecord(CreateUpdateTracker):
    class Meta:
        db_table = "consult_records"
        verbose_name = "запись на консультацию"
        verbose_name_plural = "записи на консультации"

    user = models.ForeignKey(
        "User", on_delete=models.PROTECT, db_index=True, verbose_name="Участник", related_name="consultation_records"
    )
    consultation = models.ForeignKey(
        "Consultation", on_delete=models.PROTECT, related_name="records", verbose_name="Консультация"
    )

    def __str__(self):
        return f"{self.user}"


class Activity(CreateUpdateTracker):
    class Meta:
        db_table = "activities"
        verbose_name = "активность"
        verbose_name_plural = "активности"

    class Status(models.TextChoices):
        SEND = "send", "Отправлено"
        FAILED = "failed", "Ошибка"
        NOT_SEND = "not_send", "Не отправлено"

    name = models.CharField(max_length=100, verbose_name="Название")
    date = models.DateTimeField(verbose_name="Дата и время")
    template = models.TextField(blank=True, verbose_name="Шаблон рассылки")

    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.NOT_SEND, verbose_name="Статус рассылки"
    )

    def __str__(self):
        return f"{self.name}"


class ActivityRecord(CreateUpdateTracker):
    class Meta:
        db_table = "activ_record"
        verbose_name = "запись на активность"
        verbose_name_plural = "записи на активности"

    user = models.ForeignKey(
        "User", on_delete=models.PROTECT, db_index=True, verbose_name="Участник", related_name="activity_records"
    )
    activity = models.ForeignKey(
        "Activity", on_delete=models.PROTECT, verbose_name="Активность", related_name="records"
    )

    def __str__(self):
        return f"{self.user}"


class Event(CreateUpdateTracker):
    class Meta:
        db_table = "events"
        verbose_name = "мероприятие"
        verbose_name_plural = "мероприятия"

    class Status(models.TextChoices):
        SEND = "send", "Отправлено"
        FAILED = "failed", "Ошибка"
        NOT_SEND = "not_send", "Не отправлено"

    name = models.CharField(max_length=100, verbose_name="Название")
    date = models.DateTimeField(verbose_name="Дата и время")

    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.NOT_SEND, verbose_name="Статус рассылки"
    )

    def __str__(self):
        return f"{self.name}"


class Feedback(CreateUpdateTracker):
    class Meta:
        db_table = "feedback"
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"

    user = models.ForeignKey(
        "User", on_delete=models.PROTECT, db_index=True, verbose_name="Участник", related_name="feedbacks"
    )
    event = models.ForeignKey("Event", on_delete=models.PROTECT, verbose_name="Мероприятие", related_name="feedbacks")
    impression = models.PositiveSmallIntegerField(verbose_name="Впечатление")
    liked = models.PositiveSmallIntegerField(verbose_name="Понравился спикер")
    useful = models.PositiveSmallIntegerField(verbose_name="Полезность")
    relevant = models.PositiveSmallIntegerField(verbose_name="Применимость")

    def __str__(self):
        return f"{self.event} {self.user}"


class Transfer(CreateUpdateTracker):
    class Meta:
        db_table = "transfer"
        verbose_name = "трансфер"
        verbose_name_plural = "трансфер"

    class Direction(models.TextChoices):
        TO = "to", "Туда"
        FROM = "from", "Обратно"

    class Status(models.TextChoices):
        SEND = "send", "Отправлено"
        FAILED = "failed", "Ошибка"
        NOT_SEND = "not_send", "Не отправлено"

    user = models.ForeignKey(
        "User", on_delete=models.PROTECT, db_index=True, verbose_name="Участник", related_name="transfers"
    )
    date = models.DateTimeField(verbose_name="Дата и время")
    place = models.CharField(max_length=100, verbose_name="Место")
    car_num = models.CharField(max_length=100, verbose_name="Номер машины")
    driver_num = models.CharField(max_length=100, verbose_name="Номер водителя")

    direction = models.CharField(max_length=4, choices=Direction.choices, default=Direction.TO, verbose_name="Куда")

    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.NOT_SEND, verbose_name="Статус рассылки"
    )

    def __str__(self):
        return f"{self.user}"


class Living(CreateUpdateTracker):
    class Meta:
        db_table = "living"
        verbose_name = "проживание"
        verbose_name_plural = "проживание"

    class Status(models.TextChoices):
        SEND = "send", "Отправлено"
        FAILED = "failed", "Ошибка"
        NOT_SEND = "not_send", "Не отправлено"

    user = models.ForeignKey(
        "User", on_delete=models.PROTECT, db_index=True, verbose_name="Участник", related_name="livings"
    )
    room = models.CharField(max_length=100, verbose_name="Номер")
    build = models.CharField(max_length=100, verbose_name="Корпус")
    date = models.DateField()

    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.NOT_SEND, verbose_name="Статус рассылки"
    )

    def __str__(self):
        return f"{self.user}"


class Schedule(CreateUpdateTracker):
    class Meta:
        db_table = "schedule"
        verbose_name = "расписание"
        verbose_name_plural = "расписание"

    class Status(models.TextChoices):
        SEND = "send", "Отправлено"
        FAILED = "failed", "Ошибка"
        NOT_SEND = "not_send", "Не отправлено"

    date = models.DateField(verbose_name="Дата")
    template = models.TextField(blank=True, verbose_name="Шаблон рассылки")

    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.NOT_SEND, verbose_name="Статус рассылки"
    )

    def __str__(self):
        return f"{self.date}"


class Storage(models.Model):
    class Meta:
        db_table = "storage"
        verbose_name = "хранилище"
        verbose_name_plural = "хранилище"

    key = models.CharField(max_length=256, primary_key=True, db_index=True)
    data = models.JSONField(max_length=1024, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.key}"


class MessageToDelete(models.Model):
    class Meta:
        db_table = "message"
        verbose_name = "отложенное удаление"
        verbose_name_plural = "отложенные удаления"

    class Type(models.TextChoices):
        IMENU = "imenu", "Inline Menu"
        RMENU = "rmenu", "Reply Menu"
        FLOOD = "flood", "Flood"
        NOTIF = "notif", "Notification"
        FEEDBACK = "feedback", "Feedback"
        ACTIVITY = "activity", "Activity"
        CONSULTATION = "consultation", "Consultation"
        TRANSFER = "transfer", "Transfer"
        LIVING = "living", "Living"
        SCHEDULE = "schedule", "Schedule"
        GENERAL = "general", "General"

    id = models.PositiveBigIntegerField(primary_key=True, verbose_name="Message ID")
    chat_id = models.PositiveBigIntegerField(verbose_name="Chat ID")
    type = models.CharField(max_length=12, choices=Type.choices, verbose_name="Тип")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="Создан")

    def __str__(self):
        return f"{self.id}"
