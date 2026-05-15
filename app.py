import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="나의 카드 가계부", layout="wide")

st.title("💸 개인 가계부 시스템")
st.markdown("카드사에서 다운로드한 엑셀 파일을 업로드하세요.")

# 1. 파일 업로드 기능
uploaded_file = st.file_uploader("현대카드 엑셀 파일을 선택하세요", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # 현대카드 엑셀은 보통 위쪽 2~3줄이 제목이므로 header=2 정도로 읽습니다.
        df = pd.read_excel(uploaded_file, header=2)
        
        # '승인금액' 열이 숫자가 아닌 경우를 대비해 정리
        df['승인금액'] = pd.to_numeric(df['승인금액'], errors='coerce').fillna(0)
        
        # 2. 요약 정보
        total_spent = df['승인금액'].sum()
        count = len(df)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("총 지출액", f"{int(total_spent):,} 원")
        col2.metric("결제 건수", f"{count} 건")
        col3.metric("평균 결제액", f"{int(total_spent/count) if count > 0 else 0:,} 원")

        # 3. 상세 내역 표
        st.subheader("💳 전체 이용 내역")
        # 보기 편하게 주요 컬럼만 먼저 보여줍니다.
        display_cols = ['승인일', '승인시각', '가맹점명', '승인금액', '카드종류', '이용구분']
        st.dataframe(df[display_cols], use_container_width=True)

        # 4. 차트 분석
        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🏢 가장 많이 쓴 가맹점 (TOP 10)")
            shop_sum = df.groupby('가맹점명')['승인금액'].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.bar(shop_sum, x='가맹점명', y='승인금액', color='가맹점명')
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.subheader("📅 일자별 지출 추이")
            date_sum = df.groupby('승인일')['승인금액'].sum().reset_index()
            fig2 = px.line(date_sum, x='승인일', y='승인금액', markers=True)
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다. 양식을 확인해 주세요. 오류내용: {e}")
else:
    st.info("엑셀 파일을 업로드하면 분석이 시작됩니다.")