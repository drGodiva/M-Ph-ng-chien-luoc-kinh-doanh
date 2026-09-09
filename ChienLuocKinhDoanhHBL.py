import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Mô Phỏng Kế Hoạch Kinh Doanh Herbalife", page_icon="🌿", layout="wide")

# --- 1. ĐƯỜNG DẪN TÀI NGUYÊN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

logo_path = os.path.join(ASSETS_DIR, "MBAlogo.png")
card_path = os.path.join(ASSETS_DIR, "founderMBA.jpg")
qr_path = os.path.join(ASSETS_DIR, "qr_ngan_hang.png")

# --- 2. CSS BẢNG HTML SIÊU TỐC VÀ CỐ ĐỊNH TIÊU ĐỀ (STICKY HEADER) ---
st.markdown("""
    <style>
    .main-title { color: #004D40; text-align: center; font-weight: 800; font-size: 26px; margin-bottom: 5px; }
    .sub-title { color: #D4AF37; text-align: center; font-weight: 600; font-size: 16px; margin-bottom: 25px; }
    
    .table-container {
        max-height: 600px;
        overflow-y: auto;
        overflow-x: auto;
        border-radius: 8px;
        border: 1px solid #ddd;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    
    .sticky-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14.5px;
    }
    
    .sticky-table th {
        position: sticky;
        top: 0;
        background-color: #004D40 !important;
        color: #D4AF37 !important;
        padding: 12px 10px;
        z-index: 2;
        text-align: center;
        border: 1px solid #00332a;
        white-space: nowrap;
    }
    
    .sticky-table td {
        padding: 10px 8px;
        border: 1px solid #ddd;
        text-align: right;
        white-space: nowrap; 
    }
    
    .sticky-table tr:nth-child(even) { background-color: #f4fbf7; }
    .sticky-table tr:hover { background-color: #e2f3eb; }
    .text-center { text-align: center !important; }
    .text-bold { font-weight: bold !important; }
    .highlight-col { background-color: #e8f5e9; font-weight: bold; color: #004D40; }
    </style>
""", unsafe_allow_html=True)

# --- 3. THANH CÔNG CỤ (SIDEBAR) ---
if os.path.exists(logo_path):
    st.sidebar.image(logo_path)
else:
    st.sidebar.markdown("### 🌿 MASTERING BIOLOGY")

st.sidebar.header("⚙️ CÀI ĐẶT CHIẾN LƯỢC")

vp_choice = st.sidebar.selectbox("1. Định mức VP mỗi người dùng / tháng:", options=[100, 125, 250, 500], index=1)
new_biz_rate = st.sidebar.number_input("2. Số TVKD mới tuyển mỗi tháng (mỗi TVKD):", min_value=1, max_value=5, value=1)
cust_rate = st.sidebar.number_input("3. Số khách tiêu dùng thuần túy (mỗi TVKD):", min_value=0, max_value=10, value=2)
simulation_months = st.sidebar.slider("4. Thời gian mô phỏng (Tháng):", min_value=6, max_value=24, value=16)

st.sidebar.markdown("---")
if os.path.exists(card_path): st.sidebar.image(card_path, caption="ThS. Jonathan Phụng")
if os.path.exists(qr_path): st.sidebar.image(qr_path, caption="Mã QR Kết nối")

# --- 4. THUẬT TOÁN COHORT (CHÍNH XÁC 100%, KHÔNG CRASH) ---
EARN_BASE_PER_VP = 22000   
RO_POINT_VALUE = 27500     
unit_cluster_vp = (1 + cust_rate) * vp_choice
MAX_AGE = simulation_months + 2

