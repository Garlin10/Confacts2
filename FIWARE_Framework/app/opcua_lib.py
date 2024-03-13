from opcua import Client
import logging

logging.getLogger('opcua').setLevel(logging.CRITICAL)
class Opcua():
    def __init__(self, opcuaServer):
        self.opcuaServer = opcuaServer
        self.timeout = 3

    def getValue(self, nodeId):
        client = Client(self.opcuaServer, self.timeout)
        client.connect()
        node = client.get_node(nodeId)
        value = node.get_value()
        client.disconnect()
        return value

    def getBatchValue(self, nodeIdList):
        rval = dict()
        try:
            client = Client(self.opcuaServer, self.timeout)
            client.connect()
            for i in nodeIdList:
                try:
                    node = client.get_node(i)
                    value = node.get_value()
                    rval[i] = value
                except:
                    ...
            client.disconnect()
            return rval
        except:
            return None
    def getConnection(self):
        try:
            client = Client(self.opcuaServer, self.timeout)
            client.connect()
            client.disconnect()
            return True
        except:
            return False

if __name__ == '__main__':
    sif400 = Opcua(opcuaServer="opc.tcp://130.130.130.1:4840")
    print(sif400.getConnection())
    #print(sif400.getBatchValue(nodeIdList=['ns=6;s=::AsGlobalPV:MESPAEA_rActivePower']))
    #print(sif400.getBatchValue(nodeIdList=['ns=6;s=::AsGlobalPV:MESPAEA_rActivePower', 'ns=6;s=::AsGlobalPV:MESPAEA_rAir']))
