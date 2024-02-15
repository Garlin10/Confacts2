import orion
import pelda1


orion = orion.Orion()
describer = pelda1.ConfigOperator("configs_receiver")
ids = describer.getURNs()
for id in ids:
    print('create_receiver:\t\t', id, '\t', orion.createEntity(id=id, config_path="configs_receiver"))
describer = pelda1.ConfigOperator("configs")
ids = describer.getURNs()
for id in ids:
    print('create:\t\t', id, '\t', orion.createEntity(id=id))

    



