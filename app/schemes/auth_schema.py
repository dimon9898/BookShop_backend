from pydantic import BaseModel, ConfigDict, EmailStr, Field
from database.models import UserRole



class RegisterForm(BaseModel):
    username: EmailStr = Field(..., description='Введите почту')
    plain_password: str = Field(..., min_length=8, description='Введите пароль (минимум 8 символов)')
    role: UserRole = Field(..., description='Укажите роль пользователя')



class LoginResponse(BaseModel):
    access_token: str = Field(..., description='Токен')
    token_type: str = Field(..., description='Формат токена')

    