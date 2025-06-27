from fastapi import FastAPI

app = FastAPI()

@app.get('/hello')
async def hello():
    return {"msg": "Hello World With SQLModel And Migration Example"}