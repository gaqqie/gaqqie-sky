from datetime import datetime
import json
import os
import uuid

import boto3


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
    """
    responce_data = {
        "id": id,
        "name": "sample job",
        "status": "QUEUED",
        "provider_name": "gaqqie",
        "device_name": "qiskit_simulator",
        "create_time": "2021-06-01T01:02:03.456Z",
        "end_time": None,
    }
    """
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
