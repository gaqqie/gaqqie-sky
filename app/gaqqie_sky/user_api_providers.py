import json
import os

import boto3


def get_providers(event, context):
    print(f"event={event}")

    # get device from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    provider_table_name = os.environ["DYNAMODB_TABLE_PROVIDER"]
    provider_table = dynamodb.Table(provider_table_name)
    dynamodb_response = provider_table.scan()
    provider_records = dynamodb_response["Items"]
    print(f"provider_record={provider_records}")

    # return response
    responce_data = []
    for provider_record in provider_records:
        data = {
            "name": provider_record["name"],
            "status": provider_record["status"],
            "description": provider_record["description"],
        }
        responce_data.append(data)
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response


def get_provider_by_name(event, context):
    print(f"event={event}")

    # parse request
    provider_name = event["pathParameters"]["name"]

    # get device from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    provider_table_name = os.environ["DYNAMODB_TABLE_PROVIDER"]
    provider_table = dynamodb.Table(provider_table_name)
    dynamodb_response = provider_table.get_item(Key={"name": provider_name})
    provider_record = dynamodb_response["Item"]
    print(f"provider_record={provider_record}")

    # return response
    responce_data = {
        "name": provider_record["name"],
        "status": provider_record["status"],
        "description": provider_record["description"],
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response
