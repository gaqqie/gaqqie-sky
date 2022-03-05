from typing import List
from datetime import datetime
from decimal import Decimal
import json

import boto3

# cash of boto3 objects of dynamodb tables
cash = dict()


def _get_resource(resource_name: str):
    if resource_name not in cash:
        dynamodb = boto3.resource("dynamodb")
        resource_obj = dynamodb.Table(resource_name)
        cash[resource_name] = resource_obj

    return cash[resource_name]


def insert(table_name: str, record: dict) -> None:
    """insert a record.

    Parameters
    ----------
    table_name : str
        table name to insert record.
    record : dict
        record to insert.
    """
    table = _get_resource(table_name)
    table.put_item(Item=record)


def find_all(table_name: str) -> List[dict]:
    """find all records.

    Parameters
    ----------
    table_name : str
        table name to find records.

    Returns
    -------
    List[dict]
        list of records.
    """
    table = _get_resource(table_name)
    items = table.scan()
    if "Items" in items:
        records = items["Items"]
    else:
        records = []
    return records


def find_by_id(table_name: str, key: str, key_field_name: str = "id") -> dict:
    """find specific record.

    Parameters
    ----------
    table_name : str
        table name to find the record.
    key : str
        the key that identifies the record.
    key_field_name : str, optional
        field name of the key, by default "id".

    Returns
    -------
    dict
        record.
    """
    table = _get_resource(table_name)
    item = table.get_item(Key={key_field_name: key})
    if "Item" in item:
        record = item["Item"]
    else:
        record = None
    return record


def _to_update_expression(job_record: dict) -> str:
    update_expression_parts = []
    for key in job_record.keys():
        if key == "status":
            update_expression_parts.append("#" + key + "=:" + key)
        else:
            update_expression_parts.append(key + "=:" + key)

    update_expression = "set " + ", ".join(update_expression_parts)
    return update_expression


def _to_expression_attribute_names(job_record: dict) -> str:
    expression_attribute_names = {}
    for key in job_record.keys():
        if key == "status":
            expression_attribute_names["#" + key] = key

    return expression_attribute_names


def _to_expression_attribute_values(job_record: dict) -> dict:
    expression_attribute_values = {}
    for key, value in job_record.items():
        if key in [
            "status",
            "end_time",
            "provider_name",
            "status",
            "provider_job_id",
            "description",
            "queue_message_id",
        ]:
            expression_attribute_values[":" + key] = value
        else:
            expression_attribute_values[":" + key] = Decimal(value)

    return expression_attribute_values


def update(table_name: str, key: dict, item: dict) -> None:
    """update specific record.

    Parameters
    ----------
    table_name : str
        table name to update the record.
    key : dict
        dict of the key that identifies the record.
    item : dict
        dict of the item to update.
        this item must consist of updated fields.
    """
    table = _get_resource(table_name)

    attribute_names = _to_expression_attribute_names(item)
    if len(attribute_names) == 0:
        table.update_item(
            Key=key,
            UpdateExpression=_to_update_expression(item),
            ExpressionAttributeValues=_to_expression_attribute_values(item),
            ReturnValues="UPDATED_NEW",
        )
    else:
        table.update_item(
            Key=key,
            UpdateExpression=_to_update_expression(item),
            ExpressionAttributeNames=_to_expression_attribute_names(item),
            ExpressionAttributeValues=_to_expression_attribute_values(item),
            ReturnValues="UPDATED_NEW",
        )
