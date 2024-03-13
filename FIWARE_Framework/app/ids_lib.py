#https://{IP}:{port}/{IDS_Name}/api/data-resources-consumed/{dataResourceTitle}/artifacts/{artifactTitle}/data
import requests
from requests.auth import HTTPBasicAuth
import requests
from requests.auth import HTTPBasicAuth
import json
import datetime
import pytz
# Assuming IDS_config and TimeProvider are available as per your setup
class TimeProvider():
    def GetCurrentTime(self):
        today = datetime.datetime.now()
        today = today.replace(tzinfo=pytz.UTC)
        return today.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    def GetFutureTime(self, days):
        today = datetime.datetime.now()
        first = today.replace(day=1)
        future = first + datetime.timedelta(days)
        future = future.replace(tzinfo=pytz.UTC)
        return future.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    def GetPastTime(self, days):
        today = datetime.datetime.now()
        first = today.replace(day=1)
        past = first - datetime.timedelta(days)
        past = past.replace(tzinfo=pytz.UTC)
        return past.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
class IDSResource:
    def __init__(self, ids_ip, ids_port, ids_name, data_resource_title, username, password):
        self.IDS_IP = ids_ip
        self.IDS_PORT = ids_port
        self.IDS_Name = ids_name
        self.dataResourceTitle = data_resource_title
        self.username = username
        self.password = password
        self.timeprovider = TimeProvider()

    def construct_get_url(self, artifactTitle):
        return f"https://{self.IDS_IP}:{self.IDS_PORT}/{self.IDS_Name}/api/data-resources-consumed/{self.dataResourceTitle}/artifacts/{artifactTitle}/data"

    def test_construct_get_url(self, artifactTitle):
        return f"https://{self.IDS_IP}:{self.IDS_PORT}/{self.IDS_Name}/api/data-resources-provided/{self.dataResourceTitle}/artifacts/{artifactTitle}/data"

    def get_data(self, artifactTitle):
        url = self.construct_get_url(artifactTitle)
        response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password), verify=False)
        if response.status_code == 200:
            return response.text
        else:
            return f"Failed to get data, status code: {response.status_code}"

    def test_get_data(self, artifactTitle):
        url = self.test_construct_get_url(artifactTitle)
        response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password), verify=False)
        if response.status_code == 200:
            x = response.text
            i1 = x.find("{")
            i2 = x.rfind("}") + 1
            x1 = x[i1:i2]
            return x1
        else:
            return f"Failed to get data, status code: {response.status_code}"


    def create_data_resource(self):
        data = {
            "title": self.dataResourceTitle,
            "descr": self.dataResourceTitle,
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
                "title": f"{self.dataResourceTitle} ; public access",
                "start": f"{self.timeprovider.GetPastTime(1)}",
                "end": f"{self.timeprovider.GetFutureTime(730)}",
                "consumer": "",
                "usagePolicies": [
                {
                    "type": "PROVIDE_ACCESS"
                }
                ]
            }
            ]
        }
        response = requests.post(f'https://{self.IDS_IP}:{self.IDS_PORT}/{self.IDS_Name}/api/data-resources-provided', json= data, headers = {"Content-Type": "application/json; charset=utf-8", "accept":"application/json"}, auth=HTTPBasicAuth(self.username, self.password), verify=False)
        return response
        

    def create_artifact(self, artifactTitle, data):
        url = f'https://{self.IDS_IP}:{self.IDS_PORT}/{self.IDS_Name}/api/data-resources-provided/{self.dataResourceTitle}/artifacts'
        params = {
            'artifactTitle': artifactTitle,
            'artifactIsDynamic': 'true',
            'keyWords': ['Key1', 'Key2']
        }

        # Assuming `data` is already a JSON string or a dictionary that should be converted to JSON
        if not isinstance(data, str):
            data = json.dumps(data)

        files = {'file': (f'{artifactTitle}.json', data, 'application/json')}  # Replace 'filename.json' with your actual filename

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/octet-stream'
        }
        response = requests.post(url, params=params, headers=headers, files=files, auth=HTTPBasicAuth(self.username, self.password), verify=False)
        return response


    def update_artifact(self, artifactTitle, data):
        url = f'https://{self.IDS_IP}:{self.IDS_PORT}/{self.IDS_Name}/api/data-resources-provided/{self.dataResourceTitle}/artifacts/{artifactTitle}/data'
        params = {
            'artifactTitle': artifactTitle,
            'artifactIsDynamic': 'true',
            'keyWords': ['Key1', 'Key2']
        }

        # Assuming `data` is already a JSON string or a dictionary that should be converted to JSON
        if not isinstance(data, str):
            data = json.dumps(data)

        files = {'file': (f'{artifactTitle}.json', data, 'application/json')}  # Replace 'filename.json' with your actual filename

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/octet-stream'
        }
        response = requests.put(url, params=params, headers=headers, files=files, auth=HTTPBasicAuth(self.username, self.password), verify=False)
        return response

    # Example method to demonstrate access to these instance attributes
    def print_details(self, artifactTitle):
        print(f"IDS_IP: {self.IDS_IP}")
        print(f"IDS_PORT: {self.IDS_PORT}")
        print(f"IDS_Name: {self.IDS_Name}")
        print(f"dataResourceTitle: {self.dataResourceTitle}")
        print(f"artifactTitle: {artifactTitle}")
    

if __name__ == '__main__':
    #https://79.172.212.69:8090/pbn/api/data-resources-consumed/Inesctec/artifacts/EnergyUSE/data
    resource = IDSResource('79.172.212.69', 8090, 'pbn', 'PBN4',  'admin', 'admin')
    resource.print_details('ConfactsReTest3')
    response1 = resource.create_data_resource()
    # Your original data
    datajson = {"alma": "banan"}

    # Convert the Python dictionary to a JSON formatted string
    json_str = json.dumps(datajson)
    response2 = resource.update_artifact('ConfactsReTest3', json_str)
    print(response2.text)

