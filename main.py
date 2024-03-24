import telebot
from telebot.types import InputFile
from config import TOKEN, ADMIN_ID
from gpt import generate_response
from database import create_table, update_user_settings, get_user_settings
import logging
from datetime import datetime
from database import create_table, update_user_settings, get_user_settings, recreate_table
from telebot import types
import os
bot = telebot.TeleBot(TOKEN)
log_filename = datetime.now().strftime('bot_log_%Y-%m-%d_%H-%M-%S.log')
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Словарь для хранения истории сообщений пользователей
user_messages_history = {}
MAX_HISTORY_LENGTH = 15


# Функция для отправки клавиатуры с темами
def send_question_theme_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_math = types.InlineKeyboardButton("Математика", callback_data='theme_Math')
    btn_russian = types.InlineKeyboardButton("Русский язык", callback_data='theme_Russian')
    btn_physics = types.InlineKeyboardButton("Физика", callback_data='theme_Physics')
    btn_general = types.InlineKeyboardButton("Общее", callback_data='theme_General')
    markup.add(btn_math, btn_russian, btn_physics, btn_general)
    bot.send_message(chat_id, "Выберите тему вопроса:", reply_markup=markup)


# Функция для отправки клавиатуры с уровнями сложности
def send_difficulty_level_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_easy = types.InlineKeyboardButton("Легкий", callback_data='difficulty_Easy')
    btn_medium = types.InlineKeyboardButton("Средний", callback_data='difficulty_Medium')
    btn_hard = types.InlineKeyboardButton("Сложный", callback_data='difficulty_Hard')
    markup.add(btn_easy, btn_medium, btn_hard)
    bot.send_message(chat_id, "Выберите уровень сложности:", reply_markup=markup)


# Обработка команды start
@bot.message_handler(commands=['start'])
def handle_start(message):
    send_question_theme_keyboard(message.chat.id)


# Обработка callback-ов от inline клавиатур
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data.startswith('theme_'):
        theme = call.data.split('_')[1]
        bot.answer_callback_query(call.id, f"Тема {theme} выбрана.")
        send_difficulty_level_keyboard(chat_id)
    elif call.data.startswith('difficulty_'):
        difficulty = call.data.split('_')[1]


@bot.message_handler(commands=['settheme'])
def set_theme(message):
    theme = ' '.join(message.text.split()[1:])
    if theme:
        update_user_settings(message.from_user.id, theme=theme)
        bot.reply_to(message, f"Тема установлена на '{theme}'.")
    else:
        bot.reply_to(message, "Укажите тему после команды.")

@bot.message_handler(commands=['setlevel'])
def set_level(message):
    level = ' '.join(message.text.split()[1:])
    if level:
        update_user_settings(message.from_user.id, level=level)
        bot.reply_to(message, f"Уровень сложности установлен на '{level}'.")
    else:
        bot.reply_to(message, "Укажите уровень сложности после команды.")

@bot.message_handler(commands=['debug'])
def send_log(message):
    if message.from_user.id == ADMIN_ID:
        # Проверяем, не пустой ли файл перед отправкой
        if os.path.getsize(log_filename) > 0:
            with open(log_filename, 'rb') as log:
                bot.send_document(ADMIN_ID, log)
            bot.reply_to(message, "Файл лога успешно отправлен.")
        else:
            bot.reply_to(message, "Файл лога пуст.")
    else:
        bot.reply_to(message, "У вас нет доступа к этой команде.")




@bot.message_handler(commands=['reset'])
def handle_reset(message):
    user_id = message.from_user.id
    # Проверяем, есть ли история сообщений для данного пользователя
    if user_id in user_messages_history:
        # Удаляем историю сообщений пользователя
        del user_messages_history[user_id]
        bot.reply_to(message, "Ваша история сообщений была успешно очищена.")
    else:
        bot.reply_to(message, "Ваша история сообщений уже пуста.")

def update_message_history(user_id, message, is_user_message=True):
    if user_id not in user_messages_history:
        user_messages_history[user_id] = []
    entry = {"role": "user" if is_user_message else "assistant", "content": message}
    user_messages_history[user_id].append(entry)
    user_messages_history[user_id] = user_messages_history[user_id][-MAX_HISTORY_LENGTH:]

def get_context(user_id):
    return user_messages_history.get(user_id, [])

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text
    logging.info(f"Received message from {user_id}: {text}")

    update_message_history(user_id, text, is_user_message=True)
    context_messages = get_context(user_id)
    response = generate_response(text, context_messages=context_messages)

    bot.reply_to(message, response)
    update_message_history(user_id, response, is_user_message=False)



if __name__ == '__main__':
    recreate_table()  
    bot.polling()

