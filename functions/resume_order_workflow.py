import boto3
from pydantic import BaseModel

from common import to_json
from schemas import Order


class ResumeOrderWorkflowEvent(BaseModel):
    tenant_id: str
    order_id: str


def handler(event, context):
    data = ResumeOrderWorkflowEvent(**event)

    dynamodb = boto3.resource("dynamodb")
    orders = dynamodb.Table("pc-orders")

    resp = orders.get_item(Key={"tenant_id": data.tenant_id, "order_id": data.order_id})
    item: dict | None = resp.get("Item")

    if item == None:
        raise Exception("Order not found")

    order = Order(**item)

    if order.task_token == None:
        raise Exception("Order workflow is not paused")

    sf = boto3.client("stepfunctions")
    sf.send_task_success(
        taskToken=order.task_token,
        output=to_json(order.model_dump()),
    )
