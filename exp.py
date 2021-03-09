import telegram
from configparser import ConfigParser

config = ConfigParser()
config.read('bot.ini')

TOKEN = config['BOT']['TOKEN']
URL = config['SERVER']['URL']
bot = telegram.Bot(token=TOKEN)
# print(bot.getWebhookInfo())
# print(bot.getUpdates(offset=None,timeout=10).pop())

a = None
b = None
if a == b is None:
    print("kk")
