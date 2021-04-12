import os
hostname = "google.com" #example
name = 'Naruto'
chapter = '1'
page = '001'
# url = f'https://manga4life.com/read-online/{name}-chapter-{str(chapter)}-page-{str(page)}.html'
url = 'https://manga4life.com/read-online/Naruto-chapter-1-page-001.html'
response = os.system("ping " + url+" -n 1")

if response == 0:
  print('up!')
else:
  print('down!')