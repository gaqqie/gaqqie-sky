from datetime import datetime
import uuid


def generate_id() -> str:
    return str(uuid.uuid4())


def get_datetime_str() -> str():
    return datetime.now().isoformat(timespec="milliseconds") + "Z"
