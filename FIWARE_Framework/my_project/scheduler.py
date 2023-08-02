from apscheduler.schedulers.blocking import BlockingScheduler

import orion
import pelda1

orion = orion.Orion()
describer = pelda1.ConfigOperator()
sched = BlockingScheduler()


def update(ids:list):
    orion.updateBatchValues(ids=ids)

def separateIds(ids):
    idsByIntervalsAndUrls = dict()
    for id in ids:
        refreshInterval = str(describer.getAttributesByName(id, 'refreshInterval'))
        url = describer.getAttributesByName(id, 'url')

        if refreshInterval in idsByIntervalsAndUrls:
            if url in idsByIntervalsAndUrls[refreshInterval]:
                idsByIntervalsAndUrls[refreshInterval][url].append(id)
            else:
                idsByIntervalsAndUrls[refreshInterval][url] = [id]
        else:
            idsByIntervalsAndUrls[refreshInterval] = {url:[id]}    
    return idsByIntervalsAndUrls


ids = describer.getURNs()
idsByIntervalsAndUrls = separateIds(ids)
print('ids:\t', idsByIntervalsAndUrls)


for refreshInterval in idsByIntervalsAndUrls:
    #print(refreshInterval)
    for url in idsByIntervalsAndUrls[refreshInterval]:
        #print('\t', url)
        ids = idsByIntervalsAndUrls[refreshInterval][url]
        #print('\t\t', )
        #print('-->', ids)
        sched.add_job(update, args=[ids], trigger='interval', seconds=int(refreshInterval))


sched.start()



