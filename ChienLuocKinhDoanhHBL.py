import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Mô Phỏng Kế Hoạch Kinh Doanh Herbalife",
    page_icon="🌿",
    layout="wide"
)

# --- ĐƯỜNG DẪN TÀI NGUYÊN (ASSETS) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

logo_path = os.path.join(ASSETS_DIR, "MBAlogo.png")
card_path = os.path.join(ASSETS_DIR, "founderMBA.jpg")
qr_path = os.path.join(ASSETS_DIR, "qr_ngan_hang.png")

# --- CSS TÙY BIẾN: BẢNG STICKY VÀ CHỐNG KHUẤT SỐ ---
st.markdown("""
    <style>
    .main-title { color: #004D40; text-align: center; font-weight: 800; font-size: 24px; margin-bottom: 5px; }
    .sub-title { color: #D4AF37; text-align: center; font-weight: 600; font-size: 15px; margin-bottom: 20px; }
    
    div[data-testid="metric-container"] > div > div {
        white-space: normal !important;
        overflow-wrap: break-word !important;
        font-size: 1.8rem !important; 
    }
    
    .table-container {
        max-height: 550px;
        overflow-y: auto;
        overflow-x: auto;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .sticky-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14.5px;
        text-align: right;
    }
    
    .sticky-table th {
        position: sticky;
        top: 0;
        background-color: #004D40 !important;
        color: #D4AF37 !important;
        padding: 12px 8px;
        z-index: 2;
        text-align: center;
        border: 1px solid #00332a;
        white-space: nowrap;
    }
    
    .sticky-table td {
        padding: 10px 8px;
        border: 1px solid #ddd;
        white-space: nowrap;
    }
    
    .sticky-table tr:nth-child(even) { background-color: #f4fbf7; }
    .sticky-table tr:hover { background-color: #e2f3eb; }
    .text-center { text-align: center !important; }
    .text-bold { font-weight: bold !important; }
    .highlight-col { background-color: #e8f5e9; font-weight: bold; color: #004D40; }
    </style>
""", unsafe_allow_html=True)

# --- THANH CÔNG CỤ (SIDEBAR) ---
if os.path.exists(logo_path):
    st.sidebar.image(logo_path)
else:
    st.sidebar.markdown("### 🌿 MASTERING BIOLOGY")

st.sidebar.header("⚙️ CÀI ĐẶT CHIẾN LƯỢC")

vp_choice = st.sidebar.selectbox("1. Định mức VP mỗi người dùng / tháng:", options=[100, 125, 250, 500], index=1)
new_biz_rate = st.sidebar.number_input("2. Số TVKD mới tuyển mỗi tháng (mỗi TVKD):", min_value=1, max_value=5, value=1, step=1)
cust_rate = st.sidebar.number_input("3. Số khách tiêu dùng thuần túy (mỗi TVKD):", min_value=0, max_value=10, value=2, step=1)
selected_month = st.sidebar.slider("4. Chọn tháng muốn xem kết quả:", min_value=1, max_value=36, value=6)

st.sidebar.markdown("---")
st.sidebar.markdown("**Người sáng lập & Huấn luyện viên:**")
if os.path.exists(card_path): st.sidebar.image(card_path, caption="ThS. Jonathan Phụng - Người Mài Rìu")
if os.path.exists(qr_path): st.sidebar.image(qr_path, caption="Mã QR Kết nối")

# --- GIAO DIỆN CHÍNH & TÍNH TOÁN ---
st.markdown("<div class='main-title'>HỆ THỐNG MÔ PHỎNG CHIẾN LƯỢC BẬC THANG LY KHAI HERBALIFE</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Ứng dụng phân tích thực chiến hệ thống kinh doanh theo thời gian thực</div>", unsafe_allow_html=True)

EARN_BASE_PER_VP = 22000   
RO_POINT_VALUE = 27500     
unit_cluster_vp = (1 + cust_rate) * vp_choice

cohort_new = [0] * (selected_month + 2)
data_records = []
accum_vp_founder = 0
streak_counter = 0
pres_completed_month = None

