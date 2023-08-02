import orion
import pelda1


orion = orion.Orion()
describer = pelda1.ConfigOperator()

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
print('ids', ids)
idsByIntervalsAndUrls = separateIds(ids)


for refreshInterval in idsByIntervalsAndUrls:
    for url in idsByIntervalsAndUrls[refreshInterval]:
        ids = idsByIntervalsAndUrls[refreshInterval][url]
        #print('refresh:\t', ids)
        print('batch update:')
        print('ids:\t', ids)
        print('res:\t', orion.updateBatchValues(ids=ids))
        print()



