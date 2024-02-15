from opcua import Client
import json


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
            print(client.get_root_node().get_children()
                  [0].get_children()[1].get_children())
            client.disconnect()
            return True
        except:
            return False


if __name__ == '__main__':
    def find_in_json(data, key_name):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == key_name:
                    return value
                elif isinstance(value, (dict, list)):
                    result = find_in_json(value, key_name)
                    if result is not None:
                        return result
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    result = find_in_json(item, key_name)
                    if result is not None:
                        return result
        return None
    # Read the content of the JSON file
    with open("configs/example_provider_config.json", 'r') as file:
        config_json = file.read()

    # Parse the JSON
    config = json.loads(config_json)

    # Dynamically find the URL
    url = find_in_json(config, "url")
    nodeId = find_in_json(config, "nodeId")
    if url:
        print(url)
        print(nodeId)
        opcua_test = Opcua(opcuaServer=url)
        print(opcua_test.getConnection())
        opcua_test.getNodes()
        print(opcua_test.getBatchValue(nodeIdList=[nodeId]))
    else:
        print("URL not found in the JSON file.")
