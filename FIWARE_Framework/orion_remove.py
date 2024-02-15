import orion
import pelda1


orion = orion.Orion()
describer = pelda1.ConfigOperator()

services = describer.getServices()
servicePaths = describer.getServicePaths()


for service, servicePath in zip(services, servicePaths):
    print('remove:', orion.deleteAllEntity(service=service, servicePath=servicePath))
    print('\tservice:\t', service)
    print('\tservicePath:\t', servicePath)

#print('remove:', orion.deleteAllEntity(service='ProductionLine', servicePath='/pbn/amlab/sif400'))