# A. Tiền tính hóa sự phát triển của 1 nhánh tiêu chuẩn
vp = [0] * MAX_AGE
accum = [0] * MAX_AGE
is_qualifying = [False] * MAX_AGE
is_gsv = [False] * MAX_AGE
gv = [0] * MAX_AGE
ov1 = [0] * MAX_AGE; ov2 = [0] * MAX_AGE; ov3 = [0] * MAX_AGE; ov4p = [0] * MAX_AGE
discount = [0.25] * MAX_AGE
pb_rate = [0.0] * MAX_AGE
ro_streak = [0] * MAX_AGE
rank_name = ["TV"] * MAX_AGE

for j in range(1, MAX_AGE):
    if j == 1: # Tháng 1 của tuyến dưới chỉ ăn học
        vp[j] = accum[j] = gv[j] = vp_choice
        discount[j] = 0.25
        rank_name[j] = "TV"
    else:
        vp[j] = unit_cluster_vp + sum(new_biz_rate * vp[i] for i in range(1, j))
        accum[j] = accum[j-1] + vp[j]

        if is_qualifying[j-1] or is_gsv[j-1]: is_gsv[j] = True
        if not is_gsv[j] and accum[j] >= 4000: is_qualifying[j] = True

        curr_gv = unit_cluster_vp
        curr_o1 = curr_o2 = curr_o3 = curr_o4p = 0
        for i in range(1, j):
            if is_gsv[i]:
                curr_o1 += new_biz_rate * gv[i]
                curr_o2 += new_biz_rate * ov1[i]
                curr_o3 += new_biz_rate * ov2[i]
                curr_o4p += new_biz_rate * (ov3[i] + ov4p[i])
            else:
                curr_gv += new_biz_rate * vp[i]

        gv[j], ov1[j], ov2[j], ov3[j], ov4p[j] = curr_gv, curr_o1, curr_o2, curr_o3, curr_o4p

        if is_qualifying[j] or is_gsv[j]: discount[j] = 0.50
        elif accum[j] >= 1000: discount[j] = 0.42
        elif accum[j] >= 500: discount[j] = 0.35
        else: discount[j] = 0.25

        if is_gsv[j]:
            ro_rt = 0.05 if gv[j] >= 2500 else 0.04
            ro_pts = (ov1[j] + ov2[j] + ov3[j]) * ro_rt
            ro_streak[j] = ro_streak[j-1] + 1 if ro_pts >= 10000 else 0
            if ro_streak[j] >= 3: rank_name[j] = "PRES"; pb_rate[j] = 0.06
            elif ro_pts >= 4000: rank_name[j] = "MILL"; pb_rate[j] = 0.04
            elif ro_pts >= 1000: rank_name[j] = "GET"; pb_rate[j] = 0.02
            elif gv[j] >= 10000 or (ov1[j]+ov2[j]+ov3[j]) >= 10000: rank_name[j] = "WT"
            else: rank_name[j] = "GSV"
        else:
            if is_qualifying[j] or accum[j] >= 2500: rank_name[j] = "QP"
            elif accum[j] >= 1000: rank_name[j] = "SB"
            elif accum[j] >= 500: rank_name[j] = "SC"
            else: rank_name[j] = "TV"

# Tính lượng người mới sinh ra toàn hệ thống
created_in_month = [0] * MAX_AGE
for m in range(1, MAX_AGE):
    created_in_month[m] = new_biz_rate if m == 1 else new_biz_rate + sum(created_in_month[x] * new_biz_rate for x in range(1, m))

# B. Mô phỏng Người Sáng Lập (Bạn)
st.markdown("<div class='main-title'>HỆ THỐNG MÔ PHỎNG CHIẾN LƯỢC BẬC THANG LY KHAI HERBALIFE</div>", unsafe_allow_html=True)

data_records = []
f_accum = 0
f_is_gsv = False
f_is_qualifying = False
f_streak = 0
pres_completed_month = None

