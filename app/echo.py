import json

def echo(event, context):
    print(f"event={event}")
    response = {
        "statusCode": 200,
        "body": json.dumps({"code": 200,"type": "xx","message": "echo!"}),
    }
    return response
