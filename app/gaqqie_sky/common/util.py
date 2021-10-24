from datetime import datetime
import uuid


def generate_id() -> str:
    """generate uuid.

    Returns
    -------
    str
        uuid.
    """
    return str(uuid.uuid4())


def get_datetime_str() -> str:
    """returns a date/time string in ISO format.

    Returns
    -------
    str
        a date/time string in ISO format.
    """
    return datetime.now().isoformat(timespec="milliseconds") + "Z"
