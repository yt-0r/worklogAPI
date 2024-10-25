import telebot
from telebot import types
from database.db_sqlite import auth, update

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
channels_markup.add(item1).row(item2)

# кнопки табеля
worklog_markup = types.InlineKeyboardMarkup()
sub = types.InlineKeyboardButton("Подписаться 🔔", callback_data='sub_worklog')
un_sub = types.InlineKeyboardButton("Отписаться 🔕", callback_data='un_sub_worklog')
worklog_markup.add(sub).row(un_sub)

# кнопки кадровых документов
doccorp_markup = types.InlineKeyboardMarkup()
sub = types.InlineKeyboardButton("Подписаться 🔔", callback_data='sub_doccorp')
un_sub = types.InlineKeyboardButton("Отписаться 🔕", callback_data='un_sub_doccorp')
doccorp_markup.add(sub).row(un_sub)

# кнопки моих подписок


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
    bot.send_message(message.chat.id, f"Мои подписки 👀\n📗 Табель: {worklog} \n📑 Кадровые документы: {doccorp}",
                     parse_mode='HTML')


# Обработчик для кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == 'channels':
        bot.answer_callback_query(call.id)
        bot.send_message(call.chat.id, "Доступные каналы 📺", reply_markup=channels_markup)
    elif call.data == "worklog":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Табель 📗", reply_markup=worklog_markup)
    elif call.data == "doccorp":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Кадровые документы 📑", reply_markup=doccorp_markup)

    # подписка на табель
    elif call.data == "sub_worklog" and user['worklog_errors'] == 0:
        user['worklog_errors'] = 1
        update('worklog_errors', 1, user_id=call.from_user.id)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Подписка успешно оформлена ✅")
    elif call.data == "sub_worklog" and user['worklog_errors'] == 1:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Подписка уже оформлена ⚠️")

    # отписка от табеля
    elif call.data == "un_sub_worklog" and user['worklog_errors'] == 1:
        user['worklog_errors'] = 0
        update('worklog_errors', 0, user_id=call.from_user.id)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Подписка успешно отменена ❌")
    elif call.data == "un_sub_worklog" and user['worklog_errors'] == 0:
        bot.send_message(call.message.chat.id, "Вы не подписаны на эту рассылку ⚠️")

    # подписка на кадровые
    elif call.data == "sub_doccorp" and user['doccorp_errors'] == 0:
        user['doccorp_errors'] = 1
        update('doccorp_errors', 1, user_id=call.from_user.id)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Подписка успешно оформлена ✅")
    elif call.data == "sub_doccorp" and user['doccorp_errors'] == 1:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Подписка уже оформлена ⚠️")

    # отписка от кадровых
    elif call.data == "un_sub_doccorp" and user['doccorp_errors'] == 1:
        user['doccorp_errors'] = 0
        update('doccorp_errors', 0, user_id=call.from_user.id)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Подписка успешно отменена ❌")
    elif call.data == "un_sub_doccorp" and user['worklog_errors'] == 0:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Вы не подписаны на эту рассылку ⚠️")


bot.polling(non_stop=True)
