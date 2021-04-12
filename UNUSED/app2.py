# ----------------------------------------------------------- #
#                         Python 3.9                          #
#        Telegram Bot to upload manga in pdf format           #
#                        Flask Program                        #
# ----------------------------------------------------------- #
import json
import os
import gc
import sys
import shutil
import requests
import telegram
import threading

from PIL import Image
from PyPDF2 import PdfFileMerger
from configparser import ConfigParser
from flask import Flask, request, send_from_directory
from flask_restful import Api, Resource

config = ConfigParser()
config.read('bot.ini')

TOKEN = config['BOT']['TOKEN']
URL = config['SERVER']['URL']
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

# manga_name = ""
# manga_main_url = ""
# manga_start = ""
# manga_end = ""

stop_connect = False


def link_test(url):
    status = requests.get(url, stream=True).status_code
    if status == 200:
        return True
    else:
        return False


def download_chapter(name, chapter_url, chat_id, ch):
    bin_path = "./bin/"
    if not os.path.isdir(bin_path):
        os.mkdir(bin_path)
    else:
        shutil.rmtree(bin_path)
        os.mkdir(bin_path)
    if int(ch[0]) == 0:
        ch = ch[1:]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }

    page = 1
    session = requests.Session()
    msg = bot.sendMessage(chat_id=chat_id, text="\nDownloading PAGE :000")
    pdf_filename = str(bin_path + name + " Chapter " + str(ch) + ".pdf")
    temp2 = "./bin/temp2.pdf"
    temp3 = "./bin/temp3.pdf"
    while True:
        merger = PdfFileMerger()
        temp_url = str(chapter_url + "-" + str(page).zfill(3) + ".png")
        print("[ INFO ] ", temp_url)
        try:
            img_data = session.get(temp_url, headers=headers, stream=True)
            if img_data.status_code == 200:
                bot.edit_message_text(chat_id=chat_id, text="\nDownloading PAGE :" + str(page).zfill(3),
                                      message_id=msg.message_id)
                image = Image.open(img_data.raw)
                image.load()
                image.split()
                if page == 1:
                    image.save(pdf_filename, "PDF", resolution=100.0, save_all=True)
                else:
                    image.save(temp2, "PDF", resolution=100.0, save_all=True)
                    merger.append(pdf_filename)
                    merger.append(temp2)
                    merger.write(temp3)
                    merger.close()
                    os.remove(pdf_filename)
                    os.rename(temp3, pdf_filename)
                    os.remove(temp2)
            else:
                break
        except Exception as excp:
            print("[ INFO ] ", excp)
            bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            bot.sendMessage(chat_id=chat_id, text="[ ERROR ] :" + str(excp))
            return
        page += 1
        gc.collect()

    with open(pdf_filename, 'rb') as file:
        bot.edit_message_text(chat_id=chat_id, text="Uploading PDF...", message_id=msg.message_id)
        print("[ BOT ] ", bot.sendDocument(document=file, chat_id=chat_id, ))

        bot.edit_message_text(chat_id=chat_id, text="Uploading PDF Completed", message_id=msg.message_id)

    print("[ INFO ] ", pdf_filename, " Uploaded")
    bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    shutil.rmtree(bin_path)
    gc.collect()
    return


def connect(name, manga_url, start, end, chatID):
    global stop_connect

    main_url = "/".join(manga_url.split("/")[0:-1])
    start = float(start)
    end = float(end)
    temp = float(start)

    while temp <= end:
        if stop_connect:
            sys.exit()
        ch = round(temp, 1)
        if ch.is_integer():
            chapter = str(int(ch)).zfill(4)
            stop = True
        else:
            chapter = str(ch).zfill(6)
            stop = False
        if link_test(main_url + "/" + chapter + "-001.png"):
            print("[ INFO ] ", name, " ", chapter, ": STARTED")
            download_chapter(name, str(main_url + "/" + chapter), chatID, chapter)
            print("[ INFO ] ", name, " ", chapter, ": COMPLETED")
        elif stop:
            bot.sendMessage(chat_id=chatID, text=(name + " Chapter " + chapter + " Not Found"))
            return
        else:
            print("[ INFO ] ", name, " ", chapter, ": NOT-AVAILABLE")
        temp = round(temp, 10) + round(0.1, 10)
        gc.collect()
    bot.sendMessage(chat_id=chatID, text="Completed")
    gc.collect()
    return


