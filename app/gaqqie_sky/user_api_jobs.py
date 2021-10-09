from datetime import datetime
from decimal import Decimal
import json
import os
import uuid

import boto3

from gaqqie_sky.common import util
from gaqqie_sky.resource import db
from gaqqie_sky.resource import queue
from gaqqie_sky.resource import storage


def submit_job(event, context):
    print(f"event={event}")

    # parse job
    request_data = json.loads(event["body"])

    job_id = util.generate_id()
    create_time = util.get_datetime_str()
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
    storage.put(
        os.environ["S3_BUCKET_RESULT"],
        "organization/user/" + job_id + "/instructions.json",
        job_json,
    )
    del job_record["instructions"]

    # send to SQS
    # TODO SQS doesn't need "status"
    queue_name = os.environ["SQS_QUEUE_PREFIX"] + job_record["device_name"] + ".fifo"
    response = queue.send(
        queue_name,
        job_json,
        {"job_id": {"StringValue": job_id, "DataType": "String"}},
        job_record["device_name"],
        job_id,
    )
    print(f"MessageId={response.get('MessageId')}")
    job_record["queue_message_id"] = response.get("MessageId")

    # store to DynamoDB
    db.insert(os.environ["DYNAMODB_TABLE_JOB"], job_record)

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
    job_records = db.find_all(os.environ["DYNAMODB_TABLE_JOB"])

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
    job_record = db.find_by_id(os.environ["DYNAMODB_TABLE_JOB"], id)

    # return response
    if job_record:
        # construct response data
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
    else:
        # specified record doesn't exist
        response = {
            "statusCode": 200,
        }
    print(f"response={response}")
    return response


def cancel_job_by_id(event, context):
    print(f"event={event}")

    # parse request
    id = event["pathParameters"]["id"]

    # get job from DynamoDB
    job_record = db.find_by_id(os.environ["DYNAMODB_TABLE_JOB"], id)

    if job_record:
        # update to DynamoDB
        end_time = util.get_datetime_str()
        new_job_record = {
            "status": "CANCELLED",
            "end_time": end_time,
        }
        db.update(os.environ["DYNAMODB_TABLE_JOB"], {"id": id}, new_job_record)

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
    else:
        # TODO job not found
        pass

    print(f"response={response}")
    return response


def get_result_by_job_id(event, context):
    print(f"event={event}")

    # parse request
    job_id = event["pathParameters"]["job_id"]

    # get result from S3
    results = storage.get(
        os.environ["S3_BUCKET_RESULT"], "organization/user/" + job_id + "/results.json"
    )

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
