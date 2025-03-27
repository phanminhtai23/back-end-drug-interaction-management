# routes/drugs.py
from fastapi import APIRouter, HTTPException, Depends
from utils.security import get_current_user
from database import drugs_collection
from schemas.drug import Drug

router = APIRouter()

# Lất tất cả các thuốc /drugs
@router.get("/")
async def get_all_drugs(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    drugs = await drugs_collection.find().to_list(100)
    
    # Filter and validate drugs
    valid_drugs = []
    for drug in drugs:
        try:
            valid_drugs.append(Drug(**drug))
        except Exception as e:
            print(f"Validation error: {e}, skipping invalid drug: {drug}")

    return {"message": "Got drugs successfully", "drugs": valid_drugs}


# Thêm một thuốc mới
@router.post("/")
async def add_drug(drug: Drug, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    existing_drug = await drugs_collection.find_one({"id": drug.id})
    if existing_drug:
        raise HTTPException(status_code=400, detail="Thuốc đã tồn tại !!")
    await drugs_collection.insert_one(drug.model_dump())
    return {"message": "Inserted successfully", "drugs": drug}


# tới đây
# Cập nhật thông tin một thuốc
@router.put("/{drug_id}")
async def update_drug(drug_id: str, drug: Drug, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    result = await drugs_collection.update_one({"id": drug_id}, {"$set": drug.model_dump()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "Drug updated successfully", "drug": drug}


# Xóa một thuốc
@router.delete("/{drug_id}")
async def delete_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    result = await drugs_collection.delete_one({"id": drug_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "Drug deleted successfully"}