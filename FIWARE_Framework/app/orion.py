import requests
import json


import requests
import json


def push_data_to_orion(orion_url, entity_data, fiware_service, fiware_servicepath):
    """
    Push or update data to FIWARE Orion Context Broker with support for Fiware-Service and Fiware-ServicePath headers.
    This function creates the entity if it doesn't exist and updates it if it already exists.

    Parameters:
    - orion_url: URL of the Orion Context Broker instance.
    - entity_data: A dictionary containing the data of the entity to be created or updated.
    - fiware_service: The name of the Fiware-Service (tenant) under which the entity is categorized.
    - fiware_servicepath: The service path within the Fiware-Service for hierarchical organization.
    """
    headers = {
        "Content-Type": "application/json",
        "Fiware-Service": fiware_service,
        "Fiware-ServicePath": fiware_servicepath
    }
    # Append the 'options=upsert' query parameter to enable upsert functionality
    response = requests.post(f"{orion_url}/v2/entities?options=upsert",
                             data=json.dumps(entity_data), headers=headers)

    if response.status_code in [201, 204]:
        print("Entity created or updated successfully")
    else:
        print("Error:", response.text)


def get_data_from_orion(orion_url, entity_id, fiware_service, fiware_servicepath):
    """
    Get data from FIWARE Orion Context Broker for a specific entity ID, with Fiware-Service and Fiware-ServicePath support.

    Parameters:
    - orion_url: URL of the Orion Context Broker instance.
    - entity_id: ID of the entity to query.
    - fiware_service: The name of the Fiware-Service (tenant) under which the entity is categorized.
    - fiware_servicepath: The service path within the Fiware-Service for hierarchical organization.
    """
    headers = {
        "Accept": "application/json",
        "Fiware-Service": fiware_service,
        "Fiware-ServicePath": fiware_servicepath
    }
    response = requests.get(
        f"{orion_url}/v2/entities/{entity_id}", headers=headers)

    if response.status_code == 200:
        entity_data = response.json()
        print("Entity data:", entity_data)
    else:
        print("Error:", response.text)


def create_subscription_to_quantumleap(orion_url, fiware_service, fiware_servicepath, entity_types, quantumleap_url, entity_idpattern =".*"):
    """
    Create a subscription in Orion Context Broker for notifying QuantumLeap about changes to entities of a specific type.

    Parameters:
    - orion_url: URL of the Orion Context Broker instance.
    - fiware_service: The name of the Fiware-Service (tenant) under which the entity is categorized.
    - fiware_servicepath: The service path within the Fiware-Service for hierarchical organization.
    - entity_type: Type of the entities to subscribe to.
    - quantumleap_url: URL of the QuantumLeap instance to notify.
    """
    subscription_data = {
        "description": f"Notify QuantumLeap of changes to entities",
        "subject": {
            "entities": [
                {
                    "idPattern": entity_idpattern,
                    "type": entity_type
                } for entity_type in entity_types
            ],
            "condition": {
                "attrs": []
            }
        },
        "notification": {
            "http": {
                "url": quantumleap_url
            },
            "attrs": []
        },
        "expires": "2040-01-01T14:00:00.00Z",
        "throttling": 1
    }

    headers = {
        "Content-Type": "application/json",
        "Fiware-Service": fiware_service,
        "Fiware-ServicePath": fiware_servicepath
    }

    print (subscription_data)
    response = requests.post(f"{orion_url}/v2/subscriptions",
                             data=json.dumps(subscription_data), headers=headers)

    if response.status_code == 201:
        print("Subscription created successfully")
    else:
        print("Error:", response.text)


if __name__ == '__main__':
    orion_url = "http://192.168.1.200:1026"
    fiware_service = "your_service"
    fiware_servicepath = "/your_servicepath"
    entity_type = "Room"
    quantumleap_url = "http://192.168.1.200:8668/v2/notify"

    #create_subscription_to_quantumleap(orion_url, fiware_service, fiware_servicepath, entity_type, quantumleap_url)

    # Example data to push
    entity_data = {
        "id": "Room1",
        "type": "Room",
        "humidity": {
            "value": 14.4,
            "type": "Number"
        },
        "temperature": {
            "value": 12.4,
            "type": "Number"
        }
    }

    # Pushing data to Orion (which QuantumLeap will then process)
    push_data_to_orion(orion_url, entity_data,
                       fiware_service, fiware_servicepath)

    # Getting data
    get_data_from_orion(orion_url, "Room1", fiware_service, fiware_servicepath)
