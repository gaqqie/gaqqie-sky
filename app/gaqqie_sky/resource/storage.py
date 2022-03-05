from datetime import datetime
from decimal import Decimal
import json
from typing import List

import boto3

# cash of boto3 objects of s3
cash = dict()


def _get_resource():
    if "s3" not in cash:
        resource_obj = boto3.client("s3")
        cash["s3"] = resource_obj

    return cash["s3"]


def get(bucket_name: str, key: str) -> str:
    """get data from the storage.

    Parameters
    ----------
    bucket_name : str
        bucket name to get data.
    key : str
        key of data.

    Returns
    -------
    str
        data.
    """
    s3 = _get_resource()
    s3_response = s3.get_object(Bucket=bucket_name, Key=key)
    data = s3_response["Body"].read().decode("utf-8")
    return data


def get_binary(bucket_name: str, key: str) -> str:
    """get binary data from the storage.

    Parameters
    ----------
    bucket_name : str
        bucket name to get binary data.
    key : str
        key of binary data.

    Returns
    -------
    str
        binary data.
    """
    s3 = _get_resource()
    s3_response = s3.get_object(Bucket=bucket_name, Key=key)
    data = s3_response["Body"].read()
    return data


def put(bucket_name: str, key: str, data: str) -> None:
    """put data to the storage.

    Parameters
    ----------
    bucket_name : str
        bucket name to put data.
    key : str
        key of data.
    data : str
        value of data.
    """
    s3 = _get_resource()
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=data,
        ContentType="text/json",
    )
