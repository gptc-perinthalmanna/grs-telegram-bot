from pydantic.types import UUID4
import telebot
from typing import Optional
from decouple import config
from uuid import UUID

import api
from api import NewResponse, Status
from db import convert_text_to_draft_js_raw, get_user_from_telegram_user_id, get_bot_config, set_bot_config, telegram_db as db

bot = telebot.TeleBot(config("TG_BOT_TOKEN"), parse_mode=None)

user_types_allowed_to_reply = ["admin", "greivance_cell_member", "staff"]


def check_chat_is_connected(message: telebot.types.Message, mute:bool = True) -> bool:
    try:
        result = get_bot_config()
    except Exception as e:
        bot.reply_to(message, "System Error: " + str(e))
        return False
        
    if result and result["connected_chats"] and message.chat.id in result["connected_chats"]:
        if not mute:
            bot.reply_to(message, "This chat is already connected to GRS 🤗")
        return True

    bot.reply_to(message, "This chat is not connected to any GRS 🛑")
    return False


def connect_this_chat(message: telebot.types.Message):
    try:
        result = get_bot_config()
    except Exception as e:
        bot.reply_to(message, "System Error: " + str(e))
        return False
    if result["connected_chats"] and message.chat.id in result["connected_chats"]:
        bot.reply_to(message, "This chat is already connected to GRS 🤗")
        return False
    result["connected_chats"].append(message.chat.id)
    set_bot_config(result)
    bot.reply_to(message, "This chat is now connected to GRS 🤗")
    return True


def get_post_id_if_reply_message_is_post(message: telebot.types.Message):
    err_msg = "The message you selected for add response is not a grievance. Reply with /reply command for the original greviance notification message send by this bot 🛑"
    reply_message = message.reply_to_message
    if reply_message is None:
        bot.reply_to(message, "There is no messsage selected for reply")
        return False
    if reply_message.from_user.id != bot.get_me().id:
        bot.reply_to(message, "You didn't replied to my post 🤔")
        return False
    post_id_string_start_index = message.text.find("id: ")
    if post_id_string_start_index == "-1":
        bot.reply_to(message, err_msg)
        return False
    post_id = reply_message.text[post_id_string_start_index+5:post_id_string_start_index + 5 + 36]
    if not is_valid_uuid(post_id):
        bot.reply_to(reply_message, "Invalid post id 🤔")
        return False
    if not api.is_post_id_exists(post_id):
        bot.reply_to(reply_message, "This post is not found in GRS 🛑")
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
    status_command_index = message.text.find("/status")
    if status_command_index != -1:
        status_command = message.text[status_command_index + len("/status"):]
        if status_command.startswith(" "): status_command = status_command[1:]
        for status in allowed_statuses:
            if status_command.startswith(status):
                new_status = status
                break
        else:
            bot.reply_to(message, "Invalid status change command. Allowed status changes are: ".join(allowed_statuses))
            return None
    content = convert_text_to_draft_js_raw(message.text.replace("/reply ", "").replace(f"/status {new_status}", ""))
    return NewResponse(post_key=UUID4(post_id), content=content, status=new_status, user_id=user["key"])



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
    user_key, is_disabled = get_user_from_telegram_user_id(message.from_user.id)
    if user_key is None:
        bot.reply_to(
            message, "Your account is not connected with GRS. Send your username after typing /login command")
        return None
    return user_key