for m in range(1, selected_month + 1):
    active_sponsors = 1 if m == 1 else 1 + sum(cohort_new[1:m])
    new_biz = active_sponsors * new_biz_rate
    cohort_new[m] = new_biz
    
    total_biz_members = 1 + sum(cohort_new[1:m+1])
    total_monthly_vp = total_biz_members * unit_cluster_vp
    accum_vp_founder += total_monthly_vp

    if accum_vp_founder >= 4000:
        founder_discount = 0.50
        base_rank = "GSV (50%)"
    elif accum_vp_founder >= 2500:
        founder_discount = 0.42
        base_rank = "QP (42%)"
    elif accum_vp_founder >= 1000:
        founder_discount = 0.42
        base_rank = "SB (42%)"
    elif accum_vp_founder >= 500:
        founder_discount = 0.35
        base_rank = "SC (35%)"
    else:
        founder_discount = 0.25
        base_rank = "Thành Viên (25%)"

    if m >= 7:
        ov_3_gen = total_monthly_vp * 0.70
        sup_3_gen = int(total_biz_members * 0.45)
    elif m == 6:
        ov_3_gen = total_monthly_vp * 0.50
        sup_3_gen = int(total_biz_members * 0.30)
    elif m == 5:
        ov_3_gen = total_monthly_vp * 0.30
        sup_3_gen = 1
    else:
        ov_3_gen = 0
        sup_3_gen = 0

    ro_rate = 0.05 if total_monthly_vp >= 2500 else 0.04
    ro_points = ov_3_gen * ro_rate
    rank = base_rank
    pb_rate = 0.0

    if ro_points >= 10000:
        streak_counter += 1
        if streak_counter >= 3:
            rank = "👑 Chủ Tịch (Pres)"
            pb_rate = 0.06
            if pres_completed_month is None: pres_completed_month = m
        else:
            rank = f"Chủ Tịch ({streak_counter}/3)"
            pb_rate = 0.04
    else:
        streak_counter = 0
        if ro_points >= 4000:
            rank = "Triệu Phú (Mill)"
            pb_rate = 0.04
        elif ro_points >= 1000:
            rank = "Phát Triển (GET)"
            pb_rate = 0.02
        elif total_monthly_vp >= 10000 or ov_3_gen >= 10000:
            rank = "Thế Giới (WT)"

    retail_inc = (unit_cluster_vp * EARN_BASE_PER_VP * founder_discount) / 1e6
    non_sup_vp = max(0, total_monthly_vp - ov_3_gen - unit_cluster_vp)
    diff_rate = max(0.0, founder_discount - 0.25)
    wholesale_inc = (non_sup_vp * EARN_BASE_PER_VP * diff_rate * 0.5) / 1e6
    ro_inc = (ro_points * RO_POINT_VALUE) / 1e6
    pb_inc = (ov_3_gen * EARN_BASE_PER_VP * pb_rate) / 1e6 if pb_rate > 0 else 0.0
    total_inc = retail_inc + wholesale_inc + ro_inc + pb_inc

    data_records.append({
        "Tháng": f"Tháng {m}",
        "Tuyển Mới": int(new_biz),
        "Tổng TVKD": int(total_biz_members),
        "GSV Ly Khai": int(sup_3_gen),
        "DS Nhóm": int(total_monthly_vp),
        "Điểm RO": ro_points,
        "Cấp Bậc": rank,
        "Bán Lẻ": retail_inc,
        "Sỉ": wholesale_inc,
        "RO": ro_inc,
        "TAB": pb_inc,
        "TỔNG": total_inc
    })

# --- RENDER CHỈ SỐ NHANH ---
if pres_completed_month:
    st.success(f"🎯 **XÁC NHẬN MỐC THỜI GIAN:** Lên **Nhóm Chủ Tịch (President's Team)** vào **Tháng thứ {pres_completed_month}**!")
else:
    st.info(f"👉 Đang hiển thị dữ liệu quá trình đến **Tháng {selected_month}**.")

col1, col2, col3, col4 = st.columns(4)
last_record = data_records[-1]
with col1: st.metric("Tổng TVKD Tháng Này", f"{last_record['Tổng TVKD']:,}")
with col2: st.metric("GSV Ly Khai Tháng Này", f"{last_record['GSV Ly Khai']:,}")
with col3: st.metric("Điểm RO Tháng Này", f"{last_record['Điểm RO']:,.1f}")
with col4: st.metric("TỔNG THU NHẬP Tháng Này", f"{last_record['TỔNG']:,.1f} Tr đ")

# --- RENDER BẢNG HTML (CHUẨN HÓA KHÔNG THỤT LỀ) ---
st.write("### 📋 BẢNG TIẾN ĐỘ THĂNG TIẾN, NHÂN SỰ VÀ DOANH THU")

# Cấu trúc HTML được nối chuỗi liên tục, không dùng khoảng trắng thụt lề để chống lỗi Markdown
html_table = '<div class="table-container"><table class="sticky-table"><thead><tr>'
html_table += '<th>Tháng</th><th>Tuyển Mới<br>(Người)</th><th>Tổng TVKD<br>(Người)</th>'
html_table += '<th>GSV Ly Khai<br>(Tầng 1-3)</th><th>DS Nhóm<br>(VP)</th><th>Điểm RO</th>'
html_table += '<th>Cấp Bậc<br>Của Bạn</th><th>Bán Lẻ<br>(Tr đ)</th><th>Hoa Hồng Sỉ<br>(Tr đ)</th>'
html_table += '<th>Bản Quyền RO<br>(Tr đ)</th><th>Thưởng TAB<br>(Tr đ)</th><th>TỔNG THU NHẬP<br>(Tr đ)</th>'
html_table += '</tr></thead><tbody>'

for row in data_records:
    html_table += '<tr>'
    html_table += f'<td class="text-center text-bold">{row["Tháng"]}</td>'
    html_table += f'<td class="text-center">{row["Tuyển Mới"]:,}</td>'
    html_table += f'<td class="text-center text-bold">{row["Tổng TVKD"]:,}</td>'
    html_table += f'<td class="text-center">{row["GSV Ly Khai"]:,}</td>'
    html_table += f'<td class="text-center">{row["DS Nhóm"]:,}</td>'
    html_table += f'<td class="text-center">{row["Điểm RO"]:,.1f}</td>'
    html_table += f'<td class="text-center text-bold">{row["Cấp Bậc"]}</td>'
    html_table += f'<td>{row["Bán Lẻ"]:,.1f}</td>'
    html_table += f'<td>{row["Sỉ"]:,.1f}</td>'
    html_table += f'<td>{row["RO"]:,.1f}</td>'
    html_table += f'<td>{row["TAB"]:,.1f}</td>'
    html_table += f'<td class="highlight-col">{row["TỔNG"]:,.1f}</td>'
    html_table += '</tr>'

html_table += '</tbody></table></div>'

st.markdown(html_table, unsafe_allow_html=True)

# --- BIỂU ĐỒ DOANH THU ---
st.write("### 📈 Biểu Đồ Cơ Cấu Thu Nhập (Triệu VNĐ)")
if len(data_records) > 0:
    df_chart = pd.DataFrame(data_records).set_index("Tháng")[["Bán Lẻ", "Sỉ", "RO", "TAB"]]
    st.bar_chart(df_chart)