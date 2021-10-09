import json
import os

from gaqqie_sky.resource import db
from gaqqie_sky.resource import queue


def get_devices(event, context):
    print(f"event={event}")

    # get device from DynamoDB
    device_records = db.find_all(os.environ["DYNAMODB_TABLE_DEVICE"])

    # return response
    responce_data = []
    for device_record in device_records:
        queue_name = os.environ["SQS_QUEUE_PREFIX"] + device_record["name"] + ".fifo"
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


def get_device_by_name(event, context):
    print(f"event={event}")

    # parse request
    device_name = event["pathParameters"]["name"]

    # get device from DynamoDB
    device_record = db.find_by_id(
        os.environ["DYNAMODB_TABLE_DEVICE"], device_name, key_field_name="name"
    )

    # return response
    if device_record:
        queue_name = os.environ["SQS_QUEUE_PREFIX"] + device_record["name"] + ".fifo"
        queue_obj = queue.get_queue(queue_name)

        responce_data = {
            "name": device_record["name"],
            "provider_name": device_record["provider_name"],
            "status": device_record["status"],
            "description": device_record["description"],
            "num_qubits": int(device_record["num_qubits"]),
            "max_shots": int(device_record["max_shots"]),
            "queued_jobs": int(queue_obj.attributes["ApproximateNumberOfMessages"]),
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
