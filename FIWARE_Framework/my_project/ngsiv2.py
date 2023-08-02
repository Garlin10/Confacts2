##############################################################################
##                                                                          ##
##   reference: https://fiware.github.io/specifications/ngsiv2/stable/      ##
##                                                                          ##
##############################################################################

import configparser
import json

import pelda1

config = configparser.ConfigParser()
config.read('fiware_config.ini')

describer = pelda1.ConfigOperator()



class NGSIv2():
    def __init__(self):
        #self.service = ''
        #self.service_path = ''

        #self.data = ''
        self.idDelimiter = '.'
    
    def _getInitValue(self, type):

        """If value is a string, then type Text is used
        If value is a number, then type Number is used.
        If value is a boolean, then type Boolean is used.
        If value is an object or array, then StructuredValue is used.
        If value is null, then None is used."""

        if type == 'Number' or type == 'Integer':
            return 0
        elif type == 'Float':
            return 0.0
        elif type == 'Text':
            return ''
        elif type == 'Boolean':
            return False

    def getOrionInit(self, id, config_path = "configs"):
        describer = pelda1.ConfigOperator(config_path)
        if not type(id) == list:
            name = id.split(self.idDelimiter)[-1]
            valueType = describer.getAttributesByName(id, 'valueType')
            out  =  { 
                    'id':id,
                    'type':describer.getAttributesByName(id, 'sensorType'),
                    name:   { 
                            'value': self._getInitValue(valueType), 
                            'type': valueType
                            }
                    }
            return out
        else:
            out =   { 
                    'id':id,
                    'type':describer.getAttributesByName(id, 'sensorType'),
                    }
            for i in id:
                name = i.split(self.idDelimiter)[-1]
                valueType = describer.getAttributesByName(i, 'valueType')
                out[name] = { 
                            'value': self._getInitValue(valueType), 
                            'type': valueType
                            }
            return out

    def getQuantumleapInit(self, id,config_path = "configs"):
        describer = pelda1.ConfigOperator(config_path)
        out =  {"subject":  {
                    "entities": [
                        {
                            "id": id,
                            "type": describer.getAttributesByName(id, 'sensorType')
                        }],
                    "condition": 
                        {
                        "attrs":
                            []
                        }
                    },
                "notification": 
                    {
                    "http": {"url": 'http://'+config['quantumleap']['ip']+":"+config['quantumleap']['port']+"/v2/notify"},
                    "attrs":[
                        id.split(self.idDelimiter)[-1]
                    ],
                    "onlyChangedAttrs": True,
                    "metadata": ["dateCreated", "dateModified"]
                    }
                }

        #return json.dumps(out)
        return out

    def getUpdateAttribute(self, id):
        name = id.split(self.idDelimiter)[-1]
        out = { 'entityId': id,
                'attrName': name,
                'value': describer.DowloadValue(id)
            }
        return out

    def getBatchUpdateAttribute(self, ids):
        '''input = {'type':'', 'id':'', 'name':'', 'value':''}
        out =   {
                    "actionType": "update",
                    "entities": [
                        {
                            "type": "Room",
                            "id": "Bcn-Welt",
                            "temperature": {
                                "value": 21.7
                                },
                        },
                        {
                            "type": "Room",
                            "id": "Mad_Aud",
                            "temperature": {
                                "value": 22.9
                                },
                        }
                    ]
                }'''

        values = describer.DowloadValue(ids)

        entities = list()
        for id, value in values:
            name = id.split(self.idDelimiter)[-1]
            entities.append({'type': describer.getAttributesByName(id, 'sensorType'),
                             'id': id,
                             name: {'value':value, 
                                    'type':describer.getAttributesByName(id, 'valueType')
                                    }
                            })

        out = {
                    "actionType": "update",
                    "entities": entities
                }
        #print(out)
        #print()
        return json.dumps(out)


if __name__ == '__main__':

    ngsiv2 = NGSIv2()

    ids = describer.getURNs()
    #print('ids:\t', ids)

    #print(ngsiv2.getOrionInit('ultimaker.bed.temperature.current'))
    #print(ngsiv2.getUpdateAttribute('ultimaker.bed.temperature.current'))
    #print()
    #print(ngsiv2.getBatchUpdateAttribute(ids, describer.DowloadValue(ids)))
    print(ngsiv2.getBatchUpdateAttribute(['iss.position.lat', 'iss.position.lon', 'iss.position.altitude']))
    print(ngsiv2.getBatchUpdateAttribute(['sif400.sif405.mes.busy', 'sif400.sif405.mes.movPos1']))    
    

    '''for i in ids:
        print('id:\t', i)
        #print(describer.getSensorType(i))
        print(ngsiv2.getOrionInit(i))'''

    '''values = pelda1.DowloadValue(ids)

    print(ngsiv2.getBatchUpdateAttribute(ids, values))'''
