from pymongo import MongoClient
from configparser import ConfigParser

config = ConfigParser()
config.read("bot.ini")
print(config["API"]["MONGO-DB"])

client = MongoClient(config["API"]["MONGO-DB"])
db = client.get_database("Telegram_Bot")
#
# user_db = db.list_collection_names()
# print(user_db)

doc = db.get_collection('users_inputs')
usr_data = doc.find_one({"user": "@Itachi_Uchiha_123"})
if usr_data["Active"] == "1":
    usr_data["manga-name"] = "one piece"
    usr_data["Active"] = "1"
    doc.update_one({"user": "@Itachi_Uchiha_123"},{"$set": usr_data})
print(list(doc.find()))
# # doc.drop_index([("user", 1)])
# # doc.create_index([("user", 1)], unique=True)
#
# # data = {
# #     "user": "@Itachi_Uchiha_123",
# #     "Active": "0",
# #     "manga-name": "",
# #     "manga-url": "",
# #     "manga-start": "",
# #     "manga-end": ""
# # }
# # up = {
# # "Active": "0"
# # }
# # doc.update_one({"user": "@Itachi_Uchiha_123"},{"$set":up})
#
# # try:
# #     print(doc.insert_one(data))
# # except Exception as excp:
# #     print(db.error())
# #     print(excp)
#
# # print(list(doc.find_one_and_delete({"user": "@Itachi_Uchiha_123"})))
# # print(user_db.count_documents({}))
# print(list(doc.find()))
# print(len(list(doc.find())))
