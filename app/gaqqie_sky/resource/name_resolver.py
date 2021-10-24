import os


def table_provider() -> str:
    return os.environ["TABLE_PROVIDER"]


def table_device() -> str:
    return os.environ["TABLE_DEVICE"]


def table_job() -> str:
    return os.environ["TABLE_JOB"]


def queue_device(device_name: str) -> str:
    return os.environ["QUEUE_PREFIX"] + device_name + ".fifo"


def storage_bucket_provider() -> str:
    return os.environ["BUCKET_PROVIDER"]


def storage_key_provider(provider_name: str) -> str:
    return f"{provider_name}/_provider.json"


def storage_bucket_device() -> str:
    return os.environ["BUCKET_PROVIDER"]


def storage_key_device(provider_name: str, device_name: str) -> str:
    return f"{provider_name}/{device_name}.json"


def storage_bucket_result() -> str:
    return os.environ["BUCKET_RESULT"]


def storage_key_instructions(job_id: str) -> str:
    return "organization/user/" + job_id + "/instructions.json"


def storage_key_results(job_id: str) -> str:
    return "organization/user/" + job_id + "/results.json"
