import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 본인의 구글 시트 주소를 여기에 넣으세요
SHEET_URL = "https://docs.google.com/spreadsheets/d/1tue8zzo52itHri8WX-BzkB_4gjctqXaIY3A-nXg7qPU/edit?usp=sharing"

st.set_page_config(page_title="가계부 통계 시스템", layout="wide")
st.title("📊 항목별 지출 통계 리포트")

if "docs.google.com" in SHEET_URL:
    try:
        csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv"
        df = pd.read_csv(csv_url)
        df.columns = [col.strip() for col in df.columns]

        # 금액 숫자 변환 (0원 문제 해결 코드 포함)
        if '승인금액' in df.columns:
            df['승인금액'] = df['승인금액'].astype(str).str.replace(r'[^\d]', '', regex=True)
            df['승인금액'] = pd.to_numeric(df['승인금액'], errors='coerce').fillna(0)
        
        # --- 통계 계산 시작 ---
        if '카테고리' in df.columns:
            # 2. 항목별 합계 및 건수 계산
            stats_df = df.groupby('카테고리')['승인금액'].agg(['sum', 'count']).reset_index()
            stats_df.columns = ['항목', '총 지출액', '결제 건수']
            stats_df = stats_df.sort_values(by='총 지출액', ascending=False)

            # --- 화면 구성 ---
            # 상단 요약
            total_amount = int(stats_df['총 지출액'].sum())
            st.metric("이번 달 총 지출", f"{total_amount:,} 원")
            
            st.divider()

            # 좌측: 통계 표 / 우측: 그래프
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("📋 항목별 요약")
                # 천단위 콤마 표시를 위해 포맷팅
                display_stats = stats_df.copy()
                display_stats['총 지출액'] = display_stats['총 지출액'].apply(lambda x: f"{int(x):,}원")
                display_stats['결제 건수'] = display_stats['결제 건수'].apply(lambda x: f"{x}건")
                st.table(display_stats) # 깔끔한 표 형태로 출력

            with col2:
                st.subheader("🍕 지출 비중 (차트)")
                fig_pie = px.pie(stats_df, values='총 지출액', names='항목', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_pie, use_container_width=True)

            st.divider()

            # 하단: 막대 그래프
            st.subheader("📈 항목별 지출 금액 비교")
            fig_bar = px.bar(stats_df, x='항목', y='총 지출액', text_auto=',.0f',
                             color='항목', color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_bar, use_container_width=True)

        else:
            st.warning("구글 시트에 '카테고리' 열이 없습니다. L열의 제목을 '카테고리'로 설정했는지 확인해주세요.")

        # 상세 내역 접기/펴기
        with st.expander("🔎 전체 상세 내역 보기"):
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"오류 발생: {e}")
else:
    st.info("시트 주소를 입력해주세요.")
