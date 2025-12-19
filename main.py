from fastapi import FastAPI
from routers import auth
from routers import upload
from routers  import users

from fastapi.middleware.cors import CORSMiddleware



origins = [
     "https://recyco-fe-hxbm.vercel.app",
     "https://recyco-fe-83wv.vercel.app",
      "https://recyco.me",
      "https://www.recyco.me",

     "http://localhost:3000",
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get('/')
async def root():
    return {"message":"Welcome to  RecycleHub Backend!"}

app.include_router(auth.router, tags=['Authentication'], prefix='/auth')
app.include_router(upload.router, tags=['Upload'], prefix='/upload')
app.include_router(users.router, tags=['User Listings'], prefix='/users')


#app.include_router(auth.router, tags=['Authentication second one'])





