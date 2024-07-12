notif_type = "Выберите критерий назначения рассылки"

notif_recipient = {
    "feedback": "Необходимо выбрать мероприятие, по которому хотите отправить оценку",
    "activity": "Выберите активность",
    "consultation": "Выберите консультацию",
    "roles": "Выберите роли"
}
choices_none = "Отсутствуют варианты выбора для данного критерия"

choose_person = (
    "Введи фамилию и имя или никнейм пользователя.\n"
    "Например:\n"
    "<b>Иванов Петр\n</b>"
    "<b>@PISH_ITMO_bot</b>"
)

person_found = (
    "Найден пользователь <b>{full_name}</b> (@{username}).\n"
    "Продолжить работу с ним?"
)
person_none = "Пользователь {person} не найден!\nПопробуй еще раз"

write_msg = "Напишите сообщение, которое необходимо разослать участникам"

feedback_confirm = "Вы уверены, что хотите отправить рассылку с оценкой <b>{name}</b>?"

too_long_msg = (
    "Слишком длинный текст, объём не должен превышать 4000 символов. Попробуй ещё раз"
)

type_names = {
    "user": "Участникам",
    "listener": "Слушателям",
    "expert": "Экспертам",
    "manager": "Организаторам"
}

send_confirm = "Ты хочешь отправить сообщение <b>{name}</b> следующего содержания:\n\n"
sending_in_process = "Идет процесс рассылки, ожидайте сообщение о его завершении"
sending_success = "{send_count} человек успешно получили рассылку"

feedback_message = "Вы только что посетили мероприятие <b>{name}</b>. Мы просим вас ответить на несколько вопросов."

consultation_notif = (
    "📍 Напоминаем, что вы записаны к {expert} на {date}.\n\n"
    "Ждем вас на <b>2 этаже комплекса</b>."
)
transfer_notif = (
    "🚘 Напоминаем, что завтра в {time} вас будет ожидать трансфер\n\n"
    "<b>Место сбора</b>:\n"
    "{place}\n"
    "<b>За вами подъедет:</b>\n"
    "{car_num}\n"
    "<b>Номер водителя:</b>\n"
    "{driver_num}\n\n"
    'P.s. Информация о трансфере доступна по кнопке <b>"Трансфер"</b> в меню!\n'
)
living_notif = (
    "🏘 Напоминаем, что вы живете в номере <b>{room}</b>, "
    "корпус <b>{build}</b>. Для заселения вам необходимо "
    "подойти с паспортом в ваш корпус и обратиться на ресепшн.\n\n"
    'P.s. Информация о проживании доступна по кнопке <b>"Проживание"</b> в меню!'
)