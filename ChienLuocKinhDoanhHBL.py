import streamlit as st
import pandas as pd
import os

# Cấu hình trang
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

# Tùy biến giao diện (Màu chủ đạo Emerald Green & Metallic Gold)
st.markdown("""
    <style>
    .main-title { color: #004D40; text-align: center; font-weight: 800; font-size: 26px; }
    .sub-title { color: #D4AF37; text-align: center; font-weight: 600; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# --- 1. GẮN LOGO VÀO THANH BÊN (SIDEBAR) ---
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.markdown("### 🌿 MASTERING BIOLOGY")

st.sidebar.header("⚙️ CÀI ĐẶT CHIẾN LƯỢC")

vp_choice = st.sidebar.selectbox(
    "1. Định mức VP mỗi người dùng / tháng:",
    options=[125, 250, 500],
    index=0,
    help="Điểm tiêu dùng hoặc bán lẻ định mức cho mỗi cá nhân"
)

new_biz_rate = st.sidebar.number_input(
    "2. Số TVKD mới tuyển mỗi tháng (mỗi TVKD):",
    min_value=1,
    max_value=5,
    value=1,
    step=1,
    help="Tháng đầu ăn và học, từ tháng thứ 2 bắt đầu bảo trợ số lượng này"
)

cust_rate = st.sidebar.number_input(
    "3. Số khách hàng tiêu dùng thuần túy (mỗi TVKD):",
    min_value=0,
    max_value=10,
    value=2,
    step=1,
    help="Khách hàng chỉ sử dụng sản phẩm với định mức VP đã chọn"
)

simulation_months = st.sidebar.slider(
    "4. Thời gian mô phỏng (Tháng):",
    min_value=6,
    max_value=24,
    value=16
)

# --- GẮN ẢNH FOUNDER (NAME CARD) VÀ QR CUỐI SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Người sáng lập & Huấn luyện viên:**")
if os.path.exists(card_path):
    st.sidebar.image(card_path, caption="ThS. Jonathan Phụng - Người Mài Rìu", use_container_width=True)

if os.path.exists(qr_path):
    st.sidebar.image(qr_path, caption="Mã kết nối / Đóng góp", use_container_width=True)

# --- TIÊU ĐỀ CHÍNH ---
st.markdown("<div class='main-title'>HỆ THỐNG MÔ PHỎNG CHIẾN LƯỢC BẬC THANG LY KHAI HERBALIFE</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Tích hợp đầy đủ: Hoa hồng sỉ (8% - 25%), Bản quyền RO (1% - 5%) & Hoa hồng doanh số TAB (2% - 7%)</div>", unsafe_allow_html=True)

# --- CÁC HẰNG SỐ KINH TẾ QUY CHUẨN ---
EARN_BASE_PER_VP = 22000   # 1 VP ~ 22.000 VNĐ Cơ sở thu nhập[cite: 1]
RO_POINT_VALUE = 27500     # 1 Điểm RO ~ 27.500 VNĐ[cite: 1]
cluster_vp = (1 + cust_rate) * vp_choice

# --- MÔ HÌNH HÓA THÀNH VIÊN ---
class Member:
    _id_counter = 0
    def __init__(self, join_month, upline=None):
        Member._id_counter += 1
        self.id = Member._id_counter
        self.join_month = join_month
        self.upline = upline
        self.downlines = []
        self.accum_vp = 0
        self.is_qualifying = False
        self.is_supervisor = False
        self.months_as_sup = 0
        self.tab_pb_rate = 0.0

    @property
    def discount_rate(self):
        if self.is_supervisor or self.is_qualifying:
            return 0.50
        elif self.accum_vp >= 1000:
            return 0.42
        elif self.accum_vp >= 500:
            return 0.35
        return 0.25

    def step_month(self, current_month, biz_rate):
        if current_month > self.join_month:
            for _ in range(biz_rate):
                child = Member(join_month=current_month, upline=self)
                self.downlines.append(child)

        for child in self.downlines:
            child.step_month(current_month, biz_rate)

    def finalize_month_status(self):
        for child in self.downlines:
            child.finalize_month_status()

        if self.is_qualifying:
            self.is_supervisor = True
            self.is_qualifying = False
            self.months_as_sup += 1
        elif self.is_supervisor:
            self.months_as_sup += 1
        elif self.accum_vp >= 4000:
            self.is_qualifying = True

# --- THUẬT TOÁN ĐÁNH GIÁ MẠNG LƯỚI ---
def evaluate_network(node, current_month):
    wholesale_profit_total = 0.0
    ov_3_gen = 0.0
    sup_count_3_gen = 0
    total_downline_sup_ov = 0.0

    def calculate_subtree_vp(curr):
        vp = cluster_vp
        for d in curr.downlines:
            vp += calculate_subtree_vp(d)
        return vp

    def traverse_wholesale(curr, parent_rate):
        nonlocal wholesale_profit_total
        for child in curr.downlines:
            child_rate = child.discount_rate
            diff = parent_rate - child_rate
            if diff > 0:
                child_personal_earn_base = cluster_vp * EARN_BASE_PER_VP
                wholesale_profit_total += child_personal_earn_base * diff
                traverse_wholesale(child, child_rate)

    def traverse_all_sups(curr, depth):
        nonlocal ov_3_gen, sup_count_3_gen, total_downline_sup_ov
        for child in curr.downlines:
            if child.is_supervisor:
                child_group_vp = cluster_vp
                for sub in child.downlines:
                    if not sub.is_supervisor:
                        child_group_vp += calculate_subtree_vp(sub)
                
                if 1 <= depth <= 3:
                    sup_count_3_gen += 1
                    ov_3_gen += child_group_vp

                total_downline_sup_ov += child_group_vp
                traverse_all_sups(child, depth + 1)
            else:
                traverse_all_sups(child, depth)

    if node.discount_rate > 0.25:
        traverse_wholesale(node, node.discount_rate)

    if node.is_supervisor:
        traverse_all_sups(node, 1)

    return wholesale_profit_total, ov_3_gen, sup_count_3_gen, total_downline_sup_ov

# --- CHẠY CHU KỲ TÍNH TOÁN ---
Member._id_counter = 0
founder = Member(join_month=1)
founder.accum_vp = cluster_vp

history = []
pres_qualify_streak = 0
pres_completed_month = None

for m in range(1, simulation_months + 1):
    founder.step_month(m, new_biz_rate)

    def accumulate_all(curr):
        curr.accum_vp += cluster_vp
        for d in curr.downlines:
            accumulate_all(d)
    accumulate_all(founder)

    wholesale_income, ov_3_gen, sup_3_gen, total_sup_ov = evaluate_network(founder, m)

    total_group_vp = cluster_vp
    for d in founder.downlines:
        def get_branch_vp(curr):
            v = cluster_vp
            for c in curr.downlines:
                v += get_branch_vp(c)
            return v
        total_group_vp += get_branch_vp(d)

    ro_rate = 0.05 if total_group_vp >= 2500 else 0.04
    ro_points = ov_3_gen * ro_rate

    rank = "Thành Viên (25%)"
    pb_rate = 0.0

    if ro_points >= 10000:
        pres_qualify_streak += 1
        if pres_qualify_streak >= 3:
            rank = "👑 Nhóm Chủ Tịch (President's Team)"
            pb_rate = 0.06 if total_group_vp >= 2500 else 0.0
            founder.tab_pb_rate = pb_rate
            if pres_completed_month is None:
                pres_completed_month = m
        else:
            rank = f"Chủ Tịch Đạt Chuẩn (Tháng {pres_qualify_streak}/3)"
            pb_rate = 0.04 if total_group_vp >= 3000 else 0.0
            founder.tab_pb_rate = pb_rate
    else:
        pres_qualify_streak = 0
        if ro_points >= 4000:
            rank = "Nhóm Triệu Phú (Millionaire Team)"
            pb_rate = 0.04 if total_group_vp >= 3000 else 0.0
            founder.tab_pb_rate = pb_rate
        elif ro_points >= 1000:
            rank = "Nhóm Phát Triển Toàn Cầu (GET Team)"
            pb_rate = 0.02 if total_group_vp >= 3500 else 0.0
            founder.tab_pb_rate = pb_rate
        elif total_group_vp >= 10000 or ov_3_gen >= 10000:
            rank = "Nhóm Thế Giới (World Team)"
            founder.tab_pb_rate = 0.0
        elif founder.is_supervisor:
            rank = "Giám Sát Viên (Supervisor 50%)"
            founder.tab_pb_rate = 0.0
        elif founder.is_qualifying:
            rank = "Giám Sát Viên Dự Bị (Tạm 50%)"
            founder.tab_pb_rate = 0.0
        elif founder.accum_vp >= 2500:
            rank = "Người Bán Hàng Đạt Chuẩn (QP 42%)"
        elif founder.accum_vp >= 1000:
            rank = "Nhà Kiến Tạo Thành Công (SB 42%)"
        elif founder.accum_vp >= 500:
            rank = "Tư Vấn Viên Cao Cấp (SC 35%)"

    founder.finalize_month_status()

    retail_income = cluster_vp * EARN_BASE_PER_VP * founder.discount_rate
    wholesale_val = wholesale_income
    ro_val = ro_points * RO_POINT_VALUE
    pb_val = (total_sup_ov * EARN_BASE_PER_VP) * pb_rate if pb_rate > 0 else 0

    total_est_income = retail_income + wholesale_val + ro_val + pb_val

    def count_members(curr):
        return 1 + sum(count_members(c) for c in curr.downlines)
    total_biz = count_members(founder)

    history.append({
        "Tháng": f"Tháng {m}",
        "Tổng TVKD": total_biz,
        "GSV Ly Khai (3 Tầng)": sup_3_gen,
        "Doanh Số Nhóm (VP)": total_group_vp,
        "Doanh Số 3 Tầng GSV (OV)": ov_3_gen,
        "Điểm RO": round(ro_points, 1),
        "Cấp Bậc Đạt Chuẩn": rank,
        "Tỷ Lệ PB (%)": f"{int(pb_rate*100)}%" if pb_rate > 0 else "0%",
        "Hoa Hồng Sỉ (VNĐ)": round(wholesale_val, -3),
        "Tiền Bản Quyền RO (VNĐ)": round(ro_val, -3),
        "Hoa Hồng Doanh Số PB (VNĐ)": round(pb_val, -3),
        "Tổng Thu Nhập (VNĐ)": round(total_est_income, -4)
    })

df = pd.DataFrame(history)

# --- HIỂN THỊ KẾT QUẢ THỜI ĐIỂM ĐẠT CHỦ TỊCH ---
if pres_completed_month:
    st.success(f"🎯 **XÁC NHẬN MỐC THỜI GIAN:** Hoàn thành vị trí **Nhóm Chủ Tịch (President's Team)** vào **Tháng thứ {pres_completed_month}** (Đạt chuẩn 3 tháng liên tiếp trên 10.000 Điểm RO)[cite: 1].")
else:
    st.warning("⚠️ Chưa đủ 3 tháng liên tiếp đạt 10.000 RO trong khung thời gian này. Hãy kéo tăng thời gian mô phỏng hoặc chọn định mức VP cao hơn[cite: 1].")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Tổng TVKD Cuối Kỳ", f"{df.iloc[-1]['Tổng TVKD']:,} TVKD")
with col2:
    st.metric("Điểm RO Tháng Cuối", f"{df.iloc[-1]['Điểm RO']:,} RO")
with col3:
    st.metric("Tỷ Lệ PB Đạt Được", df.iloc[-1]["Tỷ Lệ PB (%)"])
with col4:
    st.metric("Thu Nhập Tháng Cuối", f"{df.iloc[-1]['Tổng Thu Nhập (VNĐ)']/1e6:,.1f} Tr VNĐ")

st.write("---")

st.write("### 📋 BẢNG THEO DÕI THĂNG TIẾN, DOANH SỐ VÀ CƠ CẤU 4 NGUỒN THU NHẬP")
st.dataframe(
    df[[
        "Tháng", "Tổng TVKD", "GSV Ly Khai (3 Tầng)", "Doanh Số Nhóm (VP)", 
        "Doanh Số 3 Tầng GSV (OV)", "Điểm RO", "Cấp Bậc Đạt Chuẩn", "Tỷ Lệ PB (%)",
        "Hoa Hồng Sỉ (VNĐ)", "Tiền Bản Quyền RO (VNĐ)", "Hoa Hồng Doanh Số PB (VNĐ)", "Tổng Thu Nhập (VNĐ)"
    ]].style.format({
        "Tổng TVKD": "{:,.0f}",
        "GSV Ly Khai (3 Tầng)": "{:,.0f}",
        "Doanh Số Nhóm (VP)": "{:,.0f}",
        "Doanh Số 3 Tầng GSV (OV)": "{:,.0f}",
        "Điểm RO": "{:,.1f}",
        "Hoa Hồng Sỉ (VNĐ)": "{:,.0f}",
        "Tiền Bản Quyền RO (VNĐ)": "{:,.0f}",
        "Hoa Hồng Doanh Số PB (VNĐ)": "{:,.0f}",
        "Tổng Thu Nhập (VNĐ)": "{:,.0f}"
    }),
    use_container_width=True
)

st.write("### 📈 Biểu Đồ So Sánh Các Nguồn Thu Nhập Lãnh Đạo (VNĐ)")
chart_income = df.set_index("Tháng")[["Tiền Bản Quyền RO (VNĐ)", "Hoa Hồng Doanh Số PB (VNĐ)", "Hoa Hồng Sỉ (VNĐ)"]]
st.bar_chart(chart_income)