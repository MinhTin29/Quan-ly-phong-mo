import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import connect_db
import io

# --- [QUAN TRỌNG] DANH SÁCH PHÒNG TOÀN HỆ THỐNG ---
# Sau này muốn đóng phòng nào chỉ cần xóa tên phòng đó khỏi list này
rooms = ["Phòng DSA", "Phòng 1", "Phòng 2", "Phòng 3", "Phòng 4"]

# --- 1. HÀM VẼ GRID ---
def draw_grid_schedule(df_day, selected_date):
    time_slots = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
    html = """
    <style>
        .grid-container { overflow-x: auto; border: 1px solid #ddd; border-radius: 4px; background: white; }
        table { border-collapse: collapse; width: 100%; font-family: sans-serif; font-size: 11px; }
        th, td { border: 1px solid #eee; padding: 6px; text-align: center; min-width: 65px; height: 50px; }
        .room-col { 
            background: #f8f9fa; font-weight: bold; position: sticky; left: 0; 
            z-index: 5; white-space: nowrap; min-width: 90px !important; border-right: 2px solid #ddd;
        }
        .cell-box { display: flex; flex-direction: column; justify-content: center; align-items: center; line-height: 1.2; }
        .p-name { font-weight: bold; }
        .p-time { font-size: 9px; }
        .slot-waiting { background: #fef08a; } 
        .slot-busy { background: #fca5a5; font-weight: bold; color: #b91c1c; }
        .slot-done { background: #86efac; color: #166534; }
    </style>
    <div class='grid-container'><table><tr><th class='room-col'>Hệ thống Phòng</th>
    """
    for ts in time_slots: html += f"<th>{ts}</th>"
    html += "</tr>"
    
    # Sử dụng danh sách rooms linh hoạt thay vì fix cứng 1 phòng
    for p_name in rooms:
        html += f"<tr><td class='room-col'>{p_name}</td>"
        for ts in time_slots:
            slot_start = datetime.combine(selected_date, datetime.strptime(ts, "%H:%M").time())
            slot_end = slot_start + timedelta(minutes=30)
            
            c_class = ""; c_text = ""
            for _, r in df_day.iterrows():
                if r['phong_mo_an_dinh'] == p_name:
                    try:
                        m_start = datetime.strptime(f"{r['ngay_dang_ky_mo']} {r['gio_dang_ky_mo'][:5]}", "%Y-%m-%d %H:%M")
                        dur = int(r['du_kien_phut']) if r['du_kien_phut'] else 60
                        m_end = m_start + timedelta(minutes=dur)
                        
                        if m_start < slot_end and m_end > slot_start:
                            if r['trang_thai'] == 'Đang mổ': c_class = "slot-busy"
                            elif r['trang_thai'] == 'Hoàn tất': c_class = "slot-done"
                            else: c_class = "slot-waiting"
                            
                            if slot_start <= m_start < slot_end:
                                name = str(r['ten_bn']).split()[-1]
                                rs = r['thoi_gian_bat_dau_tt'][11:16] if r['thoi_gian_bat_dau_tt'] else r['gio_dang_ky_mo'][:5]
                                re = r['thoi_gian_ket_thuc_tt'][11:16] if r['thoi_gian_ket_thuc_tt'] else ""
                                
                                if r['trang_thai'] == 'Đang mổ': t_info = f"{rs}-..."
                                elif r['trang_thai'] == 'Hoàn tất': t_info = f"{rs}-{re}"
                                else: t_info = r['gio_dang_ky_mo'][:5]
                                c_text = f"<div class='cell-box'><span class='p-name'>{name}</span><span class='p-time'>{t_info}</span></div>"
                            break
                    except: continue
            html += f"<td class='{c_class}'>{c_text}</td>"
        html += "</tr>"
    st.markdown(html + "</table></div>", unsafe_allow_html=True)

