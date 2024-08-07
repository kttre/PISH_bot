# Generated by Django 4.1.7 on 2023-06-12 20:43

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pish", "0004_alter_consultation_table"),
    ]

    operations = [
        migrations.AlterField(
            model_name="consultation",
            name="start_time",
            field=models.TimeField(
                default=datetime.datetime(2023, 6, 12, 23, 43, 22, 376900),
                help_text="Для групповых должно совпадать с началом интервала.<br>Для индивидуальных должно быть в пределах интервала.",
                verbose_name="Время начала",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="self_determination_map",
            field=models.URLField(blank=True, verbose_name="Карта самоопределения"),
        ),
    ]
