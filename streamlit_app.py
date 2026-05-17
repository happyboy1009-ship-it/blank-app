import streamlit as st
import pandas as pd
from io import BytesIO

# 페이지 전체 레이아웃 및 타이틀 설정
st.set_page_config(page_title="[청출어람] 재개발 수익율 계산기", layout="wide")

# ==========================================
# 🔒 보안 설정: 요청하신 비밀번호 '0815' 반영완료!
# ==========================================
SECRET_PASSWORD = "0815" 

# 숫자에 콤마를 넣고 빼는 변환 함수 정의
def to_int(val_str):
    try:
        clean_str = val_str.replace(",", "").replace(" ", "")
        return int(clean_str) if clean_str else 0
    except ValueError:
        return 0

def fmt(val):
    return f"{int(val):,}"

# 항목 이름(1.2배)과 숫자(0.7배)의 크기를 맞춤 조절하여 출력하는 함수
def display_metric(label, value_str):
    st.markdown(
        f"""
        <div style="background-color: #1e222b; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #31333f;">
            <p style="font-size: 20px; font-weight: bold; color: #e0e0e0; margin-bottom: 5px;">{label}</p>
            <p style="font-size: 22px; font-weight: 500; color: #2ecc71; margin: 0;">{value_str}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- 🔑 비밀번호 체크 로직 ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔒 [청출어람] 보안 잠금 화면")
    st.write("이 시스템은 허가된 사용자만 이용할 수 있습니다. 비밀번호를 입력해 주세요.")
    
    user_password = st.text_input("비밀번호 입력", type="password", placeholder="비밀번호를 입력하고 엔터를 누르세요.")
    
    if user_password:
        if user_password == SECRET_PASSWORD:
            st.session_state["logged_in"] = True
            st.success("🔓 인증 성공! 잠시만 기다려주세요...")
            st.rerun()
        else:
            st.error("❌ 비밀번호가 올바르지 않습니다. 다시 입력해 주세요.")
            
    st.stop()

# =========================================================================
# 🏠 진짜 메인 프로그램 (인증 성공 시 진입)
# =========================================================================

# 매물 목록을 기억할 저장소(세션 상태)가 없으면 만들어줍니다.
if "property_list" not in st.session_state:
    st.session_state["property_list"] = []

# 메인 타이틀
st.title("🏠 [청출어람] 재개발 수익율 계산기")
st.write("재개발 매물의 정보를 입력하여 실투자금과 예상 수익률을 정밀하게 분석합니다.")

# 우측 상단에 로그아웃 버튼 배치
col_title, col_logout = st.columns([9, 1])
with col_logout:
    if st.button("🚪 로그아웃"):
        st.session_state["logged_in"] = False
        st.rerun()

st.markdown("---")

# --- 왼쪽 사이드바 메뉴 구성 ---
st.sidebar.header("📍 매물 기본 정보")
asset_name = st.sidebar.text_input("매물 이름", value="청안구 재개발 구역")
asset_source = st.sidebar.text_input("매물 출처", value="OO 부동산 / 네이버 부동산")
asset_memo = st.sidebar.text_area("매물 메모", placeholder="매물 특징이나 현장 분위기를 기록하세요.", height=150)

st.sidebar.markdown("---")

# 💰 총 투자금 계산기 섹션
st.sidebar.header("💰 총 투자금 계산기")

# 대지지분 입력
land_area_input = st.sidebar.text_input("대지지분 (평)", value="15.0")
try:
    land_area = float(land_area_input.replace(",", "")) if land_area_input else 1.0
except ValueError:
    land_area = 1.0

p_price_str = st.sidebar.text_input("매매가", value="600,000,000")
purchase_price = to_int(p_price_str)

pub_price_str = st.sidebar.text_input("공주가", value="200,000,000")
public_price = to_int(pub_price_str)

gen_price_str = st.sidebar.text_input("일반 분양가 (주변시세)", value="900,000,000")
general_sales_price = to_int(gen_price_str)

tgt_price_str = st.sidebar.text_input("예상목표금액", value="1,200,000,000")
target_price = to_int(tgt_price_str)

redev_period_str = st.sidebar.text_input("재개발 예상기간 (년)", value="5")
try:
    redev_period = int(redev_period_str)
except ValueError:
    redev_period = 0

# 🏦 금융 비용 설정 섹션
st.sidebar.header("🏦 금융 비용 설정")
loan_str = st.sidebar.text_input("대출금", value="200,000,000")
loan_amount = to_int(loan_str)

interest_rate_input = st.sidebar.text_input("금리 (%)", value="4.5")
try:
    interest_rate = float(interest_rate_input)
except ValueError:
    interest_rate = 0.0

# 총이자 수식
calculated_total_interest = int(loan_amount * (interest_rate / 100) * redev_period)
st.sidebar.text_input("총이자", value=fmt(calculated_total_interest), disabled=True)


# --- 내부 계산 로직 영역 ---
calculated_py_price = int(purchase_price / land_area) if land_area > 0 else 0
calculated_gampyung = public_price * 2
chobun_price = int(general_sales_price * 0.7)
bundam_price = chobun_price - calculated_gampyung
premium = purchase_price - calculated_gampyung
total_investment = bundam_price + purchase_price
final_net_investment = total_investment + calculated_total_interest
expected_revenue = target_price - final_net_investment


# --- 우측 메인 화면 출력 영역 ---
st.subheader(f"📊 [{asset_name}] 재개발 투자 자금 분석 결과")

# 상단 요약 정보
st.markdown(
    f"""
    <div style="font-size: 18px; color: #a0aab5; margin-bottom: 15px; line-height: 1.6;">
        📍 <b>출처:</b> {asset_source} &nbsp;|&nbsp; 📐 <b>대지지분:</b> {land_area:.1f}평 &nbsp;|&nbsp; ⏳ <b>예상 기간:</b> {redev_period}년
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# [첫 번째 줄] 평단가와 감평가
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    display_metric("📐 평단가 (매매가 / 대지지분)", f"{fmt(calculated_py_price)} 원")
with row1_col2:
    display_metric("🔍 감평가 (공주가 x 2)", f"{fmt(calculated_gampyung)} 원")

# [두 번째 줄] 조합원 분양가와 분담금
row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    display_metric("🏢 조합원 분양가 (일반분양가 x 70%)", f"{fmt(chobun_price)} 원")
with row2_col2:
    display_metric("💰 분담금 (조합원분양가 - 감평가)", f"{fmt(bundam_price)} 원")

# [세 번째 줄] 프리미엄과 총 투자금액
row3_col1, row3_col2 = st.columns(2)
with row3_col1:
    display_metric("🏢 프리미엄 (매수금액 - 감평가)", f"{fmt(premium)} 원")
with row3_col2:
    display_metric("🏢 총 투자금액 (분담금 + 매수금액)", f"{fmt(total_investment)} 원")

# [네 번째 줄] 최종 실투자금과 수익금
row4_col1, row4_col2 = st.columns(2)
with row4_col1:
    display_metric("💸 최종 실투자금 (투자금액 + 총이자)", f"{fmt(final_net_investment)} 원")
with row4_col2:
    display_metric("💰 수익금 (예상목표금액 - 최종 실투자금액)", f"{fmt(expected_revenue)} 원")

st.markdown("---")

# 매물 정보 표시
st.markdown("### 📝 매물 정보")
if asset_memo.strip():
    st.markdown(
        f"""
        <div style="background-color: #1e222b; padding: 20px; border-radius: 10px; border: 1px solid #4b5563; min-height: 100px; white-space: pre-wrap; font-size: 16px; color: #f3f4f6;">
{asset_memo}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("작성된 매물 정보가 없습니다. 왼쪽 사이드바의 '매물 메모' 칸에 내용을 입력해 보세요.")

st.markdown("---")


# =========================================================================
# 💾 임장 매물 저장 장부 기능 구현 영역
# =========================================================================
st.markdown("### 🗂️ 임장 매물 저장 장부")

# 나란히 배치하기 위해 버튼용 컬럼 공간 분할
btn_col1, btn_col2, btn_spacer = st.columns([2, 2, 6])

# 데이터 저장용 한 줄 딕셔너리 구성
current_data = {
    "매물 이름": asset_name,
    "출처": asset_source,
    "대지지분(평)": land_area,
    "매매가(원)": purchase_price,
    "공주가(원)": public_price,
    "감평가(원)": calculated_gampyung,
    "프리미엄(원)": premium,
    "분담금(원)": bundam_price,
    "총 투자금액(원)": total_investment,
    "최종 실투자금(원)": final_net_investment,
    "예상 수익금(원)": expected_revenue,
    "메모": asset_memo
}

# [버튼 1] 현재 매물 저장하기
with btn_col1:
    if st.button("📌 현재 매물 목록에 추가", use_container_width=True):
        st.session_state["property_list"].append(current_data)
        st.toast(f"✅ [{asset_name}] 장부에 추가되었습니다!")

# [버튼 2] 엑셀 파일 다운로드
with btn_col2:
    if st.session_state["property_list"]:
        df = pd.DataFrame(st.session_state["property_list"])
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='재개발 매물 목록')
        excel_data = excel_buffer.getvalue()
        
        st.download_button(
            label="📥 엑셀 파일 다운로드",
            data=excel_data,
            file_name="재개발_임장_매물목록.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.button("📥 엑셀 파일 다운로드", disabled=True, use_container_width=True, help="저장된 매물이 있어야 다운로드 가능합니다.")

# 테이블 출력 공간
if st.session_state["property_list"]:
    display_df = pd.DataFrame(st.session_state["property_list"])
    format_cols = ["매매가(원)", "공주가(원)", "감평가(원)", "프리미엄(원)", "분담금(원)", "총 투자금액(원)", "최종 실투자금(원)", "예상 수익금(원)"]
    for col in format_cols:
        display_df[col] = display_df[col].map(lambda x: f"{int(x):,}")
        
    st.dataframe(display_df, use_container_width=True)
    
    if st.button("🗑️ 장부 전체 초기화", size="small"):
        st.session_state["property_list"] = []
        st.rerun()
else:
    st.info("💡 왼쪽 사이드바에 매물 정보를 적으신 후, [📌 현재 매물 목록에 추가] 버튼을 누르면 나만의 임장 장부 표가 이곳에 생성됩니다.")

st.markdown("---")