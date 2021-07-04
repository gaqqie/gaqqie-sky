import datetime
import json
import os
import uuid

import boto3


def submit_job(event, context):
    print(f"event={event}")

    # parse job
    request_data = json.loads(event["body"])

    job_id = str(uuid.uuid4())  # UTC
    now = datetime.datetime.now()
    create_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    job_record = {"id": job_id, "status": "QUEUED", "create_time": create_time}

    if "name" in request_data:
        job_record["name"] = request_data["name"]
    if "provider_name" in request_data:
        job_record["provider_name"] = request_data["provider_name"]
    if "device_name" in request_data:
        job_record["device_name"] = request_data["device_name"]

    if "instructions" in request_data:
        instructions = request_data["instructions"]
    else:
        # TODO error
        pass

    # TODO validate job

    # store to S3
    s3 = boto3.client("s3")
    bucket_name = os.environ["S3_BUCKET_RESULT"]
    instructions_key = "organization/user/" + job_id + "/instructions.json"
    s3.put_object(
        Bucket=bucket_name,
        Key=instructions_key,
        Body=instructions,
        ContentType="text/html",
    )

    # TODO send to SQS

    # store to DynamoDB
    dynamodb = boto3.resource("dynamodb")
    job_table_name = os.environ["DYNAMODB_TABLE_JOB"]
    job_table = dynamodb.Table(job_table_name)
    job_table.put_item(Item=job_record)

    # return response
    response = {
        "statusCode": 200,
        "body": json.dumps(job_record),
    }
    print(f"response={response}")
    return response


def get_job_by_id(event, context):
    print(f"event={event}")

    # parse request
    id = event["pathParameters"]["id"]

    # get job from DynamoDB

    # return response
    responce_data = {
        "id": id,
        "name": "sample job",
        "status": "QUEUED",
        "provider_name": "gaqqie",
        "device_name": "qiskit_simulator",
        "create_time": "2021-06-01T01:02:03.456Z",
        "end_time": None,
    }
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

    # return response
    responce_data = {
        "job_id": job_id,
        "result": {"00": 498, "11": 502},
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response
