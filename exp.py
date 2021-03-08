import json


def read_input():
    with open("input.json", "r") as f:
        data = json.load(f)
    return data

s=read_input()
s = dict(s)
print(s.get("@Abhi_Prakash123"))
