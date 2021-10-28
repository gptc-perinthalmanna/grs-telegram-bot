import telebot

from func import check_chat_is_connected, check_reply_message_is_post
from db import get_user_from_username, map_telegram_user_id_to_user_from_db, update_bot_config

bot = telebot.TeleBot("2090757545:AAF00DXNp4vj_lxDeugKPG0MHgeb2zJ0kDI", parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Yeah boy. I am charged up ✨")


@bot.message_handler(commands=['connect'])
def connect_group(message: telebot.types.Message):
    chat_id = message.chat.id
    try:
        update_bot_config("connected_chats", chat_id)
        bot.reply_to(message, "This chat is connected to the GRS ✅")
    except Exception as e:
        bot.reply_to(message, "An error occured while connecting the chat. Error: " + str(e))


@bot.message_handler(commands=["reply"])
def reply_post(message: telebot.types.Message):
    if not check_chat_is_connected(message):
        return
    if not check_reply_message_is_post(message):
        return


@bot.message_handler(commands=["connectme"])
def connect_me(message: telebot.types.Message):    
    if not check_chat_is_connected(message):
        return
    username = message.text.replace("/connectme ", "")
    user = get_user_from_username(username)
    if user is None:
        bot.reply_to(message, "User not found")
        return
    map_telegram_user_id_to_user_from_db(message.from_user.id, user.key)
    bot.reply_to(message, "Your account is connected to account of " + user.first_name + " " + user.last_name + " ✅")


@bot.message_handler(func=lambda m: True)
def reply_all_messages(message):
    bot.reply_to(message, "New message is nice " + message.text)


bot.infinity_polling()


