from pydantic import BaseModel
from typing import List, Optional

class HoatChat(BaseModel):
    tenHoatChat: str
    nongDo: str

class Drug(BaseModel):
    id: str
    tenThuoc: str
    dotPheDuyet: str
    soQuyetDinh: str
    pheDuyet: str
    hieuLuc: Optional[str]
    soDangKy: str
    hoatChat: List[HoatChat]
    phanLoai: Optional[str]
    taDuoc: Optional[str]
    baoChe: str
    dongGoi: str
    tieuChuan: str
    tuoiTho: str
    congTySx: str
    congTySxCode: str
    nuocSx: str
    diaChiSx: str
    congTyDk: str
    nuocDk: str
    diaChiDk: str
    nhomThuoc: str