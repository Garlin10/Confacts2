import requests
import json
from rest_api import RestApiOperator
from opcua_lib import Opcua
from hs110_lib import Hs110
from jsonpath_ng.ext import parse
import os
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(filename='log.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y.%m.%d %H:%M:%S',
                    level=logging.WARNING)


def getrawdata(protocol, address):
    if protocol == "http_rest":
        operator = RestApiOperator()
        x = operator.getHTTP(address)
        if x != None:
            rawdict = json.loads(x.text)
            rawdata = jsondict(rawdict)
            return rawdata
        else:
            return None


class jsondict:
    def __init__(self, dict):
        self.content = dict

    def getvaluebypath(self, path):
        res = self.content
        jsonpath_expression = parse(path)
        match = jsonpath_expression.find(res)
        val = None
        for i in match:
            val = i.value
        return val


class mapping:
    def __init__(self, source, target):
        self.source = source
        self.target = target


class jobclass:
    def __init__(self, protocol, address, mappings):
        self.protocol = protocol
        self.address = address

        self.mappings = mappings

    def getupdatelist(self):
        updatelist = list()
        if self.protocol == "http_rest":
            rest_api = RestApiOperator(self.address)
            mapping_source = []
            mapping_target = []
            for mapping in self.mappings:
                mapping_source.append(mapping.source)
                mapping_target.append(mapping.target)
            x = rest_api.getBatchValues(mapping_source)
            if x is None:
                return (updatelist)
            else:
                lengthofmappings = range(len(mapping_source))
                for n in lengthofmappings:
                    updatelist.append((mapping_target[n], x[n]))
                return (updatelist)

        if self.protocol == "hs110":
            hs110 = Hs110(self.address)
            mapping_source = []
            mapping_target = []
            for mapping in self.mappings:
                mapping_source.append(mapping.source)
                mapping_target.append(mapping.target)
            x = hs110.getBatchValues(mapping_source)
            if x is None:
                return (updatelist)
            else:
                lengthofmappings = range(len(mapping_source))
                for n in lengthofmappings:
                    updatelist.append((mapping_target[n], x[n]))
                return (updatelist)

        if self.protocol == "opcua":
            opcua = Opcua(self.address)
            mapping_source = []
            mapping_target = []
            for mapping in self.mappings:
                mapping_source.append(mapping.source)
                mapping_target.append(mapping.target)
            x = opcua.getBatchValue(nodeIdList=mapping_source)
            if x is None:
                return (updatelist)
            else:
                lengthofmappings = range(len(mapping_source))
                for n in lengthofmappings:
                    updatelist.append((mapping_target[n], x[n]))
                return (updatelist)


