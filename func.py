import json
import telebot
from main import bot, db
from uuid import UUID

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

draft_js_template = {
    "blocks" : [{
        "key": "110h8",
        "text": "",
        "type": "unstyled",
        "depth": 0,
        "inlineStyleRanges": [],
        "entityRanges": [],
        "data": {}
    }],
    "entityMap": {}
}

def convert_text_to_draft_js_raw(text: str) -> str:
    draft_js_raw = draft_js_template
    draft_js_raw["blocks"][0]["text"] = text
    return json.dumps(draft_js_raw)

