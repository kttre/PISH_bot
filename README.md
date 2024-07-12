# PISH_ITMO_bot

### Описание основных модулей

- [app/delivery/\__main\__.py](https://github.com/VyachSlave/PISH_ITMO_bot/blob/main/app/delivery/bot/__main__.p)  
Главный файл, который отвечает за запуск бота. Здесь же прикрепляются все роутеры и отложенные задачи APScheduler.
- [app/apps/pish/models.py](https://github.com/VyachSlave/PISH_ITMO_bot/blob/main/app/apps/pish/models.py)  
Модели БД
- [app/apps/pish/web/admin.py](https://github.com/VyachSlave/PISH_ITMO_bot/blob/main/app/apps/pish/web/admin.py)  
Админ-панель
- [app/apps/pish/bot/utils.py](https://github.com/VyachSlave/PISH_ITMO_bot/blob/main/app/apps/pish/bot/utils.py)  
Различные вспомогательные функции, в том числе обращения в базу
- [app/apps/pish/bot/start_command](https://github.com/VyachSlave/PISH_ITMO_bot/tree/main/app/apps/pish/bot/start_command)  
Пакет бота для обработки команды /start
- [app/apps/pish/bot/registration](https://github.com/VyachSlave/PISH_ITMO_bot/tree/main/app/apps/pish/bot/registration)  
Пакет бота для обработки событий, связанных с регистрацией
- [app/apps/pish/bot/menu](https://github.com/VyachSlave/PISH_ITMO_bot/tree/main/app/apps/pish/bot/menu)  
Пакет бота для обработки основных событий.  
Корневой пакет хранит обработчики, общие для всех ролей.  
Подпакеты разделены по ролям и отвечают за конкретные из них.

#### Каждый пакет состоит из нескольких основных модулей:
- router.py – обработчики
- keyboards.py – клавиатуры
- text.py – тексты сообщений
