from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BookSchema(BaseModel):
    id: int
    title: str
    description: str
    price: float
    year: str

    model_config = ConfigDict(from_attributes=True)


class OrderItemSchema(BaseModel):
    id: int
    order_id: int
    book_id: int
    quantity: int
    unit_price: float
    total_price: float

    book: BookSchema

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(BaseModel):
    id: int
    buyer_id: int
    total_price: float
    payment_status: str
    payment_id: str
    created_at: datetime
    updated_at: datetime
    paid_at: datetime | None = None

    items: list[OrderItemSchema]
    
    model_config = ConfigDict(from_attributes=True)




class PaymentResponse(BaseModel):
    order: OrderSchema
    confirmation_url: str