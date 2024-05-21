from __future__ import annotations

import json
import random

import opcua_lib
from pydantic import BaseModel
from pthelpers import Subclasses
from typing import List, Optional, ForwardRef, Literal
import requests
import orion
import ids_lib
def readconfig(configname:str)->dict:
    f = open(f"./configs/settings/{configname}")
    return json.load(f)

class QueryResult(BaseModel):

    def GetValueNames(self) -> List[str]:
        ...

    def GetValues(self) -> dict[str, str]:
        ...

    def GetValueByName(self, name: str) -> str:
        ...

    def AddValue(self, key: str, value: str):
        ...


class DictResult(QueryResult):
    content: dict = dict()

    def GetValueNames(self) -> List[str]:
        return [str(k) for k in self.content.keys()]

    def GetValues(self) -> dict[str, str]:
        return dict([(str(k), str(self.content[k])) for k in self.content.keys()])

    def GetValueByName(self, name: str) -> object:
        if name in self.content.keys():
            return self.content[name]
        return None

    def AddValue(self, key: str, value: str):
        if key not in self.content.keys():
            self.content[key] = value


class Mapping(BaseModel):
    fromfield: str
    tofield: str


class TestMapping(Mapping):
    valuetype: Optional[str]


class QueryParser(BaseModel):
    type: str
    map: List[Mapping]="Text"


class OpcuaParser(QueryParser):
    type: str = "opcua"

    def SetServer(self, server: opcua_lib.Opcua):
        ...


class OpcuaBatchParser(OpcuaParser):
    type: Literal["opcua_batch"]
    map: List[Mapping]

    _server: Optional[opcua_lib.Opcua]
    _data: Optional[dict]

    def SetServer(self, server: opcua_lib.Opcua):
        self._server = server
        self._data = dict()

    def Parse(self):
        k: Mapping
        values:dict = self._server.getBatchValue([k.fromfield for k in self.map])
        self._data = dict()
        if values is not None:
            for k in self.map:
                if k.fromfield in values.keys():
                    self._data[k.tofield] = values[k.fromfield]

    def GetData(self) -> dict:
        return self._data

class OpcuaTestParser(OpcuaParser):
    type: Literal["opcua_test"]
    map: List[TestMapping]

    _server: Optional[opcua_lib.Opcua]
    _data: Optional[dict]

    def _generatevalue(self, valuetype:Optional[str]):
        if valuetype == "Text":
            return random.choice(["HUA", "HUE", "HUH", "AHA"]) + str(random.randint(1,100))
        if valuetype == "Number":
            return random.randint(0, 999)
        if valuetype == "Float":
            return (random.randint(0,10000))/100
        if valuetype == "Boolean":
            return random.choice([True, False])
        return None

    def SetServer(self, server: opcua_lib.Opcua):
        self._server = server
        self._data = dict()

    def Parse(self):
        k: TestMapping
        self._data = dict()
        for k in self.map:
            self._data[k.tofield] = self._generatevalue(k.valuetype)

    def GetData(self) -> dict:
        return self._data


class JsonParser(QueryParser):
    type: str = "json"

    def SetJsonData(self, jsondata: dict):
        ...


class JsonBatchParser(JsonParser):
    type: Literal["json_batch"]
    _jsondata: Optional[dict]
    _data: Optional[dict]

    def SetJsonData(self, jsondata: dict):
        self._jsondata = jsondata
        self._data = dict()

    def Parse(self):
        k: Mapping
        for k in self.map:
            value = self._jsondata
            for nestedKey in k.fromfield.split('.'):
                if nestedKey.isnumeric():
                    value = value[int(nestedKey)]
                else:
                    value = value[nestedKey]
            self._data[k.tofield] = value

    def GetData(self):
        return self._data


class Query(BaseModel):
    name: str
    type: str
    active: Optional[bool]=True
    refreshinterval: int

    def Execute(self) -> QueryResult:
        ...


class OpcuaQuery(Query):
    type: Literal["opcua"]
    address: str
    parser: Subclasses(OpcuaParser)
    _server: Optional[opcua_lib.Opcua]

    def Execute(self) -> QueryResult:
        self._server = opcua_lib.Opcua(opcuaServer=self.address)
        self.parser.SetServer(self._server)
        self.parser.Parse()
        c = self.parser.GetData()
        return DictResult(content=c)


