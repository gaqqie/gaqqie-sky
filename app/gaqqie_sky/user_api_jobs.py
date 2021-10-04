from datetime import datetime
from decimal import Decimal
import json
import os
import uuid

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


def submit_job(event, context):
    print(f"event={event}")

    # parse job
    request_data = json.loads(event["body"])

    job_id = str(uuid.uuid4())  # UTC
    create_time = datetime.now().isoformat(timespec="milliseconds") + "Z"
    job_record = {"id": job_id, "status": "QUEUED", "create_time": create_time}

    if "name" in request_data:
        job_record["name"] = request_data["name"]
    if "provider_name" in request_data:
        job_record["provider_name"] = request_data["provider_name"]
    if "device_name" in request_data:
        job_record["device_name"] = request_data["device_name"]

    if "instructions" in request_data:
        job_record["instructions"] = request_data["instructions"]
    else:
        # TODO error
        pass

    # TODO validate job
    job_json = json.dumps(job_record)

    # store to S3
    s3 = boto3.client("s3")
    bucket_name = os.environ["S3_BUCKET_RESULT"]
    instructions_key = "organization/user/" + job_id + "/instructions.json"
    s3.put_object(
        Bucket=bucket_name,
        Key=instructions_key,
        Body=job_json,
        ContentType="text/html",
    )
    del job_record["instructions"]

    # send to SQS
    # TODO SQS doesn't need "status"
    sqs = boto3.resource("sqs")
    queue_name = os.environ["SQS_QUEUE_PREFIX"] + job_record["device_name"] + ".fifo"
    print(f"queue_name={queue_name}")
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    response = queue.send_message(
        MessageBody=job_json,
        MessageAttributes={"job_id": {"StringValue": job_id, "DataType": "String"}},
        MessageGroupId=job_record["device_name"],
        MessageDeduplicationId=job_id,
    )
    print(f"MessageId={response.get('MessageId')}")
    job_record["queue_message_id"] = response.get("MessageId")

    # store to DynamoDB
    dynamodb = boto3.resource("dynamodb")
    job_table_name = os.environ["DYNAMODB_TABLE_JOB"]
    job_table = dynamodb.Table(job_table_name)
    job_table.put_item(Item=job_record)

    # return response
    response = {
        "statusCode": 200,
        "body": job_json,
    }
    print(f"response={response}")
    return response


def get_jobs(event, context):
    print(f"event={event}")

    # get job from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    job_table_name = os.environ["DYNAMODB_TABLE_JOB"]
    job_table = dynamodb.Table(job_table_name)
    dynamodb_response = job_table.scan()
    job_records = dynamodb_response["Items"]
    print(f"job_records={job_records}")

    # return response
    responce_data = []
    for job_record in job_records:
        data = {
            "id": job_record["id"],
            "status": job_record["status"],
            "provider_name": job_record["provider_name"],
            "device_name": job_record["device_name"],
            "create_time": job_record["create_time"],
        }
        responce_data.append(data)
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response


def get_job_by_id(event, context):
    print(f"event={event}")

    # parse request
    id = event["pathParameters"]["id"]

    # get job from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    job_table_name = os.environ["DYNAMODB_TABLE_JOB"]
    job_table = dynamodb.Table(job_table_name)
    dynamodb_response = job_table.get_item(Key={"id": id})
    job_record = dynamodb_response["Item"]
    print(f"job_record={job_record}")

    # return response
    responce_data = {
        "id": id,
        "status": job_record["status"],
        "provider_name": job_record["provider_name"],
        "device_name": job_record["device_name"],
        "create_time": job_record["create_time"],
    }
    if "name" in job_record:
        responce_data["name"] = job_record["name"]
    if "end_time" in job_record:
        responce_data["end_time"] = job_record["end_time"]

    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response


def cancel_job_by_id(event, context):
    print(f"event={event}")

    # parse request
    id = event["pathParameters"]["id"]

    # get job from DynamoDB
    dynamodb = boto3.resource("dynamodb")
    job_table_name = os.environ["DYNAMODB_TABLE_JOB"]
    job_table = dynamodb.Table(job_table_name)
    dynamodb_response = job_table.get_item(Key={"id": id})
    # TODO not exist "Item"
    job_record = dynamodb_response["Item"]
    print(f"job_record={job_record}")
    status = job_record["status"]
    queue_message_id = job_record["queue_message_id"]

    # delete job from SQS
    sqs = boto3.resource("sqs")
    queue_name = os.environ["SQS_QUEUE_PREFIX"] + job_record["device_name"] + ".fifo"
    print(f"queue_name={queue_name}")
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    messages = queue.receive_messages(
        MessageAttributeNames=["job_id"],
        MaxNumberOfMessages=10,
    )
    if len(messages) == 0:
        # return response
        # TODO status code
        response = {
            "statusCode": 200,
        }
    else:
        # parse message
        for message in messages:
            if message.message_id == queue_message_id:
                receipt_handle = message.receipt_handle
                print(
                    f"job_id={id}, queue_message_id={queue_message_id}, receipt_handle={receipt_handle}"
                )
                message.delete()
                break

    # update to DynamoDB
    end_time = datetime.now().isoformat(timespec="milliseconds") + "Z"
    new_job_record = {
        "status": "CANCELLED",
        "end_time": end_time,
    }
    job_table.update_item(
        Key={
            "id": id,
        },
        UpdateExpression=_to_update_expression(new_job_record),
        ExpressionAttributeNames=_to_expression_attribute_names(new_job_record),
        ExpressionAttributeValues=_to_expression_attribute_values(new_job_record),
        ReturnValues="UPDATED_NEW",
    )

    # return response
    responce_data = {
        "id": id,
        "status": "CANCELLED",
        "provider_name": job_record["provider_name"],
        "device_name": job_record["device_name"],
        "create_time": job_record["create_time"],
        "end_time": end_time,
    }
    if "name" in job_record:
        responce_data["name"] = job_record["name"]

    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response


def get_result_by_job_id(event, context):
    print(f"event={event}")

    # parse request
    job_id = event["pathParameters"]["job_id"]

    # get result from S3
    s3 = boto3.client("s3")
    bucket_name = os.environ["S3_BUCKET_RESULT"]
    results_key = "organization/user/" + job_id + "/results.json"
    s3_response = s3.get_object(Bucket=bucket_name, Key=results_key)
    results = s3_response["Body"].read().decode("utf-8")

    # return response
    responce_data = {
        "job_id": job_id,
        "results": results,
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response
