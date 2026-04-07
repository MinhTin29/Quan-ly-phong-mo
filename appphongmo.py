import streamlit as st
from database import connect_db
import app_bacsi, app_xeplich

st.set_page_config(page_title="Quản lý phòng mổ Hoàn Mỹ", layout="wide")

# Khởi tạo trạng thái đăng nhập
if 'auth' not in st.session_state: st.session_state.auth = False
if 'role' not in st.session_state: st.session_state.role = None

# --- THIẾT KẾ SIDEBAR ---
st.sidebar.markdown("""
    <style>
    .sidebar-title {
        font-size: 1.5rem !important; 
        font-weight: bold;
        color: black;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 20px;
        display: block;
    }
    </style>
    <div class='sidebar-title'>🏥 Quản lý DSA</div>
    """, unsafe_allow_html=True)

if not st.session_state.auth:
    # PHẦN 1: DÀNH CHO BÁC SĨ (Luôn hiện khi chưa login)
    st.sidebar.subheader("👨‍⚕️ Mục Bác sĩ")
    menu_bs = st.sidebar.radio("Thao tác:", ["Đăng ký ca mổ", "Tra cứu lịch mổ"])
    
    st.sidebar.divider()
    
    # PHẦN 2: KHUNG ĐĂNG NHẬP
    st.sidebar.subheader("🔐 Nhân viên Hệ thống")
    u = st.sidebar.text_input("Tài khoản", placeholder="username")
    p = st.sidebar.text_input("Mật khẩu", type="password", placeholder="password")
    
    if st.sidebar.button("ĐĂNG NHẬP", use_container_width=True):
        # --- KIỂM TRA ADMIN QUA SECRETS (ƯU TIÊN) ---
        # Tín chỉ cần dán admin_password vào phần Secrets trên web Streamlit Cloud
        if u == "admin" and p == st.secrets.get("admin_password", "admin123"):
            st.session_state.auth = True
            st.session_state.role = "Admin"
            st.rerun()
        else:
            # KIỂM TRA USER THƯỜNG TRONG DATABASE
            try:
                conn = connect_db(); cur = conn.cursor()
                cur.execute("SELECT role FROM Dim_Users WHERE username=? AND password=?", (u, p))
                res = cur.fetchone()
                if res:
                    st.session_state.auth = True
                    st.session_state.role = res[0]
                    st.rerun()
                else:
                    st.sidebar.error("Sai tài khoản/mật khẩu")
            except Exception as e:
                st.sidebar.error("Lỗi kết nối dữ liệu")

    # Hiển thị giao diện Bác sĩ mặc định
    app_bacsi.show_registration(menu_bs)

else:
    # GIAO DIỆN SAU KHI ĐĂNG NHẬP THÀNH CÔNG
    st.sidebar.success(f"Quyền: {st.session_state.role}")
    
    # Phân quyền menu nội bộ
    menu_internal = []
    if st.session_state.role in ["Admin", "GiamDoc"]:
        menu_internal.append("Tổng quan")
    if st.session_state.role in ["Admin", "XepPhong"]:
        menu_internal.append("Điều phối & Vận hành")
    if st.session_state.role == "Admin":
        menu_internal.append("Quản lý Thiết bị")
        menu_internal.append("Quản lý User")
    
    task = st.sidebar.selectbox("Chức năng hệ thống:", menu_internal)
    
    if st.sidebar.button("Đăng xuất", use_container_width=True):
        st.session_state.auth = False
        st.session_state.role = None
        st.rerun()

    # Điều hướng đến các hàm tương ứng trong app_xeplich
    if task == "Tổng quan":
        app_xeplich.show_general_view()
    elif task == "Điều phối & Vận hành":
        app_xeplich.show_scheduling()
    elif task == "Quản lý Thiết bị":
        app_xeplich.show_equipment_management()
    elif task == "Quản lý User":
        app_xeplich.show_user_management()