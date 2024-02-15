import configparser
import requests
import json
import ngsiv2
import pelda1
import IDS_put
from IDS_config import IDS_config
config = configparser.ConfigParser()
config.read('fiware_config.ini')

ngsiv2 = ngsiv2.NGSIv2()
describer = pelda1.ConfigOperator()

class Orion():
    def __init__(self):
        self.orionHost =            'http://'+config['orion']['ip']+':'+config['orion']['port']
        self.orionTimeout =         int(config['orion']['timeout'])
        self.quantumleapHost =      'http://'+config['quantumleap']['ip']+':'+config['quantumleap']['port']
        self.quantumleapTimeout =   int(config['quantumleap']['timeout'])
        self.config = IDS_config()
    
    def _getOrionData(self):
        headers = {}
        response = requests.get(self.orionHost+'/version', headers=headers, timeout=self.orionTimeout)
        return response.json()
    ###########Body converter for IDS################
    #TODO Nézzen már ki valahogy ez...
    #TODO A DataResource kreálást külön venni egy INIT függvénybe, amit lefuttatsz indításkor.
    def getentities(self, service, service_path, data):
        print(service)
        service_path = service_path.replace("/","")
        tmp = json.loads(data)
        print(tmp)
        print(len(tmp["entities"]))
        print(len(tmp["entities"]))
        if(len(tmp["entities"])>0):
            IDS_Broker = IDS_put.DataResources_ProviderSide()
            #EZ NEM JÓÓÓÓ!!!!
            existing_offers = IDS_Broker.GetDataResources()
            if(service not in existing_offers):
                IDS_Broker.CreateDataResource(service)
            with open(f"./tmp/{service_path}.json", "w") as outfile:
                outfile.write(data)
            #TODO: Ezt a függvényhívást rendberakni. 
            print(IDS_Broker.UpdateArtifact(service, service_path, f"./tmp/{service_path}.json"))
                
            print("--------------------------------")
            for entity in tmp["entities"]:
                #print(entity)
                ...
        else:
            print("No new data")
    ##################################################
    def getVersion(self):
        data = self._getOrionData()
        return data['orion']['version']
    
    def getQuantumleapVersion(self):
        headers = {}
        res = requests.get(self.quantumleapHost+'/version', headers=headers, timeout=self.quantumleapTimeout).json()['version']
        return res


    def createEntity(self, id, config_path ="configs"):
        headers = { "Content-Type": "application/json", 
                    "fiware-service": describer.getService(id), 
                    "fiware-servicepath": describer.getServicePath(id),
                    }

        data = ngsiv2.getOrionInit(id, config_path)
        #print('data\t\t', data)
        response = requests.post(self.orionHost+'/v2/entities', json=data, headers=headers, timeout=self.orionTimeout)

        return response.text

    def updateValue(self, data):
        service = describer.getService(ids[0])
        service_path = describer.getServicePath(ids[0])
        ##### rewrite ######

        headers = { "Content-Type": "text/plain", 
                    "fiware-service": service,
                    "fiware-servicepath": service_path,
                    }

        id = data['entityId']
        attrName = data['attrName']
        data = data['value']
        print("----------START--------\n")
        self.getentities(service, service_path, data)
        print("----------END-----------\n")
        url = self.orionHost+f'/v2/entities/{id}/attrs/{attrName}/value'
        response = requests.put(url, data=data, headers=headers, timeout=self.orionTimeout)
        return response.text
    
    # TODO: Ebből még egyet csinálni ahol  scnincs IDS feltöltés
    # TODO: Ezt meghívni a még megírandó IDS agent-tel.
    def updateBatchValues(self, ids):
        service = describer.getService(ids[0])
        service_path = describer.getServicePath(ids[0])
        print(f"service: {service}")
        print(f"service: {service_path}")
        
        headers = { "Content-Type": "application/json", 
                    "fiware-service": service,
                    "fiware-servicepath": service_path,
                    }
        url = self.orionHost+f'/v2/op/update'
        
        print("----------START--------\n")
        try:
        # Your existing code
            data = ngsiv2.getBatchUpdateAttribute(ids)
            print(data)
            print("ngsiv2")
        except Exception as e:
            print(f"An error occurred: {e}")   
        try:
            print("post")
            self.getentities(service, service_path, data)
            response = requests.post(url, data=data, headers=headers, timeout=self.orionTimeout)
            print("response:" +f"{response}")
        except Exception as e:
            print(f"An error occurred: {e}")     
        
        print("----------END-----------\n")
        
        return response


    def queryEntity(self, service, servicePath, id=None, type=None, options=None, attrs=None, q=None, limit=1000):
        ########################
        #  options: count
        #           keyValues
        #           values
        #           unique
        ########################

        isFirstParam = True

        headers = { "Accept": "application/json", 
                    "fiware-service": service, 
                    "fiware-servicepath": servicePath,
                    }
        
        url = self.orionHost + '/v2/entities'

        if id==None and type==None and options==None and attrs==None and q==None and limit==None:
            response = requests.get(url, headers=headers, timeout=self.orionTimeout)

            return response.json()
        else:
            if id != None:
                url += f'urn:{id}'
            if type != None:
                if isFirstParam:
                    url += f'?type={type}'
                    isFirstParam = False
                else:
                    url += f'&type={type}'
            if options != None:
                if isFirstParam:
                    url += f'?options={options}'
                    isFirstParam = False
                else:
                    url += f'&options={options}'
            if attrs != None:
                if isFirstParam:
                    url += f'?attrs={attrs}'
                    isFirstParam = False
                else:
                    url += f'&attrs={attrs}'
            if q != None:
                if isFirstParam:
                    url += f'?q={q}'
                    isFirstParam = False
                else:
                    url += f'&q={q}'
            if limit != None:
                if isFirstParam:
                    url += f'?limit={limit}'
                    isFirstParam = False
                else:
                    url += f'&limit={limit}'        

        response = requests.get(url, headers=headers, timeout=self.orionTimeout)

        return response.json()

    def deleteEntity(self, id):
        headers = { 
                    "fiware-service": describer.getService(id),
                    "fiware-servicepath": describer.getServicePath(id),
                    }
        response = requests.delete(self.orionHost+f'/v2/entities/{id}', headers=headers, timeout=self.orionTimeout)
        return response

    def getOrionIds(self, service, servicePath):
        res = list()
        for i in self.queryEntity(service=service, servicePath=servicePath):
            res.append(i['id'])
        return res

    def deleteAllEntity(self, service, servicePath):
        ids = self.getOrionIds(service, servicePath)
        for id in ids:
            self.deleteEntity(id)

    def subscribeLongTermDatabase(self, id, config_path ="configs"):
        headers = { "Accept": "application/json",
                    "Content-Type": "application/json",
                    "fiware-service": describer.getService(id),
                    "fiware-servicepath": describer.getServicePath(id)
                  }
        
        data = ngsiv2.getQuantumleapInit(id, config_path)

        response = requests.post(self.orionHost+'/v2/subscriptions', headers=headers, json=data, timeout=self.orionTimeout)

        return response

    def getSubscriptions(self, service, servicePath):
        headers = { 'fiware-service': service, 
                    'fiware-servicepath': servicePath
                   }
        res = requests.get(self.orionHost+'/v2/subscriptions', headers=headers, timeout=self.orionTimeout).json()
        return res
    
    def getQuantumleapQuery(self, id, offset=0, lastN=10, limit=10):
        headers = { 'Accept': 'application/json',
                    'fiware-service': describer.getService(id), 
                    'fiware-servicepath': describer.getServicePath(id)
                   }

        attr = id.split(ngsiv2.idDelimiter)[-1]
        res = requests.get(self.quantumleapHost+f'/v2/entities/{id}/attrs/{attr}?offset={offset}&lastN={lastN}', headers=headers, timeout=self.quantumleapTimeout).json()
        #res = requests.get(self.quantumleapHost+f'/v2/entities/{id}/attrs/{attr}', headers=headers, timeout=self.quantumleapTimeout).json()
        
        
        return res
    
    ######  https://documenter.getpostman.com/view/513743/RWEnkvDc

