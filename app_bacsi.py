import streamlit as st
import pandas as pd
from database import connect_db
from utils import LIST_KHOA

def show_registration(mode):
    conn = connect_db()
    cur = conn.cursor()
    
    if mode == "Đăng ký ca mổ":
        st.title("📝 ĐĂNG KÝ CA PHẪU THUẬT")
        
        # Lấy danh sách thiết bị từ kho (chỉ lấy máy còn số lượng > 0)
        cur.execute("SELECT equip_name FROM Dim_Equipments WHERE quantity > 0")
        list_from_db = [r[0] for r in cur.fetchall()]
        # Tạo danh sách chọn: Mặc định là 'Không', sau đó là các máy trong kho
        list_equips = ["Không"] + list_from_db

        with st.form("reg_form_bs", clear_on_submit=True):
            st.subheader("I. Thông tin Hành chính")
            c1, c2 = st.columns(2)
            myt = c1.text_input("1. Mã Y tế (MYT) *", placeholder="Nhập mã số bệnh nhân")
            ten_bn = c1.text_input("2. Tên Bệnh nhân")
            nam_sinh = c1.text_input("3. Năm sinh", value="1990")
            
            msnv = c2.text_input("4. Mã nhân viên Bác sĩ *", placeholder="Nhập MSNV của bạn")
            ten_bs = c2.text_input("5. Tên Bác sĩ phẫu thuật")
            email = c2.text_input("6. Email liên hệ (Để nhận thông báo)")
            
            st.divider()
            st.subheader("II. Chi tiết chuyên môn & Thiết bị")
            khoa = st.selectbox("7. Chuyên khoa", LIST_KHOA)
            dv = st.text_input("8. Tên dịch vụ kỹ thuật (Tên ca mổ)")
            loai = st.selectbox("9. Hình thức phẫu thuật", ["Nội soi", "Mổ hở"])
            
            # MỤC THIẾT BỊ XỔ XUỐNG: Nếu không cần thì chọn "Không cần"
            tb_yeu_cau = st.selectbox("10. Thiết bị hỗ trợ (Chọn từ danh mục kho)", list_equips)
            
            c3, c4, c5 = st.columns(3)
            ngay = c3.date_input("11. Ngày mổ dự kiến")
            gio = c4.time_input("12. Giờ mổ dự kiến")
            phut = c5.number_input("13. Thời gian dự kiến (phút)", value=60, step=15)
            
            ghi_chu = st.text_area("14. Ghi chú bổ sung (Dụng cụ đặc biệt, bệnh nền...)")

            # Nút gửi hồ sơ
            submit_btn = st.form_submit_button("GỬI HỒ SƠ ĐĂNG KÝ")
            
            if submit_btn:
                if not myt or not msnv:
                    st.error("❌ Vui lòng điền đầy đủ Mã Y tế và Mã nhân viên!")
                else:
                    try:
                        cur.execute("""
                            INSERT INTO surgeries (
                                ma_y_te, ten_bn, nam_sinh, msnv_bs, ten_bs, email_bs, 
                                chuyen_khoa, ten_dich_vu, loai_mo, thiet_bi_yeu_cau, 
                                ngay_dang_ky_mo, gio_dang_ky_mo, du_kien_phut, ghi_chu, trang_thai
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """, (
                            myt, ten_bn, nam_sinh, msnv, ten_bs, email, 
                            khoa, dv, loai, tb_yeu_cau, 
                            str(ngay), str(gio)[:5], phut, ghi_chu, 'Chờ xếp phòng'
                        ))
                        conn.commit()
                        st.success(f"✅ Đã gửi hồ sơ BN {ten_bn} thành công! Trạng thái: Chờ xếp phòng.")
                    except Exception as e:
                        st.error(f"Lỗi lưu dữ liệu: {e}")

    elif mode == "Tra cứu lịch mổ":
        st.title("🔍 TRA CỨU TRẠNG THÁI HỒ SƠ")
        search_myt = st.text_input("Nhập Mã Y tế để kiểm tra lịch mổ:", placeholder="Ví dụ: 24001234")
        
        if search_myt:
            # Truy vấn lấy thông tin chi tiết bao gồm Phòng và Giờ đã được xếp
            query = """
                SELECT ten_bn, trang_thai, phong_mo_an_dinh, gio_dang_ky_mo, ngay_dang_ky_mo, thiet_bi_yeu_cau 
                FROM surgeries 
                WHERE ma_y_te = ? 
                ORDER BY id DESC
            """
            df = pd.read_sql_query(query, conn, params=(search_myt,))
            
            if not df.empty:
                st.write(f"Kết quả cho bệnh nhân: **{df.iloc[0]['ten_bn']}**")
                
                # Định dạng lại bảng hiển thị cho chuyên nghiệp
                df_view = df.rename(columns={
                    'ten_bn': 'Bệnh nhân',
                    'trang_thai': 'Trạng thái hiện tại',
                    'phong_mo_an_dinh': 'Phòng mổ',
                    'gio_dang_ky_mo': 'Giờ mổ',
                    'ngay_dang_ky_mo': 'Ngày mổ',
                    'thiet_bi_yeu_cau': 'Thiết bị'
                })
                
                # Xử lý hiển thị giá trị trống
                df_view['Phòng mổ'] = df_view['Phòng mổ'].fillna("Đang sắp xếp...")
                
                # Hiển thị dạng bảng
                st.table(df_view)
                
                # Thông báo tóm tắt bằng màu sắc
                latest_status = df.iloc[0]['trang_thai']
                if latest_status == 'Chờ xếp phòng':
                    st.warning("🟡 Hồ sơ đang chờ Bộ phận Điều phối xếp phòng.")
                elif latest_status == 'Đã xếp lịch':
                    st.success(f"🟢 Ca mổ đã được xếp tại **{df.iloc[0]['phong_mo_an_dinh']}** lúc **{df.iloc[0]['gio_dang_ky_mo']}**.")
                elif latest_status == 'Đang mổ':
                    st.info("🔵 Ca mổ đang diễn ra.")
                elif latest_status == 'Hoàn tất':
                    st.success("⚪ Ca mổ đã kết thúc thành công.")
            else:
                st.info("Chưa có hồ sơ nào được đăng ký với Mã Y tế này.")

    conn.close()