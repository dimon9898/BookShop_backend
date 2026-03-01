from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from database.models import UserModel, BookModel
from database.db_init import get_db

from app.schemes.seller_schema import BookSchema, BookCreate
from app.auth import get_current_seller


router = APIRouter(prefix='/seller', tags=['Эндпоинты продавца'])


@router.get('/books', response_model=list[BookSchema], status_code=status.HTTP_200_OK)
async def get_seller_books(db: AsyncSession = Depends(get_db), current_seller: UserModel = Depends(get_current_seller)):

    result = await db.scalars(select(BookModel)
                              .options(selectinload(BookModel.seller))
                              .where(BookModel.seller_id == current_seller.id))
    books = result.all()

    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='У данного продавца нет актуалных книг!'
        )

    return books



@router.post('/book/add', status_code=status.HTTP_201_CREATED)
async def add_book_by_seller(book_form: BookCreate, db: AsyncSession = Depends(get_db),
                             current_seller: UserModel = Depends(get_current_seller)):
    result = await db.scalars(select(BookModel).where(BookModel.title == book_form.title)
                              .where(BookModel.seller_id == current_seller.id))
    book = result.first()

    if book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Книга с таким названием уже существует!'
        )
    
    new_book = BookModel(**book_form.model_dump(), seller_id=current_seller.id)
    db.add(new_book)
    await db.commit()
    return {'message': 'Книга успешно добавлена.'}


@router.get('/book/{book_id}', response_model=BookSchema, status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(BookModel)
                              .options(selectinload(BookModel.seller))
                              .where(BookModel.id == book_id))
    book = result.first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Книга id=[{book_id}] не существует!'
        )
    
    return book



@router.put('/edit/{book_id}', response_model=BookSchema, status_code=status.HTTP_200_OK)
async def update_book_data(book_id: int, updated_book: BookCreate, db: AsyncSession = Depends(get_db),
                           current_seller: UserModel = Depends(get_current_seller)):
    result = await db.execute(update(BookModel)
                     .options(selectinload(BookModel.seller))
                     .where(BookModel.id == book_id, BookModel.seller_id == current_seller.id)
                     .values(**updated_book)
                     .returning(BookModel))
    
    book = result.first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Книга не найдена или у вас нет прав на её редактирование'
        )
    
    await db.refresh(book, ['seller'])
    await db.commit()
    
    return book


@router.delete('/delete/{book_id}', status_code=status.HTTP_200_OK)
async def delete_book_by_seller(book_id: int, db: AsyncSession = Depends(get_db),
                                current_seller: UserModel = Depends(get_current_seller)):
    result = await db.scalars(select(BookModel)
                              .where(BookModel.id == book_id, BookModel.seller_id == current_seller.id))
    book = result.first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Книга не найдена или у вас нет прав на её редактирование'
        )
    
    await db.execute(delete(BookModel)
                     .where(BookModel.id == book_id)
                     .where(BookModel.seller_id == current_seller.id))

    await db.commit()
    return {'message': 'Товар удален!'}