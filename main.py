from pymongo import MongoClient
from configparser import ConfigParser

config = ConfigParser()
config.read("bot.ini")

client = MongoClient(config["API"]["MONGO-DB"])
db = client.get_database("Telegram_Bot")
#
# user_db = db.list_collection_names()
# print(user_db)

doc = db.get_collection('manga_url_data')
# doc.create_index([("manga-name", 1)], unique=True)
# doc.insert({"manga-name":"My-Hero-Academia","manga-url":"https://temp.compsci88.com/manga/Boku-No-Hero-Academia/0305-001.png","manga-chapter":"305"})
# print(list(doc.find()))
temp = ""
for i in doc.find():
    temp += str(i["manga-name"] + " : " + i['manga-url'] +"\n")
print(temp)
