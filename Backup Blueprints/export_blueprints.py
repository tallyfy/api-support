import requests #pip3 install requests
import json

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
blueprints = [] # A List that holds the blueprints

print("Fetching blueprints ...")
while 1:

    response = requests.get(api,headers=head).json() #Fetching blueprints

    for item in response['data']:
        blueprints.append(item) # Append Each blue print to the list

    if int(response['meta']['pagination']['current_page']) < int(response['meta']['pagination']['total_pages']): #checking if there are more pages
        api = response['meta']['pagination']['links']['next'] # moving to the next page
    else:
        break # If there are no more pages, The loop breaks


print("Saving blueprints ...")

for b in blueprints:
    with open("blueprints/"+b['id']+".json","w+") as outfile:
        json.dump(b, outfile) # Saving a single blueprint as a json file


