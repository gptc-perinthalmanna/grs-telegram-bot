import telebot
from db import telegram_db as db
from uuid import UUID

bot = telebot.TeleBot("2090757545:AAF00DXNp4vj_lxDeugKPG0MHgeb2zJ0kDI", parse_mode=None)

def check_chat_is_connected(message: telebot.types.Message):
    try:
        result = db.get("bot_config")
    except Exception as e:
        bot.reply_to(message, "System Error: " + str(e))
        return False
    if result["connected_chats"] == message.chat.id:
        return True
    bot.reply_to(message, "This chat is not connected to any GRS 🛑")
    return False


def check_reply_message_is_post(message: telebot.types.Message) -> bool:
    err_msg = "The message you selected for add response is not a grievance. Reply with /reply command for the original grevience notification message send by this bot 🛑"
    reply_message = message.reply_to_message
    if reply_message.from_user.id != bot.get_me().id:
        bot.reply_to(message, "You didn't replied to my post 🤔")
        return False
    post_id_string_start_index = message.text.find("id: ") + 4
    if post_id_string_start_index == "-1":
        bot.reply_to(message, "")
        return False
    post_id = message.text[post_id_string_start_index:post_id_string_start_index + 36]
    if not is_valid_uuid(post_id):
        bot.reply_to(message, "Invalid post id 🤔")
        return False

    return True

def is_valid_uuid(val):
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False
