from anyio import to_thread
from decimal import Decimal
import uuid
from sqlalchemy import select
from yookassa import Payment, Configuration
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database.models import OrderModel, OrderItem



async def _get_order(db: AsyncSession, order_id: int):
    result = await db.scalars(select(OrderModel)
                              .options(selectinload(OrderModel.items).selectinload(OrderItem.book),
                                       selectinload(OrderModel.buyer))
                              .where(OrderModel.id == order_id))
    order = result.first()

    return order





async def create_payment_url(db: AsyncSession, order_id: int):

    Configuration.account_id = 1170930
    Configuration.secret_key = 'test_LU9k61vQGvLthduudL-80i83_BXhIEvc_c35Z5FmdEk'

    items = []

    order = await _get_order(db, order_id)
    order_items = order.items

    for item in order_items:
        i = {
            'description': f'{item.book.title}',
            'quantity': item.quantity,
            'amount': {
                'value': f'{item.total_price:.2f}',
                'currency': 'RUB'
            },
            'vat_code': 1,
            'payment_mode': 'full_prepayment',
            'payment_subject': 'commodity'
            
        }

        items.append(i)


    payload = {
        'amount': {
            'value': f'{order.total_price:.2f}',
            'currency': 'RUB'
        },

        'confirmation': {
            'type': 'redirect',
            'return_url': 'https://google.com',
        },

        'capture': True,
        'descripiton': f'Заказ #{order.id}',
        'metadata': {
            'order_id': order.id
        },

        'receipt': {
            'customer': {
                'email': order.buyer.username
            },

            'items': items
        }
    }

    def _create_url() -> Payment:
        return Payment.create(payload, uuid.uuid4())

    payment: Payment = await to_thread.run_sync(_create_url)
    confirmation_url = getattr(payment.confirmation, 'confirmation_url', None)

    return {'id': payment.id, 'status': payment.status, 'confirmation_url': confirmation_url}        

    

