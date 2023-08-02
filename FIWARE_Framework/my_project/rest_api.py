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
    operator = RestApiOperator('http://130.130.130.199/api/warehouseStatus?stationTypeId=406')
    # print(operator.getHTTP('http://192.168.1.62/api/v1/printer'))
    # print(operator.getHTTP('http://192.168.1.62/api/v1/printer/bed/temperature/current'))
    # asd = operator.getHTTP('http://192.168.1.62/api/v1/printer')    
    # print(asd["bed"]["temperature"])
    print(operator.getBatchValues(['$.Object.Locations[?(@.LocationID=1)].SKU.ChildSKUs[0].Article.Code','$.Object.Locations[?(@.LocationID=1)].LocationStatus.Description']))