for M in range(1, simulation_months + 1):
    if f_is_qualifying:
        f_is_gsv = True
        f_is_qualifying = False

    f_gv = unit_cluster_vp
    f_ov1 = f_ov2 = f_ov3 = f_ov4p = 0
    
    # Xác định mức chiết khấu hiện tại
    if f_is_gsv or f_is_qualifying: f_discount = 0.50
    elif f_accum >= 1000: f_discount = 0.42
    elif f_accum >= 500: f_discount = 0.35
    else: f_discount = 0.25

    # Tính Doanh số & Nút chặn Hoa hồng sỉ
    f_wholesale_vp = 0
    for i in range(1, M+1):
        if is_gsv[i]:
            f_ov1 += new_biz_rate * gv[i]
            f_ov2 += new_biz_rate * ov1[i]
            f_ov3 += new_biz_rate * ov2[i]
            f_ov4p += new_biz_rate * (ov3[i] + ov4p[i])
        else:
            f_gv += new_biz_rate * vp[i]
            f_wholesale_vp += new_biz_rate * vp[i] * max(0, f_discount - discount[i])

    f_accum += f_gv # Tích lũy để thăng cấp

    if not f_is_gsv and f_accum >= 4000:
        f_is_qualifying = True
        f_discount = 0.50

    if not f_is_gsv and not f_is_qualifying:
        if f_accum >= 1000: f_discount = 0.42
        elif f_accum >= 500: f_discount = 0.35

    # Cập nhật lại Hoa hồng sỉ nếu được thăng cấp giữa tháng
    f_wholesale_vp = 0
    for i in range(1, M+1):
        if not is_gsv[i]:
            f_wholesale_vp += new_biz_rate * vp[i] * max(0, f_discount - discount[i])

    # Tính RO và Nút chặn Hoa hồng Doanh số (PB)
    f_ro_rate = 0.05 if f_gv >= 2500 else 0.04
    f_ro_pts = (f_ov1 + f_ov2 + f_ov3) * f_ro_rate
    
    f_pb_rate = 0.0
    f_rank = ""
    if f_is_gsv:
        if f_ro_pts >= 10000:
            f_streak += 1
            if f_streak >= 3:
                f_rank = "👑 PRES"; f_pb_rate = 0.06
                if pres_completed_month is None: pres_completed_month = M
            else:
                f_rank = f"PRES ĐC ({f_streak}/3)"; f_pb_rate = 0.04
        else:
            f_streak = 0
            if f_ro_pts >= 4000: f_rank = "MILL"; f_pb_rate = 0.04
            elif f_ro_pts >= 1000: f_rank = "GET"; f_pb_rate = 0.02
            elif f_gv >= 10000 or (f_ov1+f_ov2+f_ov3) >= 10000: f_rank = "WT"
            else: f_rank = "GSV"
    else:
        if f_is_qualifying or f_accum >= 2500: f_rank = "QP"
        elif f_accum >= 1000: f_rank = "SB"
        elif f_accum >= 500: f_rank = "SC"
        else: f_rank = "TV"

    f_pb_vp = 0
    for i in range(1, M+1):
        if is_gsv[i]:
            total_branch_gsv = gv[i] + ov1[i] + ov2[i] + ov3[i] + ov4p[i]
            f_pb_vp += new_biz_rate * max(0, f_pb_rate - pb_rate[i]) * total_branch_gsv

    # Tính Thu Nhập Thực Tế
    retail_inc = (unit_cluster_vp * EARN_BASE_PER_VP * f_discount) / 1e6
    wholesale_inc = (f_wholesale_vp * EARN_BASE_PER_VP) / 1e6
    ro_inc = (f_ro_pts * RO_POINT_VALUE) / 1e6
    pb_inc = (f_pb_vp * EARN_BASE_PER_VP) / 1e6
    total_inc = retail_inc + wholesale_inc + ro_inc + pb_inc

    # Thống kê tổ chức
    total_tvkd = 1 + sum(created_in_month[1:M+1])
    sys_gsv = sum(created_in_month[M - i + 1] for i in range(1, M+1) if rank_name[i] in ["GSV", "WT", "GET", "MILL", "PRES"])
    sys_tab = sum(created_in_month[M - i + 1] for i in range(1, M+1) if rank_name[i] in ["GET", "MILL", "PRES"])

    data_records.append({
        "Tháng": f"Tháng {M}",
        "TVKD": int(total_tvkd),
        "GSV": int(sys_gsv),
        "TAB": int(sys_tab),
        "DS Nhóm": int(f_gv),
        "Điểm RO": f_ro_pts,
        "Cấp Bậc": f_rank,
        "Bán Lẻ": retail_inc,
        "Sỉ": wholesale_inc,
        "RO": ro_inc,
        "Thưởng TAB": pb_inc,
        "TỔNG": total_inc
    })

