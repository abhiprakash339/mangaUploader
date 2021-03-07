import json
import time
import requests


def st(num):
    for i in range(num):
        print(i)
        time.sleep(1)
        yield "OK"


for i in st(5):
    print(i)
