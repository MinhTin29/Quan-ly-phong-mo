import streamlit as st

def apply_custom_style():
    st.markdown(f"""
        <style>
        /* 1. Nền trắng và chữ đen cơ bản - An toàn tuyệt đối */
        .stApp {{
            background-color: #FFFFFF !important;
        }}
        
        h1, h2, h3, h4, label, p, span, .stMarkdown {{
            color: #000000 !important;
            font-weight: 600 !important;
        }}

        /* 2. Giữ nguyên màu cho Grid Timeline */
        .slot-free {{ background-color: #FFFFFF; border: 1px solid #ddd; }}
        .slot-waiting {{ background-color: #FFEB3B !important; color: #000000 !important; font-weight: bold; border: 1px solid #000; }}
        .slot-busy {{ background-color: #F44336 !important; color: #FFFFFF !important; font-weight: bold; border: 1px solid #000; }}
        .slot-done {{ background-color: #4CAF50 !important; color: #FFFFFF !important; font-weight: bold; border: 1px solid #000; }}

        /* 3. Cấu hình thanh cuộn cho Grid */
        .timeline-container {{
            overflow-x: auto !important;
            border: 1px solid #ddd;
            border-radius: 8px;
        }}

        /* 4. Nút bấm hiệu ứng Scale bạn đã ưng ý */
        div.stButton > button {{
            background-color: rgb(161, 218, 221) !important;
            color: #000000 !important;
            font-weight: 700 !important;
            border: 1px solid #000 !important;
            transition: transform 0.2s !important;
        }}
        div.stButton > button:hover {{
            transform: scale(1.05) !important;
        }}

        /* 5. Sidebar màu xanh nhạt chuyên nghiệp */
        section[data-testid="stSidebar"] {{
            background-color: #DFF0F1 !important;
            border-right: 1px solid #A1DADD;
        }}
        </style>
    """, unsafe_allow_html=True)