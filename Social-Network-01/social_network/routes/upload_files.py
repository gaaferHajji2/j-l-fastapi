from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import os
from pathlib import Path

router = APIRouter()
UPLOAD_DIRECTORY = "uploads"  # Directory where files will be saved
MAX_FILE_SIZE = 1024 * 1024 * 2  # 2 MB limit
ALLOWED_FILE_TYPES = {"image/jpeg", "image/png", "application/pdf"}  # Allowed MIME types

# Ensure upload directory exists
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

@router.post('/upload/', status_code=201)
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate file size
        file.file.seek(0, 2)  # Move to end of file
        file_size = file.file.tell()
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        file.file.seek(0)  # Reset file pointer
        
        # Validate file type
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Create safe filename
        file_name = file.filename
        file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
        
        # Check if file exists and modify filename if needed
        counter = 1
        while os.path.exists(file_path):
            name, ext = os.path.splitext(file_name)
            file_path = os.path.join(UPLOAD_DIRECTORY, f"{name}_{counter}{ext}")
            counter += 1
        
        # Save file asynchronously
        async with aiofiles.open(file_path, 'wb') as out_file:
            # This Will Read Only 50KB
            while content := await file.read(1024*50):  # Read in chunks
                await out_file.write(content)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully",
                "file_path": file_path,
                "file_size": str((file_size/1024/1024).__round__(2)) + " MB",
                "content_type": file.content_type
            }
        )
    except Exception as e:

        if  isinstance(e, HTTPException) :
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        raise HTTPException(status_code=500, detail=str(e))

