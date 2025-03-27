# routes/ddi.py
from fastapi import APIRouter, HTTPException, Depends
from utils.security import get_current_user
from utils.generate_id_for_DDIs import generate_id
from database import ddi_collection
from schemas.ddi import DDI, deleteRequest

router = APIRouter()


# Lất tất cả các cặp tương tác thuốc
@router.get("/")
async def get_all_ddis(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    ddis = await ddi_collection.find().to_list(1000)

    # Filter and validate ddi
    valid_ddis = []
    for ddi in ddis:
        try:
            valid_ddis.append(DDI(**ddi))
        except Exception as e:
            print(f"Validation error: {e}, skipping invalid ddi: {ddi}")

    return {"message": "Got DDIs successfully", "ddi": valid_ddis}


# Thêm một file tương tác
@router.post("/")
async def add_drug(ddi: DDI, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not ddi:
        raise HTTPException(status_code=404, detail="DDI not found")
    
    existing_drug = await ddi_collection.find_one({"id": ddi.id})
    if existing_drug:
        raise HTTPException(status_code=400, detail="Cặp tương tác thuốc này đã tồn tại !!")
    await ddi_collection.insert_one(ddi.model_dump())
    return {"message": "Inserted DDI successfully", "ddi": ddi}



# Cập nhật thông tin một thuốc
@router.put("/{ddi_id}")
async def update_drug(ddi_id: str, ddi: DDI, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await ddi_collection.find_one({"id": ddi_id})
    if not result:
        raise HTTPException(status_code=404, detail="Drug not found")
    
    generation_id = generate_id(ddi.HoatChat_1, ddi.HoatChat_2)
    # Đã có thay đổi tên hoạt chất
    if generation_id != ddi_id:
        
        ddi.id = generation_id
        exist_ddi = await ddi_collection.find_one({"id": generation_id})
        if exist_ddi:
            raise HTTPException(status_code=400, detail="Cặp tương tác thuốc này đã tồn tại !!")
    ddi.id = generation_id
    result = await ddi_collection.update_one({"id": ddi_id}, {"$set": ddi.model_dump()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "DDI updated successfully", "ddi": ddi}


# Xóa một thuốc
@router.delete("/{drug_id}")
async def delete_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await ddi_collection.delete_one({"id": drug_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="DDIs not found")
    return {"message": "DDIs deleted successfully"}
