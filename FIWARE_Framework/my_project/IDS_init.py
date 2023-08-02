import requests
import subprocess
import json
import sys
import os
from requests.auth import HTTPBasicAuth
from IDS_get import DataResources_onBroker
from IDS_put import DataResources_ProviderSide
from time_provider import TimeProvider
from IDS_config import IDS_config
class IDS_init():
    def __init__(self):
        self.memory = []
        self.config = IDS_config()
        self.IP = self.config.IP
        self.USER = self.config.USER
        self.PASS = self.config.PASS
        self.COMPANY = self.config.COMPANY
        self.DataResources_onBroker = DataResources_onBroker()
        self.DataResources_ProviderSide = DataResources_ProviderSide()
        self.time = TimeProvider()
    def read_config_file(self, file_path):
        with open(file_path, 'r') as config_file:
            config_data = json.load(config_file)
        return config_data
    def read_all_json_files(self, folder_path):
        json_data = []
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    json_data.append(data)
        return json_data
    def load_to_memory(self, json_data):
        try:
            for i in json_data:
                try:
                    self.memory.append({"offer": i["service"], "artifact": i["service-path"][1:],"refreshInterval": i["refreshInterval"], "modificationDate": self.time.GetPastTime(120)})
                except:
                    self.memory.append({"offer": i["service"], "artifact": i["service-path"][1:], "modificationDate": self.time.GetPastTime(120)})
            return self.memory
        except:
            return None
    def create_offers(self, memory):
        existing_offers = self.DataResources_ProviderSide.GetDataResources()
        for offer in memory:
            print(offer["offer"])
            if(offer["offer"] not in existing_offers):
                self.DataResources_ProviderSide.CreateDataResource(self.IP, self.COMPANY, self.USER, self.PASS, offer["offer"])
                print(offer["offer"])
    def create_artifacts(self, memory):
        for offer in memory:
            existing_artifacts = self.DataResources_ProviderSide.GetArtifacts(offer["offer"])
            if(offer["artifact"] not in existing_artifacts):
                self.DataResources_ProviderSide.CreateArtifact(offer["offer"], offer["artifact"], "./tmp/dog.jpg")
                offer["modificationDate"] = self.time.GetCurrentTime()
                print(offer["artifact"])
                print(existing_artifacts)
        print(memory)
        return memory
            #get_ModificationDate
    def init(self, config_path):
        #PROVIDER SIDE
        memory = self.load_to_memory(self.read_all_json_files(config_path))
        self.create_offers(memory)
        tmp_memory = self.create_artifacts(memory)
        self.memory = tmp_memory
        
if __name__ == "__main__":
    init = IDS_init()
    # data = init.read_all_json_files("./configs")
    # init.load_to_memory(data)
    # print(init.memory)
    init.init("./configs")
    print()