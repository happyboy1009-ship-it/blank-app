import streamlit as st

st.set_page_config(
    page_title="[청출어람] 재개발 수익율 계산기",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 🔒 보안 설정: 요청하신 비밀번호 '0815' 반영완료!
# ==========================================
SECRET_PASSWORD = "0815"

# 숫자에 콤마를 넣고 빼는 변환 함수 정의
def to_int(val_str):
    """쉼표가 포함된 문자열을 숫자로 변환"""
    try:
        clean_str = val_str.replace(",", "").replace(" ", "")
        return int(clean_str) if clean_str else 0
    except ValueError:
        return 0


def fmt(val):
    """숫자를 쉼표가 있는 문자열로 변환"""
    return f"{int(val):,}"


# 항목 이름과 숫자를 함께 보여주는 출력 함수
def display_metric(label, value_str):
    st.markdown(
        f"""
        <div style="background-color: #1e222b; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #31333f;">
            <p style="font-size: 20px; font-weight: bold; color: #e0e0e0; margin-bottom: 5px;">{label}</p>
            <p style="font-size: 22px; font-weight: 500; color: #2ecc71; margin: 0;">{value_str}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
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

    st.title("🏠 [청출어람] 재개발 수익율 계산기")
    st.write("재개발 매물의 정보를 입력하여 실투자금과 예상 수익률을 정밀하게 분석합니다.")

    _, col_logout = st.columns([9, 1])
    with col_logout:
        if st.button("🚪 로그아웃"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.markdown("---")

    st.sidebar.header("📍 매물 기본 정보")
    asset_name = st.sidebar.text_input("매물 이름", value="청안구 재개발 구역")
    asset_source = st.sidebar.text_input("매물 출처", value="OO 부동산 / 네이버 부동산")
    asset_memo = st.sidebar.text_area(
        "매물 메모",
        placeholder="매물 특징이나 현장 분위기를 기록하세요.",
        height=150,
    )

    st.sidebar.markdown("---")
    st.sidebar.header("💰 총 투자금 계산기")

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

    st.sidebar.header("🏦 금융 비용 설정")
    loan_str = st.sidebar.text_input("대출금", value="200,000,000")
    loan_amount = to_int(loan_str)

    interest_rate_input = st.sidebar.text_input("금리 (%)", value="4.5")
    try:
        interest_rate = float(interest_rate_input)
    except ValueError:
        interest_rate = 0.0

    calculated_total_interest = int(loan_amount * (interest_rate / 100) * redev_period)
    st.sidebar.text_input("총이자", value=fmt(calculated_total_interest), disabled=True)

    calculated_py_price = int(purchase_price / land_area) if land_area > 0 else 0
    calculated_gampyung = public_price * 2
    chobun_price = int(general_sales_price * 0.7)
    bundam_price = chobun_price - calculated_gampyung
    premium = purchase_price - calculated_gampyung
    total_investment = bundam_price + purchase_price
    final_net_investment = total_investment + calculated_total_interest
    expected_revenue = target_price - final_net_investment

    st.subheader(f"📊 [{asset_name}] 재개발 투자 자금 분석 결과")
    st.markdown(
        f"""
        <div style="font-size: 18px; color: #a0aab5; margin-bottom: 15px; line-height: 1.6;">
            📍 <b>출처:</b> {asset_source} &nbsp;|&nbsp; 📐 <b>대지지분:</b> {land_area:.1f}평 &nbsp;|&nbsp; ⏳ <b>예상 기간:</b> {redev_period}년
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        display_metric("📐 평단가 (매매가 / 대지지분)", f"{fmt(calculated_py_price)} 원")
    with row1_col2:
        display_metric("🔍 감평가 (공주가 x 2)", f"{fmt(calculated_gampyung)} 원")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        display_metric("🏢 조합원 분양가 (일반분양가 x 70%)", f"{fmt(chobun_price)} 원")
    with row2_col2:
        display_metric("💰 분담금 (조합원분양가 - 감평가)", f"{fmt(bundam_price)} 원")

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        display_metric("🏢 프리미엄 (매수금액 - 감평가)", f"{fmt(premium)} 원")
    with row3_col2:
        display_metric("🏢 총 투자금액 (분담금 + 매수금액)", f"{fmt(total_investment)} 원")

    row4_col1, row4_col2 = st.columns(2)
    with row4_col1:
        display_metric("💸 최종 실투자금 (투자금액 + 총이자)", f"{fmt(final_net_investment)} 원")
    with row4_col2:
        display_metric("💰 수익금 (예상목표금액 - 최종 실투자금액)", f"{fmt(expected_revenue)} 원")

    st.markdown("---")
    st.markdown("### 📝 매물 정보")

    if asset_memo.strip():
        st.markdown(
            f"""
            <div style="background-color: #1e222b; padding: 20px; border-radius: 10px; border: 1px solid #4b5563; min-height: 100px; white-space: pre-wrap; font-size: 16px; color: #f3f4f6;">
{asset_memo}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("작성된 매물 정보가 없습니다. 왼쪽 사이드바의 '매물 메모' 칸에 내용을 입력해 보세요.")

    st.markdown("---")


if __name__ == "__main__":
    main()
