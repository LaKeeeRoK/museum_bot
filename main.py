#!/usr/bin/env python3
import csv
import logging
import time
import telebot
from telebot import types

# Установите токен вашего бота
TOKEN = " token"

# Настройка логирования
logging.basicConfig(level=logging.INFO)


class MuseumBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.steps = {
            1: ["Центр", "Север", "Запад", "Юг", "Восток"],
            2: [
                "История", "Архитектура", "Искусство", "Литература",
                "Музыка", "Наука и техника", "Природа", "Этнография"
            ],
            3: ["до 200 рублей", "200-450 рублей", "450+ рублей"],
        }
        self.texts = {
            1: "Выберите примерное местоположение:",
            2: "Выберите сферу интересов:",
            3: "Выберите ценовой диапазон:",
        }
        self.user_choices = {}
        self.data_users = {}

    def send_keyboard(self, chat_id, step):
        """Функция для отправки клавиатуры с кнопками для текущего шага."""
        try:
            keyboard = types.InlineKeyboardMarkup()

            if step == 2:
                # Получаем выбранное местоположение
                location = self.user_choices[chat_id][0]
                # Фильтруем категории по местоположению
                available_categories = self.get_available_categories(location)
                buttons = [
                    types.InlineKeyboardButton(text=btn, callback_data=f"step{step}:{btn}")
                    for btn in available_categories
                ]
            else:
                buttons = [
                    types.InlineKeyboardButton(text=btn, callback_data=f"step{step}:{btn}")
                    for btn in self.steps[step]
                ]

            keyboard.add(*buttons)
            self.bot.send_message(chat_id, self.texts[step], reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Ошибка при отправке клавиатуры: {e}")

    def get_available_categories(self, location):
        """Функция для получения доступных категорий по местоположению."""
        categories = set()
        with open("muzei.csv", "r", encoding="utf-8", errors="ignore") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=";")
            for row in csvreader:
                if row[4] == location:
                    categories.add(row[1])
        return list(categories)

    def get_museum(self, user_choices):
        """Функция для выбора музея из базы данных."""
        name, link = [], []
        location, interest = user_choices
        with open("muzei.csv", "r", encoding="utf-8", errors="ignore") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=";")
            for row in csvreader:
                if row[1] == interest and row[4] == location:
                    name.append(row[0])
                    link.append(row[-1])
        return name, link

    def start_message(self, message):
        """Обработчик команды /start."""
        try:
            self.user_choices[message.chat.id] = []
            self.bot.send_message(message.chat.id, "Привет! Я бот-помощник с выбором музея.")
            self.send_keyboard(message.chat.id, 1)
        except Exception as e:
            logging.error(f"Ошибка в обработчике команды /start: {e}")

    def callback_query(self, call):
        """Обработчик нажатий на кнопки."""
        try:
            self.bot.answer_callback_query(call.id)
            chat_id = call.message.chat.id
            if ":" not in call.data:
                logging.warning(f"Неправильный формат данных в callback_query: {call.data}")
                return

            step, user_choice = call.data.split(":")

            if chat_id not in self.user_choices:
                self.user_choices[chat_id] = []
            self.user_choices[chat_id].append(user_choice)
            self.data_users[chat_id] = [], []

            if step == "step1":
                self.send_keyboard(chat_id, 2)
            elif step == "step2":
                self.data_users[chat_id] = self.get_museum(self.user_choices[chat_id])
                if self.data_users[chat_id][0]:
                    response = "\n\n".join(
                        [f"Мы рекомендуем вам посетить {name} ({link})" for name, link in zip(self.data_users[chat_id][0], self.data_users[chat_id][1])]
                    )
                    self.bot.send_message(chat_id, response)
                    self.bot.send_message(chat_id, "Для повторного использования отправь мне команду /start")
                else:
                    self.bot.send_message(chat_id, "К сожалению, подходящих музеев не найдено. Отправьте еще раз /start")
                del self.user_choices[chat_id]
                del self.data_users[chat_id]
        except Exception as e:
            logging.error(f"Ошибка в обработчике callback_query: {e}")

    def run(self):
        self.bot.message_handler(commands=["start"])(self.start_message)
        self.bot.callback_query_handler(func=lambda call: True)(self.callback_query)

        while True:
            try:
                self.bot.polling(none_stop=True)
            except Exception as e:
                logging.error(f"Ошибка в polling: {e}")
                time.sleep(10)  # Добавляем задержку перед повторным запуском


if __name__ == "__main__":
    museum_bot = MuseumBot(TOKEN)
    museum_bot.run()
