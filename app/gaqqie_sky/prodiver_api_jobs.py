import json

from gaqqie_sky.resource import db
from gaqqie_sky.resource import queue
from gaqqie_sky.resource import storage
from gaqqie_sky.common import util
import gaqqie_sky.resource.name_resolver as resolver


def receive_job(event: dict, context: "LambdaContext") -> dict:
    """receive job.

    Parameters
    ----------
    event : dict
        event object.
    context : LambdaContext
        context object.

    Returns
    -------
    dict
        dict corresponding to http response.
    """
    print(f"event={event}")

    # parse request
    device_name = event["pathParameters"]["device_name"]

    # receive a message from queue
    queue_name = resolver.queue_device(device_name)
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
        job_record = db.find_by_id(resolver.table_job(), job_id)
        if job_record is None:
            continue
        elif job_record["status"] in ["SUCCEEDED", "CANCELLED", "FAILED"]:
            continue

        # update job status
        job_record = {
            "status": "RUNNING",
        }
        db.update(resolver.table_job(), {"id": job_id}, job_record)

        # return response
        response = {
            "statusCode": 200,
            "body": message.body,
        }
        break

    print(f"response={response}")
    return response


def register_result(event: dict, context: "LambdaContext") -> dict:
    """register result of job.

    Parameters
    ----------
    event : dict
        event object.
    context : LambdaContext
        context object.

    Returns
    -------
    dict
        dict corresponding to http response.
    """
    print(f"event={event}")
    print(f"function_name={context.function_name}")

    # parse request
    job_id = event["pathParameters"]["job_id"]
    request_data = json.loads(event["body"])
    status = request_data["status"]
    results = request_data["results"]

    # store to S3
    storage.put(
        resolver.storage_bucket_result(),
        resolver.storage_key_results(job_id),
        results,
    )

    # update to database
    end_time = util.get_datetime_str()
    job_record = {
        "status": status,
        "end_time": end_time,
    }
    db.update(resolver.table_job(), {"id": job_id}, job_record)

    # return response
    response = {
        "statusCode": 200,
    }
    print(f"response={response}")
    return response
