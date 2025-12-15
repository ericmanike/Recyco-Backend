
from fastapi import APIRouter, Depends, FastAPI, File, UploadFile, HTTPException, status,Form
import cloudinary.uploader
from typing import List
from pydantic import EmailStr
from databases import Listings,get_db
from sqlalchemy.orm import Session
from models import  ListingResponse, UserResponse
from routers.auth import get_current_user
 

router = APIRouter()
@router.post("/upload", response_model=ListingResponse)
async def  list(description: str = Form(...),
                    waste_type: str = Form(...),
                    quantity: str = Form(...),
                    unit: str = Form(...),
                    location: str = Form(...),
                    contactName: str = Form(...),
                    contactEmail: EmailStr = Form(...),
                    contactPhone: str = Form(...),
                    hazardous: bool = Form(False),
        
                 files: List[UploadFile] = File(...),
                 db: Session = Depends(get_db),
                 current_user: int = Depends(get_current_user)):
                 
    image_urls = []
    
    if files and len(files) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Maximum 5 images are allowed.")
    



    for file in files:
        try:
            result = cloudinary.uploader.upload(file.file , transformation=[{"quality": "auto:best",   # auto quality, prioritize best visual quality
            "fetch_format": "auto",   
            "width": 450, 
            "height": 450,           
            "crop": "limit",          
            "dpr": "auto", 
            ""           
            "effect": "brightness:10"}])
            image_urls.append(result.get('secure_url'))

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Image upload failed: {str(e)}")
    
    listing = Listings(
        owner=current_user.id,  
        description=description,
        waste_type=waste_type,
        quantity=quantity,
        unit=unit,
        location=location,
        contactName=contactName,
        contactEmail=contactEmail,
        contactPhone=contactPhone,
        hazardous=hazardous,
        images_url=image_urls
    )

    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing