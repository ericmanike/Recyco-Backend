from fastapi import FastAPI, UploadFile,Form,File, status, HTTPException,Depends  
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import JWTError,jwt
from passlib.context import CryptContext
from pydantic import BaseModel,EmailStr
from typing import Optional,List
from datetime import datetime, timedelta
from sqlalchemy import create_engine,Integer,String,Column,Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.middleware.cors import CORSMiddleware
from config import DATABASE_URL
import cloudinary
import cloudinary.uploader
from config import CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME
from config import SECRETE_KEY,ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM

print('These are the AUTH SECRETS', SECRETE_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM)


cloudinary.config(
cloud_name = CLOUDINARY_CLOUD_NAME,
api_key = CLOUDINARY_API_KEY,
api_secret = CLOUDINARY_API_SECRET
)





DATABASE_URL ="postgresql+psycopg2://postgres:is2004not2003@localhost:5000/wastocash"

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
sessionLocal = sessionmaker(bind=engine)


SECRETE_KEY ='114e56fd509b3b1785ef792487eccd25aaca340f21881536eb8ef4190d53f782'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE = 30

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme =OAuth2PasswordBearer(tokenUrl='/Login')
def get_hashed_password(password):
    return password_context.hash(password)






#database
class users(Base):
    __tablename__ ='users'
    id = Column(Integer, primary_key=True)
    fullName = Column(String)
    email = Column(String, unique=True)
    role = Column(String)
    phone = Column(String)
    password = Column(String)
    


    class  chat(Base):
        __tablename__ = 'chat'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer)
        message = Column(String)
        timestamp = Column(String)


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    email:str


class UserCreate(BaseModel):
    fullName:str
    email:EmailStr
    password:str
    role: str
    phone:str


class UserResponse(BaseModel):
    fullName:str
    email:EmailStr
    role: str
    phone:str

    class Config:
        from_attributes =True



#main utils
def verify_password(plain_password,hashed_password):
    return password_context.verify(plain_password,hashed_password)
  

def get_user(identifier:str,db:Session):
        user_data = db.query(users).filter((users.email == identifier) ).first()
        return user_data
        

def authenticate(email:str, password:str, db:Session):
             user = get_user(email,db)
             if not user:
                return False
             if not verify_password(password,user.password):
                return False
             return user


def create_access_token(data:dict, expire_timedelta:timedelta | None = None ):
     to_encode = data.copy()
     if  expire_timedelta:
          expire = datetime.utcnow() + expire_timedelta
     else:
          expire = datetime.utcnow() + timedelta(minutes=30)
     to_encode.update({'exp':expire})
     encode_jwt = jwt.encode(to_encode,SECRETE_KEY,algorithm=ALGORITHM)
     return encode_jwt

async def get_current_user(token:str = Depends(oauth2_scheme),
                           db:Session = Depends(get_db)):
     
     credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                           detail='could not validate credentials',
                                           headers={'WWW-Authenticate':'BEARER'})
    
     try:
          
          payload = jwt.decode(token,SECRETE_KEY, algorithms=[ALGORITHM])
          email:str = payload.get('sub')
          if email is None:
               raise credential_exception
          token_data = TokenData(email=email)
          user = get_user(token_data.email, db)

          if user is None:
               raise credential_exception
          return user
     except JWTError:
          raise credential_exception


async  def get_active_user( current_user:users = Depends(get_current_user)):
    if not current_user:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail='Inactive user user')
    return current_user
    
     
          

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/signUp', response_model=UserResponse)
async def signup(user:UserCreate,db:Session = Depends(get_db)):
    existing_user = db.query(users).filter(users.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f'Email {existing_user.email} already exist')
        
    hashed_password = get_hashed_password(user.password)
    new_user = users(fullName = user.fullName,
                       email = user.email, password = hashed_password, 
                       role=user.role, phone=user.phone)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user





@app.post('/Login', response_model=Token)
async  def login_acces_token(form_data:OAuth2PasswordRequestForm = Depends(), db:Session =Depends(get_db)):
     user = authenticate(form_data.username,form_data.password,db)
     if not user:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='incorrect username or password')

     access_token_expire =timedelta(minutes=ACCESS_TOKEN_EXPIRE)
     access_token = create_access_token(data={'sub':user.email}, expire_timedelta=access_token_expire)
     return {'access_token':access_token, 'token_type':'bearer'}
     


@app.post('/user/me', response_model=UserResponse)
async def get_current(user:users=Depends(get_active_user)):
     return user


@app.get('/users', response_model=List[UserResponse])
async def get_all_users(db:Session = Depends(get_db),user:users = Depends(get_active_user)):
    All_users = db.query(users).all()
    return All_users


