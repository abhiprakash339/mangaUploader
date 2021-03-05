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




data = read_input()
if not data["NAME"]:
    data["NAME"] = "Naruto"
    write_input(data)
print(read_input())
