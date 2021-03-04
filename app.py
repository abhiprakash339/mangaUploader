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


from flask import Flask, request
import telegram

# from telebot.credentials import bot_token, bot_user_name, URL
# from telebot.mastermind import get_response

TOKEN = "1454336471:AAGT-Euyq-39Rbw_4hBAJE6OyPxnuIkQTLM"
URL = "http://localhost:5500/"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)


def get_response(text):
    return text + text


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)

    response = get_response(text)
    bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)

    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return '.'


if __name__ == '__main__':
    app.run(threaded=True)
