import json

from gaqqie_sky.common import const
from gaqqie_sky.resource import db
from gaqqie_sky.resource import storage
import gaqqie_sky.resource.name_resolver as resolver


def register_device(event: dict, context: "LambdaContext") -> dict:
    """register device information.

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
    device_record = {
        "name": "qiskit_simulator",
        "provider_name": "gaqqie",
        "status": "ACTIVE",
        "device_type": "simulator",
        "description": "a device for test",
        "num_qubits": 10,
        "max_shots": 1024,
        "execution_type": const.EXECUTION_TYPE_PULL,
    }
    db.insert(resolver.table_device(), device_record)

    device_record = {
        "name": "ibmq_quito",
        "provider_name": "IBM",
        "status": "ACTIVE",
        "device_type": "QPU",
        "description": "5 qubit device Quito",
        "num_qubits": 5,
        "max_shots": 20000,
        "execution_type": const.EXECUTION_TYPE_PUSH_POLL,
    }
    db.insert(resolver.table_device(), device_record)

    device_record = {
        "name": "Aspen-11",
        "provider_name": "AWS_Rigetti",
        "status": "ACTIVE",
        "device_type": "QPU",
        "description": "Universal gate-model QPU based on superconducting qubits",
        "num_qubits": 38,
        "max_shots": 10000,  # TODO fix
        "execution_type": const.EXECUTION_TYPE_PUSH_NOTIFY,
    }
    db.insert(resolver.table_device(), device_record)

    # update details on storage
    storage.put(
        resolver.storage_bucket_device(),
        resolver.storage_key_device("gaqqie", "qiskit_simulator"),
        "{}",
    )
    detail_ibmq_quito = {
        "detail_description": "5 qubit device Quito.",
        "common_properties": [
            {
                "name": "Provider name",
                "value": "IBM",
            },
            {
                "name": "Status",
                "value": "ACTIVE",
            },
            {
                "name": "Device type",
                "value": "QPU",
            },
            {
                "name": "Qubits",
                "value": "5",
            },
            {
                "name": "Max shots",
                "value": "20000",
            },
        ],
        "specific_properties": [
            {
                "name": "Location",
                "value": "California, USA",
            },
            {
                "name": "Availability",
                "value": "Everyday, 15:00:00 - 19:00:00 UTC",
            },
            {
                "name": "Cost",
                "value": "$0.30 / task + $0.00035 / shot",
            },
        ],
        "calibration_1q": [
            {
                "qubit": 0,
                "T1": 27.661,
                "T2": 12.521,
                "fidelity": "99.900",
                "readout": 98.3,
            },
            {
                "qubit": 1,
                "T1": 35.419,
                "T2": 10.563,
                "fidelity": 97.817,
                "readout": 91.8,
            },
            {
                "qubit": 2,
                "T1": 24.699,
                "T2": 4.462,
                "fidelity": 99.759,
                "readout": "73.0",
            },
        ],
        "calibration_2q": [
            {
                "qubits": "0-1",
                "fidelity_cx": 90.909,
            },
            {
                "qubits": "0-7",
                "fidelity_cx": 86.904,
            },
            {
                "qubits": "1-16",
                "fidelity_cx": 80.428,
            },
        ],
    }
    storage.put(
        resolver.storage_bucket_device(),
        resolver.storage_key_device("IBM", "ibmq_quito"),
        json.dumps(detail_ibmq_quito),
    )
    storage.put(
        resolver.storage_bucket_device(),
        resolver.storage_key_device("AWS_Rigetti", "Aspen-11"),
        "{}",
    )

    # return response
    response = {
        "statusCode": 200,
    }
    return response


def update_device(event: dict, context: "LambdaContext") -> dict:
    """update device information.

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
    name = event["pathParameters"]["name"]
    request_data = json.loads(event["body"])
    provider_name = request_data["provider_name"]
    status = request_data["status"]
    description = request_data["description"]
    num_qubits = request_data["num_qubits"]
    max_shots = request_data["max_shots"]

    # update to database
    device_record = {
        "provider_name": provider_name,
        "status": status,
        "description": description,
        "num_qubits": num_qubits,
        "max_shots": max_shots,
    }
    db.update(resolver.table_device(), {"name": name}, device_record)

    # update details on storage
    if "details" in request_data:
        storage.put(
            resolver.storage_bucket_device(),
            resolver.storage_key_device(provider_name, name),
            request_data["details"],
        )

    # return response
    response = {
        "statusCode": 200,
    }
    return response
