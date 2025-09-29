from fastapi import FastAPI, File, UploadFile
import aiofiles
from pathlib import Path

UPLOAD_FOLDER = Path("JLOKA")
UPLOAD_FOLDER.mkdir(exist_ok=True)

app = FastAPI()

@app.post("/")
async def getFile(file: UploadFile = File(...)):
    # await file.seek(0, 2); # not valid now

    # t1 = file.tell() # Not valid now

    # await file.seek(0)

    file_path = UPLOAD_FOLDER / file.filename # type: ignore

    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    return { "file": file.filename, "size": file.size / 1024 if file.size is not None else 0}