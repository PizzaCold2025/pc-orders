from enum import Enum
from typing import Optional

from pydantic import BaseModel


class OrderItem(BaseModel):
    item_id: str
    quantity: int


class OrderStatus(str, Enum):
    created = "created"
    cooking = "cooking"


class Order(BaseModel):
    tenant_id: str
    order_id: str
    items: list[OrderItem]
    status: OrderStatus
    task_token: Optional[str] = None
