import shutil
from PIL import Image
import requests
import os

# file = os.listdir(dir_path)
#     # with open("dummy.pdf", 'rb') as dummy:
#     #     dummy = bot.sendDocument(document=dummy, chat_id=chatID)
#     # fileID = dummy.document.file_id
#
#
#     for i in range(2, len(file) + 1):
#         pic = dir_path + "/" + str(i).zfill(3) + ".png"
#         try:
#             img = Image.open(pic, mode='r')
#             img.load()
#             img.split()
#             im.append(img)
#         except:
#             pass
#
#     pdf_filename = "./bin/" + manga_name + " Chapter " + str(chapter) + ".pdf"
#     im1.save(pdf_filename, "PDF", resolution=100.0, save_all=True, append_images=im)
#     with open(pdf_filename, 'rb') as file:
#
#         print("[ BOT ] ", bot.sendDocument(document=file, chat_id=chatID))
#     print("[ INFO ] ", pdf_filename, " Uploaded")
#     shutil.rmtree(dir_path)
#     print("[ INFO ] ", os.listdir())
def download_chapter(chapter_url):
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
    im = list()
    while True:
        temp_url = chapter_url + "-" + str(page).zfill(3) + ".png"
        print("[ INFO ] ", temp_url)
        try:
            img_data = session.get(temp_url, headers=headers, stream=True)
            if img_data.status_code == 200:

                page_file = bin_path +str(page).zfill(3)+".png"
                image = Image.open(img_data.raw)
                image.save(page_file)
                if page == 1:
                    im1 = Image.open(page_file, mode='r')
                    im1.load()
                    im1.split()
                    os.remove(page_file)
                else:
                    pic = bin_path + str(page).zfill(3) + ".png"
                    try:
                        img = Image.open(pic, mode='r')
                        img.load()
                        img.split()
                        im.append(img)
                        os.remove(page_file)
                    except:
                        pass

                # sys.stdout.write("\r[ INFO ] Downloaded : " + str(page).zfill(3))
                # sys.stdout.flush()
            else:
                print("[ INFO ] ", chapter_url)
                break
        except Exception as excp:
            print("[ INFO ] ", excp.args)
        if page >= 10:
            break
        page += 1
    pdf_filename = page_file + "Banana Fish" + " Chapter " + str("001") + ".pdf"
    im1.save(pdf_filename, "PDF", resolution=100.0, save_all=True, append_images=im)
    return

download_chapter("https://official-complete.granpulse.us/manga/Banana-Fish/0001")