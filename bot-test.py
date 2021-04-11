import gc
import json
import os
import shutil
import threading
import telegram
import requests

from PIL import Image
from selenium import webdriver
from pymongo import MongoClient
from PyPDF2 import PdfFileMerger
from configparser import ConfigParser
from requests.adapters import HTTPAdapter
# from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from flask import Flask, request, send_from_directory
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

config = ConfigParser()
config.read('bot.ini')

TOKEN = config['BOT']['TOKEN']
URL = config['SERVER']['URL']
bot = telegram.Bot(token=TOKEN)

client = MongoClient(config["API"]["MONGO-DB"])
db = client.get_database("Telegram_Bot")
USERS = db.get_collection('users_inputs')
MANGA_COLLECTION = db.get_collection('manga_url_data')


class MangaCrowler():
    def __init__(self, name, start, end, chat_id):
        # fireFoxOptions = webdriver.FirefoxOptions()
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.set_headless()
        # self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=fireFoxOptions)
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chromeOptions)
        temp = [str(i).capitalize() for i in str(name).split()]
        self.manga_name = "-".join(temp)
        self.manga_start = start
        self.manga_end = end
        self.chat_id = chat_id
        self.session = requests.Session()

    def start_crowling(self):
        self.manga_crowler(self.manga_name, self.manga_start, self.manga_end, self.chat_id)

    def manga_crowler(self, name, start, end, chat_id):
        bin_path = f'./bin/{chat_id}/'
        if not os.path.isdir(bin_path):
            os.makedirs(bin_path)
        else:
            shutil.rmtree(bin_path)
            os.makedirs(bin_path)
        temp = float(start)
        end = float(end)

        temp2 = f"{bin_path}/temp2.pdf"
        temp3 = f"{bin_path}/temp3.pdf"
        msg = bot.sendMessage(chat_id=chat_id, text=f"{name}\n--------------------------")
        while temp <= end:
            ch = round(temp, 1)
            if ch.is_integer():
                chapter = str(int(ch))
                stop = True
            else:
                chapter = str(ch)
                stop = False
            print("[ INFO ] :", chapter)
            bot.edit_message_text(chat_id=chat_id,
                                  text=f"{name}\n--------------------------\nChapter :{str(chapter).zfill(3)}",
                                  message_id=msg.message_id)
            pdf_filename = str(bin_path + name + " Chapter " + str(chapter).zfill(3) + ".pdf")
            url = self.get_original_url(name, chapter, 1)
            temp = round(temp, 10) + round(0.1, 10)
            print("[ INFO ] Original URL :", url)
            if url is None and stop:
                break
            elif url is None and not stop:
                continue
            main_url = url[:-7]
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                "Accept-Encoding": "*",
                "Connection": "keep-alive"
            }
            page = 1
            while True:
                bot.edit_message_text(chat_id=chat_id,
                                      text=f"{name}\n=====Downloading=====\nChapter :{str(chapter).zfill(3)}\nPAGE : {page}",
                                      message_id=msg.message_id)
                merger = PdfFileMerger()
                url = f'{main_url}{str(page).zfill(3)}.png'
                self.session.mount(url, HTTPAdapter(max_retries=5))
                # code = requests.get(url, headers=headers, stream=True)
                img_data = self.session.get(url, headers=headers, stream=True)
                if img_data.status_code == 200:
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
                print(url)
                page += 1
                gc.collect()

            with open(pdf_filename, 'rb') as file:
                bot.edit_message_text(chat_id=chat_id,
                                      text=f"{name}\n=====Uploading=====\n\nChapter :{str(chapter).zfill(3)}",
                                      message_id=msg.message_id)
                print("[ BOT ] ", bot.sendDocument(document=file, chat_id=chat_id, ))

                bot.edit_message_text(chat_id=chat_id, text="Uploading PDF Completed", message_id=msg.message_id)

            print("[ INFO ] ", pdf_filename, " Uploaded")
            os.remove(pdf_filename)
            bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            gc.collect()
        shutil.rmtree(bin_path)
        self.driver.close()
        return

    def get_original_url(self, name, chapter, page):
        url = f'https://manga4life.com/read-online/{name}-chapter-{str(chapter)}-page-{str(page)}.html'
        print(url)
        try:
            self.driver.get(url)
            if "404 Page Not Found" == self.driver.title:
                return None
            w = WebDriverWait(self.driver, 8)
            w.until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="TopPage"]/div[{page + 1}]/div/img')))
            return self.driver.find_element(By.XPATH, f'//*[@id="TopPage"]/div[{page + 1}]/div/img').get_attribute(
                "ng-src")
        except:
            return None


class RespondToBot(Resource):
    def post(self):
        global stop_connect
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
            stop_connect = True
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
        elif "/help" in userText:
            msg = '/start : it will start the pdf upload\n/add {"manga-name":"One-Piece",' \
                  '"manga-url":"https://temp.compsci88.com/manga/One-Piece/1007-001.png","manga-chapter":"1007"} '
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id,
                            disable_web_page_preview=True)
            return 'OK'
        elif "/add" in userText:
            k = userText[5:]
            try:
                d = dict(json.loads(k))
                print("[ INFO ] ", d)
                MANGA_COLLECTION.insert_one(d)
                bot.sendMessage(chat_id=chat_id, text="Added", reply_to_message_id=msg_id,
                                disable_web_page_preview=True)
            except Exception as excp:
                print("[ INFO ] ", excp.args)
                bot.sendMessage(chat_id=chat_id, text=str(excp.args), reply_to_message_id=msg_id,
                                disable_web_page_preview=True)

            gc.collect()
            return "OK"
        elif "/ongoing" in userText:
            temp = ""
            for i in MANGA_COLLECTION.find():
                temp += str(i["manga-name"] + " : " + i['manga-url'] + "\n")
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
                response = "Enter Starting chapter"
            elif usr_state == 2:
                usr_data["manga-start"] = userText
                usr_data["Active"] = "3"
                response = "Enter Ending Chapter Name"
            elif usr_state == 3:
                usr_data["manga-end"] = userText
                usr_data["Active"] = "0"
                response = str(
                    "NAME  : " + usr_data["manga-name"] +
                    "\nSTART : " + usr_data["manga-start"] +
                    "\nEND   : " + usr_data["manga-end"])
                stop_connect = False
                obj = MangaCrowler(usr_data["manga-name"], usr_data["manga-start"], usr_data["manga-end"], chat_id)
                manga = threading.Thread(name="MANGA", target=obj.start_crowling())
                manga.start()
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
