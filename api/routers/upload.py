"""
Upload Router
Handles file uploads for images with organized folder structure
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
import os
import shutil
from pathlib import Path
import uuid
from datetime import datetime
from PIL import Image
import io

router = APIRouter(prefix="/upload", tags=["Upload"])

# Create uploads directory structure
BASE_UPLOAD_DIR = Path("uploads")
RESTAURANTS_DIR = BASE_UPLOAD_DIR / "restaurants"
MENU_DIR = BASE_UPLOAD_DIR / "menu"
PROFILES_DIR = BASE_UPLOAD_DIR / "profiles"
TEMP_DIR = BASE_UPLOAD_DIR / "temp"

# Create all directories
for directory in [BASE_UPLOAD_DIR, RESTAURANTS_DIR, MENU_DIR, PROFILES_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

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


def get_upload_directory(upload_type: str) -> Path:
    """Get the appropriate upload directory based on type"""
    directories = {
        "restaurant": RESTAURANTS_DIR,
        "menu": MENU_DIR,
        "profile": PROFILES_DIR,
        "temp": TEMP_DIR
    }
    return directories.get(upload_type, TEMP_DIR)


def get_url_path(upload_type: str) -> str:
    """Get the URL path for the upload type"""
    url_paths = {
        "restaurant": "restaurants",
        "menu": "menu",
        "profile": "profiles",
        "temp": "temp"
    }
    return url_paths.get(upload_type, "temp")


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    upload_type: str = Form("temp")
):
    """
    Upload a single image to organized folder
    upload_type: 'restaurant', 'menu', 'profile', or 'temp'
    Returns the URL to access the image
    """
    validate_image(file)
    
    # Get appropriate directory
    upload_dir = get_upload_directory(upload_type)
    
    # Generate descriptive filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(file.filename)[1].lower()
    unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
    unique_filename = f"{upload_type}_{timestamp}_{unique_id}{ext}"
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    finally:
        file.file.close()
    
    # Return URL with correct subfolder path
    subfolder = get_url_path(upload_type)
    url_path = f"/uploads/{subfolder}/{unique_filename}"
    
    return {
        "filename": unique_filename,
        "url": url_path,
        "type": upload_type,
        "uploaded_at": datetime.now().isoformat()
    }


@router.post("/images")
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    upload_type: str = Form("temp")
):
    """
    Upload multiple images to organized folder
    upload_type: 'restaurant', 'menu', 'profile', or 'temp'
    Returns list of URLs to access the images
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    upload_dir = get_upload_directory(upload_type)
    uploaded_files = []
    
    for file in files:
        validate_image(file)
        
        # Generate descriptive filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(file.filename)[1].lower()
        unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
        unique_filename = f"{upload_type}_{timestamp}_{unique_id}{ext}"
        file_path = upload_dir / unique_filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            subfolder = get_url_path(upload_type)
            url_path = f"/uploads/{subfolder}/{unique_filename}"
            
            uploaded_files.append({
                "filename": unique_filename,
                "url": url_path,
                "original_name": file.filename,
                "type": upload_type
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


@router.delete("/image/{upload_type}/{filename}")
async def delete_image(upload_type: str, filename: str):
    """
    Delete an uploaded image from organized folder
    """
    upload_dir = get_upload_directory(upload_type)
    file_path = upload_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        return {"message": "File deleted successfully", "filename": filename, "type": upload_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
