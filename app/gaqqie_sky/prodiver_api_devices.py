from datetime import datetime
from decimal import Decimal
import json
import os

import boto3


def _to_update_expression(provider_record: dict) -> str:
    update_expression_parts = []
    for key in provider_record.keys():
        if key == "status":
            update_expression_parts.append("#" + key + "=:" + key)
        else:
            update_expression_parts.append(key + "=:" + key)

    update_expression = "set " + ", ".join(update_expression_parts)
    return update_expression


def _to_expression_attribute_names(provider_record: dict) -> str:
    expression_attribute_names = {}
    for key in provider_record.keys():
        if key == "status":
            expression_attribute_names["#" + key] = key

    return expression_attribute_names


def _to_expression_attribute_values(provider_record: dict) -> dict:
    expression_attribute_values = {}
    for key, value in provider_record.items():
        if key in ["provider_name", "status", "description"]:
            expression_attribute_values[":" + key] = value
        else:
            expression_attribute_values[":" + key] = Decimal(value)

    return expression_attribute_values


def register_device(event, context):
    # get device from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    device_table_name = os.environ["DYNAMODB_TABLE_DEVICE"]
    device_table = dynamodb.Table(device_table_name)

    device_record = {
        "name": "qiskit_simulator",
        "provider_name": "gaqqie",
        "status": "ACTIVE",
        "description": "",
        "num_qubits": 10,
        "max_shots": 1024,
    }
    device_table.put_item(Item=device_record)

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
    dynamodb = boto3.resource("dynamodb")
    device_table_name = os.environ["DYNAMODB_TABLE_DEVICE"]
    device_table = dynamodb.Table(device_table_name)

    device_record = {
        "provider_name": provider_name,
        "status": status,
        "description": description,
        "num_qubits": num_qubits,
        "max_shots": max_shots,
    }
    device_table.update_item(
        Key={
            "name": name,
        },
        UpdateExpression=_to_update_expression(device_record),
        ExpressionAttributeNames=_to_expression_attribute_names(device_record),
        ExpressionAttributeValues=_to_expression_attribute_values(device_record),
        ReturnValues="UPDATED_NEW",
    )

    # return response
    response = {
        "statusCode": 200,
    }
    return response
