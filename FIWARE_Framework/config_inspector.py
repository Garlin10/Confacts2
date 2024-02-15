
import requests
import json
from rest_api import RestApiOperator
from opcua_lib import Opcua
from hs110_lib import Hs110
from jsonpath_ng.ext import parse
import os
import json
import logging
from pelda1 import jsondict
from pelda1 import mapping
from pelda1 import ConfigOperator
import sys
import datetime


class jobclass:
    def __init__(self, protocol, address, mappings):
        self.protocol = protocol
        self.address = address
        self.mappings = mappings

    def _getupdatelist(self):
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
                    if x[n] == None:
                        rest = RestApiOperator(self.address)
                        if rest.getConnection():
                            updatelist.append(
                                (mapping_target[n], "XPATH PROBLEM"))
                            with open('config_tester.txt', 'a') as f:
                                print(
                                    (str(datetime.datetime.now())+"\t\t" + mapping_target[n]+"\t\t\t" + "XPATH PROBLEM"), file=f)
                        else:
                            updatelist.append(
                                (mapping_target[n], "URL PROBLEM"))
                            with open('config_tester.txt', 'a') as f:
                                print(
                                    (str(datetime.datetime.now())+"\t\t" + mapping_target[n]+"\t\t\t" + "URL PROBLEM"), file=f)
                    else:
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
                    if x[n] == None:
                        if hs110.getConnection():
                            updatelist.append(
                                (mapping_target[n], "NodeID PROBLEM"))
                            with open('config_tester.txt', 'a') as f:
                                print(
                                    (str(datetime.datetime.now())+"\t" + "\t" + mapping_target[n]+"\t" + "\t" + "\t" + "NodeID PROBLEM"), file=f)
                        else:
                            updatelist.append(
                                (mapping_target[n], "URL PROBLEM"))
                            with open('config_tester.txt', 'a') as f:
                                print(
                                    (str(datetime.datetime.now())+"\t" + "\t" + mapping_target[n]+"\t" + "\t" + "\t" + "URL PROBLEM"), file=f)

                    else:
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
                if opcua.getConnection():
                    updatelist.append((mapping_target[0], "NodeID Problem"))
                    with open('config_tester.txt', 'a') as f:
                        print(
                            (str(datetime.datetime.now())+"\t" + "\t" + mapping_target[0] + "\t" + "\t" + "\t" + "NodeID PROBLEM"), file=f)
                else:
                    updatelist.append((mapping_target[0], "URL Problem"))
                    with open('config_tester.txt', 'a') as f:
                        print(
                            (str(datetime.datetime.now()) + "\t" + "\t" + mapping_target[0] + "\t" + "\t" + "\t" + "URL PROBLEM"), file=f)

            else:
                lengthofmappings = range(len(mapping_source))
                for n in lengthofmappings:
                    updatelist.append((mapping_target[n], x[n]))
            return (updatelist)


class ConfigTester(ConfigOperator):
    def _DowloadValue(self, urns):
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
                        job = jobclass(proto, url, [mapping(xpath, urns)])
                        updatelist = job._getupdatelist()
                    else:
                        job = jobclass(proto, "http://"+url,
                                       [mapping(xpath, urns)])
                        updatelist = job._getupdatelist()
                else:
                    for x in urns:
                        mappings.append(
                            mapping((self.getAttributesByName(x, "xpath")), x))
                    job = jobclass(proto, "http://"+url, mappings)
                    updatelist = job._getupdatelist()
            if ("opcua" == proto):
                if (isinstance(urns, str)):
                    nodeId = self.getAttributesByName(urns, "nodeId")
                    job = jobclass(proto, url, [mapping(nodeId, urns)])
                    updatelist = job._getupdatelist()
                else:
                    for x in urns:
                        mappings.append(
                            mapping(self.getAttributesByName(x, "nodeId"), x))
                    job = jobclass(proto, url, mappings)
                    updatelist = job._getupdatelist()
            if ("hs110" == proto):
                if (isinstance(urns, str)):
                    nodeId = self.getAttributesByName(urns, "nodeId")
                    job = jobclass(proto, url, [mapping(nodeId, urns)])
                    updatelist = job._getupdatelist()
                else:
                    for x in urns:
                        mappings.append(
                            mapping(self.getAttributesByName(x, "nodeId"), x))
                    job = jobclass(proto, url, mappings)
                    updatelist = job._getupdatelist()
            # getlistPrinted(mappings)

            # updatelist = job.getupdatelist()
            # updatelist = None
            logging.warning(str(updatelist))
            return updatelist
        return None

    def test_config(self, path_to_json):
        if path_to_json is not None:
            self.update_init([path_to_json])
        x = (tester.getURNs())
        for y in x:
            print(str(tester._DowloadValue(y)))


if __name__ == '__main__':
    tester = ConfigTester()
    tester.test_config('./configs/ultimaker_test_config.json')
    #tester.test_config(None)
