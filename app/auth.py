from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from database.db_init import get_db
from database.models import UserModel

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/login')


def hash_password(plain_password: str) -> str:
    pwd_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hshd_pwd = bcrypt.hashpw(pwd_bytes, salt)
    return hshd_pwd.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_pwd_bytes = plain_password.encode('utf-8')
    hshd_pwd_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_pwd_bytes, hshd_pwd_bytes)



async def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_MINUTE)
    to_encode.update({'exp': expires_at})
    access_token = jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), settings.ALGORITHM)
    return access_token






async def get_current_user(token: str = Depends(oauth2_schema), db: AsyncSession = Depends(get_db)):
    credentials_exception = (
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось проверить ваши данные.'
        )
    )

    try:
        data = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM])
        username = data.get('sub')

        if username is None:
            raise credentials_exception

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Токен просрочен!'
        )    
    except JWTError:
        raise credentials_exception
    
    user = await db.scalar(select(UserModel).where(UserModel.username == username))

    if not user:
        raise credentials_exception

    return user



async def get_current_seller(user: UserModel = Depends(get_current_user)):

    if user.role != 'seller':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Доступ разрещен только продавцам!'
        )
    
    return user


async def get_current_buyer(user: UserModel = Depends(get_current_user)):

    if user.role != 'buyer':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Доступ разрещен только покупателям!!'
        )
    
    return user