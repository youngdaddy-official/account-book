import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="나의 구글시트 가계부", layout="wide")

st.title("📊 구글 시트 연동 가계부")
st.info("구글 시트의 내용을 실시간으로 불러옵니다.")

# 1. 구글 시트 주소 입력 (한 번만 입력하면 됩니다)
# 시트의 '공유' 설정을 '링크가 있는 모든 사용자에게 공개'로 바꿔주셔야 합니다.
# " " 사이에 본인의 구글 시트 주소를 통째로 넣으세요
sheet_url = "https://docs.google.com/spreadsheets/d/1tue8zzo52itHri8WX-BzkB_4gjctqXaIY3A-nXg7qPU/edit?usp=sharing"

if sheet_url and "docs.google.com" in sheet_url:
    try:
        # 구글 시트 주소를 데이터를 읽을 수 있는 주소로 변환
        csv_url = sheet_url.split("/edit")[0] + "/export?format=csv"
        df = pd.read_csv(csv_url)
        
        # 승인금액 숫자 변환
        if '승인금액' in df.columns:
            df['승인금액'] = pd.to_numeric(df['승인금액'], errors='coerce').fillna(0)
        
        # 요약 정보
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 지출액", f"{int(df['승인금액'].sum()):,} 원")
        with col2:
            st.metric("결제 건수", f"{len(df)} 건")

        # 데이터 표
        st.subheader("📝 상세 내역")
        st.dataframe(df, use_container_width=True)

        # 그래프
        if '가맹점명' in df.columns:
            st.subheader("🏢 가맹점별 지출 TOP 10")
            shop_sum = df.groupby('가맹점명')['승인금액'].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.bar(shop_sum, x='가맹점명', y='승인금액', color='가맹점명')
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"시트를 불러올 수 없습니다. 공유 설정을 확인해주세요! 에러: {e}")
else:
    st.warning("상단에 올바른 구글 시트 주소를 입력해주세요.")
