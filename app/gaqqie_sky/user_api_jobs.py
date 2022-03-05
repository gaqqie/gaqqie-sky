import json

import boto3

from gaqqie_sky.common import const
from gaqqie_sky.common import util
from gaqqie_sky.resource import db
from gaqqie_sky.resource import function
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

        # get device from database
        device_record = db.find_by_id(
            resolver.table_device(), request_data["device_name"], key_field_name="name"
        )
    if "instructions" in request_data:
        job_record["instructions"] = request_data["instructions"]

    # validate job
    instructions = json.loads(request_data["instructions"])
    num_qubits = instructions["config"]["n_qubits"]
    shots = instructions["config"]["shots"]

    if device_record["status"] == "UNSUBMITTABLE":
        description = "device status is UNSUBMITTABLE."
        job_record["description"] = description
        job_record["status"] = "FAILED"
        job_record["end_time"] = util.get_datetime_str()
        print(description)
    elif num_qubits > device_record["num_qubits"]:
        description = f"number of qubits exceeds the limit of device({device_record['num_qubits']})."
        job_record["description"] = description
        job_record["status"] = "FAILED"
        job_record["end_time"] = util.get_datetime_str()
        print(description)
    elif shots > device_record["max_shots"]:
        description = f"number of shots exceeds the limit of device({device_record['max_shots']})."
        job_record["description"] = description
        job_record["status"] = "FAILED"
        job_record["end_time"] = util.get_datetime_str()
        print(description)

    # job_json for datastore, queue
    job_json = json.dumps(job_record)
    # job_record for database
    del job_record["instructions"]

    # store to datastore
    storage.put(
        resolver.storage_bucket_result(),
        resolver.storage_key_instructions(job_id),
        job_json,
    )

    # store to database
    db.insert(resolver.table_job(), job_record)

    # check execution_type of device
    if job_record["status"] == "FAILED":
        pass
    elif device_record["execution_type"] == const.EXECUTION_TYPE_PULL:
        # send to queue
        queue_name = resolver.queue_device(job_record["device_name"])
        response = queue.send(
            queue_name,
            job_json,
            {"job_id": {"StringValue": job_id, "DataType": "String"}},
            job_record["device_name"],
            job_id,
        )
        queue_message_id = response.get("MessageId")
        print(f"MessageId={queue_message_id}")

        # update to database
        job_record = {
            "queue_message_id": queue_message_id,
        }
        db.update(resolver.table_job(), {"id": job_id}, job_record)

    elif device_record["provider_name"] == "IBM":
        # invoke to ibm_provider
        """
        request_data["id"] = job_id
        function.invoke_async(
            resolver.function_name("InnnerApiSubmitJobToIbm"), json.dumps(request_data)
        )
        """
        function.invoke_async(
            resolver.function_name("InnnerApiSubmitJobToIbm"), json.dumps(job_record)
        )

    # return response
    response = {
        "statusCode": 200,
        "headers": util.get_cors_response_headers(),
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
        if "name" in job_record:
            data["name"] = job_record["name"]
        if "end_time" in job_record:
            data["end_time"] = job_record["end_time"]
        responce_data.append(data)

    response = {
        "statusCode": 200,
        "headers": util.get_cors_response_headers(),
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
            "headers": util.get_cors_response_headers(),
            "body": json.dumps(responce_data),
        }
    else:
        # specified record doesn't exist
        response = {
            "statusCode": 200,
            "headers": util.get_cors_response_headers(),
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
            "headers": util.get_cors_response_headers(),
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
        "headers": util.get_cors_response_headers(),
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response
