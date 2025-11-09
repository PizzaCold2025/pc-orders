import boto3
from pydantic import BaseModel

from common import parse_body, response, to_json
from schemas import Order, OrderStatus


class StartCookingOrderRequest(BaseModel):
    tenant_id: str
    order_id: str


def handler(event, context):
    data, err = parse_body(StartCookingOrderRequest, event)
    if err != None:
        return err

    assert data != None

    dynamodb = boto3.resource("dynamodb")
    orders = dynamodb.Table("pc-orders")

    resp = orders.get_item(Key={"tenant_id": data.tenant_id, "order_id": data.order_id})
    item: dict | None = resp.get("Item")

    if item == None:
        return response(404, {"message": "Order not found."})

    order = Order(**item)

    if order.status != OrderStatus.created:
        return response(409, {"message": "Order is not in 'created' status."})

    update_resp = orders.update_item(
        Key={"tenant_id": data.tenant_id, "order_id": data.order_id},
        UpdateExpression="SET #s = :new_status",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":new_status": OrderStatus.cooking},
        ConditionExpression="attribute_exists(tenant_id) AND attribute_exists(order_id)",
        ReturnValues="ALL_NEW",
    )

    new_order = update_resp["Attributes"]

    events = boto3.client("events")
    events.put_events(
        Entries=[
            {
                "Source": "pc.orders",
                "DetailType": "order.status_update",
                "Detail": to_json(new_order),
            }
        ]
    )

    return response(200, new_order)
