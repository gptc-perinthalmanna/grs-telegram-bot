from deta import Deta
import os

deta = Deta(os.environ['DETA_TOKEN'])
db = deta.Base("telegram_db")

db.put({"connected_chats": "test"}, "bot_config")