class ConfigOperator():

    def __init__(self,json_path = "configs"):

        jsonList = self.readJsons(json_path)
        self.services = []
        self.servicePaths = []
        self.data = []
        self.data_list = []
        self.services_by_urn = []
        self.update_init(jsonList)

    def update_init(self, ListOfJson):
        self.jsonList = ListOfJson
        self.services = []
        self.servicePaths = []
        self.data = []
        self.data_list = []
        self.services_by_urn = []
        for n in self.jsonList:
            f = open(n)
            temp_data = json.load(f)
            temp_service = self.saveServices(temp_data)
            temp_servicePath = self.saveServicePaths(temp_data)
            if temp_service not in self.services:
                self.services.append(temp_service)
            if temp_servicePath not in self.servicePaths:
                self.servicePaths.append(temp_servicePath)
            self.data.extend(temp_data)
            self.data_list.extend(self.getDatafromJson(temp_data))
            self.services_by_urn.extend(self.saveServicesbyURN(
                self.getDatafromJson(temp_data), temp_service, temp_servicePath))
            f.close()
        pass

    def saveServicesbyURN(self, temp_data, service, service_path):
        urnsandservices = list()
        for x in temp_data:
            if len(x[0]) > 0:
                if x[0] not in urnsandservices:
                    urnsandservices.append([x[0], service, service_path])
        return urnsandservices

    def saveServices(self, json_load):
        listofdata = self.getDatafromJson(json_load)
        for x in listofdata:
            if "service" == x[1]:
                return x[2]
        return

    def saveServicePaths(self, json_load):
        listofdata = self.getDatafromJson(json_load)
        for x in listofdata:
            if "service-path" == x[1]:
                return x[2]
        return
    def saveProvider(self, json_load):
        listofdata = self.getDatafromJson(json_load)
        for x in listofdata:
            if "provider" == x[1]:
                return x[2]
        return

    def getServices(self):
        return self.services

    def getServicePaths(self):
        return self.servicePaths

    def readJsons(self, json_path):
        path_to_json = os.path.join(os.getcwd(), rf'{json_path}')

        json_files = []
        for pos_json in os.listdir(path_to_json):
            if pos_json.endswith('.json'):
                json_files.append(os.path.join(path_to_json, pos_json))
        return json_files

    def convertXpath(self, xpath):
        xpath = xpath[1:]
        return xpath.replace(".", "/")

    def getDatafromJson(self, wanna_be_urn):
        l = self._getDatafromJson(wanna_be_urn, "")
        return l

    def _getDatafromJson(self, wanna_be_urn, path):
        rval = list()
        for x in list(wanna_be_urn.keys()):
            if (type(wanna_be_urn[x]) == dict):
                rval.extend(self._getDatafromJson(
                    wanna_be_urn[x], path+"."+str(x)))
            else:

                rval.append([str(path)[1:], str(x), str(wanna_be_urn[x])])
        return rval

    def getURNs(self):
        urns = list()
        for x in self.data_list:
            if len(x[0]) > 0:
                if x[0] not in urns:
                    urns.append(x[0])
        return urns

    def getAttributesByName(self, urn, name):
        for e in self.data_list:
            if urn in e[0]:
                if name in e[1]:
                    return e[2]
        return

    def getService(self, urn):
        urns = self.services_by_urn
        for x in urns:
            if urn == x[0]:
                return x[1]
        return

    def getServicePath(self, urn):
        urns = self.services_by_urn
        for x in urns:
            if urn == x[0]:
                return x[2]
        return

    def urlChanger(self,url):
        # Get today's date
        presentday = datetime.now()  # or presentday = datetime.today()
        # Get Tomorrow
        tomorrow = presentday + timedelta(1)
        # strftime() is to format date according to
        # the need by converting them to string
        today = presentday.strftime('%d-%m-%Y')
        tomorrow = tomorrow.strftime('%d-%m-%Y')
        temp_url= url.format(today=today, tomorrow=tomorrow)
        print(temp_url)
        return temp_url

    def DowloadValue(self, urns):
        mappings = []
        if len(urns) > 0:
            if (isinstance(urns, str)):
                proto = self.getAttributesByName(urns, "proto")
                url = self.getAttributesByName(urns, "url")
            else:
                proto = self.getAttributesByName(urns[0], "proto")
                url = self.getAttributesByName(urns[0], "url")
            # print('proto:', proto)

            if ("http_rest" == proto):
                if (isinstance(urns, str)):
                    xpath = (self.getAttributesByName(urns, "xpath"))
                    if url.startswith('http://') or url.startswith('https://'):
                        job = jobclass(proto, self.urlChanger(url), [mapping(xpath, urns)])
                        updatelist = job.getupdatelist()
                    else:
                        job = jobclass(proto, self.urlChanger("http://"+url),
                                       [mapping(xpath, urns)])
                        updatelist = job.getupdatelist()
                else:
                    for x in urns:
                        xpath_temp = (self.getAttributesByName(x, "xpath"))
                        mappings.append(mapping(xpath_temp, 
                                                x))
                    job = jobclass(proto, self.urlChanger("http://"+url), mappings)
                    updatelist = job.getupdatelist()
            if ("opcua" == proto):
                if (isinstance(urns, str)):
                    print(self.getAttributesByName(urns, "nodeId"))
                    nodeId = (self.getAttributesByName(urns, "nodeId"))
                    #urlChanger is not necessary
                    job = jobclass(proto, self.urlChanger(url), [mapping(nodeId, urns)])
                    updatelist = job.getupdatelist()
                else:
                    for x in urns:
                        mappings.append(mapping(self.getAttributesByName(x, "nodeId"), 
                                                x))
                    #urlChanger is not necessary
                    job = jobclass(proto, self.urlChanger(url), mappings)
                    updatelist = job.getupdatelist()
            if ("hs110" == proto):
                if (isinstance(urns, str)):
                    nodeId = (self.getAttributesByName(urns, "nodeId"))
                    #urlChanger is not necessary
                    job = jobclass(proto, self.urlChanger(url), [mapping(nodeId, urns)])
                    updatelist = job.getupdatelist()
                else:
                    for x in urns:
                        mappings.append(mapping(self.getAttributesByName(x, "nodeId"), 
                                                x))
                    #urlChanger is not necessary
                    job = jobclass(proto, self.urlChanger(url), mappings)
                    updatelist = job.getupdatelist()
            # getlistPrinted(mappings)

            # updatelist = job.getupdatelist()
            # updatelist = None
            #logging.warning(str(updatelist))
            return updatelist
        return None


def getlistPrinted(list):
    i = 0
    for e in list:
        # print(str(i)+ " " + e)
        i += 1


if __name__ == '__main__':
    operator = ConfigOperator()
    # x = operator.getDatafromJson(operator.data)
    # # urns = operator.getURNs()
    # # print(operator.getService(urns[0]))
    # # print(operator.getServicePath(urns[0]))
    # # getlistPrinted(operator.getURNs())
    # # print(operator.DowloadValue(operator.getURNs()[0]))
    # x = operator.getDatafromJson(operator.data)
    # #getlistPrinted(operator.data_list)
    # #getlistPrinted(operator.getURNs())
    # x = operator.getURNs()
    # for i in range(len(x)):
    #     print(i)
    x = operator.getURNs()

    getlistPrinted(x)
    for y in x:
        print(operator.DowloadValue(y))
