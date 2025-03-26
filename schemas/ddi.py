from pydantic import BaseModel


class DDI(BaseModel):
    TenThuoc: str
    HoatChat_1: str
    HoatChat_2: str
    MucDoNghiemTrong: str
    CanhBaoTuongTacThuoc: str
