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
from pymongo import MongoClient

config = ConfigParser()
config.read('bot.ini')

TOKEN = config['BOT']['TOKEN']
URL = config['SERVER']['URL']
bot = telegram.Bot(token=TOKEN)
config = ConfigParser()
config.read("bot.ini")
print(config["API"]["MONGO-DB"])

client = MongoClient(config["API"]["MONGO-DB"])
db = client.get_database("Telegram_Bot")
#
# user_db = db.list_collection_names()
# print(user_db)
USERS = db.get_collection('users_inputs')

app = Flask(__name__)
api = Api(app)

manga_name = ""
manga_main_url = ""
manga_start = ""
manga_end = ""

stop_connect = False

uni_message = ""


def link_test(url):
    status = requests.get(url, stream=True).status_code
    if status == 200:
        return True
    else:
        return False


def download_chapter(chapter_url, chat_id, ch):
    global manga_name
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
    pdf_filename = str(bin_path + manga_name + " Chapter " + str(ch) + ".pdf")
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


def connect(manga_name, manga_url, manga_start, manga_end, chatID):
    global stop_connect

    main_url = "/".join(manga_main_url.split("/")[0:-1])
    start = float(manga_start)
    end = float(manga_end)
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
            print("[ INFO ] ", chapter, ": STARTED")
            download_chapter(str(main_url + "/" + chapter), chatID, chapter)
            print("[ INFO ] ", chapter, ": COMPLETED")
        elif stop:
            bot.sendMessage(chat_id=chatID, text=(manga_name + " Chapter " + chapter + " Not Found"))
            return
        else:
            print("[ INFO ] ", chapter, ": NOT-AVAILABLE")
        temp = round(temp, 10) + round(0.1, 10)
        gc.collect()
    bot.sendMessage(chat_id=chatID, text="Completed")
    gc.collect()
    return


class RespondToBot(Resource):
    def post(self):
        global uni_message
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        user = update.message.from_user.name
        update_id = update.update_id + 1
        print("[ BOT ] Update ID :", update_id)
        chat_id = update.message.chat.id
        msg_id = update.message.message_id

        # Telegram understands UTF-8, so encode text for unicode compatibility
        userText = update.message.text.encode('utf-8').decode()
        print("[INFO] got text message :", userText)
        usr_data = USERS.find_one({"user": user})
        usr_state = int(usr_data["Active"])

        if userText == "/start":
            usr_data["Active"] = "1"
            usr_data["manga-name"] = ""
            usr_data["manga-url"] = ""
            usr_data["manga-start"] = ""
            usr_data["manga-end"] = ""
            response = "Enter Manga Name"
            USERS.update_one({"user": user}, {"$set": usr_data})
            print("[ BOT ] ", bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id))
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
            return "OK"
        elif usr_state > 0:
            if usr_state == 1:
                usr_data["manga-name"] = userText
                usr_data["Active"] = "2"
                response = "Enter Manga URL"
            elif usr_state == 2:
                usr_data["manga-url"] = userText
                usr_data["Active"] = "3"
                response = "Enter Starting chapter"
            elif usr_state == 3:
                usr_data["manga-start"] = userText
                usr_data["Active"] = "4"
                response = "Enter Ending Chapter Name"
            elif usr_state == 4:
                usr_data["manga-end"] = userText
                usr_data["Active"] = "0"
                response = str(
                    "NAME  : " + usr_data["manga-name"] +
                    "URL   : " + usr_data["manga-url"] +
                    "START : " + usr_data["manga-start"] +
                    "END   : " + usr_data["manga-end"])
                thd = threading.Thread(name="connect_thread", target=connect, args=(usr_data["manga-name"],usr_data["manga-url"],usr_data["manga-start"],usr_data["manga-end"],chat_id,))
                thd.start()
            bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
            USERS.update_one({"user": user}, {"$set": usr_data})
            return 'OK'
        else:
            response = "Restart the Bot by Sending '/start' command"
            bot.sendMessage(chat_id=chat_id, text=response)
            return 'OK'


class SetWebhook(Resource):
    def get(self):
        s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
        if s:
            return "WEBHOOK SETUP SUCCESSFUL"
        else:
            return "WEBHOOK SETUP FAILED"


class Favicon(Resource):
    def get(self):
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                                   mimetype='image/vnd.microsoft.icon')


class Index(Resource):
    def get(self):
        return 'WELCOME TO MANGA-UPLOADER'


api.add_resource(RespondToBot, '/{}'.format(TOKEN), methods=['POST'])
api.add_resource(Index, "/")
api.add_resource(Favicon, '/favicon.ico')
api.add_resource(SetWebhook, '/setwebhook')
if __name__ == '__main__':
    app.run(threaded=True)
