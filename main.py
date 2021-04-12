name = 'Naruto'
chapter = '1'
page = '001'
import requests
url = f'https://manga4life.com/read-online/{name}-chapter-{str(chapter)}-page-{str(page)}.html'
url_state = requests.get(url)
if url_state.status_code != 200:
    print('[INFO] : Manga Not Found')