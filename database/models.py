from datetime import datetime
import enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import DateTime, String, Numeric, ForeignKey, Enum



class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    SELLER = 'seller'
    BUYER = 'buyer'



class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32))
    hashed_password: Mapped[str] = mapped_column(String(512))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.BUYER)

    books: Mapped[list['BookModel']] = relationship('BookModel', back_populates='seller')
    cart: Mapped[list['CartModel']] = relationship('CartModel', back_populates='buyer')
    orders: Mapped[list['OrderModel']] = relationship('OrderModel', back_populates='buyer')


class BookModel(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(512))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    year: Mapped[str] = mapped_column(String(4))

    seller_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    seller: Mapped['UserModel'] = relationship('UserModel', back_populates='books')
    cart: Mapped[list['CartModel']] = relationship('CartModel', back_populates='book')
    order_items: Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='book') 



class CartModel(Base):
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'))
    quantity: Mapped[int] = mapped_column(default=1)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2))

    buyer: Mapped['UserModel'] = relationship('UserModel', back_populates='cart')
    book: Mapped['BookModel'] = relationship('BookModel', back_populates='cart')



class OrderModel(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    total_price: Mapped[float] = mapped_column(Numeric(10, 2))
    payment_status: Mapped[str] = mapped_column(String(20), default='pending')
    payment_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='order')
    buyer: Mapped['UserModel'] = relationship('UserModel', back_populates='orders')


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'))
    quantity: Mapped[int] = mapped_column()
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    total_price: Mapped[float] = mapped_column(Numeric(10,2))

    order: Mapped['OrderModel'] = relationship('OrderModel', back_populates='items')
    book: Mapped['BookModel'] = relationship('BookModel', back_populates='order_items')
