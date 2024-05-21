import datetime

from fastapi import FastAPI
import schedule
import threading
import time
import uvicorn
import logging
import os
app = FastAPI()

import configmodel

from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.access")
def job():
    logging.info("Job started.")
    try:
        #Insert your scheduled job here!
        print("Job is running at the moment")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        logging.info("Job finished.")

def cfjob(modelpath:str, querylist:List[str]):
    print (f"{datetime.datetime.now()} -- Executing {modelpath} with queries {querylist}")
    model:configmodel.Provider = configmodel.Provider.parse_file(modelpath)
    model.Push(querylist)
    print (f"{datetime.datetime.now()} -- Finished executing {modelpath} with queries {querylist}")

class SchedulerThread(threading.Thread):
    @classmethod
    def run(cls):
        while True:
            schedule.run_pending()
            time.sleep(1)

scheduler_thread = SchedulerThread()

def getconfigfiles(configpath:str = "./configs/models"):
    files = os.listdir(configpath)
    filenames = [configpath + "/" + f for f in files if  os.path.isfile(configpath + "/" +f)]
    return filenames


@app.get("/start")
def start_scheduling():
    if not schedule.jobs:

        configfiles = getconfigfiles()
        for cf in configfiles:
            model:configmodel.Provider = configmodel.Provider.parse_file(cf)
            qsgs = model.getqueryschedulegroups()
            qsq:configmodel.QueryScheduleGroup
            for qsg in qsgs:
                print (f"Scheduling query group {qsg.querynames} to run every {qsg.refreshinterval} seconds")
                schedule.every(qsg.refreshinterval).seconds.do(cfjob, cf, qsg.querynames)

        if not scheduler_thread.is_alive():
            scheduler_thread.start()
        return {"message": "Scheduling started."}
    return {"message": "Scheduling is already running."}

@app.get("/createschemas")
def createschemas():
    configfiles = getconfigfiles()
    for cf in configfiles:
        model: configmodel.Provider = configmodel.Provider.parse_file(cf)
        model.PushSchema()

@app.get("/stop")
def stop_scheduling():
    schedule.clear()
    return {"message": "Scheduling stopped."}

@app.get("/status")
def is_scheduling_running():
    return {"running": bool(schedule.jobs)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")