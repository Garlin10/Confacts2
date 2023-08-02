from opcua import Client


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
        resList = list()
        try:
            client = Client(self.opcuaServer, self.timeout)
            client.connect()
            for i in nodeIdList:
                node = client.get_node(i)
                value = node.get_value()
                resList.append(value)
            client.disconnect()
            return resList
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
    def getNodes(self):
        try:
            client = Client(self.opcuaServer, self.timeout)
            client.connect()
            print(client.get_root_node().get_children()[0].get_children()[1].get_children())
            client.disconnect()
            return True
        except:
            return False
if __name__ == '__main__':
    sif400 = Opcua(opcuaServer="opc.tcp://192.168.1.250:4840")
    print(sif400.getConnection())
    sif400.getNodes()
    print(sif400.getBatchValue(nodeIdList=['s=RootNode_Ciklusido']))
    #print(sif400.getBatchValue(nodeIdList=['ns=6;s=::AsGlobalPV:MESPAEA_rActivePower', 'ns=6;s=::AsGlobalPV:MESPAEA_rAir']))
