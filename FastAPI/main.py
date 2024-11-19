from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone


class User(BaseModel):
    name: str = Field(..., min_length=1) # requires name length of at least 1
    email: EmailStr
    password: str

class Login(BaseModel):
   email: EmailStr
   password: str

class Token(BaseModel):
   access_token: str
   token_type: str

class TokenData(BaseModel):
   email: EmailStr

# password hashing setup
pwd_cxt = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

# hashing functions
class Hash():
    @staticmethod
    # Accepts password(str) and returns hashed password(str)
    def bcrypt(password:str) -> str:
        return pwd_cxt.hash(password)
    
    @staticmethod
    # Accepts plaintext password, hashed password, and returns bool for verification
    def verify(hashed: str, plain: str) -> bool:
        return pwd_cxt.verify(plain, hashed)
    
# token setup
SECRET_KEY = "URgbP75FiM!YkZPF535UZPucsUR*G8*@zt" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

# Ceate JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy() # copy input data
    if expires_delta: # set expiration time
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire}) # update expiration time 
        return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM) # encode token


def verify_token(token:str,credentials_exception: HTTPException):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		email: EmailStr = payload.get("sub")
		if email is None: # exception if no username
			raise credentials_exception
		return TokenData(email=email) # return TokenData instance
	except JWTError: # exception if token invalid/expired
	    raise credentials_exception

# Users post credentials to the /login endpoint to obtain access token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#checks if token is valid to return user 
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=401,
        detail= "Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return verify_token(token, credentials_exception)


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
mongodb_uri = 'mongodb://localhost:27017/DebuggerData'
client = AsyncIOMotorClient(mongodb_uri)
database = client["DebuggerData"]
users = database["Users"]


@app.post('/register')
async def create_user(request: User):
    # check if email already in use
    existing_user = await users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # hash the password
    hashed_pass = Hash.bcrypt(request.password)

    # create User object
    user_object = dict(request)
    user_object["password"] = hashed_pass

    # Insert the new user into the database
    result = await users.insert_one(user_object)
    if result.inserted_id:
        return {"res": "created"}
    else:
        raise HTTPException(status_code=500, detail="User registration failed")

@app.post('/login')
async def login(request: OAuth2PasswordRequestForm = Depends()):
    # find user with given email
    user = await users.find_one({"email": request.username})
    if not user:
        raise HTTPException(status_code=404, detail="No user found with this email")

    # checks given password is correct
    if not Hash.verify(user["password"], request.password):
        raise HTTPException(status_code=403, detail="Incorrect email or password")

    # creates access token
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {"access_token": access_token, "token_type": "bearer"}

#@app.post('/forgot-password')
