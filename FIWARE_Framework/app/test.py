import json

import configmodel
import orion
from typing import List
import os

def t1():
    m:configmodel.Provider = configmodel.Provider.parse_file('configs/recycling_module.json')
    #m.groups[0].queries[0].Execute()
    #v = m.groups[0].queries[2].Execute()
    z = m.getqueryschedulegroups()

    m.evaluatefields(querylist=["recycling_opcua"])
    x = m.getmappings("fiware")

    orion_url = "http://192.168.1.200:1026"
    fiware_service = "your_service"
    fiware_servicepath = "/your_servicepath"
    print(z[0])

    s = json.dumps(x[0])

    print(s)
    orion.push_data_to_orion(orion_url, x[0],
                       fiware_service, fiware_servicepath)

def t2():
    m:configmodel.Provider = configmodel.Provider.parse_file('configs/recycling_module.json')
    z:List[configmodel.QueryScheduleGroup] = m.getqueryschedulegroups()
    zx:configmodel.QueryScheduleGroup
    for zx in z:
        m1:configmodel.Provider = configmodel.Provider.parse_file('configs/recycling_module.json')
        m1.Push(zx.querynames)


def t3():
    m:configmodel.Provider = configmodel.Provider.parse_file('configs/recycling_module.json')
    m.PushSchema()
    print("a")

def t4():
    m:configmodel.Provider = configmodel.Provider.parse_file('configs/recycling_module.json')
    m.evaluatefields(["idstest"])


def t5():
    m:configmodel.Provider = configmodel.Provider.parse_file('configs/inegitest.json')
    z:List[configmodel.QueryScheduleGroup] = m.getqueryschedulegroups()
    zx:configmodel.QueryScheduleGroup
    for zx in z:
        m1:configmodel.Provider = configmodel.Provider.parse_file('configs/inegitest.json')
        m1.Push(zx.querynames)

def getconfigfiles(configpath:str = "./configs/models"):
    files = os.listdir(configpath)
    filenames = [configpath + "/" + f for f in files if  os.path.isfile(configpath + "/" +f)]
    return filenames



if __name__ == '__main__':
    getconfigfiles()
    print("a")