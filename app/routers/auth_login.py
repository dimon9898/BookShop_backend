from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import UserModel
from database.db_init import get_db
from app.schemes.auth_schema import RegisterForm, LoginResponse
from app.auth import hash_password, verify_password, create_access_token



router = APIRouter(prefix='/auth', tags=['Авторизация | Аутентификация'])



@router.post('/register', status_code=status.HTTP_200_OK)
async def register(form: RegisterForm, db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(UserModel).where(UserModel.username == form.username))
    user = result.first()

    if user:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail='Пользователь с таким именем уже существует!'
        )
    
    new_user = UserModel(username=form.username,
                         hashed_password=hash_password(form.plain_password),
                         role=form.role
                         )
    db.add(new_user)
    await db.commit()

    return {'message': 'Вы успешно зарегистрировались!'}


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(UserModel).where(UserModel.username == form.username))
    user = result.first()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неправильный логин или пароль!'
        )
    
    access_token = await create_access_token(data={'sub': user.username, 'role': user.role})

    return LoginResponse(
        access_token=access_token,
        token_type='bearer'
    )