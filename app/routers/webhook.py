from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from ipaddress import ip_address, ip_network
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_init import get_db

from config import settings
from app.checkout import update_payment_data

router = APIRouter(prefix='/yookassa', tags=['Обработка платежа'])

def check_ip(ip: str):
    if not ip:
        return False
    
    address = ip_address(ip)

    for mask in settings.ALLOWED_IPS:
        if '/' in mask:
            if address in ip_network(mask):
                return True
        else:
            if address == ip_address(mask):
                return True    

def get_client_ip(request: Request):
    x_forwarded_for = request.headers.get('x-forwarded-for')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()

    return request.client.host if request.client else None




@router.post('/webhook', status_code=status.HTTP_200_OK)
async def payment_webhook(request: Request, background_task: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    ip = get_client_ip(request)

    if not ip:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка при получение ip адреса'
        )
    
    check = check_ip(ip)

    if not check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Вашему IP доступ запрещен!'
        )
    
    response = await request.json()

    if response['status'] == 'payment.succeeded':
        object_data = response.get('object')
        await background_task.add_task(update_payment_data, db, object_data)
    

    return {'ok': True}