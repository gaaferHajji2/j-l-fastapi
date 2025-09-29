from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/")
async def getFile(file: UploadFile = File(...)):
    # await file.seek(0, 2); # not valid now

    # t1 = file.tell() # Not valid now

    # await file.seek(0)

    return { "file": file.filename, "size": file.size / 1024 if file.size is not None else 0}