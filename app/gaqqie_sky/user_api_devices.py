import json
import os

import boto3


def get_device_by_name(event, context):
    print(f"event={event}")

    # parse request
    device_name = event["pathParameters"]["name"]

    # get device from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    device_table_name = os.environ["DYNAMODB_TABLE_DEVICE"]
    device_table = dynamodb.Table(device_table_name)
    dynamodb_response = device_table.get_item(Key={"name": device_name})
    device_record = dynamodb_response["Item"]
    print(f"device_record={device_record}")

    # return response
    responce_data = {
        "name": device_record["name"],
        "provider_name": device_record["provider_name"],
        "status": device_record["status"],
        "num_qubits": int(device_record["num_qubits"]),
        "max_shots": int(device_record["max_shots"]),
        "queued_jobs": int(device_record["queued_jobs"]),
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response
