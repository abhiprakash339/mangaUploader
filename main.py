name = 'Naruto'
chapter = '1'
page = '001'
import requests
url = f'https://manga4life.com/read-online/{name}-chapter-{str(chapter)}-page-{str(page)}.html'
url_state = requests.get(url)
print(url_state.text)