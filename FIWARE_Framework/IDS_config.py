
import json

class IDS_config():
    def __init__(self):
        
        self.config = self.read_config_file("./IDS_config.json")
        self.IP = self.config["IP"]
        self.USER = self.config["USER"]
        self.PASS = self.config["PASS"]
        self.COMPANY = self.config["COMPANY"]
    def read_config_file(self, file_path):
        with open(file_path, 'r') as config_file:
            config_data = json.load(config_file)
        return config_data