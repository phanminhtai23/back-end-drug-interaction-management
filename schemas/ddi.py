from pydantic import BaseModel


class DDI(BaseModel):
    id: str
    TenThuoc: str
    HoatChat_1: str
    HoatChat_2: str
    MucDoNghiemTrong: str
    CanhBaoTuongTacThuoc: str

class deleteRequest(BaseModel):
        HoatChat_1: str
        HoatChat_2: str