class RestQuery(Query):
    type: Literal["rest"]
    address: str
    parser: Subclasses(JsonParser)
    _json: dict

    def Execute(self) -> QueryResult:
        result = requests.get(self.address)
        self.parser.SetJsonData(result.json())
        self.parser.Parse()
        c = self.parser.GetData()
        return DictResult(content=c)


class IdsQuery(Query):
    type: Literal["ids"]
    config: str
    data_resource_title: str
    artifact_title: str
    parser: Subclasses(JsonParser)

    def Execute(self)->QueryResult:
        cfg = readconfig(self.config)
        idsip = cfg["ip"]
        idsport = cfg["port"]
        idsname = cfg["ids_name"]
        username = cfg["username"]
        password = cfg["password"]

        res = ids_lib.IDSResource(ids_ip=idsip, ids_port=idsport, ids_name=idsname, data_resource_title=self.data_resource_title, username=username, password=password)
        data = res.test_get_data(self.artifact_title)
        jsondata = json.loads(data)
        self.parser.SetJsonData(jsondata)
        self.parser.Parse()
        c = self.parser.GetData()
        return DictResult(content=c)


class QueryField(BaseModel):
    name: str
    fieldname: Optional[str]=None
    sensorType: Optional[str]=None
    valueType: str
    query: str
    address: str
    subscribe: Optional[str] = None
    value: Optional[object] = None


class Entity(BaseModel):
    type: str


class JsonEntity(Entity):
    def Generate(self, fields:List[QueryField]) -> object:
        ...


class FiwareEntity(JsonEntity):
    type: Literal["fiware_entity"]
    entityid: str
    entitytype: str
    subscribe: Optional[bool]=True
    values: List[str]
    extraperfield:List[Mapping]

    def _getfieldbyname(self, name:str, flds:List[QueryField])->QueryField:
        qf:QueryField
        for qf in flds:
            if qf.name == name:
                return qf
        return None

    def Generate(self, fields:List[QueryField]) -> dict:
        rval = {
            "id": self.entityid,
            "type": self.entitytype
        }

        valuecount = 0

        for v in self.values:
            qf:QueryField = self._getfieldbyname(v, fields)
            if qf.value is not None:
                valuecount = valuecount + 1
                if qf.fieldname is not None:
                    fn = qf.fieldname
                else:
                    fn = v
                rval[fn] = dict()
                rval[fn]["value"] = qf.value
                m:Mapping
                for m in self.extraperfield:
                    rval[fn][m.tofield] = dict(qf)[m.fromfield]

        if valuecount > 0:
            return rval
        return None

    def GenerateDefault(self, fields:List[QueryField]) -> dict:
        rval = {
            "id": self.entityid,
            "type": self.entitytype
        }

        valuecount = 0

        for v in self.values:
            qf:QueryField = self._getfieldbyname(v, fields)
            valuecount = valuecount + 1
            if qf.fieldname is not None:
                fn = qf.fieldname
            else:
                fn = v
            rval[fn] = dict()
            rval[fn]["value"] = ""
            m:Mapping
            for m in self.extraperfield:
                rval[fn][m.tofield] = dict(qf)[m.fromfield]

        if valuecount > 0:
            return rval
        return None

class DataMapping(BaseModel):
    name: str
    type: str
    entities: List[Subclasses(Entity)]

    def Push(self, fields:List[QueryField]):
        ...

    def PushSchema(self, fields:List[QueryField]):
        ...
class FiwareMapping(DataMapping):
    type: Literal["fiware"]
    service: str
    service_path: str
    subscribe: Optional[bool]=False
    config: str
    entities: List[Subclasses(JsonEntity)]

    def Push(self, fields:List[QueryField]):

        cfg = readconfig(self.config)
        orion_url = cfg['orion']['url']

        e:JsonEntity
        for e in self.entities:
            entity = e.Generate(fields)
            if entity is not None:
                print(f"orion.push_data_to_orion(orion_url={orion_url}, entity_data={entity}, fiware_service={self.service}, fiware_servicepath={self.service_path})")
                orion.push_data_to_orion(orion_url=orion_url, entity_data=entity, fiware_service=self.service, fiware_servicepath=self.service_path)

    def PushSchema(self, fields:List[QueryField]):

        cfg = readconfig(self.config)
        orion_url = cfg['orion']['url']
        qlurl = cfg['quantumleap']['url']
        e:FiwareEntity
        for e in self.entities:
            if e.subscribe:
                orion.create_subscription_to_quantumleap(orion_url=orion_url, entity_types=[e.entitytype], fiware_service=self.service, fiware_servicepath=self.service_path, quantumleap_url=qlurl, entity_idpattern=e.entityid)


