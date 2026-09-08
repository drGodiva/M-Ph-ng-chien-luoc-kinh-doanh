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

# CSS màu sắc Emerald Green (#004D40) & Metallic Gold (#D4AF37)
st.markdown("""
    <style>
    .main-title { color: #004D40; text-align: center; font-weight: 800; font-size: 24px; margin-bottom: 5px; }
    .sub-title { color: #D4AF37; text-align: center; font-weight: 600; font-size: 15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: LOGO VÀ THIẾT LẬP ---
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
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
if os.path.exists(card_path):
    st.sidebar.image(card_path, caption="ThS. Jonathan Phụng - Người Mài Rìu", use_container_width=True)

if os.path.exists(qr_path):
    st.sidebar.image(qr_path, caption="Mã QR Kết nối / Đóng góp", use_container_width=True)

# --- TIÊU ĐỀ ---
st.markdown("<div class='main-title'>HỆ THỐNG MÔ PHỎNG CHIẾN LƯỢC BẬC THANG LY KHAI HERBALIFE</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Chiến lược sao chép (1 TVKD + 2 Khách hàng + Bạn = 4 người dùng) chuẩn Quy chế Trả thưởng</div>", unsafe_allow_html=True)

# Các hằng số quy chuẩn Herbalife Việt Nam
EARN_BASE_PER_VP = 22000   # 1 VP ~ 22.000 VNĐ Cơ sở thu nhập
RO_POINT_VALUE = 27500     # 1 Điểm RO ~ 27.500 VNĐ
unit_cluster_vp = (1 + cust_rate) * vp_choice

# --- THUẬT TOÁN COHORT TỐC ĐỘ CAO (CHỐNG TREO 100%) ---
# Mảng lưu số lượng TVKD gia nhập ở từng tháng
cohort = [0] * (simulation_months + 2)
cohort[1] = 1 # Tháng 1 bạn tuyển 1 TVKD trực tiếp

data_records = []
accum_vp_founder = 0
pres_qualify_streak = 0
pres_completed_month = None

for m in range(1, simulation_months + 1):
    # Người bảo trợ hành động ở tháng m = Bạn (1) + Những TVKD vào từ tháng (m-1) trở về trước
    active_sponsors = 1 + sum(cohort[1:m]) if m > 1 else 1
    
    # Số TVKD mới gia nhập tháng m
    new_biz = active_sponsors * new_biz_rate
    cohort[m] = new_biz
    
    # Tổng TVKD trong toàn hệ thống (bao gồm cả bạn)
    total_biz_members = 1 + sum(cohort[1:m+1])
    
    # Tổng doanh số toàn đội trong tháng
    total_monthly_vp = total_biz_members * unit_cluster_vp
    accum_vp_founder += total_monthly_vp
    
    # Đánh giá cấp bậc cá nhân của Người bảo trợ
    if accum_vp_founder >= 4000:
        founder_discount = 0.50
        base_rank = "Giám Sát Viên (50%)"
    elif accum_vp_founder >= 2500:
        founder_discount = 0.42
        base_rank = "Người Bán Hàng ĐC (QP 42%)"
    elif accum_vp_founder >= 1000:
        founder_discount = 0.42
        base_rank = "Kiến Tạo TC (SB 42%)"
    elif accum_vp_founder >= 500:
        founder_discount = 0.35
        base_rank = "Tư Vấn Cao Cấp (SC 35%)"
    else:
        founder_discount = 0.25
        base_rank = "Thành Viên (25%)"

    # Điểm ly khai & Doanh số mạng lưới 3 tầng GSV (OV)
    # Tuyến dưới tích lũy đủ 4.000 VP thì ly khai (thường từ tháng thứ 4-5 trở đi)
    # F1 ly khai ở tháng 5, F2 ở tháng 6, F3 ở tháng 7...
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

    # Điểm Royalty Overrides (RO): nhận 5% khi Doanh số nhóm >= 2.500 VP
    ro_rate = 0.05 if total_monthly_vp >= 2500 else 0.04
    ro_points = ov_3_gen * ro_rate

    # Xét danh hiệu TAB Team & Mốc Chủ Tịch
    rank = base_rank
    pb_rate = 0.0

    if ro_points >= 10000:
        pres_qualify_streak += 1
        if pres_qualify_streak >= 3:
            rank = "👑 Nhóm Chủ Tịch (Pres Team)"
            pb_rate = 0.06
            if pres_completed_month is None:
                pres_completed_month = m
        else:
            rank = f"Chủ Tịch Đạt Chuẩn ({pres_qualify_streak}/3)"
            pb_rate = 0.04
    else:
        pres_qualify_streak = 0
        if ro_points >= 4000:
            rank = "Nhóm Triệu Phú (Mill Team)"
            pb_rate = 0.04
        elif ro_points >= 1000:
            rank = "Nhóm Phát Triển (GET Team)"
            pb_rate = 0.02
        elif total_monthly_vp >= 10000 or ov_3_gen >= 10000:
            rank = "Nhóm Thế Giới (World Team)"

    # Phân bổ thu nhập (Đơn vị: Triệu VNĐ)
    # 1. Bán lẻ cụm cá nhân (Bạn + 2 Khách)
    retail_inc = (unit_cluster_vp * EARN_BASE_PER_VP * founder_discount) / 1e6
    
    # 2. Hoa hồng sỉ (Nhận từ các nhánh chưa ly khai)
    non_sup_vp = max(0, total_monthly_vp - ov_3_gen - unit_cluster_vp)
    diff_rate = max(0.0, founder_discount - 0.25)
    wholesale_inc = (non_sup_vp * EARN_BASE_PER_VP * diff_rate * 0.5) / 1e6
    
    # 3. Bản quyền RO
    ro_inc = (ro_points * RO_POINT_VALUE) / 1e6
    
    # 4. Hoa hồng doanh số TAB (PB)
    pb_inc = (ov_3_gen * EARN_BASE_PER_VP * pb_rate) / 1e6 if pb_rate > 0 else 0.0
    
    total_inc = retail_inc + wholesale_inc + ro_inc + pb_inc

    data_records.append({
        "Tháng": f"Tháng {m}",
        "Tổng TVKD": total_biz_members,
        "GSV 3 Tầng": sup_3_gen,
        "Doanh Số Nhóm": total_monthly_vp,
        "Điểm RO": round(ro_points, 1),
        "Cấp Bậc Đạt Được": rank,
        "Bán Lẻ (Tr đ)": round(retail_inc, 2),
        "Hoa Hồng Sỉ (Tr đ)": round(wholesale_inc, 2),
        "Bản Quyền RO (Tr đ)": round(ro_inc, 2),
        "Thưởng TAB (Tr đ)": round(pb_inc, 2),
        "TỔNG THU NHẬP (Tr đ)": round(total_inc, 2)
    })

df = pd.DataFrame(data_records)

# --- THÔNG BÁO KẾT QUẢ VỊ TRÍ CHỦ TỊCH ---
if pres_completed_month:
    st.success(f"🎯 **XÁC NHẬN MỐC THỜI GIAN:** Bạn hoàn thành vị trí **Nhóm Chủ Tịch (President's Team)** vào **Tháng thứ {pres_completed_month}** (Đủ 3 tháng liên tiếp $\ge$ 10.000 RO theo Kế hoạch trả thưởng)[cite: 1]!")
else:
    st.warning("⚠️ Trong khung thời gian này chưa đủ 3 tháng liên tiếp $\ge$ 10.000 RO. Kéo tăng thanh thời gian mô phỏng bên trái[cite: 1].")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Tổng TVKD Cuối Kỳ", f"{df.iloc[-1]['Tổng TVKD']:,} người")
with col2:
    st.metric("GSV 3 Tầng Ly Khai", f"{df.iloc[-1]['GSV 3 Tầng']:,} GSV")
with col3:
    st.metric("Điểm RO Tháng Cuối", f"{df.iloc[-1]['Điểm RO']:,} RO")
with col4:
    st.metric("TỔNG THU NHẬP Tháng Cuối", f"{df.iloc[-1]['TỔNG THU NHẬP (Tr đ)']:.1f} Triệu VNĐ")

st.write("---")

st.write("### 📋 BẢNG THEO DÕI THĂNG TIẾN, DOANH SỐ VÀ CƠ CẤU 4 NGUỒN THU NHẬP")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.write("### 📈 Biểu Đồ Tăng Trưởng Thu Nhập Hệ Thống (Triệu VNĐ)")
chart_data = df.set_index("Tháng")[["Bán Lẻ (Tr đ)", "Hoa Hồng Sỉ (Tr đ)", "Bản Quyền RO (Tr đ)", "Thưởng TAB (Tr đ)"]]
st.bar_chart(chart_data)