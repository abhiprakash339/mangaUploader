# from flask import Flask,request
#
# app = Flask(__name__)
#
# token = "1454336471:AAGT-Euyq-39Rbw_4hBAJE6OyPxnuIkQTLM"
#
# base_url = "https://api.telegram.org/bot" + token
#
#
# @app.route(base_url+'/getUpdates?timeout=100')
# def hello_world():
#     return request
#
#
# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5500)

# -----------------------------------------------------------------------
import os

from flask import Flask, request, send_from_directory
import telegram

TOKEN = "1454336471:AAGT-Euyq-39Rbw_4hBAJE6OyPxnuIkQTLM"
URL = "https://manga-uploader.herokuapp.com/"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

name = ""
manga_url = ""
start = 0
end = 0

def get_response(text):
    return text + text


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global name,manga_url,start,end
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    userText = update.message.text.encode('utf-8').decode()
    print("[INFO] got text message :", userText)

    if userText == "/start":
        name = ""
        manga_url = ""
        start = 0
        end = 0
        response = "Enter Manga Name"
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'
    elif name == "":
        name = userText
        response = "Enter Manga URL"
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'
    elif manga_url == "":
        manga_url = userText
        response = "Enter Starting Chapter Number"
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'
    elif start == 0:
        start = int(userText)
        response = "Enter Ending Chapter Number"
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'
    elif end == 0:
        end = int(userText)
        response = "[ INPUT ] Name :"+name+" URL :"+manga_url+" START :"+str(start)+" END :"+str(end)
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
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    return 'WELCOME TO MANGA-UPLOADER'


if __name__ == '__main__':
    app.run(threaded=True)
