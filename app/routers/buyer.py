from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import UserModel, BookModel, CartModel
from database.db_init import get_db
from app.schemes.buyer_schema import BookSchema, CartItem
from app.auth import get_current_buyer

router = APIRouter(prefix='/buyer', tags=['Эндпоинты покупателя'])


@router.get('/books', response_model=list[BookSchema], status_code=status.HTTP_200_OK)
async def get_all_books(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(BookModel)
                              .options(selectinload(BookModel.seller))
                              .order_by(BookModel.id))
    
    books = result.all()

    if not books:
        return []

    return books

@router.get('/cart/items', response_model=list[CartItem], status_code=status.HTTP_200_OK)
async def get_buyer_cart_items(db: AsyncSession = Depends(get_db), current_buyer: UserModel = Depends(get_current_buyer)):
    result = await db.scalars(select(CartModel)
                              .options(selectinload(CartModel.book).selectinload(BookModel.seller))
                              .where(CartModel.buyer_id == current_buyer.id))
    items = result.all()

    if not items:
        return []
    
    return items


@router.get('/book/{book_id}', response_model=BookSchema, status_code=status.HTTP_200_OK)
async def get_book_info(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(BookModel)
                              .options(selectinload(BookModel.seller))
                              .where(BookModel.id == book_id))
    book = result.first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Книга не найдена!'
        )

    return book

@router.post('/cart/add/{book_id}', status_code=status.HTTP_201_CREATED)
async def add_book_to_cart(book_id: int, db: AsyncSession = Depends(get_db), 
                           current_buyer: UserModel = Depends(get_current_buyer)):
    result = await db.scalars(select(BookModel).where(BookModel.id == book_id))
    book = result.first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Книга не найдена!'
        )


    book_stmt = await db.scalars(select(CartModel)
                                 .options(selectinload(CartModel.book))
                                 .where(CartModel.book_id == book_id))
    has_book = book_stmt.first()

    if not has_book:
        new_book = CartModel(
            buyer_id=current_buyer.id,
            book_id=book_id,
            total_price=book.price
        )

        db.add(new_book)
        await db.commit()
        return {'message': 'Товар добавлен в корзину'}
    
    has_book.quantity += 1
    has_book.total_price = has_book.quantity * has_book.book.price

    await db.commit()
    await db.refresh(has_book)

    return has_book