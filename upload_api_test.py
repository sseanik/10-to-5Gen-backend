import requests

files = {'file': open('inputs/transcript_1.vtt','rb')}
# files = {'file': open('inputs/file.txt','rb')}

# print(files)

# 13.211.169.215:5000
# 127.0.0.1:5000

# url = "http://13.211.169.215:5000/files/agile"

# r = requests.get(url)

# url = "http://13.211.169.215:5000/uploadtranscript"

# url = "http://13.211.169.215:5000/masterlist"

url = "http://13.211.169.215:5000/files/1"

r = requests.get(url)



# r = requests.post(url, files=files)

# r = requests.post(url,data={'name':'test_name','date':'1/1/2000'},files=files)

# r = requests.post(url,data={'name':'test_name_4','meetingType':'Standup'},files=files)



print(r.json())