#!/usr/bin/env python3
import telebot
from telebot import types
import time
import logging
import sqlite3
import csv

# Установите токен вашего бота
TOKEN = 'token'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объекта бота
bot = telebot.TeleBot(TOKEN)

# Словарь с шагами и кнопками
steps = {
    1: ['Центр', 'Север', 'Запад', 'Юг', 'Восток'],
    2: ['История', 'Архитектура', 'Искусство', 'Литература', 'Музыка', 'Наука и техника', 'Природа', 'Этнография'],
    3: ["до 200 рублей", "200-450 рублей", '450+ рублей'] 
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

# Функция для выбора музея из базы данных
def get_museum(user_choices, user_id=0):
    name = []
    link = []
    location, interest = user_choices
    with open('muzei.csv', 'r',encoding='utf-8', errors='ignore') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        for row in csvreader:
            if row[1] == interest and row[4] == location:
                name.append(row[0])
                link.append(row[-1])
    return name, link



# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        user_choices[message.chat.id] = []
        bot.send_message(message.chat.id, "Привет! Я бот-помощник с выбором музея.")
        send_keyboard(message.chat.id, 1)
    except Exception as e:
        logging.error(f'Ошибка в обработчике команды /start: {e}')

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        if ':' not in call.data:
            logging.warning(f'Неправильный формат данных в callback_query: {call.data}')
            return

        step, user_choice = call.data.split(':')

        if chat_id not in user_choices:
            user_choices[chat_id] = []
        user_choices[chat_id].append(user_choice)
        data_users[chat_id] = [], []

        if step == 'step1':
            send_keyboard(chat_id, 2)
        elif step == 'step2':
            data_users[chat_id] = get_museum(user_choices[chat_id])
            if len(data_users[chat_id][0]) > 0:
                response = ""
                for i in range(len(data_users[chat_id][0])):
                    response += f'Мы рекомендуем вам посетить {data_users[chat_id][0][i]}, {data_users[chat_id][1][i]}\n\n'

                bot.send_message(chat_id, response)

                bot.send_message(chat_id, "Для повторного использования отправь мне команду /start")
            else:
                bot.send_message(chat_id, 'К сожалению, подходящих музеев не найдено. Отправьте еще раз /start')


            del user_choices[chat_id]  # Удаляем запись о выборе пользователя
            del data_users[chat_id]
    except Exception as e:
        logging.error(f'Ошибка в обработчике callback_query: {e}')

# Запуск бота с обработкой исключений
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f'Ошибка в polling: {e}')
        time.sleep(10)  # Добавляем задержку перед повторным запуском
