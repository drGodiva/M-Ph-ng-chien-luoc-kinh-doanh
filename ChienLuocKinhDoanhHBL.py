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

# Tùy biến giao diện (Màu Emerald Green & Metallic Gold)
st.markdown("""
    <style>
    .main-title { color: #004D40; text-align: center; font-weight: 800; font-size: 24px; margin-bottom: 5px; }
    .sub-title { color: #D4AF37; text-align: center; font-weight: 600; font-size: 15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 1. SIDEBAR ---
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

# --- TIÊU ĐỀ CHÍNH ---
st.markdown("<div class='main-title'>HỆ THỐNG MÔ PHỎNG CHIẾN LƯỢC BẬC THANG LY KHAI HERBALIFE</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Chiến lược sao chép (1 TVKD + 2 Khách hàng + Bạn = 4 người dùng) chuẩn Quy chế Trả thưởng</div>", unsafe_allow_html=True)

EARN_BASE_PER_VP = 22000   # 1 VP ~ 22.000 VNĐ Cơ sở thu nhập
RO_POINT_VALUE = 27500     # 1 Điểm RO ~ 27.500 VNĐ[cite: 1]

# Cụm tiêu dùng trực tiếp của mỗi TVKD gồm chính họ + khách hàng tiêu dùng
unit_cluster_vp = (1 + cust_rate) * vp_choice

# --- CẤU TRÚC THÀNH VIÊN VÀ MÔ HÌNH HỆ THỐNG ---
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
        # Người sáng lập hành động ngay tháng 1; TVKD tuyến dưới tháng đầu ăn & học, tháng sau tuyển
        can_recruit = (self.upline is None) or (current_month > self.join_month)
        if can_recruit:
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
        elif self.accum_vp >= 4000 and not self.is_supervisor:
            self.is_qualifying = True

# --- THUẬT TOÁN TÍNH DOANH SỐ LY KHAI, HOA HỒNG SỈ VÀ RO ---
def evaluate_network(node):
    wholesale_profit_total = 0.0
    ov_3_gen = 0.0
    sup_count_3_gen = 0
    total_downline_sup_ov = 0.0

    def calculate_subtree_vp(curr):
        vp = unit_cluster_vp
        for d in curr.downlines:
            vp += calculate_subtree_vp(d)
        return vp

    def traverse_wholesale(curr, parent_rate):
        nonlocal wholesale_profit_total
        for child in curr.downlines:
            child_rate = child.discount_rate
            diff = parent_rate - child_rate
            if diff > 0:
                child_earn_base = unit_cluster_vp * EARN_BASE_PER_VP
                wholesale_profit_total += child_earn_base * diff
                traverse_wholesale(child, child_rate)

    def traverse_all_sups(curr, depth):
        nonlocal ov_3_gen, sup_count_3_gen, total_downline_sup_ov
        for child in curr.downlines:
            if child.is_supervisor:
                child_group_vp = unit_cluster_vp
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

# --- CHẠY CHU KỲ MÔ PHỎNG ---
Member._id_counter = 0
founder = Member(join_month=1)

history = []
pres_streak = 0
pres_completed_month = None

for m in range(1, simulation_months + 1):
    founder.step_month(m, new_biz_rate)

    def accumulate_all(curr):
        curr.accum_vp += unit_cluster_vp
        for d in curr.downlines:
            accumulate_all(d)
    accumulate_all(founder)

    wholesale_income, ov_3_gen, sup_3_gen, total_sup_ov = evaluate_network(founder)

    total_group_vp = unit_cluster_vp
    for d in founder.downlines:
        def get_branch_vp(curr):
            v = unit_cluster_vp
            for c in curr.downlines:
                v += get_branch_vp(c)
            return v
        total_group_vp += get_branch_vp(d)

    ro_rate = 0.05 if total_group_vp >= 2500 else 0.04
    ro_points = ov_3_gen * ro_rate

    rank = "Thành Viên (25%)"
    pb_rate = 0.0

    if ro_points >= 10000:
        pres_streak += 1
        if pres_streak >= 3:
            rank = "👑 Nhóm Chủ Tịch (Pres Team)"
            pb_rate = 0.06 if total_group_vp >= 2500 else 0.0
            if pres_completed_month is None:
                pres_completed_month = m
        else:
            rank = f"Chủ Tịch Đạt Chuẩn ({pres_streak}/3)"
            pb_rate = 0.04 if total_group_vp >= 3000 else 0.0
    else:
        pres_streak = 0
        if ro_points >= 4000:
            rank = "Nhóm Triệu Phú (Mill Team)"
            pb_rate = 0.04 if total_group_vp >= 3000 else 0.0
        elif ro_points >= 1000:
            rank = "Nhóm Phát Triển (GET Team)"
            pb_rate = 0.02 if total_group_vp >= 3500 else 0.0
        elif total_group_vp >= 10000 or ov_3_gen >= 10000:
            rank = "Nhóm Thế Giới (World Team)"
        elif founder.is_supervisor:
            rank = "Giám Sát Viên (50%)"
        elif founder.is_qualifying:
            rank = "GSV Dự Bị (Tạm 50%)"
        elif founder.accum_vp >= 2500:
            rank = "Người Bán Hàng ĐC (QP 42%)"
        elif founder.accum_vp >= 1000:
            rank = "Kiến Tạo TC (SB 42%)"
        elif founder.accum_vp >= 500:
            rank = "Tư Vấn Cao Cấp (SC 35%)"

    founder.finalize_month_status()

    # Tính thu nhập (Đổi thành đơn vị Triệu VNĐ cho trực quan, vừa vặn màn hình)
    retail_income = (unit_cluster_vp * EARN_BASE_PER_VP * founder.discount_rate) / 1e6
    wholesale_val = wholesale_income / 1e6
    ro_val = (ro_points * RO_POINT_VALUE) / 1e6
    pb_val = ((total_sup_ov * EARN_BASE_PER_VP) * pb_rate) / 1e6 if pb_rate > 0 else 0.0

    total_income = retail_income + wholesale_val + ro_val + pb_val

    def count_members(curr):
        return 1 + sum(count_members(c) for c in curr.downlines)
    total_biz = count_members(founder)

    history.append({
        "Tháng": f"Tháng {m}",
        "Tổng TVKD": total_biz,
        "GSV 3 Tầng": sup_3_gen,
        "Doanh Số Nhóm": total_group_vp,
        "Điểm RO": round(ro_points, 1),
        "Cấp Bậc Đạt Được": rank,
        "Bán Lẻ (Tr đ)": round(retail_income, 2),
        "Hoa Hồng Sỉ (Tr đ)": round(wholesale_val, 2),
        "Bản Quyền RO (Tr đ)": round(ro_val, 2),
        "Thưởng TAB (Tr đ)": round(pb_val, 2),
        "TỔNG THU NHẬP (Tr đ)": round(total_income, 2)
    })

df = pd.DataFrame(history)

# --- THÔNG BÁO VỊ TRÍ CHỦ TỊCH ---
if pres_completed_month:
    st.success(f"🎯 **XÁC NHẬN MỐC THỜI GIAN:** Bạn hoàn thành vị trí **Nhóm Chủ Tịch (President's Team)** vào **Tháng thứ {pres_completed_month}** (Đủ 3 tháng liên tiếp $\ge$ 10.000 RO theo Kế hoạch trả thưởng)[cite: 1]!")
else:
    st.warning("⚠️ Trong khung thời gian này chưa đủ 3 tháng liên tiếp $\ge$ 10.000 RO. Kéo tăng số tháng ở thanh bên trái.")

# --- THỐNG KÊ NHANH ---
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

# --- BẢNG HIỂN THỊ ĐẦY ĐỦ CÁC CỘT THU NHẬP (ẨN INDEX, VỪA KHÍT MÀN HÌNH) ---
st.write("### 📋 BẢNG THEO DÕI THĂNG TIẾN, DOANH SỐ VÀ CƠ CẤU 4 NGUỒN THU NHẬP")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True  # Ẩn cột số 0, 1, 2... thừa thãi
)

# --- BIỂU ĐỒ TRỰC QUAN HÓA ---
st.write("### 📈 Biểu Đồ Tăng Trưởng Thu Nhập Hệ Thống (Triệu VNĐ)")
chart_income = df.set_index("Tháng")[["Bán Lẻ (Tr đ)", "Hoa Hồng Sỉ (Tr đ)", "Bản Quyền RO (Tr đ)", "Thưởng TAB (Tr đ)"]]
st.bar_chart(chart_income)