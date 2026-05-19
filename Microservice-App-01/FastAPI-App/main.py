from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*']
)
redis = get_redis_connection(
    host = "localhost",
    port = 6379,
    decode_responses = True,
)

class Product(HashModel, index=True):
    name: str
    price: float
    quantity: int

    class Meta:
        database: redis

class Delivery(HashModel, index = True):
    budget: int = 0
    notes: str = ''

    class Meta:
        database=redis

class Event(HashModel, index = True):
    delivery_id: str = None
    type: str = ''
    data: str = ''

    class Meta:
        database=redis

@app.post('/deliveries/create')
async def create_delivery(request: Request):
    body = await request.json()
    delivery = Delivery(budget=body['data']['budget'], notes=body['data']['notes']).save()
    return delivery