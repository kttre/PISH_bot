register = "Здесь вы можете записаться к эксперту на <b>групповую</b> или <b>личную</b> встречу"
register_unavailable = (
    "Пока запись недоступна. \n"
    "Регистрация откроется за сутки до встречи с экспертом "
    "и закроется за 5 минут до старта встреч с экспертами"
    )

deregister = "Здесь вы можете отменить свои записи к экспертам на <b>групповые</b> или <b>личные</b> встречи"
deregister_unavailable = "У вас нет записей на предстоящие {consultation_type} встречи"


def diary(diary_list):
    group_consultations = diary_list.get("group")
    personal_consultations = diary_list.get("personal")

    text = "Групповые встречи:\n"
    if group_consultations:
        for consultation in group_consultations:
            text += f"{consultation['date']} вы записаны к {consultation['full_name']}\n"
    else:
        text += "Вы не записаны на встречи\n"

    text += "\nИндивидуальная встреча:\n"
    if personal_consultations:
        for consultation in personal_consultations:
            text += f"{consultation['date']} вы записаны к {consultation['full_name']}\n"
    else:
        text += "Вы не записаны на встречу\n"

    return text


diary_none = (
    "Пока вы не записаны ни на одну встречу с экспертом. "
    'Для записи вернитесь в основное меню и нажмите <b>«Записаться»</b>'
)
intervals = "Выберите временной слот, в который вы хотите записаться. Вы можете выбрать <b>1 эксперта</b>."


def experts(is_group):
    if is_group:
        return (
            "Ниже вы увидите всех экспертов, к которым можно записаться. "
            "Встреча пройдет в <b>групповом</b> формате по 8 человек."
        )
    else:
        return (
            "Ниже вы увидите всех экспертов, к которым можно записаться. "
            "Консультации проходят в индивидуальном формате."
        )
    

experts_none = "Нет доступных экспертов в данном временном промежутке"
dates_none = "У данного эксперта отсутствует время записи"
dates_choose = "Доступны следующие временные слоты. После выбора времени, нажмите на кнопку <b>«Подтвердить»</b>"
register_confirm = "Вы хотите записаться к"
register_end = "Вы успешно записаны"
register_error = "Во время регистрации произошла ошибка, попробуйте еще раз"

deregister_choose = "Выберите запись, которую хотите отменить:"
deregister_confirm = "Вы хотите отменить запись к"
deregister_end = "Вы успешно отменили запись"
deregister_error = "Во время отмены записи произошла ошибка, попробуйте еще раз"
