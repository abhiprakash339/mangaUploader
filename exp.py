# import csv
# with open("input.csv","w") as file:
#     writer = csv.writer(file)
#     writer.writerows([['name',''],['manga_url',''],[]])

from configparser import ConfigParser

config = ConfigParser()
config.read('bot.ini')

config['INPUT']['NAME'] = "P"
if not config['INPUT']['NAME']:
    print("kk",config['INPUT']['NAME'])