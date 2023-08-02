import requests
import configparser
from IDS_get import DataResources_ConsumerSide
import os
import json
from orion  import Orion
from IDS_init import IDS_init
from datetime import datetime
from time_provider import TimeProvider
class IDS_To_Fiware():
    def __init__(self):
        self.Broker = DataResources_ConsumerSide()
        self.init = IDS_init()
        self.init.init("./configs_receiver")
    def test(self, job):
        print(job["modificationDate"])
        offline_mod_date = (job["modificationDate"])
        #Mert ez lista...
        online_mod_date = (self.Broker.get_ModificationDate(job["offer"], job["artifact"])["modificationDate"])
        
        offline_tmp = f'{offline_mod_date}'
        online_tmp = f'{online_mod_date}'
        print(offline_tmp)
        print(online_tmp)
        # Convert strings to datetime objects
        # Convert strings to datetime objects
        online_mod_date = datetime.strptime(online_mod_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        offline_mod_date = datetime.strptime(offline_mod_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        print(offline_mod_date)
        print(online_mod_date)
        if(online_mod_date > offline_mod_date):
            data = self.Broker.getFile(job["offer"],job["artifact"])
            return {"offer":job["offer"], "artifact":job["artifact"], "content":data}
        return None
    def orion_send(self,  merged_service):
        #TODO: IP és port szerzés
        IP = "79.172.212.69"
        PORT = "1026"
        service = merged_service["offer"]
        print(service)
        service_path = merged_service["artifact"]
        service_path = "/"+ service_path
        print(service_path)
        headers = { "Content-Type": "application/json", 
                    "fiware-service": service,
                    "fiware-servicepath": service_path,
                    }
        url = 'http://'+IP+':'+PORT+f'/v2/op/update'
        data = merged_service["content"]
        #Mert a Context broker csak a " karaktert ismeri.
        data = str(data)
        data = data.replace("'", '\"')
        response = requests.post(url, data=data, headers=headers)
        print(self.init.memory)
        return response
if __name__ == "__main__":
    to_fiware = IDS_To_Fiware()
    print(to_fiware.init.memory)
    tmp = to_fiware.test(to_fiware.init.memory[0])
    print(tmp)
    print(to_fiware.orion_send(tmp).text)    