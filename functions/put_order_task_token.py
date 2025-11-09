import boto3
from pydantic import BaseModel


class PutTaskTokenEvent(BaseModel):
    tenant_id: str
    order_id: str
    task_token: str


def handler(event, context):
    data = PutTaskTokenEvent(**event)

    dynamodb = boto3.resource("dynamodb")
    orders = dynamodb.Table("pc-orders")

    orders.update_item(
        Key={"tenant_id": data.tenant_id, "order_id": data.order_id},
        UpdateExpression="SET task_token = :token",
        ExpressionAttributeValues={":token": data.task_token},
    )
