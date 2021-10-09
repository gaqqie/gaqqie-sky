import json
import os

from gaqqie_sky.resource import db


def get_providers(event, context):
    print(f"event={event}")

    # get provider from DynamoDB
    provider_records = db.find_all(os.environ["DYNAMODB_TABLE_PROVIDER"])

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
    provider_record = db.find_by_id(
        os.environ["DYNAMODB_TABLE_PROVIDER"], provider_name, key_field_name="name"
    )

    # return response
    if provider_record:
        # construct response data
        responce_data = {
            "name": provider_record["name"],
            "status": provider_record["status"],
            "description": provider_record["description"],
        }
        response = {
            "statusCode": 200,
            "body": json.dumps(responce_data),
        }
    else:
        response = {
            "statusCode": 200,
        }
    print(f"response={response}")
    return response
