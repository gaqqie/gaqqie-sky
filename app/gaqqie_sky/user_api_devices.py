import json

from gaqqie_sky.resource import db
from gaqqie_sky.resource import queue
from gaqqie_sky.resource import storage
import gaqqie_sky.resource.name_resolver as resolver


def get_devices(event: dict, context: "LambdaContext") -> dict:
    """get device informations.

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
    print(f"event={event}")

    # get device from database
    device_records = db.find_all(resolver.table_device())

    # return response
    responce_data = []
    for device_record in device_records:
        queue_name = resolver.queue_device(device_record["name"])
        queue_obj = queue.get_queue(queue_name)

        data = {
            "name": device_record["name"],
            "provider_name": device_record["provider_name"],
            "status": device_record["status"],
            "description": device_record["description"],
            "num_qubits": int(device_record["num_qubits"]),
            "max_shots": int(device_record["max_shots"]),
            "queued_jobs": int(queue_obj.attributes["ApproximateNumberOfMessages"]),
        }
        responce_data.append(data)
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response


def get_device_by_name(event: dict, context: "LambdaContext") -> dict:
    """get specific device information.

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
    print(f"event={event}")

    # parse request
    device_name = event["pathParameters"]["name"]

    # get device from database
    device_record = db.find_by_id(
        resolver.table_device(), device_name, key_field_name="name"
    )

    # get provider from strage
    details = storage.get(
        resolver.storage_bucket_provider(),
        resolver.storage_key_device(device_record["provider_name"], device_name),
    )

    # return response
    if device_record:
        queue_name = resolver.queue_device(device_record["name"])
        queue_obj = queue.get_queue(queue_name)

        responce_data = {
            "name": device_record["name"],
            "provider_name": device_record["provider_name"],
            "status": device_record["status"],
            "description": device_record["description"],
            "num_qubits": int(device_record["num_qubits"]),
            "max_shots": int(device_record["max_shots"]),
            "queued_jobs": int(queue_obj.attributes["ApproximateNumberOfMessages"]),
            "details": details,
        }
        response = {
            "statusCode": 200,
            "body": json.dumps(responce_data),
        }
    else:
        # specified record doesn't exist
        response = {
            "statusCode": 200,
        }
    print(f"response={response}")
    return response
