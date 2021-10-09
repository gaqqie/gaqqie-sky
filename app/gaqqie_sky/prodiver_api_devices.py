import json
import os

from gaqqie_sky.resource import db


def register_device(event, context):
    device_record = {
        "name": "qiskit_simulator",
        "provider_name": "gaqqie",
        "status": "ACTIVE",
        "description": "",
        "num_qubits": 10,
        "max_shots": 1024,
    }
    db.insert(os.environ["DYNAMODB_TABLE_DEVICE"], device_record)

    # return response
    response = {
        "statusCode": 200,
    }
    return response


def update_device(event, context):
    # parse request
    name = event["pathParameters"]["name"]
    request_data = json.loads(event["body"])
    provider_name = request_data["provider_name"]
    status = request_data["status"]
    description = request_data["description"]
    num_qubits = request_data["num_qubits"]
    max_shots = request_data["max_shots"]

    # update to DynamoDB
    device_record = {
        "provider_name": provider_name,
        "status": status,
        "description": description,
        "num_qubits": num_qubits,
        "max_shots": max_shots,
    }
    db.update(os.environ["DYNAMODB_TABLE_DEVICE"], {"name": name}, device_record)

    # return response
    response = {
        "statusCode": 200,
    }
    return response
