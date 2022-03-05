import json
import os
import sys
import time

import numpy as np
from qiskit import IBMQ
from qiskit import QuantumCircuit, execute
from qiskit.assembler import disassemble
from qiskit.providers.jobstatus import JobStatus, JOB_FINAL_STATES
from qiskit.qobj import QasmQobj

from gaqqie_sky.common import util
from gaqqie_sky.resource import db
from gaqqie_sky.resource import queue
from gaqqie_sky.resource import storage
import gaqqie_sky.resource.name_resolver as resolver


def _get_provider():
    if IBMQ.active_account() is None:
        ibmq_token = os.environ["IBMQ_TOKEN"]
        provider = IBMQ.enable_account(ibmq_token)
    else:
        provider = IBMQ.get_provider(hub="ibm-q", group="open", project="main")

    return provider


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

    # parse parameter
    job_id = event["id"]
    device_name = event["device_name"]
    # instructions = event["instructions"]

    # get result from storage
    job_json = storage.get(
        resolver.storage_bucket_result(),
        resolver.storage_key_instructions(job_id),
    )

    # parse circuit
    instructions_str = json.loads(job_json)["instructions"]
    qobj_json = json.loads(instructions_str)
    print(f"qobj_json={qobj_json}")
    # qobj_json = json.loads(instructions)
    qobj = QasmQobj.from_dict(qobj_json)
    circuit = disassemble(qobj)[0]

    # get backend
    provider = _get_provider()
    backend = provider.get_backend(device_name)

    # execute circuit
    job = execute(circuit, backend)
    provider_job_id = job.job_id()
    job_record = {
        "provider_job_id": provider_job_id,
    }
    db.update(resolver.table_job(), {"id": job_id}, job_record)
    print(f"submit_job job_id={job_id} provider_job_id={provider_job_id}")


def poll_jobs(event: dict, context: "LambdaContext") -> dict:
    print(f"context={context}")

    # get job from database
    job_records = db.find_all(resolver.table_job())

    # filter queued data
    queued_data = []
    for job_record in job_records:
        if job_record["status"] == "QUEUED" and job_record["provider_name"] == "IBM":
            queued_data.append(job_record)
    print(f"queued records={len(queued_data)}")

    # poll status and result of jobs
    provider = _get_provider()
    for job_record in queued_data:
        print(f"job_record={job_record}")
        job_id = job_record["id"]
        provider_job_id = job_record["provider_job_id"]
        device_name = job_record["device_name"]
        job = provider.get_backend(device_name).retrieve_job(provider_job_id)
        if job.status() not in JOB_FINAL_STATES:
            continue

        if job.status() == JobStatus.DONE:
            print(f"SUCCEEDED job_id={job_id} provider_job_id={provider_job_id}")
            status = "SUCCEEDED"
            result = job.result()
            result_dict = result.to_dict()
            result_dict["backend_name"] = device_name
            # TODO
            if "date" in result_dict:
                del result_dict["date"]
            result_json = json.dumps(result_dict, indent=2)

            # store to S3
            storage.put(
                resolver.storage_bucket_result(),
                resolver.storage_key_results(job_id),
                result_json,
            )
        elif job.status() == JobStatus.CANCELLED:
            status = "CANCELLED"
        elif job.status() == JobStatus.ERROR:
            status = "FAILED"

        # update to database
        end_time = util.get_datetime_str()
        job_record = {
            "status": status,
            "end_time": end_time,
        }
        db.update(resolver.table_job(), {"id": job_id}, job_record)
        print(f"updated job_id={job_id} provider_job_id={provider_job_id}")
