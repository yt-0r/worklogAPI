import telebot
from telebot import types
from db_sqlite import auth, update

bot_token = '7256671211:AAGTZKYiVcg_y3jfvBBqtBXLHilIwG7he3Q'
bot = telebot.TeleBot(bot_token)

# Создаем клавиатуру с кнопками
start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("Доступные каналы 📺")
item2 = types.KeyboardButton("Мои подписки 👀")
start_markup.add(item1).row(item2)

# кнопки доступных каналов
channels_markup = types.InlineKeyboardMarkup()
item1 = types.InlineKeyboardButton("Ошибки табеля 📗", callback_data='worklog')
item2 = types.InlineKeyboardButton("Ошибки кадровых документов 📑", callback_data='doccorp')
item3 = types.InlineKeyboardButton("Ошибки переадресации 📞📲", callback_data='redirect')

channels_markup.add(item1).row(item2).row(item3)

# кнопки табеля
worklog_markup = types.InlineKeyboardMarkup()
sub = types.InlineKeyboardButton("Подписаться 🔔", callback_data='sub_worklog')
unsub = types.InlineKeyboardButton("Отписаться 🔕", callback_data='unsub_worklog')
worklog_markup.add(sub).row(unsub)

# кнопки кадровых документов
doccorp_markup = types.InlineKeyboardMarkup()
sub = types.InlineKeyboardButton("Подписаться 🔔", callback_data='sub_doccorp')
unsub = types.InlineKeyboardButton("Отписаться 🔕", callback_data='unsub_doccorp')
doccorp_markup.add(sub).row(unsub)

# кнопки переадресации
redirect_markup = types.InlineKeyboardMarkup()
sub = types.InlineKeyboardButton("Подписаться 🔔", callback_data='sub_redirect')
unsub = types.InlineKeyboardButton("Отписаться 🔕", callback_data='unsub_redirect')
redirect_markup.add(sub).row(unsub)

user = {}


# Обработчик команды /start или /help для приветствия пользователя и отправки кнопок
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    global user
    user = auth(user_id, user_name)

    bot.send_message(message.chat.id, "Главное меню", reply_markup=start_markup)


@bot.message_handler(func=lambda message: message.text == 'Доступные каналы 📺')
def send_channels(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    global user
    user = auth(user_id, user_name)

    bot.send_message(message.chat.id, "Доступные каналы 📺", reply_markup=channels_markup)


@bot.message_handler(func=lambda message: message.text == 'Мои подписки 👀')
def send_my_channels(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    global user
    user = auth(user_id, user_name)

    worklog = 'Активна ✅' if user['worklog_errors'] == 1 else 'Неактивна ❌'
    doccorp = 'Активна ✅' if user['doccorp_errors'] == 1 else 'Неактивна ❌'
    redirect = 'Активна ✅' if user['redirect_errors'] == 1 else 'Неактивна ❌'

    bot.send_message(message.chat.id, f"Мои подписки 👀\n"
                                      f"📗 Табель: {worklog} \n"
                                      f"📑 Кадровые документы: {doccorp} \n"
                                      f"📞📲 Переадресация: {redirect}",
                     parse_mode='HTML')


# Обработчик для кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    print(user)

    if call.data == "channels":
        bot.answer_callback_query(call.id)
        bot.send_message(call.chat.id, "Доступные каналы 📺", reply_markup=channels_markup)
    elif call.data == "worklog":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Табель 📗", reply_markup=worklog_markup)
    elif call.data == "doccorp":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Кадровые документы 📑", reply_markup=doccorp_markup)
    elif call.data == "redirect":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Переадресация 📞📲", reply_markup=redirect_markup)


    # обрабатываем подписку
    elif call.data.split('_')[0] == "sub" and user[f"{call.data.split('_')[1]}_errors"] == 0:

        subscribe = f"{call.data.split('_')[1]}_errors"
        user[subscribe] = 1
        update(subscribe, 1, user_id=call.from_user.id)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Подписка успешно оформлена ✅")

    elif call.data.split('_')[0] == "sub" and user[f"{call.data.split('_')[1]}_errors"] == 1:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Подписка уже оформлена ⚠️")

    # обрабатываем отписку
    elif call.data.split('_')[0] == "unsub" and user[f"{call.data.split('_')[1]}_errors"] == 1:
        subscribe = f"{call.data.split('_')[1]}_errors"
        user[subscribe] = 0
        update(subscribe, 0, user_id=call.from_user.id)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Подписка успешно отменена ❌")
    elif call.data.split('_')[0] == "unsub" and user[f"{call.data.split('_')[1]}_errors"] == 0:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Вы не подписаны на эту рассылку ⚠️")

    #
    # # подписка на табель
    # elif call.data == "sub_worklog" and user['worklog_errors'] == 0:
    #     user['worklog_errors'] = 1
    #     update('worklog_errors', 1, user_id=call.from_user.id)
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Подписка успешно оформлена ✅")
    # elif call.data == "sub_worklog" and user['worklog_errors'] == 1:
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Подписка уже оформлена ⚠️")
    #
    # # отписка от табеля
    # elif call.data == "unsub_worklog" and user['worklog_errors'] == 1:
    #     user['worklog_errors'] = 0
    #     update('worklog_errors', 0, user_id=call.from_user.id)
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Подписка успешно отменена ❌")
    # elif call.data == "unsub_worklog" and user['worklog_errors'] == 0:
    #     bot.send_message(call.message.chat.id, "Вы не подписаны на эту рассылку ⚠️")
    #
    # # подписка на кадровые
    # elif call.data == "sub_doccorp" and user['doccorp_errors'] == 0:
    #     user['doccorp_errors'] = 1
    #     update('doccorp_errors', 1, user_id=call.from_user.id)
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Подписка успешно оформлена ✅")
    # elif call.data == "sub_doccorp" and user['doccorp_errors'] == 1:
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Подписка уже оформлена ⚠️")
    #
    # # отписка от кадровых
    # elif call.data == "unsub_doccorp" and user['doccorp_errors'] == 1:
    #     user['doccorp_errors'] = 0
    #     update('doccorp_errors', 0, user_id=call.from_user.id)
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Подписка успешно отменена ❌")
    # elif call.data == "unsub_doccorp" and user['worklog_errors'] == 0:
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Вы не подписаны на эту рассылку ⚠️")
    #
    #     # подписка на переадресацию
    # elif call.data == "sub_redirect" and user['redirect_errors'] == 0:
    #     user['redirect_errors'] = 1
    #     update('redirect_errors', 1, user_id=call.from_user.id)
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Подписка успешно оформлена ✅")
    # elif call.data == "sub_redirect" and user['redirect_errors'] == 1:
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Подписка уже оформлена ⚠️")
    #
    # # отписка от переадресации
    # elif call.data == "unsub_redirect" and user['redirect_errors'] == 1:
    #     user['redirect_errors'] = 0
    #     update('redirect_errors', 0, user_id=call.from_user.id)
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Подписка успешно отменена ❌")
    # elif call.data == "unsub_redirect" and user['redirect_errors'] == 0:
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Вы не подписаны на эту рассылку ⚠️")


bot.polling(non_stop=True)