if __name__ == '__main__':
    

    orion = Orion()

    
    ids = describer.getURNs()
    #print('all id:\t', ids)
    #print('ids:\t', ids)
    print('orion version:\t\t\t', orion.getVersion())
    print('quantumleap version:\t\t', orion.getQuantumleapVersion())

    
    print('query:\t\t', orion.queryEntity(service='iss', servicePath='/space/iss'))
    ids = ['iss.position.lat', 'iss.position.lon', 'iss.position.altitude']
    print('batch update:\t', orion.updateBatchValues(ids=ids))
    print('query:\t\t', orion.queryEntity(service='iss', servicePath='/space/iss'))






    #print('create:\t\t', orion.createEntity(id='ultimaker.bed.temperature.current'))
    #print('create:\t\t', orion.createEntity(id='ultimaker.bed.temperature.target'))
    #print('query:\t\t', orion.queryEntity(service='3dprinter', servicePath='/pbn/amlab/ultimaker'))
    #print('update:\t', orion.updateValue(data=data))
    #print('batch update:\t', orion.updateBatchValues(ids=ids))
    #print('query:\t\t', orion.queryEntity(service='3dprinter', servicePath='/pbn/amlab/ultimaker'))
    #orion.deleteAllEntity(service='3dprinter', servicePath='/pbn/amlab/ultimaker')
    #print('quantumleap subscriptions:\t', orion.getSubscriptions('ProductionLine', '/pbn/amlab/sif400'))
    #print('quantumleat query:\t\t', orion.getQuantumleapQuery('iss.position.lat'))

