from datetime  import datetime, timedelta
from fastapi import Depends, HTTPException, status, APIRouter, Response, Cookie
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi_mail import MessageType
from jose import JWTError,jwt
from passlib.context import CryptContext
import pydantic
from config import SECRETE_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from databases import users
from databases import get_db,users
from sqlalchemy.orm import Session
from models import UserCreate,TokenData,Token, UserResponse, PasswordResetRequest, PasswordResetBody
from utils.resend_email import send_email
from models import  EmailSchema
from utils.resetPasswordbody import reset_password_body



password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_hashed_password(password):
    return password_context.hash(password)

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)


def get_user(email:str,db:Session):
        user_data = db.query(users).filter((users.email == email) ).first()
        return user_data

def authenticate_user(email:str,password:str,db:Session):
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
 


async def get_current_user(token:str = Cookie(None),
                           db:Session = Depends(get_db)):
     
     credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                           detail='could not validate credentials',
                            
                                           headers={'WWW-Authenticate':'Bearer'})
     
     if not token:
          raise credential_exception
    
     try:
          payload = jwt.decode(token,SECRETE_KEY, algorithms=[ALGORITHM])
          email:str = payload.get('sub')
          user_id: int = payload.get('uid')
          if email is None:
               raise credential_exception
          token_data = TokenData(email=email, uid=user_id)
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


#reset password 

def create_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode = {"sub": email, "exp": expire, "type": "password_reset"}
    return jwt.encode(to_encode, SECRETE_KEY, algorithm=ALGORITHM)


async def reset_password( token: str, email:str, new_password:str,db:Session):
       
       try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])    
        token_email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if token_email != email or token_type != "password_reset":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        
       except JWTError:
          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        
       user = get_user(email, db)
       if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
       hashed_password = get_hashed_password(new_password)
       user.password = hashed_password
       db.commit()
       db.refresh(user)
       return {"message": "Your password has been reset "}


router = APIRouter()


@router.post('/signUp', response_model=UserResponse)
async def signup(user:UserCreate,db:Session = Depends(get_db)):
    existing_user = db.query(users).filter(users.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code =status.HTTP_409_CONFLICT,detail=f'Email {existing_user.email} already exist')
        
    hashed_password = get_hashed_password(user.password)
    new_user = users(fullName = user.fullName,
                       email = user.email, password = hashed_password, 
                       role=user.role, phone=user.phone)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user




@router.post('/login')
async  def login_acces_token(response: Response, form_data:OAuth2PasswordRequestForm =Depends(), db:Session = Depends(get_db)):
     user = authenticate_user(form_data.username,form_data.password,db)
     if not user:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='incorrect username or password')
     
     access_token_expire =timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
     access_token = create_access_token(data={'sub':user.email, 'uid': user.id}, expire_timedelta=access_token_expire)
     response.set_cookie(key="token",
                          value=access_token, 
                          httponly=True,
                          secure=True,
                          samesite="none",
                          max_age=(int(ACCESS_TOKEN_EXPIRE_MINUTES)*60),
                          path= '/',
                          )
                          
     return { "fullName": user.fullName, "email": user.email,  "role": user.role, "phone": user.phone, "userId": user.id, } 
    
@router.get('/me', response_model=UserResponse)
async def read_users_me(current_user: users = Depends(get_active_user)):
    return current_user

@router.post('/request-reset')
async def request_reset_password(email:PasswordResetRequest,  db: Session = Depends(get_db)):
    user = get_user(email.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    reset_token = create_reset_token(email.email)
    reset_link = f"http://localhost:3000/resetPassword?token={reset_token}&email={email.email}"
   
    email_body = reset_password_body(reset_link, user.fullName)  
    res =  send_email(to_email=email.email, subject="Password Reset Request", html_body=email_body)
    return res

   

@router.post('/reset-password')
async def reset_user_password(body: PasswordResetBody, db:Session= Depends(get_db)):
   return  await reset_password(body.token, body.email, body.new_password, db)


@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie(key="token",
                            secure=True,
                            samesite="none",
                            path='/')
    return {"message": "Successfully logged out"}


@router.put( 'update-profile', response_model=UserResponse)
async def update_profile(updated_user: UserResponse,
                         current_user: users = Depends(get_active_user),
                         db: Session = Depends(get_db)):
    user = db.query(users).filter(users.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.fullName = updated_user.fullName
    user.phone = updated_user.phone
    user.role = updated_user.role
    user.distance = updated_user.distance
    user.location = updated_user.location
    user.about = updated_user.about
    user.images_url = updated_user.images_url

    db.commit()
    db.refresh(user)
    return {"fullName": user.fullName, "email": user.email,  "role":
             user.role, "phone": user.phone, "userId": user.id,
               "distance": user.distance, "location": user.location, 
               "about": user.about, "images_url": user.images_url } 

