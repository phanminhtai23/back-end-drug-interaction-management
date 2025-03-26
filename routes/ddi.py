# routes/ddi.py
from fastapi import APIRouter, HTTPException
from database import ddi_collection
from schemas.ddi import DDI

router = APIRouter()


@router.get("/", response_model=list[DDI])
async def get_all_ddi():
    return await ddi_collection.find().to_list(100)


@router.post("/", response_model=DDI)
async def add_ddi(ddi: DDI):
    await ddi_collection.insert_one(ddi.dict())
    return ddi
