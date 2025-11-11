import json
from decimal import Decimal
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def parse_body(model: type[T], event: dict):
    try:
        body = json.loads(event["body"])
        return model(**body), None
    except (KeyError, json.JSONDecodeError, ValidationError):
        return None, response(400, {"message": "Invalid request body."})


def response(status_code: int, body: Any):
    raw_body = None

    if body != None:
        if type(body) == str:
            raw_body = body
        else:
            raw_body = to_json(body)

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": raw_body,
    }


def json_default(obj: dict):
    if isinstance(obj, Decimal):
        return float(obj)

    raise TypeError


def to_json(obj: dict):
    return json.dumps(obj, default=json_default)
