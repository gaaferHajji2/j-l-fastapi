from fastapi import FastAPI, status

app = FastAPI()

@app.get('/home', status_code=status.HTTP_200_OK)
async def get_home():
    return { "home": "Main Page - Home" }