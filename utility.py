import os
import openai
import json  

openai.api_key = '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'
openai.Model.list()

def AIGEN(filename):

    with open("uploads/"+filename,'r') as file:
        data = file.read()

        print(data)

        Compute_Create_Meeting_Minutes(data)

def Compute_Create_Meeting_Minutes(data):

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a project management assistant, skilled in explaining complex programming concepts with creative flair."},
            # {"role": "user", "content": "Can you imagine and create a transcript from a fictional meeting involving four people."}

            {"role": "user", "content": "Below is the transcript from a meeting. Please create minutes for this meeting."},
            {"role": "user", "content": data}
        ]
    )

    f = open("processed/minutes.txt", "w")
    f.write(str(completion.choices[0].message))
    f.close()

    # the json file where the output must be stored  
    out_file = open("processed/minutes.json", "w")  
    
    json.dump(completion.choices[0].message, out_file, indent = 6)  
    
    out_file.close()

    print(completion.choices[0].message)


def Compute_Suggest_Jira_Tickets():
    pass