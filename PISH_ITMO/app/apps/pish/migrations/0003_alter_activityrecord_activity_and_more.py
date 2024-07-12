# Generated by Django 4.1.7 on 2023-06-12 14:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pish', '0002_user_self_determination_map'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityrecord',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='records', to='pish.activity', verbose_name='Активность'),
        ),
        migrations.AlterField(
            model_name='activityrecord',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='activity_records', to='pish.user', verbose_name='Участник'),
        ),
        migrations.AlterField(
            model_name='consultation',
            name='expert',
            field=models.ForeignKey(limit_choices_to=models.Q(('status', 'expert')), on_delete=django.db.models.deletion.PROTECT, related_name='consultations', to='pish.user', verbose_name='Эксперт'),
        ),
        migrations.AlterField(
            model_name='consultationrecord',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_records', to='pish.user', verbose_name='Участник'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='feedbacks', to='pish.event', verbose_name='Мероприятие'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='feedbacks', to='pish.user', verbose_name='Участник'),
        ),
        migrations.AlterField(
            model_name='living',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='livings', to='pish.user', verbose_name='Участник'),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transfers', to='pish.user', verbose_name='Участник'),
        ),
    ]