# --- 5. RENDER BẢNG STICKY VÀ HIỂN THỊ ---
if pres_completed_month:
    st.success(f"🎯 **XÁC NHẬN MỐC THỜI GIAN:** Lên **Nhóm Chủ Tịch (President's Team)** vào **Tháng thứ {pres_completed_month}** (Đạt chuẩn 3 tháng liên tiếp >= 10.000 RO)[cite: 1]!")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Tổng TVKD Cuối Kỳ", f"{data_records[-1]['TVKD']:,}")
with col2: st.metric("Hệ Thống GSV (Gồm TAB)", f"{data_records[-1]['GSV']:,}")
with col3: st.metric("Hệ Thống TAB Team", f"{data_records[-1]['TAB']:,}")
with col4: st.metric("TỔNG THU NHẬP Tháng Cuối", f"{data_records[-1]['TỔNG']:,.1f} Tr đ")

st.write("### 📋 BẢNG TIẾN ĐỘ THĂNG TIẾN, NHÂN SỰ VÀ DOANH THU")
html_table = '''
<div class="table-container">
    <table class="sticky-table">
        <thead>
            <tr>
                <th>Tháng</th>
                <th>Tổng<br>TVKD</th>
                <th>Số GSV<br>Ly Khai</th>
                <th>Số TAB<br>Team</th>
                <th>DS Nhóm<br>(VP)</th>
                <th>Điểm RO</th>
                <th>Cấp Bậc<br>Của Bạn</th>
                <th>Bán Lẻ<br>(Tr đ)</th>
                <th>Hoa Hồng Sỉ<br>(Tr đ)</th>
                <th>Bản Quyền RO<br>(Tr đ)</th>
                <th>Thưởng TAB<br>(Tr đ)</th>
                <th>TỔNG THU NHẬP<br>(Tr đ)</th>
            </tr>
        </thead>
        <tbody>
'''

for row in data_records:
    html_table += f'''
        <tr>
            <td class="text-center text-bold">{row['Tháng']}</td>
            <td class="text-center">{row['TVKD']:,}</td>
            <td class="text-center">{row['GSV']:,}</td>
            <td class="text-center">{row['TAB']:,}</td>
            <td class="text-center">{row['DS Nhóm']:,}</td>
            <td class="text-center">{row['Điểm RO']:,.1f}</td>
            <td class="text-center text-bold">{row['Cấp Bậc']}</td>
            <td>{row['Bán Lẻ']:,.1f}</td>
            <td>{row['Sỉ']:,.1f}</td>
            <td>{row['RO']:,.1f}</td>
            <td>{row['Thưởng TAB']:,.1f}</td>
            <td class="highlight-col">{row['TỔNG']:,.1f}</td>
        </tr>
    '''

html_table += '</tbody></table></div>'
st.markdown(html_table, unsafe_allow_html=True)

st.write("### 📈 Biểu Đồ Cơ Cấu Thu Nhập (Triệu VNĐ)")
df_chart = pd.DataFrame(data_records).set_index("Tháng")[["Bán Lẻ", "Sỉ", "RO", "Thưởng TAB"]]
st.bar_chart(df_chart)