import streamlit as st

# Danh mục chuyên khoa chuẩn của bệnh viện
LIST_KHOA = [
    "Ngoại Tim Mạch", "Ngoại Thần Kinh", "Ngoại Tiêu Hóa", 
    "Chấn thương chỉnh hình", "Sản Phụ Khoa", "Tai Mũi Họng", 
    "Răng Hàm Mặt", "Ung Bướu", "Nội soi tiêu hóa"
]

# Trạng thái hiển thị
STATUS_MAP = {
    "Chờ duyệt": {"color": "#FFB300", "icon": "🟡", "text": "Đang chờ điều phối"},
    "Đã xếp lịch": {"color": "#14B8A6", "icon": "🗓️", "text": "Đã có lịch mổ"},
    "Đang mổ": {"color": "#EF4444", "icon": "🔴", "text": "Đang phẫu thuật"},
    "Hoàn tất": {"color": "#22C55E", "icon": "🟢", "text": "Ca mổ hoàn tất"}
}