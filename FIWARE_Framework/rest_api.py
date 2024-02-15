import collections
import json
import requests
import os, json
from jsonpath_ng.ext import parse
class RestApiOperator():
    def __init__(self, rest_api_address):
        self.address = rest_api_address
    def getHTTP(self, url):
        #headers  = {service, service_path)
        headers = {'Accept': 'application/json'}
        try:
            api_response = requests.get(url)
            if api_response.status_code != 200:
                raise( "BAD URL")
            return api_response
        except:
            #print( "BAD URL")
            return None
    def getrawdata(self, address):
            x = self.getHTTP(address)            
            if x != None:
                rawdict = json.loads(x.text)
                return rawdict
            else:
                return None
    def getBatchValues(self, paths):
        res = self.getrawdata(self.address)
        val = []
        for path in paths:
            print(path)
            jsonpath_expression = parse(path)
            match = jsonpath_expression.find(res)
            if len(match) == 0:
                #print("BAD Xpath")
                val.append(None)
            for i in match:
                val.append(i.value)
        return val
    def getConnection(self):
        #headers  = {service, service_path)
        headers = {'Accept': 'application/json'}
        try:
            api_response = requests.get(self.address)
            if api_response.status_code != 200:
                return False
            return True
        except:
            return False
if __name__ == "__main__":
    def find_in_json(data, key_name):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == key_name:
                    return value
                elif isinstance(value, (dict, list)):
                    result = find_in_json(value, key_name)
                    if result is not None:
                        return result
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    result = find_in_json(item, key_name)
                    if result is not None:
                        return result
        return None
    # Read the content of the JSON file
    with open("configs/example_provider_config.json", 'r') as file:
        config_json = file.read()

    # Parse the JSON
    config = json.loads(config_json)

    # Dynamically find the URL
    url = find_in_json(config, "url")
    operator = RestApiOperator(url)