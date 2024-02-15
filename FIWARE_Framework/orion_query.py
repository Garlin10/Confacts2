import orion
import pelda1

orion = orion.Orion()
describer = pelda1.ConfigOperator()


services = describer.getServices()
servicePaths = describer.getServicePaths()

for service, servicePath in zip(services, servicePaths):
    print('service:\t', service, '\nservicePath:\t', servicePath)
    print('query:\t\t', orion.queryEntity(service=service, servicePath=servicePath))
    print()



