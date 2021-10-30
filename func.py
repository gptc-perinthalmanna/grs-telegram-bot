import telebot
from typing import Optional
from decouple import config
from uuid import UUID
from passlib.context import CryptContext

from api import NewResponse, Status
import api
from db import convert_text_to_draft_js_raw, get_user_from_telegram_user_id, telegram_db as db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bot = telebot.TeleBot(config("TG_BOT_TOKEN"), parse_mode=None)

user_types_allowed_to_reply = ["admin", "greivance_cell_member", "staff"]


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


def get_post_id_if_reply_message_is_post(message: telebot.types.Message) -> bool:
    err_msg = "The message you selected for add response is not a grievance. Reply with /reply command for the original greviance notification message send by this bot 🛑"
    reply_message = message.reply_to_message
    if reply_message is None:
        bot.reply_to(message, "There is no messsage selected for reply")
        return False
    if reply_message.from_user.id != bot.get_me().id:
        bot.reply_to(message, "You didn't replied to my post 🤔")
        return False
    post_id_string_start_index = message.text.find("id: ") + 5
    if post_id_string_start_index == "-1":
        bot.reply_to(message, err_msg)
        return False
    post_id = reply_message.text[post_id_string_start_index:post_id_string_start_index + 36]
    if not is_valid_uuid(post_id):
        bot.reply_to(reply_message, "Invalid post id 🤔")
        return False
    return post_id


def is_valid_uuid(val):
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False


def create_response_object_for_post(post_id:str, message: telebot.types.Message, user: dict):
    new_status = "replied"
    allowed_statuses = [el.value for el in Status]
    # Fetch change status command from message
    status_command_index = message.text.find("/changestatus")
    if status_command_index != -1:
        status_command = message.text[status_command_index + len("/changestatus"):]
        if status_command.startswith(" "): status_command = status_command[1:]
        for status in allowed_statuses:
            if status_command.startswith(status):
                new_status = status
                break
        else:
            bot.reply_to(message, "Invalid status change command. Allowed status changes are: " + str(allowed_statuses))
            return None
    content = convert_text_to_draft_js_raw(message.text.replace("/reply ", "").replace(f"/changestatus {new_status}", ""))
    return NewResponse(post_key=post_id, content=content, status=new_status, user_id=user["key"])


def verify_password(user: dict, password: str):
    return pwd_context.verify(password, user["hashed_password"])


def check_user_permissions_and_return_user(message: telebot.types.Message) -> dict:
    user_key, is_user_disabled = get_user_from_telegram_user_id(message.from_user.id)
    if user_key is None or is_user_disabled is True:
        bot.reply_to( message, "Your account is not connected with GRS. Send your username after typing /login command")
        return None

    user = api.get_user_from_user_id(user_key)
    if user is None:
        bot.reply_to(message, "Your account is not found in GRS 🛑")
        return None

    if user["type"] not in user_types_allowed_to_reply:
        bot.reply_to(message, "You are not allowed to reply to this post 🛑")
        return None
    return user


def get_user_from_message(message: telebot.types.Message) -> Optional[dict]:
    user_key, is_disabled = db.get_user_from_telegram_user_id(message.from_user.id)
    if user_key is None:
        bot.reply_to(
            message, "Your account is not connected with GRS. Send your username after typing /login command")
        return None
    
    user = api.get_user_from_user_id(user_key)
    if user is None:
        bot.reply_to(message, "Your account is not found in GRS 🛑")
        return None
    return user