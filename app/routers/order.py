from decimal import Decimal
from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from database.models import UserModel, BookModel, CartModel, OrderModel, OrderItem
from database.db_init import get_db
from app.schemes.order_schema import OrderSchema, OrderItemSchema, BookSchema, PaymentResponse
from app.auth import get_current_buyer
from app.checkout import create_payment_url


router = APIRouter(prefix='/order', tags=['Заказы'])


async def _get_created_order(db: AsyncSession, order_id):
    result = await db.scalars(select(OrderModel)
                              .options(selectinload(OrderModel.items)
                                       .selectinload(OrderItem.book))
                              .where(OrderModel.id == order_id))
    order = result.first()

    return order





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
        await db.flush()
        payment = await create_payment_url(db, new_order.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Ошибка при создание платежа: {e}'
        )       
    

    new_order.payment_status = payment.get('status')
    new_order.payment_id = payment.get('id')


    await db.execute(delete(CartModel).where(CartModel.buyer_id == current_buyer.id))
    await db.commit()


    order = await _get_created_order(db, new_order.id)

    return PaymentResponse(order=order, confirmation_url=payment.get('confirmation_url'))
