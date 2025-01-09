from fastapi import FastAPI;

app = FastAPI();

@app.get("/")
async def getHelloMessage():
    return { "Message": "Hello" };