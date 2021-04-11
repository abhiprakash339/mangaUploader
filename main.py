from flask import Flask, request, send_from_directory
from flask_restful import Api, Resource
from dataclasses import dataclass
from functools import cache

app = Flask(__name__)
api = Api(app)


# @cache
@dataclass(frozen=True, order=True)
class Home(Resource):
    def get(self):
        return 'WELCOME TO MANGA-UPLOADER'


api.add_resource(Home, "/")
if __name__ == "__main__":
    a = '/start One Piece 450-450'
    if '/start' in a:
        k = str(a.removeprefix('/start')).strip()
        name = ' '.join(k.split()[0:-1])
        chapter = k.split()[-1]
        start = chapter.split('-')[0]
        end = chapter.split('-')[1]
        print('name:', name, '\nstart :', start, '\nEND :', end)
    # app.run(port=3000, debug=True)
