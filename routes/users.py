from fastapi import APIRouter, HTTPException
from database import users_collection
from schemas.user import UserCreate, UserResponse
from utils.security import hash_password, verify_password

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_pw
    result = await users_collection.insert_one(user_data)
    return UserResponse(id=str(result.inserted_id), **user.dict())


@router.post("/login")
async def login(user: UserCreate):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": str(db_user["_id"])}


@router.get("/", response_model=list[UserResponse])
async def get_all_users():
    users = await users_collection.find().to_list(100)
    return [UserResponse(id=str(user["_id"]), **user) for user in users]
