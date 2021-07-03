import json

def get_device_by_name(event, context):
    print(f"event={event}")
    name = event["pathParameters"]["name"]
    responce_data = {
      "name": name,
      "provider_name": "gaqqie",
      "status": "ACTIVE",
      "num_qubits": 10,
      "max_shots": 1024,
      "queued_jobs": 10,
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response
