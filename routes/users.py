from fastapi import APIRouter, HTTPException, Depends
from database import users_collection, tokens_collection
from schemas.user import UserRegister, LoginRequest, UserResponse
from utils.security import hash_password, verify_password, get_current_user
from utils.jwt import create_access_token
from fastapi.encoders import jsonable_encoder
# Assuming tokens_collection is defined in database


router = APIRouter()

@router.post("/register")
async def register(user: UserRegister):
    # Check if the email is already registered
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email đã đã được đăng ký")
    
    # Hash the user's password
    user_data = user.model_dump()
    user_data["email"] = user.email
    user_data["password"] = hash_password(user.password)
    user_data["full_name"] = user.full_name
    user_data["role"] = "admin"

    print(user_data)
    
    # Insert the new user into the database
    result = await users_collection.insert_one(user_data)
    
    # Return the created user response
    return {
        "status_code": 200,
        "message": "Đăng ký tài khoản thành công",
        "user_id": str(result.inserted_id)
    }

@router.post("/login")
async def login(user: LoginRequest):
    db_user = await users_collection.find_one({"email": user.email})
    # Check if the user exists and the password is correct
    if not db_user: 
        raise HTTPException(status_code=404, detail="Email chưa đăng ký tài khoản")
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Sai mật khẩu")
    
    # Đăng nhập thành công, tạo access token
    access_token, created_at, expires_at = create_access_token(
        data={"sub": db_user["email"]})
    # Save the token to the tokens collection
    token_data = {
        "username": db_user["email"],
        "token": access_token,
        "expires_at": expires_at,
        "created_at": created_at,
        "device_info": user.device_info,
        "is_revoked": False
    }
    await tokens_collection.insert_one(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Đăng nhập thành công",
        "full_name": db_user["full_name"],
    }


@router.get("/")
async def get_all_users(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    users = await users_collection.find().to_list(100)
    valid_users = []
    for user in users:
        try:
            valid_users.append(UserRegister(**user))
        except Exception as e:
            print(f"Validation error: {e}, skipping invalid drug: {user}")

    return {"message": "Got users successfully", "users": valid_users}
