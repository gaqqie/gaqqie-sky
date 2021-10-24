from datetime import datetime
from decimal import Decimal
import json
from typing import List

import boto3

# cash of boto3 objects of sqs queue
cash = dict()


def _get_resource(resource_name: str):
    if resource_name not in cash:
        sqs = boto3.resource("sqs")
        resource_obj = sqs.get_queue_by_name(QueueName=resource_name)
        cash[resource_name] = resource_obj

    return cash[resource_name]


def get_queue(queue_name: str):
    """returns specific queue.

    Parameters
    ----------
    queue_name : str
        queue name

    Returns
    -------
    [type]
        specific queue object.
    """
    return _get_resource(queue_name)


def send(
    queue_name: str,
    message: str,
    attributes: dict,
    group_id: str,
    deduplication_id: str,
) -> dict:
    """send a message.

    Parameters
    ----------
    queue_name : str
        queue name.
    message : str
        message.
    attributes : dict
        dict of message attributes.
    group_id : str
        group id.
    deduplication_id : str
        deduplication id.

    Returns
    -------
    dict
        return value from queue.
        it contains "queue_message_id"(unique id of message).
    """
    queue = _get_resource(queue_name)
    response = queue.send_message(
        MessageBody=message,
        MessageAttributes=attributes,
        MessageGroupId=group_id,
        MessageDeduplicationId=deduplication_id,
    )
    return response


def receive(
    queue_name: str, message_attribute_names: List[str], max_number_of_messages: int = 1
) -> List[dict]:
    """receive message.

    Parameters
    ----------
    queue_name : str
        queue name.
    message_attribute_names : List[str]
        message attribute names to receive.
    max_number_of_messages : int, optional
        max number of messages to receive, by default 1

    Returns
    -------
    dict
        list of messages.
        if messages don't exist, returns the list of length zero.
    """
    # get messages from queue
    queue = _get_resource(queue_name)
    messages = queue.receive_messages(
        MessageAttributeNames=message_attribute_names,
        MaxNumberOfMessages=max_number_of_messages,
    )
    return messages
