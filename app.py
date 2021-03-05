# ----------------------------------------------------------- #
#                         Python 3.9                          #
#        Telegram Bot to upload manga in pdf format           #
#                        Flask Program                        #
# ----------------------------------------------------------- #

import os
import telegram

from configparser import ConfigParser
from flask import Flask, request, send_from_directory

config = ConfigParser()
config.read('bot.ini')

TOKEN = config['BOT']['TOKEN']
URL = config['SERVER']['URL']

bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

# name = None
# manga_url = None
# start = None
# end = None
data = {
    "name": None,
    "manga_url": None,
    "start": None,
    "end": None
}


def get_response(text):
    return text + text


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global data
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    userText = update.message.text.encode('utf-8').decode()
    print("[INFO] got text message :", userText)

    if userText == "/start":
        data["name"] = data["manga_url"] = data["start"] = data["end"] = None
        response = "Enter Manga Name"
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'
    elif data["name"] is None:
        data["name"] = userText
        response = "Enter Manga URL"+str(data)
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'
    elif data["manga_url"] is None:
        data["manga_url"] = userText
        response = "Enter Starting Chapter Number"+str(data)
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'
    elif data["start"] is None:
        data["start"] = int(userText)
        response = "Enter Ending Chapter Number"+str(data)
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'
    elif data["end"] is None:
        data["end"] = int(userText)
        response = "[ INPUT ] "+str(data)
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "WEBHOOK SETUP SUCCESSFUL"
    else:
        return "WEBHOOK SETUP FAILED"


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    return 'WELCOME TO MANGA-UPLOADER'


if __name__ == '__main__':
    app.run(threaded=True)
