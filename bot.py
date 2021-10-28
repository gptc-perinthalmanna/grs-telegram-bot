from deta import Deta

deta = Deta("c0rmafqp_DcHD6D4eq4eoBTpK9a6b6adA2yvtu4N2")
db = deta.Base("telegram_db")

db.put({"connected_chats": "test"}, "bot_config")