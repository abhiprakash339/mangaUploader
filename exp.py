import json

#
# with open("input.csv", "w",newline="") as file:
#     writer = csv.writer(file)
#     writer.writerows([['NAME', '0'], ['MANGA_URL', '0'], ['START', '0'], ['END', '0']])
k = {
    "NAME": "",
    "MANGA_URL": "",
    "START": "",
    "END": ""
}


def read_input():
    with open("input.json", "r") as f:
        data = json.load(f)
    return data


def write_input(data):
    with open("input.json", "w") as f:
        f.write(str(json.dumps(data)))


data = read_input()
if not data["@Abhi_Prakash123"]["NAME"]:
    data["@Abhi_Prakash123"]["NAME"] = "Naruto"
    write_input(data)
print(read_input()["@Abhi_Prakash123"]["NAME"])
