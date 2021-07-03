import json

def submit_job(event, context):
    print(f"event={event}")
    responce_data = json.loads(event["body"])
    responce_data["id"] = "zzz"
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response

def get_job_by_id(event, context):
    print(f"event={event}")
    id = event["pathParameters"]["id"]
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
    job_id = event["pathParameters"]["job_id"]
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
