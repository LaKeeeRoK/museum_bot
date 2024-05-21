import telebot
from telebot import types

# Укажите токен вашего бота
TOKEN = 'token'

# Создание объекта бота
bot = telebot.TeleBot(TOKEN)

# Словарь, где ключ - это номер шага, а значение - список кнопок для этого шага
steps = {
    1: ['Центр', 'Город', "Ленинградская область"],
    2: ['История города', 'Теника', "ВОВ", "Необычное"],
    3: ["До 500 рублей", "До тысячи", "Пушкниская карта"]
}
text = {
    1:"Выбери примерное местоположение",
    2:"Выбери сферу интереса",
    3:"Выбери ценовой диапазон",
}

# Словарь для хранения выбранных пользователем кнопок
user_choices = {}


# Функция для отправки клавиатуры с кнопками для текущего шага
def send_keyboard(chat_id, step):
    global text
    keyboard = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text=btn, callback_data=btn) for btn in steps[step]]
    keyboard.add(*buttons)
    bot.send_message(chat_id, text[step], reply_markup=keyboard)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    user_choices[message.chat.id] = []
    bot.send_message(message.chat.id, "Привет, Я Бот помошник с выбором музея. ")
    send_keyboard(message.chat.id, 1)


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user_choice = call.data
    if chat_id not in user_choices:
        user_choices[chat_id] = []
    user_choices[chat_id].append(user_choice)

    if user_choice in steps[1]:
        send_keyboard(chat_id, 2)
    elif user_choice in steps[2]:
        send_keyboard(chat_id, 3)
    else:
        bot.send_message(chat_id, f'Вы выбрали комбинацию: {", ".join(user_choices[chat_id])}')
        del user_choices[chat_id]  # Удаляем запись о выборе пользователя


# Запуск бота
bot.polling()