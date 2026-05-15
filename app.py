import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 여기에 본인의 구글 시트 주소를 붙여넣으세요! (따옴표 " " 사이에 넣기)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1tue8zzo52itHri8WX-BzkB_4gjctqXaIY3A-nXg7qPU/edit?usp=sharing"

st.set_page_config(page_title="나의 전용 가계부", layout="wide")
st.title("💸 나의 스마트 가계부 (자동 연동)")

if "docs.google.com" in SHEET_URL:
    try:
        # 구글 시트를 읽을 수 있는 형식으로 변환
        csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv"
        df = pd.read_csv(csv_url)
        
        # 열 이름의 공백 제거
        df.columns = [col.strip() for col in df.columns]

        # 2. 승인금액 0원 문제 해결 (쉼표 제거 및 숫자 변환)
        if '승인금액' in df.columns:
            # 숫자가 아닌 문자(쉼표 등) 제거 후 숫자로 변환
            df['승인금액'] = df['승인금액'].astype(str).str.replace(r'[^\d]', '', regex=True)
            df['승인금액'] = pd.to_numeric(df['승인금액'], errors='coerce').fillna(0)
        
        # 상단 요약 수치
        total_sum = int(df['승인금액'].sum())
        col1, col2 = st.columns(2)
        col1.metric("이번 달 총 지출", f"{total_sum:,} 원")
        col2.metric("총 결제 건수", f"{len(df)} 건")

        st.divider()

        # 데이터 표 보여주기
        st.subheader("📝 상세 지출 내역")
        st.dataframe(df, use_container_width=True)

        # 3. 카테고리별 차트 (L열의 이름이 '카테고리'라고 되어 있어야 합니다)
        if '카테고리' in df.columns:
            st.subheader("🏢 카테고리별 지출 비중")
            cat_sum = df.groupby('카테고리')['승인금액'].sum().sort_values(ascending=False).reset_index()
            fig = px.pie(cat_sum, values='승인금액', names='카테고리', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"데이터를 불러오지 못했습니다. 주소나 공유 설정을 확인하세요! 에러: {e}")
else:
    st.warning("코드 상단의 SHEET_URL 변수에 올바른 주소를 넣어주세요.")
