import telebot
from telebot import types

# Установите токен вашего бота
TOKEN = '7036666957:AAGq0yvxuIQJUGixBK4S4gQTY0CbsFlf6KU'

# Создание объекта бота
bot = telebot.TeleBot(TOKEN)

# Словарь с шагами и кнопками
steps = {
    1: ['Центр', 'Север', 'Запад', 'Юг', 'Восток'],
    2: ['История', 'Архитектура', 'Искусство', 'Литература', 'Музыка', 'Наука и техника', 'Природа', 'Этнография'],
    3: ["До 200 рублей", "200-450 рублей", '450+ рублей'] 
    }
texts = {
    1: "Выберите примерное местоположение:",
    2: "Выберите сферу интересов:",
    3: "Выберите ценовой диапазон:"
}

# Словарь для хранения выбранных пользователем кнопок
user_choices = {}


# Функция для отправки клавиатуры с кнопками для текущего шага
def send_keyboard(chat_id, step):
    try:
        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text=btn, callback_data=f'step{step}:{btn}') for btn in steps[step]]
        keyboard.add(*buttons)
        bot.send_message(chat_id, texts[step], reply_markup=keyboard)
    except Exception as e:
        logging.error(f'Ошибка при отправке клавиатуры: {e}')
data_users = {}


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
