import boto3

from schemas import Order

sfn = boto3.client("stepfunctions")
dynamodb = boto3.resource("dynamodb")
orders = dynamodb.Table("pc-orders")


def handler(event, context):
    order = Order(**event["detail"])

    # TODO: use environment variable
    execution = sfn.start_execution(
        stateMachineArn="arn:aws:states:us-east-1:603103502342:stateMachine:pc-order-workflow",
        input=order.model_dump_json(),
    )

    orders.update_item(
        Key={"tenant_id": order.tenant_id, "order_id": order.order_id},
        UpdateExpression="SET execution_arn = :arn",
        ExpressionAttributeValues={":arn": execution["executionArn"]},
    )
