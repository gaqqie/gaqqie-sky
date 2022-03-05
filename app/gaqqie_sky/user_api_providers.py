import json

from gaqqie_sky.common import util
from gaqqie_sky.resource import db
from gaqqie_sky.resource import storage
import gaqqie_sky.resource.name_resolver as resolver


def get_providers(event: dict, context: "LambdaContext") -> dict:
    """get provider informations.

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

    # get provider from database
    provider_records = db.find_all(resolver.table_provider())

    # return response
    responce_data = []
    for provider_record in provider_records:
        data = {
            "name": provider_record["name"],
            "status": provider_record["status"],
            "description": provider_record["description"],
        }
        responce_data.append(data)
    response = {
        "statusCode": 200,
        "headers": util.get_cors_response_headers(),
        "body": json.dumps(responce_data),
    }
    print(f"response={response}")
    return response


def get_provider2(event: dict, context: "LambdaContext") -> dict:
    return get_provider_by_name(event, context)


def get_provider_by_name(event: dict, context: "LambdaContext") -> dict:
    """get specific provider information.

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
    provider_name = event["pathParameters"]["name"]

    # get provider from database
    provider_record = db.find_by_id(
        resolver.table_provider(), provider_name, key_field_name="name"
    )

    # get provider from strage
    details = storage.get(
        resolver.storage_bucket_provider(),
        resolver.storage_key_provider(provider_name),
    )

    # return response
    if provider_record:
        # construct response data
        responce_data = {
            "name": provider_record["name"],
            "status": provider_record["status"],
            "description": provider_record["description"],
            "details": json.loads(details),
            # "details": details,
        }
        response = {
            "statusCode": 200,
            "headers": util.get_cors_response_headers(),
            "body": json.dumps(responce_data),
        }
    else:
        response = {
            "statusCode": 200,
            "headers": util.get_cors_response_headers(),
        }
    print(f"response={response}")
    return response
