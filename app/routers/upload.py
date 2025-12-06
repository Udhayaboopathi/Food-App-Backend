"""
Upload Router
Handles file uploads for images
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import shutil
from pathlib import Path
import uuid
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["Upload"])

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile) -> bool:
    """Validate image file type and size"""
    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return True


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a single image
    Returns the URL to access the image
    """
    validate_image(file)
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    finally:
        file.file.close()
    
    # Return URL
    return {
        "filename": unique_filename,
        "url": f"/uploads/{unique_filename}",
        "uploaded_at": datetime.now().isoformat()
    }


@router.post("/images")
async def upload_multiple_images(files: List[UploadFile] = File(...)):
    """
    Upload multiple images
    Returns list of URLs to access the images
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    uploaded_files = []
    
    for file in files:
        validate_image(file)
        
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": unique_filename,
                "url": f"/uploads/{unique_filename}",
                "original_name": file.filename
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save {file.filename}: {str(e)}")
        finally:
            file.file.close()
    
    return {
        "count": len(uploaded_files),
        "files": uploaded_files,
        "uploaded_at": datetime.now().isoformat()
    }


@router.delete("/image/{filename}")
async def delete_image(filename: str):
    """
    Delete an uploaded image
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        return {"message": "File deleted successfully", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
