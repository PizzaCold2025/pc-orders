from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel

from common import parse_body, response
from schemas import OrderSubscription


class SubscribeRequest(BaseModel):
    action: str
    tenant_id: str
    order_id: Optional[str]


dynamodb = boto3.resource("dynamodb")
subscriptions = dynamodb.Table("pc-order-subscriptions")


def handler(event, context):
    data, err = parse_body(SubscribeRequest, event)
    if err != None:
        return err

    assert data != None

    connection_id = event["requestContext"]["connectionId"]
    connected_at = event["requestContext"]["connectedAt"]

    resp = subscriptions.query(
        IndexName="connection-id-index",
        KeyConditionExpression=Key("connection_id").eq(connection_id),
        Limit=1,
    )

    if resp["Count"] > 0:
        return response(200, {"message": "Already subscribed."})

    new_subscription = OrderSubscription(
        tenant_id=data.tenant_id,
        order_id=data.order_id,
        connection_id=connection_id,
        connected_at=connected_at,
    )

    subscriptions.put_item(Item=new_subscription.model_dump())

    return response(200, {"message": "Subscribed."})