# --- 2. GIAO DIỆN TỔNG QUAN ---
def show_general_view():
    st.header("📊 TỔNG QUAN HỆ THỐNG PHÒNG MỔ")
    conn = connect_db()
    ngay_view = st.date_input("Ngày theo dõi:", value=datetime.now())
    
    # SỬA LẠI: Lấy dữ liệu của tất cả các phòng nằm trong danh sách rooms
    df_day = pd.read_sql_query(
        "SELECT * FROM surgeries WHERE ngay_dang_ky_mo = ?", 
        conn, params=(str(ngay_view),)
    )
    # Chỉ giữ lại các ca thuộc danh sách phòng đang mở
    df_day = df_day[df_day['phong_mo_an_dinh'].isin(rooms) | df_day['phong_mo_an_dinh'].isna()]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng ca mổ", len(df_day))
    m2.metric("Chờ thực hiện", len(df_day[df_day['trang_thai']=='Chờ xếp phòng']))
    m3.metric("Đang thực hiện", len(df_day[df_day['trang_thai']=='Đang mổ']))
    m4.metric("Hoàn tất", len(df_day[df_day['trang_thai']=='Hoàn tất']))
    
    draw_grid_schedule(df_day, ngay_view)
    
    if st.session_state.get('role') == 'Admin':
        st.divider()
        with st.expander("📥 TRÍCH XUẤT DỮ LIỆU HỆ THỐNG", expanded=False):
            c1, c2 = st.columns(2)
            d_start = c1.date_input("Từ ngày:", value=datetime.now() - timedelta(days=7))
            d_end = c2.date_input("Đến ngày:", value=datetime.now())
            if st.button("🚀 CHUẨN BỊ FILE PHÂN TÍCH", use_container_width=True):
                df_export = pd.read_sql_query(
                    "SELECT * FROM surgeries WHERE ngay_dang_ky_mo BETWEEN ? AND ?", 
                    conn, params=(str(d_start), str(d_end))
                )
                if not df_export.empty:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df_export.to_excel(writer, index=False, sheet_name='Hospital_Analytic')
                    st.download_button(label="📥 TẢI FILE EXCEL", data=buffer.getvalue(), file_name=f"Hospital_Report_{d_start}_{d_end}.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
                else: st.warning("Không có dữ liệu.")

    st.subheader("📋 Chi tiết danh sách ca mổ")
    st.dataframe(df_day, use_container_width=True)

# --- 3. GIAO DIỆN ĐIỀU PHỐI ---
def show_scheduling():
    st.header("🗓️ ĐIỀU PHỐI VẬN HÀNH")
    conn = connect_db(); cur = conn.cursor()
    ngay = st.date_input("Ngày làm việc:", value=datetime.now(), key="s_date")
    
    # Hiện thị toàn bộ ca của các phòng đang mở
    df_day = pd.read_sql_query("SELECT * FROM surgeries WHERE ngay_dang_ky_mo = ?", conn, params=(str(ngay),))
    df_day = df_day[df_day['phong_mo_an_dinh'].isin(rooms) | df_day['phong_mo_an_dinh'].isna()]
    
    draw_grid_schedule(df_day, ngay)
    st.divider()
    
    # Bước 1: Phê duyệt ca mới
    df_new = pd.read_sql_query("SELECT * FROM surgeries WHERE trang_thai = 'Chờ xếp phòng'", conn)
    if not df_new.empty:
        with st.expander("📝 Phê duyệt và Xếp phòng mổ", expanded=True):
            opts = {f"BN: {r['ten_bn']} | ĐK: {r['gio_dang_ky_mo']}": r['id'] for _, r in df_new.iterrows()}
            sid = st.selectbox("Chọn hồ sơ:", list(opts.keys()))
            cur.execute("SELECT gio_dang_ky_mo FROM surgeries WHERE id=?", (opts[sid],))
            g_def = cur.fetchone()[0]
            
            # SỬA LẠI: Cho phép chọn phòng từ danh sách rooms thay vì fix cứng DSA
            c1, c2 = st.columns(2)
            p_mo = c1.selectbox("Gán phòng mổ:", rooms)
            g_chot = c2.text_input("Giờ thực hiện xác nhận:", value=g_def)
            
            if st.button("XÁC NHẬN ĐIỀU PHỐI"):
                cur.execute("UPDATE surgeries SET phong_mo_an_dinh=?, gio_dang_ky_mo=?, trang_thai='Đã xếp lịch' WHERE id=?", (p_mo, g_chot, opts[sid]))
                conn.commit(); st.rerun()

    # Bước 2: Vận hành thực tế
    st.subheader("🚀 Ghi nhận thực tế vận hành")
    df_run = df_day[df_day['trang_thai'].isin(['Đã xếp lịch', 'Đang mổ', 'Hoàn tất'])]
    for _, r in df_run.iterrows():
        status_icon = "🟢" if r['trang_thai'] == 'Hoàn tất' else "🔴" if r['trang_thai'] == 'Đang mổ' else "🟡"
        with st.expander(f"{status_icon} {r['phong_mo_an_dinh']} | {r['ten_bn']} | {r['trang_thai']}"):
            col1, col2 = st.columns(2)
            now_full = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if r['trang_thai'] == 'Đã xếp lịch' and col1.button("BẮT ĐẦU", key=f"s{r['id']}"):
                cur.execute("UPDATE surgeries SET trang_thai='Đang mổ', thoi_gian_bat_dau_tt=? WHERE id=?", (now_full, r['id']))
                if r['thiet_bi_yeu_cau'] != 'Không cần':
                    cur.execute("UPDATE Dim_Equipments SET quantity = quantity - 1 WHERE equip_name=? AND quantity > 0", (r['thiet_bi_yeu_cau'],))
                conn.commit(); st.rerun()
            elif r['trang_thai'] == 'Đang mổ' and col2.button("KẾT THÚC", key=f"e{r['id']}"):
                cur.execute("UPDATE surgeries SET trang_thai='Hoàn tất', thoi_gian_ket_thuc_tt=? WHERE id=?", (now_full, r['id']))
                if r['thiet_bi_yeu_cau'] != 'Không cần':
                    cur.execute("UPDATE Dim_Equipments SET quantity = quantity + 1 WHERE equip_name=?", (r['thiet_bi_yeu_cau'],))
                conn.commit(); st.rerun()
            else:
                st.write(f"⏱ Thực tế: {r['thoi_gian_bat_dau_tt']} ➔ {r['thoi_gian_ket_thuc_tt']}")

# --- QUẢN LÝ THIẾT BỊ & USER (GIỮ NGUYÊN) ---
def show_equipment_management():
    st.header("🔧 QUẢN LÝ THIẾT BỊ")
    conn = connect_db(); cur = conn.cursor()
    with st.form("e_f"):
        n = st.text_input("Tên máy"); q = st.number_input("Số lượng", min_value=0, step=1)
        if st.form_submit_button("LƯU THIẾT BỊ"):
            if n:
                cur.execute("INSERT OR REPLACE INTO Dim_Equipments (equip_name, quantity) VALUES (?,?)", (n, q))
                conn.commit(); st.rerun()
    st.table(pd.read_sql_query("SELECT equip_name, quantity FROM Dim_Equipments", conn))

def show_user_management():
    st.header("👥 QUẢN TRỊ NGƯỜI DÙNG")
    conn = connect_db(); cur = conn.cursor()
    with st.form("u_f"):
        u = st.text_input("Tên đăng nhập"); p = st.text_input("Mật khẩu")
        r = st.selectbox("Quyền hạn", ["Admin", "XepPhong", "GiamDoc"])
        if st.form_submit_button("TẠO TÀI KHOẢN"):
            if u and p:
                cur.execute("INSERT OR IGNORE INTO Dim_Users (username, password, role) VALUES (?,?,?)", (u, p, r))
                conn.commit(); st.rerun()
    st.table(pd.read_sql_query("SELECT username, role FROM Dim_Users", conn))