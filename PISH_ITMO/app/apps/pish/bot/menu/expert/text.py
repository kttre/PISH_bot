def consultations(consultations_list):
    text = list()
    text.append("К вам записаны:\n")
    for consultation in consultations_list:
        text.append(f"<b>{consultation['date']}</b>\n")
        for user_data in consultation['users']:
            if user_data[1]:
                text.append(f'<a href="{user_data[1]}">{user_data[0]}</a>\n')
            else:
                text.append(f"{user_data[0]}\n")
        text.append(f"{'—' * 10}\n")

    return ''.join(text)


consultations_none = "Записи на ваши консультации отсутствуют."