class IdsMapping(DataMapping):
    type: Literal["ids"]
    data_resource_title: str
    config: str
    entities: List[Subclasses(JsonEntity)]
    def Push(self, fields:List[QueryField]):
        cfg = readconfig(self.config)
        idsip = cfg["ip"]
        idsport = cfg["port"]
        idsname = cfg["ids_name"]
        username = cfg["username"]
        password = cfg["password"]

        res = ids_lib.IDSResource(ids_ip=idsip, ids_port=idsport, ids_name=idsname, data_resource_title=self.data_resource_title, username=username, password=password)

        e:FiwareEntity
        for e in self.entities:
            entity = e.Generate(fields)
            if entity is not None:
                res.update_artifact(e.entityid, entity)

    def PushSchema(self, fields:List[QueryField]):
        cfg = readconfig(self.config)
        idsip = cfg["ip"]
        idsport = cfg["port"]
        idsname = cfg["ids_name"]
        username = cfg["username"]
        password = cfg["password"]


        res = ids_lib.IDSResource(ids_ip=idsip, ids_port=idsport, ids_name=idsname, data_resource_title=self.data_resource_title, username=username, password=password)
        res.create_data_resource()

        entity:FiwareEntity
        for entity in self.entities:
            res.create_artifact(entity.entityid, entity.GenerateDefault(fields))


class BasicGroup(BaseModel):
    ...


DataGroup = ForwardRef("DataGroup")


class DataGroup(BasicGroup):
    type: str
    service_path: Optional[str] = None
    mappings: List[Subclasses(DataMapping)]
    queries: List[Subclasses(Query)]
    fields: List[QueryField]
    def GetFields(self, querylist:Optional[List[str]]):
        ...

    def PushAllMappings(self, querylist:Optional[List[str]]):
        self.GetFields(querylist)
        m:DataMapping
        for m in self.mappings:
            m.Push(self.fields)

    def PushSchema(self):
        m:DataMapping
        for m in self.mappings:
            m.PushSchema(self.fields)


class SubGroup(DataGroup):
    type: Literal["subgroup"]
    name: str

    def GetQueryByName(self, queryname: str) -> Optional[Query]:
        q: Query
        for q in self.queries:
            if q.name == queryname:
                return q
        return None

    def ExecuteQuery(self, queryname: str) -> QueryResult:
        q: Query = self.GetQueryByName(queryname)
        return q.Execute()

    def GetMappedResult(self, queryname: str):
        qr: QueryResult = self.ExecuteQuery(queryname)

    def GetFields(self, querylist:Optional[List[str]] = None):
        queryresults: dict[str, QueryResult] = dict()
        q: Query
        for q in self.queries:
            if querylist is None or q.name in querylist:
                qr:QueryResult = q.Execute()
                queryresults[q.name] = qr

        f: QueryField
        for f in self.fields:
            if querylist is None or f.query in querylist:
                f.value = queryresults[f.query].GetValueByName(f.address)

DataGroup.model_rebuild()




class QueryScheduleGroup(BaseModel):
    querynames: List[str]
    refreshinterval: int


class Provider(BaseModel):
    type:Literal["provider"]
    groups:List[Subclasses(DataGroup)]

    def getqueryschedulegroups(self):
        g:DataGroup
        d:dict = dict()
        for g in self.groups:
            q: Query
            for q in g.queries:
                if q.active:
                    if q.refreshinterval in d.keys():
                        d[q.refreshinterval].append(q)
                    else:
                        d[q.refreshinterval] = list([q])
        rval:List[QueryScheduleGroup] = list()

        for k in d.keys():
            rval.append(QueryScheduleGroup(refreshinterval=k, querynames=[q.name for q in d[k]]))

        return rval

    def evaluatefields(self, querylist:Optional[List[str]]):
        g:DataGroup
        for g in self.groups:
            g.GetFields(querylist)

    def getmappings(self, mappingtype:str = None):
        x = list()

        g:DataGroup
        for g in self.groups:
            m:DataMapping
            for m in g.mappings:
                if mappingtype is None or m.type == mappingtype:
                    e:Entity
                    for e in m.entities:
                        d: dict = e.Generate(g.fields)
                        if d is not None:
                            x.append(d)
        return x

    def Push(self, querylist:Optional[List[str]]):
        g: DataGroup
        for g in self.groups:
            g.PushAllMappings(querylist)

    def PushSchema(self):
        g: DataGroup
        for g in self.groups:
            g.PushSchema()