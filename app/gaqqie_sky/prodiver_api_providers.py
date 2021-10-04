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
    print(f"update_expression={update_expression}")
    return update_expression


def _to_expression_attribute_names(provider_record: dict) -> str:
    expression_attribute_names = {}
    for key in provider_record.keys():
        if key == "status":
            expression_attribute_names["#" + key] = key

    print(f"expression_attribute_names={expression_attribute_names}")
    return expression_attribute_names


def _to_expression_attribute_values(provider_record: dict) -> dict:
    expression_attribute_values = {}
    for key, value in provider_record.items():
        if key in ["status", "description"]:
            expression_attribute_values[":" + key] = value
        else:
            expression_attribute_values[":" + key] = Decimal(value)

    print(f"expression_attribute_values={expression_attribute_values}")
    return expression_attribute_values


def register_provider(event, context):
    # get provider from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    provider_table_name = os.environ["DYNAMODB_TABLE_PROVIDER"]
    provider_table = dynamodb.Table(provider_table_name)

    provider_record = {
        "name": "gaqqie",
        "status": "ACTIVE",
        "description": "a provider for test",
    }
    provider_table.put_item(Item=provider_record)

    # return response
    response = {
        "statusCode": 200,
    }
    return response


def update_provider(event, context):
    # parse request
    name = event["pathParameters"]["name"]
    request_data = json.loads(event["body"])
    status = request_data["status"]
    description = request_data["description"]

    # update to DynamoDB
    dynamodb = boto3.resource("dynamodb")
    provider_table_name = os.environ["DYNAMODB_TABLE_PROVIDER"]
    provider_table = dynamodb.Table(provider_table_name)

    provider_record = {
        "status": status,
        "description": description,
    }
    print(f"name={name}")
    print(f"provider_record={provider_record}")
    provider_table.update_item(
        Key={
            "name": name,
        },
        UpdateExpression=_to_update_expression(provider_record),
        ExpressionAttributeNames=_to_expression_attribute_names(provider_record),
        ExpressionAttributeValues=_to_expression_attribute_values(provider_record),
        ReturnValues="UPDATED_NEW",
    )

    # return response
    response = {
        "statusCode": 200,
    }
    return response
