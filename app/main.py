from fastapi import FastAPI

from app.routers import auth_login, seller, buyer, order, webhook

app = FastAPI()

app.include_router(auth_login.router)
app.include_router(seller.router)
app.include_router(buyer.router)
app.include_router(order.router)
app.include_router(webhook.router)

@app.get('/')
async def solo():
    return {'message': 'FastAPI is ready!'}

