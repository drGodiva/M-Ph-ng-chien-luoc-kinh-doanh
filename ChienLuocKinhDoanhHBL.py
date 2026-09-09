import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Mô Phỏng Kế Hoạch Kinh Doanh Herbalife",
    page_icon="🌿",
    layout="wide"
)

# 1. CẤU HÌNH ĐƯỜNG DẪN ẢNH AN TOÀN
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

logo_path = os.path.join(ASSETS_DIR, "MBAlogo.png")
card_path = os.path.join(ASSETS_DIR, "founderMBA.jpg")
qr_path = os.path.join(ASSETS_DIR, "qr_ngan_hang.png")

# 2. CSS TÙY BIẾN GIAO DIỆN & BẢNG HTML
st.markdown("""
    <style>
    .main-title { color: #004D40; text-align: center; font-weight: 800; font-size: 24px; margin-bottom: 5px; }
    .sub-title { color: #D4AF37; text-align: center; font-weight: 600; font-size: 15px; margin-bottom: 20px; }
    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 14px; margin-top: 15px; }
    .html-table th { background-color: #004D40; color: white; padding: 10px; border: 1px solid #ddd; text-align: center; }
    .html-table td { padding: 8px; border: 1px solid #ddd; text-align: center; }
    .html-table tr:nth-child(even) { background-color: #f4fbf7; }
    </style>
""", unsafe_allow_html=True)

# 3. THANH CÔNG CỤ SIDEBAR
if os.path.exists(logo_path):
    st.sidebar.image(logo_path)

st.sidebar.header("⚙️ CÀI ĐẶT CHIẾN LƯỢC")
vp_choice = st.sidebar.selectbox("1. Định mức VP mỗi người dùng / tháng:", options=[125, 250, 500], index=0)
new_biz_rate = st.sidebar.number_input("2. Số TVKD mới tuyển mỗi tháng (mỗi TVKD):", min_value=1, max_value=5, value=1)
cust_rate = st.sidebar.number_input("3. Số khách tiêu dùng thuần túy (mỗi TVKD):", min_value=0, max_value=10, value=2)
simulation_months = st.sidebar.slider("4. Thời gian mô phỏng (Tháng):", min_value=6, max_value=24, value=16)

st.sidebar.markdown("---")
st.sidebar.markdown("**Người sáng lập & Huấn luyện viên:**")
if os.path.exists(card_path):
    st.sidebar.image(card_path, caption="ThS. Jonathan Phụng - Người Mài Rìu")
if os.path.exists(qr_path):
    st.sidebar.image(qr_path, caption="Mã QR Kết nối")

# 4. GIAO DIỆN CHÍNH & TÍNH TOÁN
st.markdown("<div class='main-title'>HỆ THỐNG MÔ PHỎNG CHIẾN LƯỢC BẬC THANG LY KHAI HERBALIFE</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Đã tối ưu hóa công nghệ HTML hiển thị tốc độ cao - Chống sập hệ thống</div>", unsafe_allow_html=True)

EARN_BASE_PER_VP = 22000
RO_POINT_VALUE = 27500
unit_cluster_vp = (1 + cust_rate) * vp_choice

cohort = [0] * (simulation_months + 2)
cohort[1] = 1

display_records = []
accum_vp_founder = 0
streak_counter = 0
pres_completed_month = None

for m in range(1, simulation_months + 1):
    active_sponsors = 1 + sum(cohort[1:m]) if m > 1 else 1
    cohort[m] = active_sponsors * new_biz_rate
    
    total_biz_members = 1 + sum(cohort[1:m+1])
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

    display_records.append({
        "Tháng": f"Tháng {m}",
        "TVKD": f"{int(total_biz_members):,}",
        "GSV Ly Khai": f"{int(sup_3_gen):,}",
        "DS Nhóm(VP)": f"{int(total_monthly_vp):,}",
        "Điểm RO": f"{ro_points:,.1f}",
        "Cấp Bậc": rank,
        "Bán Lẻ (Tr)": f"{retail_inc:,.1f}",
        "Sỉ (Tr)": f"{wholesale_inc:,.1f}",
        "Bản Quyền RO (Tr)": f"{ro_inc:,.1f}",
        "Thưởng TAB (Tr)": f"{pb_inc:,.1f}",
        "TỔNG (Tr đ)": f"{total_inc:,.1f}"
    })

if pres_completed_month:
    st.success(f"🎯 **Hoàn thành Nhóm Chủ Tịch (President's Team)** vào **Tháng thứ {pres_completed_month}** (Đạt chuẩn 3 tháng liên tiếp >= 10.000 RO).")

col1, col2, col3, col4 = st.columns(4)
df_display = pd.DataFrame(display_records)
with col1: st.metric("Tổng TVKD Cuối Kỳ", df_display.iloc[-1]["TVKD"])
with col2: st.metric("GSV Ly Khai Cuối Kỳ", df_display.iloc[-1]["GSV Ly Khai"])
with col3: st.metric("Điểm RO Tháng Cuối", df_display.iloc[-1]["Điểm RO"])
with col4: st.metric("TỔNG THU NHẬP Tháng Cuối", df_display.iloc[-1]["TỔNG (Tr đ)"])

# 5. RENDER BẢNG BẰNG HTML THUẦN (Bỏ qua st.dataframe gây sập)
html_table = df_display.to_html(index=False, classes="html-table", escape=False)
st.markdown(html_table, unsafe_allow_html=True)