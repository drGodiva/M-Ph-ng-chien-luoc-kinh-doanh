import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Mô Phỏng Kế Hoạch Kinh Doanh Herbalife",
    page_icon="🌿",
    layout="wide"
)

# Đường dẫn thư mục tài nguyên assets
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CURRENT_DIR, "assets")

logo_path = os.path.join(ASSETS_DIR, "MBAlogo.png")
card_path = os.path.join(ASSETS_DIR, "founderMBA.jpg")
qr_path = os.path.join(ASSETS_DIR, "qr_ngan_hang.png")

# CSS màu sắc thương hiệu
st.markdown("""
    <style>
    .main-title { color: #004D40; text-align: center; font-weight: 800; font-size: 24px; margin-bottom: 5px; }
    .sub-title { color: #D4AF37; text-align: center; font-weight: 600; font-size: 15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: HIỂN THỊ HÌNH ẢNH AN TOÀN ---
try:
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path)
    else:
        st.sidebar.markdown("### 🌿 MASTERING BIOLOGY")
except Exception:
    st.sidebar.markdown("### 🌿 MASTERING BIOLOGY")

st.sidebar.header("⚙️ CÀI ĐẶT CHIẾN LƯỢC")

vp_choice = st.sidebar.selectbox(
    "1. Định mức VP mỗi người dùng / tháng:",
    options=[125, 250, 500],
    index=0
)

new_biz_rate = st.sidebar.number_input(
    "2. Số TVKD mới tuyển mỗi tháng (mỗi TVKD):",
    min_value=1,
    max_value=5,
    value=1,
    step=1
)

cust_rate = st.sidebar.number_input(
    "3. Số khách hàng tiêu dùng thuần túy (mỗi TVKD):",
    min_value=0,
    max_value=10,
    value=2,
    step=1
)

simulation_months = st.sidebar.slider(
    "4. Thời gian mô phỏng (Tháng):",
    min_value=6,
    max_value=24,
    value=16
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Người sáng lập & Huấn luyện viên:**")
try:
    if os.path.exists(card_path):
        st.sidebar.image(card_path, caption="ThS. Jonathan Phụng - Người Mài Rìu")
    if os.path.exists(qr_path):
        st.sidebar.image(qr_path, caption="Mã QR Kết nối")
except Exception:
    pass

# --- TIÊU ĐỀ CHÍNH ---
st.markdown("<div class='main-title'>HỆ THỐNG MÔ PHỎNG CHIẾN LƯỢC BẬC THANG LY KHAI HERBALIFE</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Chiến lược sao chép (1 TVKD + 2 Khách hàng + Bạn = 4 người dùng) chuẩn Quy chế Trả thưởng</div>", unsafe_allow_html=True)

EARN_BASE_PER_VP = 22000   # 1 VP ~ 22.000 VNĐ Cơ sở thu nhập[cite: 1]
RO_POINT_VALUE = 27500     # 1 Điểm RO ~ 27.500 VNĐ[cite: 1]
unit_cluster_vp = (1 + cust_rate) * vp_choice

# --- TÍNH TOÁN MA TRẬN TĂNG TRƯỞNG ---
cohort = [0] * (simulation_months + 2)
cohort[1] = 1

data_records = []
accum_vp_founder = 0
streak_counter = 0
pres_completed_month = None

for m in range(1, simulation_months + 1):
    active_sponsors = 1 + sum(cohort[1:m]) if m > 1 else 1
    new_biz = active_sponsors * new_biz_rate
    cohort[m] = new_biz
    
    total_biz_members = 1 + sum(cohort[1:m+1])
    total_monthly_vp = total_biz_members * unit_cluster_vp
    accum_vp_founder += total_monthly_vp

    if accum_vp_founder >= 4000:
        founder_discount = 0.50
        base_rank = "Giám Sát Viên (50%)"[cite: 1]
    elif accum_vp_founder >= 2500:
        founder_discount = 0.42
        base_rank = "Người Bán Hàng ĐC (QP 42%)"[cite: 1]
    elif accum_vp_founder >= 1000:
        founder_discount = 0.42
        base_rank = "Kiến Tạo TC (SB 42%)"[cite: 1]
    elif accum_vp_founder >= 500:
        founder_discount = 0.35
        base_rank = "Tư Vấn Cao Cấp (SC 35%)"[cite: 1]
    else:
        founder_discount = 0.25
        base_rank = "Thành Viên (25%)"[cite: 1]

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

    ro_rate = 0.05 if total_monthly_vp >= 2500 else 0.04[cite: 1]
    ro_points = ov_3_gen * ro_rate

    rank = base_rank
    pb_rate = 0.0

    if ro_points >= 10000:[cite: 1]
        streak_counter += 1
        if streak_counter >= 3:[cite: 1]
            rank = "👑 Nhóm Chủ Tịch (Pres Team)"[cite: 1]
            pb_rate = 0.06[cite: 1]
            if pres_completed_month is None:
                pres_completed_month = m
        else:
            rank = f"Chủ Tịch Đạt Chuẩn ({streak_counter}/3)"[cite: 1]
            pb_rate = 0.04[cite: 1]
    else:
        streak_counter = 0
        if ro_points >= 4000:[cite: 1]
            rank = "Nhóm Triệu Phú (Mill Team)"[cite: 1]
            pb_rate = 0.04[cite: 1]
        elif ro_points >= 1000:[cite: 1]
            rank = "Nhóm Phát Triển (GET Team)"[cite: 1]
            pb_rate = 0.02[cite: 1]
        elif total_monthly_vp >= 10000 or ov_3_gen >= 10000:[cite: 1]
            rank = "Nhóm Thế Giới (World Team)"[cite: 1]

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
        "GSV 3 Tầng": int(sup_3_gen),
        "DS Nhóm (VP)": int(total_monthly_vp),
        "Điểm RO": round(ro_points, 1),
        "Cấp Bậc Đạt Chuẩn": rank,
        "Bán Lẻ (Tr đ)": round(retail_inc, 2),
        "Hoa Hồng Sỉ (Tr đ)": round(wholesale_inc, 2),
        "Bản Quyền RO (Tr đ)": round(ro_inc, 2),
        "Thưởng TAB (Tr đ)": round(pb_inc, 2),
        "TỔNG THU NHẬP (Tr đ)": round(total_inc, 2)
    })

df = pd.DataFrame(data_records)

# --- THÔNG BÁO HOÀN THÀNH CHỦ TỊCH ---
if pres_completed_month:
    st.success(f"🎯 **XÁC NHẬN MỐC THỜI GIAN:** Bạn hoàn thành vị trí **Nhóm Chủ Tịch (President's Team)** vào **Tháng thứ {pres_completed_month}** (Đạt chuẩn 3 tháng liên tiếp $\ge$ 10.000 RO theo Kế hoạch trả thưởng)[cite: 1]!")
else:
    st.warning("⚠️ Trong khung thời gian này chưa đủ 3 tháng liên tiếp $\ge$ 10.000 RO. Kéo tăng thanh thời gian mô phỏng bên trái.[cite: 1]")

# --- METRICS TỔNG QUAN ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Tổng TVKD Cuối Kỳ", f"{df.iloc[-1]['Tổng TVKD']:,} người")
with col2:
    st.metric("GSV 3 Tầng Ly Khai", f"{df.iloc[-1]['GSV 3 Tầng']:,} GSV")
with col3:
    st.metric("Điểm RO Tháng Cuối", f"{df.iloc[-1]['Điểm RO']:,} RO")
with col4:
    st.metric("TỔNG THU NHẬP Tháng Cuối", f"{df.iloc[-1]['TỔNG THU NHẬP (Tr đ)']:.2f} Tr đ")

st.write("---")

# --- BẢNG DỮ LIỆU HIỂN THỊ TRỰC TIẾP ---
st.write("### 📋 BẢNG THEO DÕI THĂNG TIẾN, DOANH SỐ VÀ CƠ CẤU 4 NGUỒN THU NHẬP")
st.dataframe(df, use_container_width=True)

# --- BIỂU ĐỒ DOANH THU ---
st.write("### 📈 Biểu Đồ Cơ Cấu Thu Nhập (Triệu VNĐ)")
chart_data = df.set_index("Tháng")[["Bán Lẻ (Tr đ)", "Hoa Hồng Sỉ (Tr đ)", "Bản Quyền RO (Tr đ)", "Thưởng TAB (Tr đ)"]]
st.bar_chart(chart_data)