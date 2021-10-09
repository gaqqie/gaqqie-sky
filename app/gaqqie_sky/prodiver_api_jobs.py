import json
import os

from gaqqie_sky.resource import db
from gaqqie_sky.resource import queue
from gaqqie_sky.resource import storage
from gaqqie_sky.common import util


def receive_job(event, context):
    print(f"event={event}")

    # parse request
    device_name = event["pathParameters"]["device_name"]

    # receive a message from SQS
    queue_name = os.environ["SQS_QUEUE_PREFIX"] + device_name + ".fifo"
    while True:
        messages = queue.receive(queue_name, ["job_id"], 1)

        # message doesn't exist
        if len(messages) == 0:
            response = {
                "statusCode": 200,
            }
            break

        # parse message and delete from queue
        message = messages[0]
        job_id = message.message_attributes["job_id"]["StringValue"]
        message.delete()

        # check job status
        job_record = db.find_by_id(os.environ["DYNAMODB_TABLE_JOB"], job_id)
        if job_record is None:
            continue
        elif job_record["status"] in ["SUCCEEDED", "CANCELLED", "FAILED"]:
            continue

        # update job status
        job_record = {
            "status": "RUNNING",
        }
        db.update(os.environ["DYNAMODB_TABLE_JOB"], {"id": job_id}, job_record)

        # return response
        response = {
            "statusCode": 200,
            "body": message.body,
        }
        break

    print(f"response={response}")
    return response


def register_result(event, context):
    print(f"event={event}")

    # parse request
    job_id = event["pathParameters"]["job_id"]
    request_data = json.loads(event["body"])
    status = request_data["status"]
    results = request_data["results"]

    # store to S3
    storage.put(
        os.environ["S3_BUCKET_RESULT"],
        "organization/user/" + job_id + "/results.json",
        results,
    )

    # update to DynamoDB
    end_time = util.get_datetime_str()
    job_record = {
        "status": status,
        "end_time": end_time,
    }
    db.update(os.environ["DYNAMODB_TABLE_JOB"], {"id": job_id}, job_record)

    # return response
    response = {
        "statusCode": 200,
    }
    print(f"response={response}")
    return response
