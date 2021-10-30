import json
from decouple import config
from typing import Optional, Tuple
from uuid import UUID
from deta import Deta


deta = Deta(config("DETA_TOKEN"))
telegram_db = deta.Base("telegram_db")
telegram_user_map_db = deta.Base("telegram_user_map_db")


# BOT CONFIGURATION

def get_bot_config():
    return telegram_db.get("bot_config")


def set_bot_config(config):
    telegram_db.put(config, "bot_config")


def update_bot_config(key, value):
    config = get_bot_config()
    if config is None:
        config = {}
    if isinstance(value, list):
        config[key].append(value)
    elif isinstance(value, dict):
        config[key].update(value)
    else:
        config[key] = value
    telegram_db.put(config, "bot_config")


# USERNAME AND TELEGRAM USERID MAP


def get_user_from_telegram_user_id(telegram_user_id) -> Optional[Tuple[str, bool]]:
    res = telegram_user_map_db.get(str(telegram_user_id))
    if res is None:
        return None, None
    return res['user_id'], res['disabled']


def put_user_from_telegram_user_id(telegram_user_id, user_id, disabled=True):
    telegram_user_map_db.put(
        {"user_id": user_id, "disabled": disabled}, str(telegram_user_id))

# DRAFT JS


draft_js_template = {
    "blocks": [{
        "key": "110h8",
        "text": "",
        "type": "unstyled",
        "depth": 0,
        "inlineStyleRanges": [],
        "entityRanges": [],
        "data": {}
    },
        {
        "key": "8icme",
        "text": "This message is sent from 🤖 Telegram bot",
        "type": "blockquote",
        "depth": 0,
        "inlineStyleRanges": [
            {
                "offset": 0,
                "length": 40,
                "style": "fontsize-12"
            },
            {
                "offset": 0,
                "length": 40,
                "style": "CODE"
            }
        ],
        "entityRanges": [],
        "data": {}
    }],
    "entityMap": {}
}


def convert_text_to_draft_js_raw(text: str) -> str:
    draft_js_raw = draft_js_template
    draft_js_raw["blocks"][0]["text"] = text
    return json.dumps(draft_js_raw)
