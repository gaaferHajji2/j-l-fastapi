from fastapi import FastAPI

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get('/hello')
async def hello():
    return {"msg": "Hello World With SQLModel And Migration Example"}