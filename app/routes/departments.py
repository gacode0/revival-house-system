from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.department import Department, DepartmentCreate
from bson import ObjectId
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/", response_model=Department)
async def create_department(
    department: DepartmentCreate,
    db: AsyncIOMotorClient = Depends(lambda: router.db)
):
    if await db["departments"].find_one({"name": department.name}):
        raise HTTPException(status_code=400, detail="Department exists")
    
    dept_dict = department.dict()
    dept_dict.update({
        "members": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    result = await db["departments"].insert_one(dept_dict)
    new_dept = await db["departments"].find_one({"_id": result.inserted_id})
    new_dept["id"] = str(new_dept["_id"])
    return Department(**new_dept)

@router.get("/", response_model=List[Department])
async def get_departments(db: AsyncIOMotorClient = Depends(lambda: router.db)):
    return [
        Department(**{**dept, "id": str(dept["_id"])})
        async for dept in db["departments"].find()
    ]

@router.post("/{department_id}/members/{user_id}")
async def add_member(
    department_id: str,
    user_id: str,
    db: AsyncIOMotorClient = Depends(lambda: router.db)
):
    # Verify department exists
    department = await db["departments"].find_one({"_id": ObjectId(department_id)})
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Update both records transactionally
    await db["departments"].update_one(
        {"_id": ObjectId(department_id)},
        {"$addToSet": {"members": user_id}}
    )
    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"department": department["name"]}}
    )
    return {"message": "Member added"}

@router.delete("/{department_id}/members/{user_id}")
async def remove_member(
    department_id: str,
    user_id: str,
    db: AsyncIOMotorClient = Depends(lambda: router.db)
):
    await db["departments"].update_one(
        {"_id": ObjectId(department_id)},
        {"$pull": {"members": user_id}}
    )
    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$unset": {"department": ""}}
    )
    return {"message": "Member removed"}