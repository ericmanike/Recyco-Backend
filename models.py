from pydantic import BaseModel, EmailStr
from fastapi_mail import MessageType
from typing import List, Optional



#-------user models-----------------
class UserCreate (BaseModel):
    fullName: str   
    email: EmailStr
    password: str
    role: str
    phone: str
    distance: Optional[float] = None  # optional field for distance
    location: Optional[str] = None
    about: Optional[str] = None
    images_url: Optional[List[str]] = []  # optional, filled after upload

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    fullName:str
    email:EmailStr
    role: str
    phone:str
    distance: Optional[float] = None  # optional field for distance
    location: Optional[str] = None
    about: Optional[str] = None
    images_url: Optional[List[str]] = []
    
    class Config:
         from_attributes=True
         orm_mode = True




#-------listings  models-----------------
class ListingCreate(BaseModel):
    owner: int
    waste_type: str
    quantity: str
    unit: str
    description: Optional[str] = None
    location: str
    contactName: str
    contactEmail: EmailStr
    contactPhone: str
    hazardous: bool = False
    images_url: Optional[List[str]] = []  # optional, filled after upload

    class Config:
        orm_mode = True


class ListingResponse(BaseModel):
    id: int
    owner: int
    waste_type: str
    quantity: str
    unit: str
    description: Optional[str]
    location: str
    contactName: str
    contactEmail: EmailStr
    contactPhone: str
    hazardous: bool
    images_url: List[str]


    class Config:
        from_attributes=True
        orm_mode = True


class ListingShchema(BaseModel):
    description: str
    waste_type: str
    quantity: str
    unit: str
    location: str
    contactName: str
    contactEmail: EmailStr
    contactPhone: str
    hazardous: bool
    images_url: List[str]

    class Config:
        orm_mode = True






#-----------auth models----------------
class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    email:str
    uid: int




class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetBody(BaseModel):
    token: str
    email: EmailStr
    new_password: str


class ChatMessageCreate(BaseModel):
    receiver_id: int
    message: str

    class Config:
        orm_mode = True

    


class notificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    category: str
    is_read: bool
    timestamp: str

    class Config:
        from_attributes=True
        orm_mode = True


class EmailSchema(BaseModel):
    recipients: List[EmailStr]
    subject: str
    body: str
    subtype: Optional[MessageType] = MessageType.html  # html or plain text
