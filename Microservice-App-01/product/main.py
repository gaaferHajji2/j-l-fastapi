from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from redis_om.model.model import NotFoundError

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
    db=0,
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

def format(pk: str):
    product = Product.get(pk)
    return {
        "pk": pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
    }

@app.get('/products')
async def get_all_products():
    return [format(pk) for pk in Product.all_pks()]

@app.post('/products')
async def create_product(product: Product):
    product.save()
    return product

@app.get("/product/{pk}")
async def get_product_by_pk(pk: str):
    try:
        return format(pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail={"msg": "Model Not Found"})

@app.delete("/product/{pk}")
async def delete_product_by_pk(pk: str):
    return Product.delete(pk)
