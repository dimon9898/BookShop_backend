from pydantic import BaseModel, ConfigDict



class SellerSchema(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)





class BookSchema(BaseModel):
    id: int
    title: str
    description: str
    price: float
    year: str
    seller_id: int
    seller: SellerSchema


    model_config = ConfigDict(from_attributes=True)


class CartItem(BaseModel):
    id: int
    buyer_id: int
    book_id: int
    quantity: int
    total_price: float

    book: BookSchema

    model_config = ConfigDict(from_attributes=True)