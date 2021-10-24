import json

from gaqqie_sky.resource import db
from gaqqie_sky.resource import storage
import gaqqie_sky.resource.name_resolver as resolver


def register_device(event: dict, context: "LambdaContext") -> dict:
    """register device information.

    Parameters
    ----------
    event : dict
        event object.
    context : LambdaContext
        context object.

    Returns
    -------
    dict
        dict corresponding to http response.
    """
    device_record = {
        "name": "qiskit_simulator",
        "provider_name": "gaqqie",
        "status": "ACTIVE",
        "description": "",
        "num_qubits": 10,
        "max_shots": 1024,
    }
    db.insert(resolver.table_device(), device_record)

    # update details on storage
    storage.put(
        resolver.storage_bucket_device(),
        resolver.storage_key_device("gaqqie", "qiskit_simulator"),
        "{}",
    )

    # return response
    response = {
        "statusCode": 200,
    }
    return response


def update_device(event: dict, context: "LambdaContext") -> dict:
    """update device information.

    If the device does not exist, registers it.

    Parameters
    ----------
    event : dict
        event object.
    context : LambdaContext
        context object.

    Returns
    -------
    dict
        dict corresponding to http response.
    """
    # parse request
    name = event["pathParameters"]["name"]
    request_data = json.loads(event["body"])
    provider_name = request_data["provider_name"]
    status = request_data["status"]
    description = request_data["description"]
    num_qubits = request_data["num_qubits"]
    max_shots = request_data["max_shots"]

    # update to database
    device_record = {
        "provider_name": provider_name,
        "status": status,
        "description": description,
        "num_qubits": num_qubits,
        "max_shots": max_shots,
    }
    db.update(resolver.table_device(), {"name": name}, device_record)

    # update details on storage
    if "details" in request_data:
        storage.put(
            resolver.storage_bucket_device(),
            resolver.storage_key_device(provider_name, name),
            request_data["details"],
        )

    # return response
    response = {
        "statusCode": 200,
    }
    return response
