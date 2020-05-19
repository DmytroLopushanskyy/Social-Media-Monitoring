"""
Parse web page end extract telegram channels from it
"""
DATA = []
INP = ""
while INP != "stop":
    INP = input()
    if INP.startswith("@"):
        DATA.append(INP)
    elif INP.startswith("AAAA"):
        DATA.append("https://t.me/joinchat/" + INP)

print(len(DATA), DATA)
