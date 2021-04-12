name = 'Naruto'
chapter = '1.5'
page = '001'
import requests
url = f'https://manga4life.com/read-online/{name}-chapter-{str(chapter)}-page-{str(page)}.html'
url_state = requests.get(url)
for i in url_state.iter_lines():
    if 'title' in i.decode():
        if '404' in i.decode():
            print('404')
        break
if url_state.status_code != 200:
    print('[INFO] : Manga Not Found')