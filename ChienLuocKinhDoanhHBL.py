import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Mô Phỏng Kế Hoạch Kinh Doanh Herbalife", page_icon="🌿", layout="wide")

# --- 1. ĐƯỜNG DẪN TÀI NGUYÊN (ASSETS) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

logo_path = os.path.join(ASSETS_DIR, "MBAlogo.png")
card_path = os.path.join(ASSETS_DIR, "founderMBA.jpg")
qr_path = os.path.join(ASSETS_DIR, "qr_ngan_hang.png")

# --- 2. GIAO DIỆN TÙY BIẾN ---
st.markdown("""
    <style>
    .main-title { color: #004D40; text-align: center; font-weight: 800; font-size: 26px; margin-bottom: 5px; }
    .sub-title { color: #D4AF37; text-align: center; font-weight: 600; font-size: 16px; margin-bottom: 25px; }
    div[data-testid="metric-container"] > div > div { white-space: normal !important; overflow-wrap: break-word !important; font-size: 1.8rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. THANH CÔNG CỤ (SIDEBAR) ---
if os.path.exists(logo_path):
    st.sidebar.image(logo_path)

st.sidebar.header("⚙️ CÀI ĐẶT CHIẾN LƯỢC")
vp_choice = st.sidebar.selectbox("1. Định mức VP mỗi người dùng / tháng:", options=[100, 125, 250, 500], index=1)
new_biz_rate = st.sidebar.number_input("2. Số TVKD mới tuyển mỗi tháng (mỗi TVKD):", min_value=1, max_value=5, value=1)
cust_rate = st.sidebar.number_input("3. Số khách tiêu dùng thuần túy (mỗi TVKD):", min_value=0, max_value=10, value=2)
selected_month = st.sidebar.slider("4. Chọn tháng muốn xem kết quả:", min_value=1, max_value=36, value=10)

st.sidebar.markdown("---")
if os.path.exists(card_path): st.sidebar.image(card_path, caption="ThS. Jonathan Phụng")
if os.path.exists(qr_path): st.sidebar.image(qr_path, caption="Mã QR Kết nối")

# --- 4. THUẬT TOÁN TOÁN HỌC CHÍNH XÁC 100% ---
EARN_BASE_PER_VP = 22000   
RO_POINT_VALUE = 27500     
unit_cluster_vp = (1 + cust_rate) * vp_choice
MAX_AGE = selected_month + 2

# Ma trận lưu trữ lịch sử phát triển của 1 Nhánh tiêu chuẩn
vp_hist = [0] * MAX_AGE
accum_hist = [0] * MAX_AGE
gv_hist = [0] * MAX_AGE
ov1_hist = [0] * MAX_AGE; ov2_hist = [0] * MAX_AGE; ov3_hist = [0] * MAX_AGE; ov4p_hist = [0] * MAX_AGE
is_qgsv = [False] * MAX_AGE; is_gsv = [False] * MAX_AGE
discount = [0.25] * MAX_AGE
pb_rate_hist = [0.0] * MAX_AGE
ro_streak = [0] * MAX_AGE

# Tính toán cây gia phả tiến hóa
for k in range(1, MAX_AGE):
    own_vp = vp_choice if k == 1 else unit_cluster_vp
    vp_hist[k] = own_vp + new_biz_rate * sum(vp_hist[1:k])
    accum_hist[k] = accum_hist[k-1] + vp_hist[k]
    
    if is_qgsv[k-1] or is_gsv[k-1]: is_gsv[k] = True
    if not is_gsv[k] and accum_hist[k] >= 4000: is_qgsv[k] = True
        
    my_gv = own_vp
    my_ov1 = my_ov2 = my_ov3 = my_ov4p = 0
    for i in range(2, k+1):
        f1_age = k - i + 1
        if is_gsv[f1_age]:
            my_ov1 += new_biz_rate * gv_hist[f1_age]
            my_ov2 += new_biz_rate * ov1_hist[f1_age]
            my_ov3 += new_biz_rate * ov2_hist[f1_age]
            my_ov4p += new_biz_rate * (ov3_hist[f1_age] + ov4p_hist[f1_age])
        else:
            my_gv += new_biz_rate * vp_hist[f1_age]
            
    gv_hist[k], ov1_hist[k], ov2_hist[k], ov3_hist[k], ov4p_hist[k] = my_gv, my_ov1, my_ov2, my_ov3, my_ov4p
    
    if is_gsv[k] or is_qgsv[k]: discount[k] = 0.50
    elif accum_hist[k] >= 1000: discount[k] = 0.42
    elif accum_hist[k] >= 500: discount[k] = 0.35
    else: discount[k] = 0.25

    if is_gsv[k]:
        ro_pts = (my_ov1 + my_ov2 + my_ov3) * (0.05 if my_gv >= 2500 else 0.04)
        ro_streak[k] = ro_streak[k-1] + 1 if ro_pts >= 10000 else 0
        if ro_streak[k] >= 3: pb_rate_hist[k] = 0.06
        elif ro_pts >= 4000: pb_rate_hist[k] = 0.04
        elif ro_pts >= 1000: pb_rate_hist[k] = 0.02

# Áp dụng cho góc nhìn của Người Sáng Lập (Founder)
st.markdown("<div class='main-title'>HỆ THỐNG MÔ PHỎNG CHIẾN LƯỢC BẬC THANG LY KHAI HERBALIFE</div>", unsafe_allow_html=True)

data_records = []
pres_completed_month = None

for M in range(1, selected_month + 1):
    k = M + 1 # Tuổi của hệ thống (Bạn đã hoạt động trước tháng 1)
    
    # Cấp số nhân chính xác
    total_members = (1 + new_biz_rate) ** M
    downlines = total_members - 1
    new_recruits = new_biz_rate * ((1 + new_biz_rate) ** (M - 1))
    
    f_gv = gv_hist[k]
    f_ro_pts = (ov1_hist[k] + ov2_hist[k] + ov3_hist[k]) * (0.05 if f_gv >= 2500 else 0.04)
    f_discount = discount[k]
    f_pb_rate = pb_rate_hist[k]
    
    # Danh hiệu
    if is_gsv[k]:
        if ro_streak[k] >= 3: 
            f_rank = "👑 PRES"
            if pres_completed_month is None: pres_completed_month = M
        elif ro_streak[k] > 0: f_rank = f"PRES ĐC ({ro_streak[k]}/3)"
        elif f_ro_pts >= 4000: f_rank = "MILL"
        elif f_ro_pts >= 1000: f_rank = "GET"
        elif f_gv >= 10000 or (ov1_hist[k]+ov2_hist[k]+ov3_hist[k]) >= 10000: f_rank = "WT"
        else: f_rank = "GSV (50%)"
    else:
        if is_qgsv[k] or accum_hist[k] >= 2500: f_rank = "QP (42%)"
        elif accum_hist[k] >= 1000: f_rank = "SB (42%)"
        elif accum_hist[k] >= 500: f_rank = "SC (35%)"
        else: f_rank = "TV (25%)"

    # Tính nút chặn sỉ và PB
    f_wholesale = 0
    f_pb_vp = 0
    gsv_count_3gen = 0
    
    for x in range(1, M+1):
        f1_age = M - x + 1
        if not is_gsv[f1_age]:
            f_wholesale += new_biz_rate * vp_hist[f1_age] * max(0, f_discount - discount[f1_age])
        else:
            gsv_count_3gen += new_biz_rate # Ước tính số lượng nhánh GSV
            branch_total = gv_hist[f1_age] + ov1_hist[f1_age] + ov2_hist[f1_age] + ov3_hist[f1_age] + ov4p_hist[f1_age]
            f_pb_vp += new_biz_rate * branch_total * max(0, f_pb_rate - pb_rate_hist[f1_age])

    retail_inc = (unit_cluster_vp * EARN_BASE_PER_VP * f_discount) / 1e6
    wholesale_inc = (f_wholesale * EARN_BASE_PER_VP) / 1e6
    ro_inc = (f_ro_pts * RO_POINT_VALUE) / 1e6
    pb_inc = (f_pb_vp * EARN_BASE_PER_VP) / 1e6
    total_inc = retail_inc + wholesale_inc + ro_inc + pb_inc

    data_records.append({
        "Tháng": f"Tháng {M}",
        "Tuyển Mới": new_recruits,
        "Tuyến Dưới": downlines,
        "Tổng TVKD": total_members,
        "DS Nhóm": f_gv,
        "Điểm RO": f_ro_pts,
        "Cấp Bậc": f_rank,
        "Bán Lẻ": retail_inc,
        "Sỉ": wholesale_inc,
        "RO": ro_inc,
        "TAB": pb_inc,
        "TỔNG": total_inc
    })

# --- 5. RENDER BẢNG HTML CHỐNG SỌC VÀ CỐ ĐỊNH TIÊU ĐỀ ---
if pres_completed_month:
    st.success(f"🎯 **ĐẠT CHUẨN:** Hoàn thành **Nhóm Chủ Tịch (President's Team)** vào **Tháng thứ {pres_completed_month}**!")

col1, col2, col3, col4 = st.columns(4)
last = data_records[-1]
with col1: st.metric("Tổng Tuyến Dưới Cuối Kỳ", f"{int(last['Tuyến Dưới']):,}")
with col2: st.metric("Điểm RO Tháng Cuối", f"{last['Điểm RO']:,.1f}")
with col3: st.metric("Cấp Bậc Hiện Tại", last['Cấp Bậc'])
with col4: st.metric("TỔNG THU NHẬP Tháng Cuối", f"{last['TỔNG']:,.1f} Tr đ")

# Thiết kế HTML Inline cứng: Trị dứt điểm mọi lỗi giao diện Streamlit
html_table = '''
<div style="max-height: 600px; overflow-y: scroll; border: 1px solid #444; border-radius: 6px; margin-top: 15px;">
    <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 15px;">
        <thead style="position: sticky; top: 0; background-color: #004D40; z-index: 100;">
            <tr>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Tháng</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Tuyển Mới<br>(Người)</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Tuyến Dưới<br>(2^n - 1)</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Tổng TVKD<br>(2^n)</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">DS Nhóm<br>(VP)</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Điểm RO</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Cấp Bậc</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Bán Lẻ<br>(Tr đ)</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Hoa Hồng Sỉ<br>(Tr đ)</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Bản Quyền RO<br>(Tr đ)</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222;">Thưởng TAB<br>(Tr đ)</th>
                <th style="padding: 12px; color: #D4AF37; border: 1px solid #222; background-color: #00332a;">TỔNG<br>(Tr đ)</th>
            </tr>
        </thead>
        <tbody>
'''

for row in data_records:
    html_table += f'''
        <tr style="background-color: transparent;">
            <td style="padding: 10px; border: 1px solid #555; font-weight: bold;">{row['Tháng']}</td>
            <td style="padding: 10px; border: 1px solid #555;">{int(row['Tuyển Mới']):,}</td>
            <td style="padding: 10px; border: 1px solid #555;">{int(row['Tuyến Dưới']):,}</td>
            <td style="padding: 10px; border: 1px solid #555; font-weight: bold;">{int(row['Tổng TVKD']):,}</td>
            <td style="padding: 10px; border: 1px solid #555;">{int(row['DS Nhóm']):,}</td>
            <td style="padding: 10px; border: 1px solid #555;">{row['Điểm RO']:,.1f}</td>
            <td style="padding: 10px; border: 1px solid #555; font-weight: bold; color: #D4AF37;">{row['Cấp Bậc']}</td>
            <td style="padding: 10px; border: 1px solid #555; text-align: right;">{row['Bán Lẻ']:,.1f}</td>
            <td style="padding: 10px; border: 1px solid #555; text-align: right;">{row['Sỉ']:,.1f}</td>
            <td style="padding: 10px; border: 1px solid #555; text-align: right;">{row['RO']:,.1f}</td>
            <td style="padding: 10px; border: 1px solid #555; text-align: right;">{row['TAB']:,.1f}</td>
            <td style="padding: 10px; border: 1px solid #555; text-align: right; font-weight: bold; color: #4CAF50;">{row['TỔNG']:,.1f}</td>
        </tr>
    '''

html_table += '</tbody></table></div>'
st.markdown(html_table, unsafe_allow_html=True)

st.write("### 📈 Biểu Đồ Cơ Cấu Thu Nhập (Triệu VNĐ)")
df_chart = pd.DataFrame(data_records).set_index("Tháng")[["Bán Lẻ", "Sỉ", "RO", "TAB"]]
st.bar_chart(df_chart)