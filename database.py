import sqlite3

def connect_db():
    conn = sqlite3.connect('hospital.db', check_same_thread=False)
    cur = conn.cursor()
    
    # 1. Bảng surgeries: Lưu 14 mục đăng ký + 2 mục vận hành thực tế (Ngày & Giờ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS surgeries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_y_te TEXT,
            ten_bn TEXT,
            nam_sinh TEXT,
            msnv_bs TEXT,
            ten_bs TEXT,
            email_bs TEXT,
            chuyen_khoa TEXT,
            ten_dich_vu TEXT,
            loai_mo TEXT,
            thiet_bi_yeu_cau TEXT DEFAULT 'Không cần',
            
            -- PHẦN ĐĂNG KÝ (Bác sĩ nhập)
            ngay_dang_ky_mo TEXT,      -- Ví dụ: 2026-03-19
            gio_dang_ky_mo TEXT,       -- Ví dụ: 14:07
            du_kien_phut INTEGER,
            ghi_chu TEXT,
            
            -- PHẦN ĐIỀU PHỐI & VẬN HÀNH
            phong_mo_an_dinh TEXT,
            trang_thai TEXT DEFAULT 'Chờ xếp phòng',
            
            -- LƯU ĐẦY ĐỦ NGÀY VÀ GIỜ THỰC TẾ (YYYY-MM-DD HH:MM:SS)
            thoi_gian_bat_dau_tt TEXT, 
            thoi_gian_ket_thuc_tt TEXT
        )
    """)

    # 2. Bảng Dim_Users: Phân quyền
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Dim_Users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            email TEXT
        )
    """)

    # 3. Bảng Dim_Equipments: Quản lý kho máy móc
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Dim_Equipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equip_name TEXT UNIQUE,
            quantity INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    return conn

def init_default_data():
    conn = connect_db()
    cur = conn.cursor()
    # Tạo admin mặc định
    cur.execute("INSERT OR IGNORE INTO Dim_Users VALUES (?,?,?,?)", ('admin', 'admin123', 'Admin', 'admin@hm.com'))
    # Tạo thiết bị mẫu
    equips = [('Máy C-Arm', 2), ('Máy nội soi tầng', 3), ('Máy gây mê', 5)]
    cur.executemany("INSERT OR IGNORE INTO Dim_Equipments (equip_name, quantity) VALUES (?,?)", equips)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_default_data()
    print("✅ Database hoàn tất: Đã sẵn sàng lưu Ngày và Giờ vận hành thực tế.")