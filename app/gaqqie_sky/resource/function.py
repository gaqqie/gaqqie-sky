import boto3

# cash of boto3 objects of lambda
cash = dict()


def _get_client():
    if "lambda" not in cash:
        client_obj = boto3.client("lambda")
        cash["lambda"] = client_obj

    return cash["lambda"]


def invoke_sync(function_name: str, payload: dict) -> dict:
    """Invoke the function synchronously.

    Parameters
    ----------
    function_name : str
        function name.
    payload : dict
        input parameters of the function.

    Returns
    -------
    dict
        responce data.
    """
    client = _get_client()
    response = client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=payload,
    )
    return response


def invoke_async(function_name: str, payload: dict) -> None:
    """Invoke the function asynchronously.

    Parameters
    ----------
    function_name : str
        function name.
    payload : dict
        input parameters of the function.
    """
    client = _get_client()
    client.invoke(
        FunctionName=function_name,
        InvocationType="Event",
        Payload=payload,
    )
