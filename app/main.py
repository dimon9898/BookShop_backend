from fastapi import FastAPI



app = FastAPI()


@app.get('/')
async def solo():
    return {'message': 'FastAPI is ready!'}

