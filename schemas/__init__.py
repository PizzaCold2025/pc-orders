from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class OrderItem(BaseModel):
    item_id: str
    quantity: int


class OrderStatus(str, Enum):
    wait_for_cook = "wait_for_cook"
    cooking = "cooking"
    wait_for_dispatcher = "wait_for_dispatcher"
    dispatching = "dispatching"
    wait_for_deliverer = "wait_for_deliverer"
    delivering = "delivering"
    complete = "complete"


class Order(BaseModel):
    tenant_id: str
    order_id: str
    items: list[OrderItem]
    status: OrderStatus
    execution_arn: Optional[str] = None
    task_token: Optional[str] = None


class FullOrder(Order):
    execution: Optional[Any] = None
    execution_history: Optional[Any] = None


class OrderSubscription(BaseModel):
    tenant_id: str
    order_id: Optional[str] = None
    connection_id: str
    connected_at: int
