# routes/drugs.py
from fastapi import APIRouter, HTTPException
from database import drugs_collection
from schemas.drug import Drug

router = APIRouter()


@router.get("/", response_model=list[Drug])
async def get_all_drugs():
    print("Getting all drugs")
    drugs = await drugs_collection.find().to_list(100)
    # Xử lý dữ liệu không hợp lệ
    # Xử lý dữ liệu không hợp lệ
    valid_drugs = []
    for drug in drugs:
        try:
            # Thử chuyển đổi dữ liệu thành mô hình Drug
            valid_drugs.append(Drug(**drug))
        except Exception as e:
            # In lỗi và dữ liệu không hợp lệ
            print(f"Error: {e}")
            print(f"Invalid data: {drug}")

    # Trả về danh sách các thuốc hợp lệ
    return valid_drugs



@router.post("/", response_model=Drug)
async def add_drug(drug: Drug):
    existing_drug = await drugs_collection.find_one({"id": drug.id})
    if existing_drug:
        raise HTTPException(status_code=400, detail="Thuốc đã tồn tại !!")
    await drugs_collection.insert_one(drug.model_dump())
    return drug


@router.put("/{drug_id}")
async def update_drug(drug_id: str, drug: Drug):
    result = await drugs_collection.update_one({"id": drug_id}, {"$set": drug.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "Drug updated successfully"}


@router.delete("/{drug_id}")
async def delete_drug(drug_id: str):
    result = await drugs_collection.delete_one({"id": drug_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "Drug deleted successfully"}
