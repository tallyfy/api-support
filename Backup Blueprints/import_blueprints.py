import requests #pip3 install requests
import json
import os
import time


org_id = ""
access_token = ""

def read_credentials():
    with open("credentials.txt", "r") as f:
        for line in f:
            org_id = line.split(':')[1].strip('\r\n')
            nextline = next(f)
            access_token = nextline.split(':')[1]
        return org_id, access_token

org_id, access_token = read_credentials()

api = "https://api.tallyfy.com/organizations/"+org_id+"/checklists" #API_URL

#Request headers#
head = {
'Accept': 'application/json',
'Authorization': "Bearer "+access_token,
}
#################

blueprints = os.listdir("blueprints/") # List blueprints in the directory

for blueprint in blueprints:
    print("Creating blueprint - "+ blueprint)

    # Opening JSON file
    f = open('blueprints/' + blueprint, )

    # returns JSON object as
    # a dictionary
    data = json.load(f)
    ######## Delete not required parameters
    del data['id']
    del data['owner_id']
    del data['created_by']
    del data['alias']
    del data['steps_count']
    del data['industry_tags']
    del data['topic_tags']
    del data['folder_id']
    del data['kickoff_title']
    del data['kickoff_description']
    del data['started_processes']
    del data['created_at']
    del data['last_updated']
    del data['archived_at']
    ######## Delete not required parameters

    ##### Making calls to the API
    try: # Check if we made a successful call
        resp = requests.post(url=api, json=data, headers=head)
        # print("Blueprint was created successfully !")
    except:
        print("There was an error with blueprint - "+blueprint)
        

    time.sleep(1)  # Wait a second after an API call


