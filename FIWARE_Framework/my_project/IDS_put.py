import requests
import subprocess
import urllib3
import json
from requests.auth import HTTPBasicAuth
from time_provider import TimeProvider
from IDS_config import IDS_config

# IP = "79.172.212.69:8090"
# USER = "admin"
# PASS = "admin"
# COMPANY = "pbn"
class DataResources_ProviderSide():
    def __init__(self):
        self.config = IDS_config()
        
    def get_ModificationDate(self,  offer,artifact, IP = None, COMPANY = None, USER = None, PASS = None):
        if IP is None:
            IP = self.config.IP
        if COMPANY is None:
            COMPANY = self.config.COMPANY
        if USER is None:
            USER = self.config.USER
        if PASS is None:
            PASS = self.config.PASS
        auth = HTTPBasicAuth(USER, PASS) 
        url = f'https://{IP}/{COMPANY}/api/data-resources-provided/{offer}/artifacts/{artifact}'
        headers = {'accept': 'application/json'}

        response = requests.get(url, headers=headers, auth=auth, verify=False)

        if response.status_code == 200:
            json_data = response.json()
            return json_data["modificationDate"]
        # Process the JSON data as needed
        else:
            print('Request failed with status code:', response.status_code)
            return None
    def GetDataResources(self,IP = None, COMPANY = None, USER = None, PASS = None):
        if IP is None:
            IP = self.config.IP
        if COMPANY is None:
            COMPANY = self.config.COMPANY
        if USER is None:
            USER = self.config.USER
        if PASS is None:
            PASS = self.config.PASS
        list = []
        auth = HTTPBasicAuth(USER, PASS)
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = requests.get(f'https://{IP}/{COMPANY}/api/data-resources-provided', headers=headers, auth=auth, verify=False).text
        tmp = json.loads(data)
        for catalog in tmp:
            for offer in catalog["offeredResources"]:
                list.append(offer["title"])
        return(list)
    def GetArtifacts(self, offer, IP = None, COMPANY = None, USER = None, PASS = None):
        if IP is None:
            IP = self.config.IP
        if COMPANY is None:
            COMPANY = self.config.COMPANY
        if USER is None:
            USER = self.config.USER
        if PASS is None:
            PASS = self.config.PASS
        list = []
        auth = HTTPBasicAuth(USER, PASS)
        headers = {"Content-Type": "application/json; charset=utf-8"}
        url = f'https://{IP}/{COMPANY}/api/data-resources-provided/{offer}/artifacts'
        data = requests.get(url, headers=headers, auth=auth, verify=False).text
        offers = json.loads(data)
        for offer in offers:
                list.append(offer["title"])
        return(list)
    #TODO paraméterezni a keyWords részt (Még nem tudom mi menjen oda)
    def CreateDataResource(self, offer_title, IP = None, COMPANY = None, USER = None, PASS = None ):
        if IP is None:
            IP = self.config.IP
        if COMPANY is None:
            COMPANY = self.config.COMPANY
        if USER is None:
            USER = self.config.USER
        if PASS is None:
            PASS = self.config.PASS
        time = TimeProvider()
        yesterday = time.GetPastTime(1)
        future_time = time.GetFutureTime(730)
        auth = HTTPBasicAuth(USER, PASS)
        headers = {"Content-Type": "application/json; charset=utf-8", "accept":"application/json"}
        data = {
            "title": offer_title,
            "descr": offer_title,
            "keywords": [
            "term1",
            "term2"
            ],
            "license": "http://...url-for-the-license.../",
            "standard": "http://...url-for-standard-used.../",
            "endpointDocumentation": "https://...url-for-technical-doc.../",
            "keyValueSet": {
            "key1": "value1",
            "key2": "value2"
            },
            "contracts": [
            {
                "title": f"{offer_title} ; public access",
                "start": f"{yesterday}",
                "end": f"{future_time}",
                "consumer": "",
                "usagePolicies": [
                {
                    "type": "PROVIDE_ACCESS"
                }
                ]
            }
            ]
        }
        print(requests.post(f'https://{IP}/{COMPANY}/api/data-resources-provided', json= data, headers=headers, auth=auth, verify=False))
    def CreateArtifact(self, offer_title, artifact_title, file_path, IP = None, COMPANY = None, USER = None, PASS = None):
        if IP is None:
            IP = self.config.IP
        if COMPANY is None:
            COMPANY = self.config.COMPANY
        if USER is None:
            USER = self.config.USER
        if PASS is None:
            PASS = self.config.PASS
        auth = HTTPBasicAuth(USER, PASS)
        url = f'https://{IP}/{COMPANY}/api/data-resources-provided/{offer_title}/artifacts'
        params = {
            'artifactTitle': artifact_title,
            'artifactIsDynamic': 'true',
            'keyWords': ['Key1', 'Key2']
        }

        files = {'file': open(file_path, 'rb')}

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/octet-stream'
        }
        response = requests.post(url, params=params, headers=headers, files=files, auth=auth, verify=False)
        return response
    def UpdateArtifact(self, offer_title, artifact_title, file_path, IP = None, COMPANY = None, USER = None, PASS = None):
        if IP is None:
            IP = self.config.IP
        if COMPANY is None:
            COMPANY = self.config.COMPANY
        if USER is None:
            USER = self.config.USER
        if PASS is None:
            PASS = self.config.PASS
        auth = HTTPBasicAuth(USER, PASS)
        #TODO: Ez nagyon ocsmány. Rá kéne keresni, hogy lehet ezt szebben.
        artifactTitle = "{artifactTitle}"
        url = f'https://{IP}/{COMPANY}/api/data-resources-provided/{offer_title}/artifacts/{artifactTitle}/data?artifactTitle={artifact_title}'
        
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/octet-stream'
        }
        with open(file_path, 'rb') as file:
            response = requests.put(url, headers=headers, data=file, auth=auth, verify=False)

        print(response.status_code)
if __name__ == "__main__":
    urllib3.disable_warnings()
    Broker = DataResources_ProviderSide()
    # Broker.CreateDataResource("PBN")
    #Broker.CreateArtifact(IP, COMPANY, USER, PASS,"PBN","EnergyUSE2","./tmp/EnergyUSE.json")
    # Broker.UpdateArtifact("PBN","EnergyUSE","./tmp/EnergyUSE.json")
    # Broker.get_ModificationDate("PBN","EnergyUSE")
    #Broker.UpdateArtifact("TestPBN","FirstTry",'./dog.jpg')
    print(Broker.GetDataResources(IP, COMPANY, USER, PASS))
    print(Broker.GetArtifacts(IP, COMPANY, USER, PASS, "PBN"))