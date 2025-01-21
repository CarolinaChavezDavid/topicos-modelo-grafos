from fastapi import FastAPI, HTTPException, Depends
from pymemcache.client import base
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Optional

app = FastAPI()
memcache_client = base.Client(("localhost", 11211))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class User(BaseModel):
    username: str
    user_type: str  # "premium" or "freepremium"

class UserInDB(User):
    hashed_password: str

def get_user(username: str) -> Optional[UserInDB]:
    user_data = memcache_client.get(username)
    if user_data:
        user_dict = json.loads(user_data)
        return UserInDB(**user_dict)
    return None

def save_user(user: UserInDB):
    memcache_client.set(user.username, json.dumps(user.dict()))

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    user = get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

def get_current_premium_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != "premium":
        raise HTTPException(status_code=403, detail="Access forbidden for non-premium users")
    return current_user

# Routes
@app.post("/register")
def register(username: str, password: str, user_type: str):
    if get_user(username):
        raise HTTPException(status_code=400, detail="User already exists")
    if user_type not in ["premium", "freepremium"]:
        raise HTTPException(status_code=400, detail="Invalid user type")

    hashed_password = hash_password(password)
    user = UserInDB(username=username, user_type=user_type, hashed_password=hashed_password)
    save_user(user)
    return {"message": "User registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/protected-premium")
def protected_premium_route(current_user: User = Depends(get_current_premium_user)):
    return {"message": f"Welcome, premium user {current_user.username}!"}

@app.get("/protected-freepremium")
def protected_freepremium_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user.username}! You have access to freepremium content."}