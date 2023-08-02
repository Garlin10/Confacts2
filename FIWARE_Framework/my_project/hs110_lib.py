import json
import socket
from struct import pack
from jsonpath_ng.ext import parse


class Hs110():
    def __init__(self, ip, port=9999):
        self.ip = ip
        self.port = port

        self.commands = {'info'     : '{"system":{"get_sysinfo":{}}}',
                        'on'       : '{"system":{"set_relay_state":{"state":1}}}',
                        'off'      : '{"system":{"set_relay_state":{"state":0}}}',
                        'cloudinfo': '{"cnCloud":{"get_info":{}}}',
                        'wlanscan' : '{"netif":{"get_scaninfo":{"refresh":0}}}',
                        'time'     : '{"time":{"get_time":{}}}',
                        'schedule' : '{"schedule":{"get_rules":{}}}',
                        'countdown': '{"count_down":{"get_rules":{}}}',
                        'antitheft': '{"anti_theft":{"get_rules":{}}}',
                        'reboot'   : '{"system":{"reboot":{"delay":1}}}',
                        'reset'    : '{"system":{"reset":{"delay":1}}}',
                        'energy'   : '{"emeter":{"get_realtime":{}}}'
                        }
        self.energyCommandXPath = {
            '1.0':{ 'current_a':{'path':'$.emeter.get_realtime.current', 'conversation': 1}, 
                    'voltage_v':{'path':'$.emeter.get_realtime.voltage', 'conversation': 1}, 
                    'power_w':{'path':'$.emeter.get_realtime.power', 'conversation': 1},
                    'total_wh':{'path':'$.emeter.get_realtime.total', 'conversation': 1}
                    },
            '2.0':{ 'current_a':{'path':'$.emeter.get_realtime.current_ma', 'conversation': 0.001}, 
                    'voltage_v':{'path':'$.emeter.get_realtime.voltage_mv', 'conversation': 0.001}, 
                    'power_w':{'path':'$.emeter.get_realtime.power_mw', 'conversation': 0.001},
                    'total_wh':{'path':'$.emeter.get_realtime.total_wh', 'conversation': 1}
                    }
        }

        self.infoCommandXPath = {
            'sw_ver':'$.system.get_sysinfo.sw_ver',
            'hw_ver':'$.system.get_sysinfo.hw_ver',
            'mac':'$.system.get_sysinfo.mac',
            'rssi':'$.system.get_sysinfo.rssi',
            'model':'$.system.get_sysinfo.model',
            'deviceId':'$.system.get_sysinfo.deviceId',
            'hwId':'$.system.get_sysinfo.hwId',
            'fwId':'$.system.get_sysinfo.fwId',
            'oemId':'$.system.get_sysinfo.oemId',
            'alias':'$.system.get_sysinfo.alias',
            'dev_name':'$.system.get_sysinfo.dev_name',
            'relay_state':'$.system.get_sysinfo.relay_state',
            'on_time':'$.system.get_sysinfo.on_time',
        }

        self.energyCommands = [i for i in self.energyCommandXPath['2.0']]
        self.infoCommands = [i for i in self.infoCommandXPath]
        self.allCommands = list()

        self.allCommands.extend(self.energyCommands)
        self.allCommands.extend(self.infoCommands)
        
        try:
            self.hw_ver = self._getRawData('info')['system']['get_sysinfo']['hw_ver']
        except:
            self.hw_ver = None

    def _int_to_bytes(self, x):
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')

    def _encrypt(self, string):
        key = 171
        result = pack('>I', len(string))
        for i in string:
            a = key ^ ord(i)
            key = a
            result += self._int_to_bytes(a)
        return result

    def _decrypt(self, string):
        key = 171
        result = ""
        for i in string:
            a = key ^ i
            key = i
            result += chr(a)
        return result

    def _query(self, cmd):
        try:
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.connect((self.ip, self.port))
            sock_tcp.send(self._encrypt(cmd))
            data = sock_tcp.recv(2048)
            sock_tcp.close()
            return(self._decrypt(data[4:]))
        except socket.error:
            return None
            quit("Cound not connect to host " + self.ip + ":" + str(self.port))
            return("Cound not connect to host " + ip + ":" + str(port))
    def getConnection(self):
        try:
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.connect((self.ip, self.port))
            sock_tcp.close()
            return(True)
        except:
            return False
            

    def _getRawData(self, command):
        cmd = self.commands[command]
        res_raw = self._query(cmd)
        if res_raw == None:
            return None
        res = json.loads(res_raw)
        return res

    def _getEnergyValue(self, data, command):
        try:
            #res = self.getRawData('energy')
            xpath = self.energyCommandXPath[self.hw_ver][command]['path']
            jsonpath_expression = parse(xpath)
            match = jsonpath_expression.find(data)
            value = match[0].value
            return value * self.energyCommandXPath[self.hw_ver][command]['conversation']
        except:
            return None
    
    def _getInfoValue(self, data, command):
        try:
            #res = self.getRawData('info')
            xpath = self.infoCommandXPath[command]
            jsonpath_expression = parse(xpath)
            match = jsonpath_expression.find(data)
            value = match[0].value
            return value
        except:
            return None

    def getValue(self, command):
            if command in self.energyCommands:
                data = self._getRawData('energy')
                return self._getEnergyValue(data, command)
            elif command in self.infoCommands:   
                data = self._getRawData('info')   
                return self._getInfoValue(data, command)            
            else:
                pass


    def getBatchValues(self, commandList):

        data = {
                'energy': self._getRawData('energy'),
                'info': self._getRawData('info')
                }
        res = list()

        for command in commandList:
            #print(command)
            if command not in self.allCommands:
                res.append(None)
            elif command in self.energyCommands:
                res.append(self._getEnergyValue(data['energy'], command))
            elif command in self.infoCommands:
                res.append(self._getInfoValue(data['info'], command))       
            else:
                pass

        return res

        


if __name__ == '__main__':

    for i in ['192.168.1.16', '192.168.1.17']:
        powermeter = Hs110(ip=i)
        print(f'ip:\t\t {i}')
        print('alias:\t\t', powermeter.getValue('alias'))
        print('hw_ver:\t\t', powermeter.getValue('hw_ver'))
        print('power_w:\t', powermeter.getValue('power_w'))
        print('total_wh:\t', powermeter.getValue('total_wh'))
        print('batch:\t\t', powermeter.getBatchValues(['alias', 'power_w', 'hw_ver']))
        print()





