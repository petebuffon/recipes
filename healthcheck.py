import requests

try:
    r = requests.get("http://127.0.0.1:8288")
    if str(r) == "<Response [200]>":
        print(0)
    else:
        print(1)
except:
    print(1)
