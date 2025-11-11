import boto3
from boto3.dynamodb.conditions import Attr, Key
from pydantic import BaseModel, ValidationError

from schemas import Order, OrderSubscription

# TODO: use environment variables
APIGW_DOMAIN = "xc9viv9bpa.execute-api.us-east-1.amazonaws.com"
APIGW_STAGE = "dev"
ENDPOINT_URL = f"https://{APIGW_DOMAIN}/{APIGW_STAGE}"


dynamodb = boto3.resource("dynamodb")
subscriptions = dynamodb.Table("pc-order-subscriptions")
api_gw = boto3.client("apigatewaymanagementapi", endpoint_url=ENDPOINT_URL)


def handler(event, context):
    order = Order(**event["detail"])

    resp = subscriptions.query(
        KeyConditionExpression=Key("tenant_id").eq(order.tenant_id),
        FilterExpression=(
            Attr("order_id").eq(order.order_id) | Attr("order_id").eq(None)
        ),
    )

    items: list[dict] = resp["Items"]
    print("items: ", items)

    for item in items:
        sub = None

        try:
            sub = OrderSubscription(**item)
        except (KeyError, ValidationError):
            continue

        if sub.order_id == None or sub.order_id == order.order_id:
            api_gw.post_to_connection(
                ConnectionId=sub.connection_id, Data=order.model_dump_json()
            )
