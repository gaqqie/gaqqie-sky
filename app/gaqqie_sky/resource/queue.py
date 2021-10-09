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
    return _get_resource(queue_name)


def send(
    queue_name: str,
    message: str,
    attributes: dict,
    group_id: str,
    deduplication_id: str,
) -> dict():
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
) -> dict:
    # get messages from SQS
    queue = _get_resource(queue_name)
    messages = queue.receive_messages(
        MessageAttributeNames=message_attribute_names,
        MaxNumberOfMessages=max_number_of_messages,
    )
    return messages
