import json

from gaqqie_sky.common import util
from gaqqie_sky.resource import db
from gaqqie_sky.resource import queue
from gaqqie_sky.resource import storage
import gaqqie_sky.resource.name_resolver as resolver


def submit_job(event: dict, context: "LambdaContext") -> dict:
    """submit job.

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
        resolver.storage_bucket_result(),
        resolver.storage_key_instructions(job_id),
        job_json,
    )
    del job_record["instructions"]

    # send to queue
    # TODO queue doesn't need "status"
    queue_name = resolver.queue_device(job_record["device_name"])
    response = queue.send(
        queue_name,
        job_json,
        {"job_id": {"StringValue": job_id, "DataType": "String"}},
        job_record["device_name"],
        job_id,
    )
    print(f"MessageId={response.get('MessageId')}")
    job_record["queue_message_id"] = response.get("MessageId")

    # store to database
    db.insert(resolver.table_job(), job_record)

    # return response
    response = {
        "statusCode": 200,
        "body": job_json,
    }
    print(f"response={response}")
    return response


def get_jobs(event: dict, context: "LambdaContext") -> dict:
    """get job informations.

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

    # get job from database
    job_records = db.find_all(resolver.table_job())

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


def get_job_by_id(event: dict, context: "LambdaContext") -> dict:
    """get specific job information.

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
    id = event["pathParameters"]["id"]

    # get job from database
    job_record = db.find_by_id(resolver.table_job(), id)

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


def cancel_job_by_id(event: dict, context: "LambdaContext") -> dict:
    """cancel specific job.

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
    id = event["pathParameters"]["id"]

    # get job from database
    job_record = db.find_by_id(resolver.table_job(), id)

    if job_record:
        # update database
        end_time = util.get_datetime_str()
        new_job_record = {
            "status": "CANCELLED",
            "end_time": end_time,
        }
        db.update(resolver.table_job(), {"id": id}, new_job_record)

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


def get_result_by_job_id(event: dict, context: "LambdaContext") -> dict:
    """get result of specific job.

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
    job_id = event["pathParameters"]["job_id"]

    # get result from storage
    results = storage.get(
        resolver.storage_bucket_result(),
        resolver.storage_key_results(job_id),
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
