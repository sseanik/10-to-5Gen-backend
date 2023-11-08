import requests

files = {'file': open('inputs/transcript_1.vtt','rb')}
# files = {'file': open('inputs/file.txt','rb')}

# print(files)

# 13.211.169.215:5000
# 127.0.0.1:5000

# url = "http://13.211.169.215:5000/files/agile"

# r = requests.get(url)

# upload a new file. takes 30-60 seconds to process. Returns ID, name etc.
url = "http://127.0.0.1:5000/uploadtranscript"
r = requests.post(url,data={'name':'test_name_5','meetingType':'Standup'},files=files)



# Gets the list of all files with ID, name etc.
# url = "http://13.211.169.215:5000/masterlist"

# request the AI results for a specified file ID e.g. 1
# url = "http://13.211.169.215:5000/files/<file ID>"

# r = requests.get(url)



# r = requests.post(url, files=files)

# r = requests.post(url,data={'name':'test_name','date':'1/1/2000'},files=files)

# r = requests.post(url,data={'name':'test_name_4','meetingType':'Standup'},files=files)



print(r.json())