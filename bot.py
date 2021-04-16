import gc
import json
import os
import shutil
import threading

import psutil
import telegram
import requests

# from functools import cache
from PIL import Image

from pymongo import MongoClient
from PyPDF2 import PdfFileMerger
from configparser import ConfigParser
from requests.adapters import HTTPAdapter
# from webdriver_manager.firefox import GeckoDriverManager

from selenium import webdriver
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

UpDateId = None
chromeOptions = webdriver.ChromeOptions()
chromeOptions.set_headless()


# @cache
class MangaCrowler():
    def __init__(self, name, start, end, chat_id):
        # fireFoxOptions = webdriver.FirefoxOptions()

        temp = [str(i).capitalize() for i in str(name).split()]
        self.manga_name = "-".join(temp)
        self.pdf_name = str(name)
        self.manga_start = start
        self.manga_end = end
        self.chat_id = chat_id
        self.session = requests.Session()
        self.manga_crowler_thread = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive"
        }

    def start_crowling(self):
        self.manga_crowler_thread = threading.Thread(name="MANGA", target=self.manga_crowler, args=(
            self.manga_name, self.manga_start, self.manga_end, self.chat_id,))
        print('[INFO] Thread Created')
        self.manga_crowler_thread.start()
        print('[INFO] Thread STarted')

    def stop_crowling(self):
        pass

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

        while temp <= end:
            gc.collect()
            ch = round(temp, 1)
            if ch.is_integer():
                chapter = str(int(ch))
                stop = True
            else:
                chapter = str(ch)
                stop = False
            temp = round(temp, 10) + round(0.1, 10)
            pdf_filename = str(bin_path + self.pdf_name + " Chapter " + str(chapter).zfill(3) + ".pdf")
            state, url, total_page = self.get_original_url(name, chapter, 1)
            print('[INFO] Total Page :',total_page)
            state = str(state)
            url = str(url)
            if state == 'ERROR' and stop:
                bot.sendMessage(chat_id=chat_id, text='ERROR :\n' + url)
                break
            elif state == 'ERROR' and not stop:
                continue
            msg = bot.sendMessage(chat_id=chat_id, text=f"{name}\n\nInitializing :")

            print("[ INFO ] Original URL :", url)
            main_url = url[:-7]

            page = 1
            bot.edit_message_text(chat_id=chat_id,
                                  text=f"{name}\n\nDownloading :\n\nChapter :{str(chapter).zfill(3)}\nPAGE :{page}\nPercentage :0%",
                                  message_id=msg.message_id)
            while True:
                gc.collect()
                bot.edit_message_text(chat_id=chat_id,
                                      text=f"{name}\n\nDownloading :\n\nChapter :{str(chapter).zfill(3)}\nPAGE : {page}\nPercentage :{int(float(page/total_page) * 100)}%",
                                      message_id=msg.message_id)
                merger = PdfFileMerger()
                url = f'{main_url}{str(page).zfill(3)}.png'
                # self.session.mount(url, HTTPAdapter(max_retries=5))
                img_data = None
                for _ in range(5):
                    try:
                        img_data = requests.get(url, headers=self.headers, stream=True)
                        break
                    except Exception as excp:
                        pass
                # img_data = self.session.get(url, headers=self.headers, stream=True)
                if img_data is None:
                    print('PAGE MISSED')
                    break
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
                    image.close()
                    del image
                else:
                    break
                print('[INFO] PAGE: ', page)
                print('[INFO] Memory Usage :', psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
                page += 1
                merger.close()
                del merger
                gc.collect()

            with open(pdf_filename, 'rb') as file:
                bot.edit_message_text(chat_id=chat_id,
                                      text=f"{name}\n=====Uploading=====\n\nChapter :{str(chapter).zfill(3)}",
                                      message_id=msg.message_id)
                if len(self.pdf_name + " Chapter " + str(chapter).zfill(3) + ".pdf") > 45:
                    print("[ BOT ] ",
                          bot.sendDocument(document=file, chat_id=chat_id, caption='#' + str(chapter).zfill(3)))
                else:
                    print("[ BOT ] ", bot.sendDocument(document=file, chat_id=chat_id))

                bot.edit_message_text(chat_id=chat_id, text="Uploading PDF Completed", message_id=msg.message_id)

            print("[ INFO ] ", pdf_filename, " Uploaded")
            os.remove(pdf_filename)
            bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            gc.collect()

        shutil.rmtree(bin_path)
        # self.driver.quit()
        return

    def get_original_url(self, name, chapter, page):
        url = f'https://manga4life.com/read-online/{name}-chapter-{str(chapter)}-page-{str(page)}.html'
        url_state = requests.get(url)
        for i in url_state.iter_lines():
            if 'title' in i.decode():
                if '404' in i.decode():
                    print('[INFO] : Manga Not Found')
                    gc.collect()
                    return 'ERROR', f'{0} chapter {1}Manga Not Found'.format(name, str(chapter)), 0
                break

        # self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=fireFoxOptions)
        global chromeOptions
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chromeOptions)
        try:
            driver.get(url)
            if "404 Page Not Found" == driver.title:
                print('[INFO] : Manga Not Found')

                driver.quit()
                gc.collect()
                return 'ERROR', 'Manga Not Found', 0
            w = WebDriverWait(driver, 8)
            w.until(EC.visibility_of_element_located(
                (By.XPATH, f'//*[@id="TopPage"]/div[{page + 1}]/div/img')))  # //*[@id="TopPage"]/div[2]/div/img
            del w
            url_data = driver.find_element(By.XPATH, f'//*[@id="TopPage"]/div[{page + 1}]/div/img').get_attribute(
                "ng-src")
            # ---- find page ----
            toppage = driver.find_element_by_id("TopPage")
            ng_scopes = toppage.find_elements_by_class_name("ng-scope")
            counter = 0
            for ng_scope in ng_scopes:
                if ng_scope.get_attribute("ng-repeat") == 'Page in vm.Pages':
                    counter += 1
            # --------------------
            driver.quit()
            gc.collect()
            return 'OK', url_data, counter
        except Exception as excp:
            print('[INFO] ERROR :', excp.args)
            return 'ERROR', excp.args, 0


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global UpDateId
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    user = update.message.from_user.name
    update_id = update.update_id
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    userText = update.message.text.encode('utf-8').decode()
    print("[INFO] got text message :", userText)
    print("[INFO] UPDATE ID :", update_id)
    print('[INFO] UpDateId :', UpDateId)
    print("[INFO] CHAT ID :", chat_id)
    print("[INFO] MESSAGE ID :", msg_id)
    print("[INFO] USER :", user)
    usr_data = USERS.find_one({"user": user})
    usr_state = int(usr_data["Active"])
    if '@Itachi_Uchiha_123' != user:
        bot.sendMessage(chat_id=chat_id, text="You are Not allowed to Use This BOT")
        return 'OK'
    if '/start' in userText:
        if UpDateId == update_id:
            return 'OK'
        else:
            UpDateId = update_id
            print('[INFO] After UpDateId :', UpDateId)
        print(type(userText))
        k = str(userText.strip('/start')).strip()
        print(k)
        name = ' '.join(k.split()[0:-1])
        chapter = k.split()[-1]
        start = chapter.split('-')[0]
        end = chapter.split('-')[1]
        obj = MangaCrowler(name, start, end, chat_id)
        obj.start_crowling()
        print('[INFO] Object Created')
        return 'OK'
    else:
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


api.add_resource(Index, "/")
api.add_resource(Favicon, '/favicon.ico')
api.add_resource(SetWebhook, '/setwebhook')
if __name__ == '__main__':
    app.run(threaded=True)
