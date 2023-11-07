import requests

files = {'file': open('inputs/file.txt','rb')}

url = "http://127.0.0.1:5000"

r = requests.post(url, files=files)

# r = requests.get(url)


print(r.json())