import orion
import pelda1

orion = orion.Orion()
describer = pelda1.ConfigOperator()
describer_receiver = pelda1.ConfigOperator("configs_receiver")



ids = describer.getURNs()
ids_receiver = describer_receiver.getURNs()
for id in ids:
    subscribe = describer.getAttributesByName(id, 'subscribe')
    if type(subscribe) == bool:
        if describer.getAttributesByName(id, 'subscribe'):
            print('quantumleap subscription:\t', orion.subscribeLongTermDatabase(id))
    elif type(subscribe) == str:
        if describer.getAttributesByName(id, 'subscribe').lower() == 'true':
            print('quantumleap subscription:\t', orion.subscribeLongTermDatabase(id))
for id in ids_receiver:
    subscribe = describer_receiver.getAttributesByName(id, 'subscribe')
    if type(subscribe) == bool:
        if describer_receiver.getAttributesByName(id, 'subscribe'):
            print('quantumleap subscription:\t', orion.subscribeLongTermDatabase(id, "configs_receiver"))
    elif type(subscribe) == str:
        if describer_receiver.getAttributesByName(id, 'subscribe').lower() == 'true':
            print('quantumleap subscription:\t', orion.subscribeLongTermDatabase(id, "configs_receiver"))