def get_bot_inputs(chat_id, msg, update_id):
    bot.sendMessage(chat_id=chat_id, text=msg)
    input_update = bot.getUpdates(offset=update_id, timeout=200)
    if not input_update:
        bot.sendMessage(text="timeout Send '/start' agian")
        return None, None
    input_message = input_update.pop().message
    input_txt = input_message.text
    input_id = input_message.message_id
    return input_txt, input_id


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global stop_connect
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    user = update.message.from_user.name
    update_id = update.update_id
    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    userText = update.message.text.encode('utf-8').decode()
    print("[INFO] got text message :", userText)

    if userText == "/start":
        bot.deleteWebhook()
        # if dict(data).get(user, None) is None:
        #     bot.sendMessage(chat_id=chat_id, text="You Are Not Allowed", reply_to_message_id=msg_id)
        #     return "OK"
        # ------------------ <name> --------------------- #
        update_id += 1
        name, name_id = get_bot_inputs(chat_id, "Enter Manga Name", update_id)
        if '/start' in name:
            bot.sendMessage(chat_id=chat_id,text="send '/start again")
            bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
            return 'OK'
        # ------------------ </name> -------------------- #
        # ------------------ <manga-url> --------------------- #
        update_id += 1
        manga_url, manga_url_id = get_bot_inputs(chat_id, "Enter Manga URL", update_id)
        if '/start' in manga_url:
            bot.sendMessage(chat_id=chat_id,text="send '/start again")
            bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
            return 'OK'
        # ------------------ </mang-url> -------------------- #
        # ------------------ <start> --------------------- #
        update_id += 1
        start, start_id = get_bot_inputs(chat_id, "Enter Starting Chapter", update_id)
        if '/start' in start:
            bot.sendMessage(chat_id=chat_id,text="send '/start again")
            bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
            return 'OK'
        # ------------------ </start> -------------------- #
        # ------------------ <end> --------------------- #
        update_id += 1
        end, end_id = get_bot_inputs(chat_id, "Enter Ending Chapter", update_id)
        if '/start' in end:
            bot.sendMessage(chat_id=chat_id,text="send '/start again")
            bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
            return 'OK'
        # ------------------ </end> -------------------- #
        print("[ BOT ] ", name, " : ", manga_url, " : ", start, " : ", end)
        if name == manga_url == start == end is None:
            bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
            return 'OK'

        thd = threading.Thread(name="connect_thread", target=connect, args=(name, manga_url, start, end, chat_id,))
        thd.start()

        bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
        gc.collect()
        return 'OK'
    elif "/add" in userText:
        k = userText[5:]
        d = dict(json.loads(k))
        print("[ INFO ] ", d)
        with open("manga_data.json", "r") as read_json:
            m = dict(json.load(read_json))
            key = list(d.keys())[0]
            m[key] = d[key]
        print(json.dumps(m))
        with open("manga_data.json", "w") as write_json:
            write_json.write(json.dumps(m))
        bot.sendMessage(chat_id=chat_id, text="Added", reply_to_message_id=msg_id, disable_web_page_preview=True)
        gc.collect()
        return "OK"
    elif "/ongoing" in userText:
        with open("manga_data.json", "r") as read_json:
            m = dict(json.load(read_json))
            temp = ""
            for i in m:
                temp += i + " : " + m[i] + "\n"
            bot.sendMessage(chat_id=chat_id, text=temp, reply_to_message_id=msg_id, disable_web_page_preview=True)
        gc.collect()
        return "OK"

    elif "/select" in userText:
        k = userText.split()[1]
        return 'OK'
    else:
        response = "Restart the Bot by Sending '/start' command"
        bot.sendMessage(chat_id=chat_id, text=response)
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


@app.route("/test")
def test():
    bot.deleteWebhook()

    up = bot.getUpdates(offset=None, timeout=200)
    print(up.pop().message.text)
    # bot.sendMessage(text=)
    bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    print(bot.getWebhookInfo())
    return "OK"


@app.route('/')
def index():
    return 'WELCOME TO MANGA-UPLOADER'


if __name__ == '__main__':
    app.run(threaded=True)
