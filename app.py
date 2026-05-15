import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="나의 구글시트 가계부", layout="wide")

st.title("📊 구글 시트 연동 가계부")

# 구글 시트 주소 입력 (본인의 시트 주소를 " " 사이에 넣으세요)
sheet_url = st.text_input("구글 시트 주소를 입력하세요", "여기에_구글시트_주소를_복사하세요")

if sheet_url and "docs.google.com" in sheet_url:
    try:
        csv_url = sheet_url.split("/edit")[0] + "/export?format=csv"
        df = pd.read_csv(csv_url)
        
        # 1. 컬럼명 공백 제거 (승인금액 앞뒤에 공백이 있을 수 있음)
        df.columns = [col.strip() for col in df.columns]

        # 2. 승인금액 숫자 변환 로직 보강
        if '승인금액' in df.columns:
            # 숫자가 아닌 모든 문자(쉼표, 원, 공백 등)를 제거합니다.
            df['승인금액'] = df['승인금액'].astype(str).str.replace(r'[^\d]', '', regex=True)
            # 빈 칸이나 변환 실패 건을 숫자로 바꿉니다.
            df['승인금액'] = pd.to_numeric(df['승인금액'], errors='coerce').fillna(0)
        
        # 요약 정보 표시
        total_sum = int(df['승인금액'].sum())
        total_count = len(df)
        
        col1, col2 = st.columns(2)
        col1.metric("총 지출액", f"{total_sum:,} 원")
        col2.metric("결제 건수", f"{total_count} 건")

        st.subheader("📝 상세 내역")
        st.dataframe(df, use_container_width=True)

        # 그래프 그리기 (카테고리 열이 L열 또는 '카테고리'일 때)
        category_col = '카테고리' if '카테고리' in df.columns else None
        if category_col:
            st.subheader("🏢 카테고리별 지출")
            cat_sum = df.groupby(category_col)['승인금액'].sum().sort_values(ascending=False).reset_index()
            fig = px.bar(cat_sum, x=category_col, y='승인금액', color=category_col, text_auto=',.0f')
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
else:
    st.info("앱 상단에 구글 시트 주소를 입력하면 가계부가 나타납니다.")
