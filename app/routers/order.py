from decimal import Decimal
from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import UserModel, BookModel, CartModel, OrderModel, OrderItem
from database.db_init import get_db
from app.schemes.order_schema import OrderSchema, OrderItemSchema, BookSchema
from app.auth import get_current_buyer


router = APIRouter(prefix='/order', tags=['Заказы'])


@router.get('/list', response_model=list[OrderSchema], status_code=status.HTTP_200_OK)
async def get_buyer_orders(db: AsyncSession = Depends(get_db), current_buyer: UserModel = Depends(get_current_buyer)):
    result = await db.scalars(select(OrderModel)
                              .options(selectinload(OrderModel.items).selectinload(OrderItem.book))
                              .where(OrderModel.buyer_id == current_buyer.id)
                              .order_by(OrderModel.id.desc()))
    
    orders = result.all()
    

    if not orders:
        return []
    
    return orders


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_order(db: AsyncSession = Depends(get_db), current_buyer: UserModel = Depends(get_current_buyer)):
    cart_result = await db.scalars(select(CartModel)
                                   .options(selectinload(CartModel.book))
                                   .where(CartModel.buyer_id == current_buyer.id))
    
    cart_items = cart_result.all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Корзина данного пользователя пуста!'
        )
    
    new_order = OrderModel(buyer_id=current_buyer.id)
    total_amount = Decimal('0')


    for item in cart_items:
        book = item.book
        
        unit_price = book.price
        total_price = unit_price * item.quantity
        total_amount += total_price

        order_item = OrderItem(
            book_id=item.book.id,
            quantity=item.quantity,
            unit_price=unit_price,
            total_price=total_price
        )

        new_order.items.append(order_item)

    new_order.total_price = total_amount
    db.add(new_order)

    try:
        pass
    except Exception as e:
        pass        