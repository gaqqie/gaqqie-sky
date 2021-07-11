from datetime import datetime
from decimal import Decimal
import json
import os

import boto3


def register_device(event, context):
    # get device from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    device_table_name = os.environ["DYNAMODB_TABLE_DEVICE"]
    device_table = dynamodb.Table(device_table_name)

    device_record = {
        "name": "qiskit_simulator",
        "provider_name": "gaqqie",
        "status": "ACTIVE",
        "num_qubits": 10,
        "max_shots": 1024,
        "queued_jobs": 10,
    }
    device_table.put_item(Item=device_record)

    # return response
    response = {
        "statusCode": 200,
    }
    return response
