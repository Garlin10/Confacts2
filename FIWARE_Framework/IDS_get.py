import requests
import subprocess
import json
import sys
from requests.auth import HTTPBasicAuth
from IDS_config import IDS_config
# IP = "79.172.212.69:8090"
# USER = "admin"
# PASS = "admin"
# COMPANY= "pbn"
class DataResources_onBroker():
    def __init__(self):
        self.config = IDS_config()
# Authentication in Requests with HTTPBasicAuth
    def GetAllOffer(self):
        IP = self.config.IP
        COMPANY = self.config.COMPANY
        USER = self.config.USER
        PASS = self.config.PASS
        auth = HTTPBasicAuth(USER, PASS)
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = requests.get(f'https://{IP}/{COMPANY}/api/data-resources-on-broker/all', headers=headers, auth=auth, verify=False)
        
        return data.text
    def GetSelectedOffer(self,offer):
        IP = self.config.IP
        COMPANY = self.config.COMPANY
        USER = self.config.USER
        PASS = self.config.PASS
        auth = HTTPBasicAuth(USER, PASS)
        
        headers = {"Content-Type": "application/json; charset=utf-8"}
        print(requests.get(f'https://{IP}/pbn/api/data-resources-on-broker/selectedoffer?offer={offer}', headers=headers, auth=auth, verify=False).json())
class DataResources_ConsumerSide():
    def __init__(self):
        self.config = IDS_config()
    #Give a title get all the offers's address in list
    def getFileTitlesOfOffer(self, offer):
        IP = self.config.IP
        COMPANY = self.config.COMPANY
        USER = self.config.USER
        PASS = self.config.PASS
        url = f'https://{IP}/{COMPANY}/api/data-resources-provided/{offer}/artifacts'
        links = []
        auth = HTTPBasicAuth(USER, PASS)
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.get(url, headers=headers, auth=auth, verify=False).text
        res = json.loads(response)
        # try:
        #     for i  in res["representations"]:
        #         for y in i["artifacts"]:
        #             links.append([y["title"], y["remoteId"]])
        # except:
        #     print(res)
        return res
    def getFile(self, offer, artifact):
        IP = self.config.IP
        COMPANY = self.config.COMPANY
        USER = self.config.USER
        PASS = self.config.PASS
        auth = HTTPBasicAuth(USER, PASS)
        url = f'https://{IP}/{COMPANY}/api/data-resources-consumed/Inesctec/artifacts/{artifact}/data'
        headers = {'accept': 'application/octet-stream',"Content-Type": "application/json; charset=utf-8"}

        response = requests.get(url, headers=headers, auth=auth, verify=False)

        if response.status_code == 200:
            content_str = response.content.decode('utf-8')  # Decode the bytes to a string using utf-8 encoding
            return {"offer": offer, "artifact": artifact, "content": content_str}
        else:
            print("Failed to download the file")
            return None
    def get_ModificationDate(self, offer,artifact):
        IP = self.config.IP
        COMPANY = self.config.COMPANY
        USER = self.config.USER
        PASS = self.config.PASS
        auth = HTTPBasicAuth(USER, PASS) 
        url = f'https://{IP}/{COMPANY}/api/data-resources-consumed/{offer}/artifacts/{artifact}'
        headers = {'accept': 'application/json'}

        response = requests.get(url, headers=headers, auth=auth, verify=False)

        if response.status_code == 200:
            json_data = response.json()
            print(json_data)
            date = json_data["modificationDate"]
            print(date)
            return {"offer": offer, "artifact": artifact, "modificationDate": date}
        # Process the JSON data as needed
        else:
            print('Request failed with status code:', response.status_code)
            return None
if __name__ == "__main__":
    Broker = DataResources_ConsumerSide()
    #Artifacts = Broker.getFileTitlesOfOffer("PBN")
    #print(Artifacts)
    Broker.getFile("Inesctec", "EnergyUSE", "./tmp/EnergyUSE2.json")
    #Broker.get_ModificationDate("Inesctec", "EnergyUSE")
    #Broker.getFile("https://79.172.212.69:8080/pbn/api/artifacts/ddce8f86-93b8-4f33-b55a-661d1cad9e8f", "./test.json")
    #https://79.172.212.69:8080/pbn/api/artifacts/6b0a6fcc-cf7e-45a3-9485-67f17b2c1cb2
    #Broker.getFile("https://79.172.212.69:8080/pbn/api/artifacts/d7de4696-5d3d-4f92-9171-3267f4b4419e","./dog.png")