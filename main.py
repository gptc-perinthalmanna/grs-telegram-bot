import telebot, db, time, api, func
from decouple import config

bot = telebot.TeleBot(config("TG_BOT_TOKEN"), parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "Yeah boy. I am charged up ✨")
        return

    user_key, = db.get_user_from_telegram_user_id(message.from_user.id)
    if user_key is None:
        bot.reply_to(message, "This bot is not intended to use in private chats ✨")
        return
    user = api.get_user_from_id(user_key)
    if user is None:
        bot.reply_to(message, "Your account is not found in GRS 🛑")

    bot.send_message(
        message.chat.id, f"Hello {user['first_name']} {user['last_name']}! Send your account password of GRS 🔒 after typing /password .\n")


@bot.message_handler(commands=['password'])
def check_password(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "This command only supported in Private chats 🛑")
        return

    userid = func.get_user_from_message(message)
    if userid is None: 
        bot.reply_to(message, "User Not found!")
        return

    password = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None
    if password is None:
        bot.reply_to(message, "Please send your password 🔒. Enter your password after /password command. You just sent a blank /password command.")
        return

    msg = bot.reply_to(message, "Checking password...")
    user = api.get_user_from_user_id(userid)
    time.sleep(5)
    if api.get_other_user_token(user['username'], password):
        db.put_user_from_telegram_user_id(message.from_user.id, userid, disabled=False)
        bot.edit_message_text("Password is correct! ✅ Your account is Logged in ✨", message.chat.id, msg.message_id)
        return

    bot.edit_message_text("Waiting...", message.chat.id, msg.message_id)
    time.sleep(5)
    bot.edit_message_text("Password is incorrect! ❌", message.chat.id, msg.message_id)


@bot.message_handler(commands=['connect'])
def connect_group(message: telebot.types.Message):
    if func.check_chat_is_connected(message, False):
        return

    if message.chat.type == 'private':
        bot.reply_to(message, "This command only supported in Group chats 🛑")
        return
    
    user_key = func.get_user_from_message(message)
    if user_key is None:
        bot.reply_to(message, "Your account is not found in GRS 🛑")
        return
    
    user = api.get_user_from_user_id(user_key)
    if user is None:
        bot.reply_to(message, "Your account is not found in GRS 🛑")
        return
    
    if user["type"] not in ["admin", "staff"]:
        bot.reply_to(message, "Only admins can use this command 🛑")
        return

    try:
        func.connect_this_chat(message)
        return
    except Exception as e:
        bot.reply_to(message, "An error occured while connecting the chat. Error: " + str(e))


@bot.message_handler(commands=["reply"])
def reply_post(message: telebot.types.Message):
    if not func.check_chat_is_connected(message):
        return

    user = func.check_user_permissions_and_return_user(message)
    if user is None:
        return

    post_id = func.get_post_id_if_reply_message_is_post(message)
    if post_id is None:
        return

    response = func.create_response_object_for_post(post_id, message, user)
    if response is None:
        return
    if api.add_new_response_to_post(response):
        bot.reply_to(message, "Added response successfully ✅")
    else:
        bot.reply_to(message, "An error occured while adding response. Please try again 🛑")


@bot.message_handler(commands=["login"])
def connect_me(message: telebot.types.Message):
    if message.chat.type != 'private':
        if not func.check_chat_is_connected(message):
            return

    username = message.text.replace("/login ", "")

    user_id, is_disabled = db.get_user_from_telegram_user_id(message.from_user.id)
    if user_id and not is_disabled:
        bot.reply_to(message, "Your account is already connected ✅")
        return
        
    user = api.get_user_from_username(username)
    if user is None:
        bot.reply_to(message, "User not found")
        return
    db.put_user_from_telegram_user_id(message.from_user.id, user["key"])
    bot.reply_to(
        message, f"Found your account on GRS ✅ \n Click the @{bot.get_me().username} and Press Start \n Follow instructions to Login")


@bot.message_handler(commands=["help"])
def bot_commands_help(message: telebot.types.Message):
    if not func.check_chat_is_connected(message):
        return
    bot.reply_to(message, "Commands: \n /connect - Connect this chat to the GRS \n /reply - Reply to a post \n /login - Connect your account to the GRS") 


@bot.message_handler(func=lambda m: True)
def reply_all_messages(message):
    bot.reply_to(message, "☺️ I know")


bot.infinity_polling()
