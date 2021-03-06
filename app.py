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


def link_test(url):
    status = requests.get(url, stream=True).status_code
    if status == 200:
        return True
    else:
        return False


def download_chapter(chapter_url):
    if not os.path.isdir("./bin"):
        os.mkdir("./bin")
    else:
        shutil.rmtree("./bin")
        os.mkdir("./bin")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }

    page = 1
    session = requests.Session()
    while True:
        temp_url = chapter_url + "-" + str(page).zfill(3) + ".png"
        print("[ INFO ] ", temp_url)
        try:
            img_data = session.get(temp_url, headers=headers, stream=True)
            if img_data.status_code == 200:
                image = Image.open(img_data.raw)
                image.save("./bin/" + str(page).zfill(3) + ".png")
                # sys.stdout.write("\r[ INFO ] Downloaded : " + str(page).zfill(3))
                # sys.stdout.flush()
            else:
                print("[ INFO ] ", chapter_url)
                break
        except Exception as excp:
            print("[ INFO ] ", excp.args)

        page += 1
    gc.collect()
    return


def pdf_convert(chapter, chatID):
    dir_path = "./bin"
    file = os.listdir(dir_path)

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
    # time.sleep(2)
    print("[ INFO ] " + str(chapter) + " Uploaded")
    print("[ INFO ] ", os.listdir())
    try:
        print("[ INFO ] ", os.listdir(dir_path))
    except:
        pass
    shutil.rmtree(dir_path)

    gc.collect()
    return


def connect(chatID):
    stop = False

    main_url = "/".join(manga_main_url.split("/")[0:-1])
    start = float(manga_start)
    end = float(manga_end)
    temp = float(start)

    while temp <= end:
        ch = round(temp, 1)
        if ch.is_integer():
            chapter = str(int(ch)).zfill(4)
            stop = True
        else:
            chapter = str(ch).zfill(6)
            stop = False
        if link_test(main_url + "/" + chapter + "-001.png"):
            print("[ INFO ] ", chapter, ": STARTED")
            print("[ INFO ] chaper URL :", (main_url + "/" + chapter))
            download_chapter(main_url + "/" + chapter)
            pdf_convert(chapter, chatID)
            print("[ INFO ] ", chapter, ": DONE")
        elif stop:
            return
        else:
            print("[ INFO ] ", chapter, ": SKIPPED")
        temp = round(temp, 10) + round(0.1, 10)
        gc.collect()


def read_input():
    with open("input.json", "r") as f:
        data = json.load(f)
    return data


def write_input(data):
    with open("input.json", "w") as f:
        f.write(str(json.dumps(data)))


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global manga_name, manga_main_url, manga_start, manga_end
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
        data = read_input()

        data[user]["NAME"] = ""
        data[user]["MANGA_URL"] = ""
        data[user]["START"] = ""
        data[user]["END"] = ""

        write_input(data)

        response = "Enter Manga Name"
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)

        return 'OK'
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

        response = "Name : " + manga_name + "\nURL :" + manga_main_url + "\nSTART :" + manga_start + "\nEND :" + manga_end + "\nDownloading chapters ..."
        manga_main_url = data[user]["MANGA_URL"]
        write_input(data)
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
        connect(chat_id)
        return 'OK'
    else:
        response = "Restart the Bot by Sending '/start' command"
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
    app.run(threaded=True, debug=True)
    # url = "https://fan-trash.lowee.us/manga/One-Piece/1006-001.png"
    # connect_url(url)
