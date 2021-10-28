from typing import List
from uuid import UUID
from deta import Deta
import datetime
from func import convert_text_to_draft_js_raw

deta = Deta("c0rmafqp_DcHD6D4eq4eoBTpK9a6b6adA2yvtu4N2")
telegram_db = deta.Base("telegram_db")
users_db = deta.Base('users')
posts_db = deta.Base("posts")


def get_bot_config():
    return telegram_db.get("bot_config")


def set_bot_config(config):
    telegram_db.put(config, "bot_config")


def update_bot_config(key, value):
    config = get_bot_config()
    if isinstance(value, list):
        config[key].append(value)
    elif isinstance(value, dict):
        config[key].update(value)
    else:
        config[key] = value
    telegram_db.put(config, "bot_config")


def get_user_from_username(username):
    fetch = users_db.fetch({'username': username}, limit=1)
    if fetch.count > 0:
        return fetch.items[0]
    else:
        return None


def map_telegram_user_id_to_user_from_db(telegram_user_id, key):
    user_id_list = telegram_db.get("mapped_users")
    if user_id_list is None:
        user_id_list = {}
    user_id_list["telegram_user_id"] = key
    telegram_db.put(user_id_list, "mapped_users")


def get_user_from_telegram_user_id(telegram_user_id):
    user_id_list = telegram_db.get("mapped_users")
    if user_id_list is None:
        return None
    if telegram_user_id in user_id_list:
        return user_id_list[telegram_user_id]
    return None


statuses = ['draft', 'open', 'replied', 'authorResponded', 'adminResponded',
            'closed', 'deleted', 'hidden', 'priorityChanged', 'solved']


def put_new_response_for_post(post_id, response_text: str, telegram_user_id: int):
    post = posts_db.get(post_id)
    if post is None:
        raise Exception("Post not found")

    user_id = get_user_from_telegram_user_id(telegram_user_id)
    if user_id is None:
        raise Exception("User not found")

    new_status = "replied"
    status = response_text[response_text.find("/changestatus ") + len(
        "/changestatus "): response_text.find("\n", response_text.find("/changestatus "))]
    if status in statuses:
        new_status = status

    response = create_response_object(
        user_id, response_text, len(post['responses']), post['status'], new_status)

    if not 'responses' in post:
        post['responses'] = []
    post['responses'].append(response)
    posts_db.put(post, post_id)
    return True


def create_response_object(user_id, text, response_index, prev_status,  current_status="replied"):
    return {
        'author': UUID(str(user_id)).hex,
        'content': convert_text_to_draft_js_raw(text),
        "deleted": False,
        "id": response_index,
        "modified": datetime.datetime.now().isoformat(),
        "published": datetime.datetime.now().isoformat(),
        "statusChange": {
            "prev": prev_status,
            "to": current_status
        },
        "visible": True
    }
