import json

from gaqqie_sky.resource import db
from gaqqie_sky.resource import storage
import gaqqie_sky.resource.name_resolver as resolver


def register_provider(event: dict, context: "LambdaContext") -> dict:
    """register provider information.

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
    # insert summary data on db
    provider_record = {
        "name": "gaqqie",
        "status": "ACTIVE",
        "description": "a provider for test",
    }
    db.insert(resolver.table_provider(), provider_record)

    provider_record = {
        "name": "IBM",
        "status": "ACTIVE",
        "description": "IBM Quantum Services",
    }
    db.insert(resolver.table_provider(), provider_record)

    provider_record = {
        "name": "AWS_Rigetti",
        "status": "ACTIVE",
        "description": "Rigetti quantum processors",
    }
    db.insert(resolver.table_provider(), provider_record)

    # update details on storage
    storage.put(
        resolver.storage_bucket_provider(),
        resolver.storage_key_provider("gaqqie"),
        "{}",
    )
    detail_ibm = {
        "name": "IBM",
        "detail": "IBM quantum processors are universal, gate-model machines based on superconducting qubits.",
        "common_properties": [
            {
                "name": "Status",
                "value": "ACTIVE",
            },
        ],
        "specific_properties": [
            {
                "name": "Requirements",
                "value": "need IBM Q accunt",
            },
        ],
    }
    storage.put(
        resolver.storage_bucket_provider(),
        resolver.storage_key_provider("IBM"),
        json.dumps(detail_ibm),
    )
    storage.put(
        resolver.storage_bucket_provider(),
        resolver.storage_key_provider("AWS_Rigetti"),
        "{}",
    )

    # return response
    response = {
        "statusCode": 200,
    }
    return response


def update_provider(event: dict, context: "LambdaContext") -> dict:
    """update provider information.

    If the device does not exist, registers it.

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
    # parse request
    print(event)
    name = event["pathParameters"]["name"]
    request_data = json.loads(event["body"])
    status = request_data["status"]
    description = request_data["description"]

    # update data on database
    provider_record = {
        "status": status,
        "description": description,
    }
    db.update(resolver.table_provider(), {"name": name}, provider_record)

    # update details on storage
    if "details" in request_data:
        storage.put(
            resolver.storage_bucket_provider(),
            resolver.storage_key_provider(name),
            request_data["details"],
        )

    # return response
    response = {
        "statusCode": 200,
    }
    return response
