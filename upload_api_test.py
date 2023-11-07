import requests

files = {'file': open('inputs/transcript_1.vtt','rb')}
# files = {'file': open('inputs/file.txt','rb')}

# print(files)

url = "http://13.211.169.215:5000/retrohelp"

r = requests.post(url, files=files)

# r = requests.get(url)


print(r.json())