import schedule
import time
from IDS_To_Fiware import IDS_To_Fiware
from functools import partial

class IDS_Agent():
    def __init__(self):    
        self.to_fiware = IDS_To_Fiware()
        
    def job(self, episode):
        tmp = self.to_fiware.test(episode)
        print(tmp)
        try:
            print(self.to_fiware.orion_send(tmp))
        except:
            print("Orion error")
            
    def generate_jobs(self, memory):
        for episode in memory:
            interval = episode["refreshInterval"]
            schedule.every(interval).seconds.do(partial(self.job, episode))
            
if __name__ == "__main__":
    agent = IDS_Agent()
    agent.generate_jobs(agent.to_fiware.init.memory)
    while True:
        schedule.run_pending()
        time.sleep(1)
