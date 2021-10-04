import json
import os

import boto3


def get_devices(event, context):
    print(f"event={event}")

    # get device from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    device_table_name = os.environ["DYNAMODB_TABLE_DEVICE"]
    device_table = dynamodb.Table(device_table_name)
    dynamodb_response = device_table.scan()
    device_records = dynamodb_response["Items"]
    print(f"device_records={device_records}")

    sqs = boto3.resource("sqs")

    # return response
    responce_data = []
    for device_record in device_records:
        queue_name = os.environ["SQS_QUEUE_PREFIX"] + device_record["name"] + ".fifo"
        print(f"queue_name={queue_name}")
        queue = sqs.get_queue_by_name(QueueName=queue_name)

        data = {
            "name": device_record["name"],
            "provider_name": device_record["provider_name"],
            "status": device_record["status"],
            "description": device_record["description"],
            "num_qubits": int(device_record["num_qubits"]),
            "max_shots": int(device_record["max_shots"]),
            "queued_jobs": int(queue.attributes["ApproximateNumberOfMessages"]),
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
    dynamodb = boto3.resource("dynamodb")
    device_table_name = os.environ["DYNAMODB_TABLE_DEVICE"]
    device_table = dynamodb.Table(device_table_name)
    dynamodb_response = device_table.get_item(Key={"name": device_name})
    device_record = dynamodb_response["Item"]
    print(f"device_record={device_record}")

    # get queue from SQS
    sqs = boto3.resource("sqs")
    queue_name = os.environ["SQS_QUEUE_PREFIX"] + device_record["name"] + ".fifo"
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    # return response
    responce_data = {
        "name": device_record["name"],
        "provider_name": device_record["provider_name"],
        "status": device_record["status"],
        "description": device_record["description"],
        "num_qubits": int(device_record["num_qubits"]),
        "max_shots": int(device_record["max_shots"]),
        "queued_jobs": int(queue.attributes["ApproximateNumberOfMessages"]),
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response
