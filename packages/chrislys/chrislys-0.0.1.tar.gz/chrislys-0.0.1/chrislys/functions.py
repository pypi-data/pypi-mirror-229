import requests 
import urllib3

global cred

def qualys_cred(username, api_key):
    global cred
    cred = (username, api_key)

def listHostText():
    global cred
    headers = {
        'X-Requested-With': 'Curl',
    }
    url = f"https://qualysguard.qg4.apps.qualys.com//api/2.0/fo/asset/host/?action=list"
    response = requests.get(url, headers=headers, auth=cred)
    return response.text

def listVm(qids):
    global cred
    headers = {
        'X-Requested-With': 'Curl',
    }
    url = f"https://qualysguard.qg4.apps.qualys.com/api/2.0/fo/asset/host/vm/detection/?action=list&qids={qids}&status=Active&show_asset_id=1&truncation_limit=0"
    response = requests.get(url, headers=headers, auth=cred)
    return response.text

def mrAsmelash():
    print("What's up Eyakem! Thanks for downloading my library\n\n--Chris Nam")