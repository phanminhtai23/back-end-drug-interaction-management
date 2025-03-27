# routes/ddi.py
from fastapi import APIRouter, HTTPException, Depends
from utils.security import get_current_user
from utils.generate_id_for_DDIs import generate_id
from database import ddi_collection
from schemas.ddi import DDI
from schemas.urls import ExtractRequest
import requests
from utils.gemini_model import GeminiModel
import io
import PIL.Image

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
        raise HTTPException(
            status_code=400, detail="Cặp tương tác thuốc này đã tồn tại !!")
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
            raise HTTPException(
                status_code=400, detail="Cặp tương tác thuốc này đã tồn tại !!")
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
    if not drug_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy id thuốc")

    result = await ddi_collection.delete_one({"id": drug_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="DDIs not found")
    return {"message": "DDIs deleted successfully"}


# Trích DDIs từ file pdf
@router.post("/extract")
async def extract_ddi_from_pdf(document_urls: ExtractRequest, user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    gemini_model = GeminiModel()

    # Không tìm thấy url
    if not document_urls:
        raise HTTPException(status_code=404, detail="document urls not found")

    # Kiểm tra dữ liệu hợp lệ
    if not document_urls.document_urls:
        raise HTTPException(
            status_code=400, detail="Không có dữ liệu được gửi")

    # Kiểm tra nếu gửi toàn ảnh
    if all(doc.endswith((".jpg", ".jpeg", ".png")) for doc in document_urls.document_urls):
        # Tiếp tục xử lý nếu chỉ gửi ảnh
        imgs_arr = []
        for img_url in document_urls.document_urls:
            response = requests.get(img_url)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Không thể truy cập file pdf từ url: {img_url} được cung cấp")
            image = PIL.Image.open(io.BytesIO(
                response.content))
            imgs_arr.append(image)

        DDIs_from_gemini = gemini_model.images_to_DDIs(imgs_arr)

        if DDIs_from_gemini is None:
            raise HTTPException(
                status_code=404, detail=f"Không tìm thấy cặp thuốc tương tác")
        else:  # trích thành công có DDIs
            # print("Co gui anh:\n", type(DDIs_from_gemini), DDIs_from_gemini)
            return {"message": "Extracting successfully", "DDIs": DDIs_from_gemini}

    # Kiểm tra nếu gửi PDF
    elif len(document_urls.document_urls) == 1 and document_urls.document_urls[0].endswith(".pdf"):
        # Check if the PDF URL is accessible
        pdf_url = document_urls.document_urls[0]
        try:
            response = requests.get(pdf_url, allow_redirects=True)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Không thể truy cập file pdf từ url được cung cấp")
            else:  # get file pdf ok -> gọi gemini

                DDIs_from_gemini = gemini_model.pdf_to_DDIs(pdf_url)

                if DDIs_from_gemini is None:
                    raise HTTPException(
                        status_code=404, detail=f"Không tìm thấy cặp thuốc tương tác")
                else:  # trích thành công có DDIs
                    # print("type:\n", type(DDis_from_gemini), DDis_from_gemini)
                    return {"message": "Extracting successfully", "DDIs": DDIs_from_gemini}

        except Exception as e:
            raise HTTPException(status_code=404, detail=f"{str(e)}")

    # Nếu không hợp lệ
    else:
        raise HTTPException(
            status_code=400,
            detail="Dữ liệu không hợp lệ: chỉ được gửi 1 file PDF hoặc nhiều file ảnh (.jpg, .jpeg, .png)"
        )
