from fastapi import APIRouter, UploadFile, File
import os

router = APIRouter()

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload/")
#upload_file function to handle file uploads to the uploads directory
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"filename": file.filename, "message": "File uploaded successfully!"}


@router.get("/files/")
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return {"uploaded_files": files}


from fastapi.responses import FileResponse

@router.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}
