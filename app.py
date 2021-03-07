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
from configparser import ConfigParser
from flask import Flask, request, send_from_directory

config = ConfigParser()
config.read('bot.ini')

TOKEN = config['BOT']['TOKEN']
URL = config['SERVER']['URL']
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

manga_name = ""
manga_main_url = ""
manga_start = ""
manga_end = ""

stop_connect = False


def link_test(url):
    status = requests.get(url, stream=True).status_code
    if status == 200:
        return True
    else:
        return False


def download_chapter(chapter_url, chat_id):
    global manga_name
    bin_path = "./bin/"
    if not os.path.isdir(bin_path):
        os.mkdir(bin_path)
    else:
        shutil.rmtree(bin_path)
        os.mkdir(bin_path)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }

    page = 1
    session = requests.Session()
    msg = bot.sendMessage(chat_id=chat_id, text="\nDownloading PAGE :000")
    im = list()
    while True:
        temp_url = chapter_url + "-" + str(page).zfill(3) + ".png"
        print("[ INFO ] ", temp_url)
        img_path = bin_path + str(page).zfill(3) + ".png"
        try:
            img_data = session.get(temp_url, headers=headers, stream=True)
            if img_data.status_code == 200:
                bot.edit_message_text(chat_id=chat_id, text="\nDownloading PAGE :" + str(page).zfill(3), message_id=msg.message_id)
                image = Image.open(img_data.raw)
                image.save(img_path)
                if page == 1:
                    im1 = Image.open(img_path, mode='r')
                    im1.load()
                    im1.split()
                    os.remove(img_path)
                else:
                    img = Image.open(img_path, mode='r')
                    img.load()
                    img.split()
                    im.append(img)
                    os.remove(img_path)
            else:
                break
        except Exception as excp:
            print("[ INFO ] ", excp)
            bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            bot.sendMessage(chat_id=chat_id, text="[ ERROR ] :" + str(excp))
            return
        page += 1
    pdf_filename = bin_path + manga_name + " Chapter " + str("001") + ".pdf"
    bot.edit_message_text(chat_id=chat_id, text="Making Pdf...", message_id=msg.message_id)
    im1.save(pdf_filename, "PDF", resolution=100.0, save_all=True, append_images=im)
    with open(pdf_filename, 'rb') as file:
        bot.edit_message_text(chat_id=chat_id, text="Uploading PDF...", message_id=msg.message_id)
        print("[ BOT ] ", bot.sendDocument(document=file, chat_id=chat_id))
        bot.edit_message_text(chat_id=chat_id, text="Uploading PDF Completed", message_id=msg.message_id)
    print("[ INFO ] ", pdf_filename, " Uploaded")
    bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    gc.collect()
    shutil.rmtree(bin_path)
    return


def pdf_convert(chapter, chatID):
    if int(chapter[0]) == 0:
        chapter = chapter[1:]
    dir_path = "./bin/"
    file = os.listdir(dir_path)
    # with open("dummy.pdf", 'rb') as dummy:
    #     dummy = bot.sendDocument(document=dummy, chat_id=chatID)
    # fileID = dummy.document.file_id
    im1 = Image.open(dir_path + "/001.png", mode='r')
    im1.load()
    im1.split()
    im = list()
    for i in range(2, len(file) + 1):
        pic = dir_path + "/" + str(i).zfill(3) + ".png"
        try:
            img = Image.open(pic, mode='r')
            img.load()
            img.split()
            im.append(img)
        except:
            pass

    pdf_filename = "./bin/" + manga_name + " Chapter " + str(chapter) + ".pdf"
    im1.save(pdf_filename, "PDF", resolution=100.0, save_all=True, append_images=im)
    with open(pdf_filename, 'rb') as file:

        print("[ BOT ] ", bot.sendDocument(document=file, chat_id=chatID))
    print("[ INFO ] ", pdf_filename, " Uploaded")
    shutil.rmtree(dir_path)
    print("[ INFO ] ", os.listdir())

    gc.collect()
    return


def connect(chatID):
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
            download_chapter(main_url + "/" + chapter, chatID)
            # pdf_convert(chapter, chatID)
            print("[ INFO ] ", chapter, ": COMPLETED")
        elif stop:
            bot.sendMessage(chat_id=chatID, text=(manga_name + " Chapter " + chapter + " Not Found"))
            return
        else:
            print("[ INFO ] ", chapter, ": NOT-AVAILABLE")
        temp = round(temp, 10) + round(0.1, 10)
        gc.collect()
    bot.sendMessage(chat_id=chatID, text="Completed")
    return


def read_input():
    with open("input.json", "r") as f:
        data = json.load(f)
    return data


def write_input(data):
    with open("input.json", "w") as f:
        f.write(str(json.dumps(data)))


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global manga_name, manga_main_url, manga_start, manga_end, stop_connect
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    user = update.message.from_user.name
    # of = update.update_id + 1
    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    userText = update.message.text.encode('utf-8').decode()
    print("[INFO] got text message :", userText)

    if userText == "/start":
        stop_connect = True

        data = read_input()

        data[user]["NAME"] = ""
        data[user]["MANGA_URL"] = ""
        data[user]["START"] = ""
        data[user]["END"] = ""

        write_input(data)

        response = "Enter Manga Name"
        print("[ BOT ]", bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id))

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
        return "OK"
    elif "/ongoing" in userText:
        with open("manga_data.json", "r") as read_json:
            m = dict(json.load(read_json))
            temp = ""
            for i in m:
                temp += i + " : " + m[i] + "\n"
            bot.sendMessage(chat_id=chat_id, text=temp, reply_to_message_id=msg_id, disable_web_page_preview=True)
        return "OK"

    elif "/select" in userText:
        k = userText.split()[1]
        return "OK"

    elif not read_input()[user]["NAME"]:
        data = read_input()
        data[user]["NAME"] = userText

        write_input(data)

        response = "Enter URL"
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)

        return 'OK'
    elif not read_input()[user]["MANGA_URL"]:
        data = read_input()
        data[user]["MANGA_URL"] = userText
        write_input(data)

        response = "Starting Chapter"
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)

        return 'OK'
    elif not read_input()[user]["START"]:
        data = read_input()
        data[user]["START"] = userText
        response = "Ending Chapter"
        write_input(data)
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        return 'OK'
    elif not read_input()[user]["END"]:
        data = read_input()
        data[user]["END"] = userText

        manga_name = data[user]["NAME"]
        manga_main_url = data[user]["MANGA_URL"]
        manga_start = data[user]["START"]
        manga_end = data[user]["END"]

        response = "NAME   :" + manga_name + "\nURL    :" + manga_main_url + "\nSTART  :" + manga_start + "\nEND    :" + manga_end + "\n\nDownloading Chapters ..."
        manga_main_url = data[user]["MANGA_URL"]
        write_input(data)
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, disable_web_page_preview=True)
        stop_connect = False
        thd = threading.Thread(name="connect_thread", target=connect, args=(chat_id,))
        thd.start()
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


@app.route('/')
def index():
    return 'WELCOME TO MANGA-UPLOADER'


if __name__ == '__main__':
    app.run(threaded=True)
