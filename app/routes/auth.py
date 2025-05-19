from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.user import UserCreate, UserInDB, UserUpdate
from app.utils.security import get_password_hash, create_access_token, verify_password
from app.config.settings import settings
from bson import ObjectId
import secrets
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType  # Added MessageType

router = APIRouter()

# Updated Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME="mail.gacode@gmail.com",
    MAIL_PASSWORD="xxez uwik lwdn lstz",
    MAIL_FROM="mail.gacode@gmail.com",
    MAIL_PORT=465,  # Changed from 587 to 465
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,  # Changed for port 465
    MAIL_SSL_TLS=True,  # Changed for port 465
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TIMEOUT=30  # Added timeout
)

async def get_user_by_email(db: AsyncIOMotorClient, email: str) -> UserInDB | None:
    user = await db["users"].find_one({"email": email})
    if user:
        user["id"] = str(user["_id"])
        return UserInDB(**user)
    return None

async def get_db():
    return router.db

@router.post("/register", response_model=UserInDB)
async def register(user_data: UserCreate, db: AsyncIOMotorClient = Depends(get_db)):
    if await get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict(exclude={"password"})
    user_dict.update({
        "password_hash": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    result = await db["users"].insert_one(user_dict)
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    created_user["id"] = str(created_user["_id"])
    return UserInDB(**created_user)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorClient = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.patch("/users/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    db: AsyncIOMotorClient = Depends(get_db)
):
    update_dict = update_data.dict(exclude_unset=True)
    if "password" in update_dict:
        update_dict["password_hash"] = get_password_hash(update_dict.pop("password"))
    
    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_dict}
    )
    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    updated_user["id"] = str(updated_user["_id"])
    return UserInDB(**updated_user)

@router.post("/password-reset/request")
async def request_password_reset(
    email: str = Body(..., embed=True),
    db: AsyncIOMotorClient = Depends(get_db)
):
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    reset_token = secrets.token_urlsafe(32)
    await db["users"].update_one(
        {"email": email},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_expires": datetime.utcnow() + timedelta(hours=1)
        }}
    )
    
    # Updated MessageSchema with required fields
    message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        body=f"Your reset token: {reset_token}",
        subtype=MessageType.plain,  # Required field
        template_body=None  # Added to prevent validation errors
    )
    
    await FastMail(conf).send_message(message)
    return {"message": "Reset email sent"}

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    token: str = Body(...),
    new_password: str = Body(...),
    db: AsyncIOMotorClient = Depends(get_db)
):
    user = await db["users"].find_one({
        "reset_token": token,
        "reset_token_expires": {"$gt": datetime.utcnow()}
    })
    if not user:
        raise HTTPException(status_code=400, detail="Invalid/expired token")
    
    await db["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": get_password_hash(new_password)},
         "$unset": {"reset_token": "", "reset_token_expires": ""}}
    )
    return {"message": "Password updated"}