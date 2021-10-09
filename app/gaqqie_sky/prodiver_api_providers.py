import json
import os

from gaqqie_sky.resource import db


def register_provider(event, context):
    provider_record = {
        "name": "gaqqie",
        "status": "ACTIVE",
        "description": "a provider for test",
    }
    db.insert(os.environ["DYNAMODB_TABLE_PROVIDER"], provider_record)

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
    provider_record = {
        "status": status,
        "description": description,
    }
    db.update(os.environ["DYNAMODB_TABLE_PROVIDER"], {"name": name}, provider_record)

    # return response
    response = {
        "statusCode": 200,
    }
    return response
