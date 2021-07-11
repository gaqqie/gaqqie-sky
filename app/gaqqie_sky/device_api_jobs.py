from datetime import datetime
from decimal import Decimal
import json
import os

import boto3


def _to_update_expression(job_record: dict) -> str:
    update_expression_parts = []
    for key in job_record.keys():
        if key == "status":
            update_expression_parts.append("#" + key + "=:" + key)
        else:
            update_expression_parts.append(key + "=:" + key)

    update_expression = "set " + ", ".join(update_expression_parts)
    return update_expression


def _to_expression_attribute_names(job_record: dict) -> str:
    expression_attribute_names = {}
    for key in job_record.keys():
        if key == "status":
            expression_attribute_names["#" + key] = key

    return expression_attribute_names


def _to_expression_attribute_values(job_record: dict) -> dict:
    expression_attribute_values = {}
    for key, value in job_record.items():
        if key in ["status", "end_time"]:
            expression_attribute_values[":" + key] = value
        else:
            expression_attribute_values[":" + key] = Decimal(value)
    return expression_attribute_values


def receive_job(event, context):
    print(f"event={event}")

    # parse request
    device_name = event["pathParameters"]["device_name"]

    # receive a message from SQS
    sqs = boto3.resource("sqs")
    queue_name = os.environ["SQS_QUEUE_PREFIX"] + device_name + ".fifo"
    print(f"queue_name={queue_name}")
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    messages = queue.receive_messages(
        MessageAttributeNames=["job_id"],
        MaxNumberOfMessages=1,
    )
    if len(messages) == 0:
        # return response
        # TODO status code
        response = {
            "statusCode": 200,
        }
    else:
        # parse message
        message = messages[0]
        receipt_handle = message.receipt_handle
        # print(f"job_id={job_id}, receipt_handle={receipt_handle}")
        print(f"receipt_handle={receipt_handle}")
        print(f"attributes={message.attributes}")
        print(f"message_attributes={message.message_attributes}")
        print(f"message_id={message.message_id}")
        job_id = message.message_attributes["job_id"]["StringValue"]
        message.delete()

        # update to DynamoDB
        dynamodb = boto3.resource("dynamodb")
        job_table_name = os.environ["DYNAMODB_TABLE_JOB"]
        job_table = dynamodb.Table(job_table_name)
        job_record = {
            "status": "RUNNING",
        }
        job_table.update_item(
            Key={
                "id": job_id,
            },
            UpdateExpression=_to_update_expression(job_record),
            ExpressionAttributeNames=_to_expression_attribute_names(job_record),
            ExpressionAttributeValues=_to_expression_attribute_values(job_record),
            ReturnValues="UPDATED_NEW",
        )

        # return response
        response = {
            "statusCode": 200,
            "body": message.body,
        }

    print(f"response={response}")
    return response


def register_result(event, context):
    print(f"event={event}")

    # parse request
    job_id = event["pathParameters"]["job_id"]
    request_data = json.loads(event["body"])
    status = request_data["status"]
    results = request_data["results"]

    end_time = datetime.now().isoformat(timespec="milliseconds") + "Z"

    # store to S3
    s3 = boto3.client("s3")
    bucket_name = os.environ["S3_BUCKET_RESULT"]
    results_key = "organization/user/" + job_id + "/results.json"
    s3.put_object(
        Bucket=bucket_name,
        Key=results_key,
        Body=results,
        ContentType="text/html",
    )

    # update to DynamoDB
    dynamodb = boto3.resource("dynamodb")
    job_table_name = os.environ["DYNAMODB_TABLE_JOB"]
    job_table = dynamodb.Table(job_table_name)
    job_record = {
        "status": status,
        "end_time": end_time,
    }
    job_table.update_item(
        Key={
            "id": job_id,
        },
        UpdateExpression=_to_update_expression(job_record),
        ExpressionAttributeNames=_to_expression_attribute_names(job_record),
        ExpressionAttributeValues=_to_expression_attribute_values(job_record),
        ReturnValues="UPDATED_NEW",
    )

    # return response
    response = {
        "statusCode": 200,
    }
    print(f"response={response}")
    return response
