import json

str = '/add {"One-Piece":"https://hot.leanbox.us/manga/One-Piece/1006-001.png"}'
str = str[5:]
print(str)

print(json.loads(str))