import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 본인의 구글 시트 주소를 여기에 넣으세요
SHEET_URL = "https://docs.google.com/spreadsheets/d/1tue8zzo52itHri8WX-BzkB_4gjctqXaIY3A-nXg7qPU/edit?usp=sharing"

st.set_page_config(page_title="프리미엄 가계부 분석기", layout="wide")
st.title("📑 전 항목 다이나믹 가계부 분석 시스템")

if "docs.google.com" in SHEET_URL:
    try:
        # 데이터 로드
        csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv"
        df = pd.read_csv(csv_url)
        df.columns = [col.strip() for col in df.columns]

        # 승인금액 숫자 변환
        if '승인금액' in df.columns:
            df['승인금액'] = df['승인금액'].astype(str).str.replace(r'[^\d]', '', regex=True)
            df['승인금액'] = pd.to_numeric(df['승인금액'], errors='coerce').fillna(0)
        
        # --- 사이드바 설정 ---
        st.sidebar.header("⚙️ 분석 설정")
        
        group_col = st.sidebar.selectbox(
            "무엇을 기준으로 분석할까요?",
            options=df.columns.tolist(),
            index=df.columns.tolist().index('카테고리') if '카테고리' in df.columns else 0
        )

        unique_vals = sorted(df[group_col].unique().tolist())
        selected_vals = st.sidebar.multiselect(
            f"[{group_col}] 내에서 선택하세요",
            options=unique_vals,
            default=unique_vals
        )

        filtered_df = df[df[group_col].isin(selected_vals)]

        # --- 대시보드 요약 ---
        total_sum = int(filtered_df['승인금액'].sum())
        total_count = len(filtered_df)
        
        c1, c2, c3 = st.columns(3)
        c1.metric(f"선택된 {group_col} 합계", f"{total_sum:,} 원")
        c2.metric("결제 건수", f"{total_count} 건")
        c3.metric("평균 결제액", f"{int(total_sum/total_count) if total_count > 0 else 0:,} 원")

        st.divider()

        # --- 차트 영역 (정렬된 데이터 사용) ---
        stats = filtered_df.groupby(group_col)['승인금액'].sum().reset_index()
        # 여기서 '총합계' 기준 내림차순 정렬
        stats = stats.sort_values(by='승인금액', ascending=False)

        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.subheader(f"📊 {group_col}별 지출 비중")
            fig_pie = px.pie(stats, values='승인금액', names=group_col, hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            st.subheader(f"📈 {group_col}별 지출 순위")
            fig_bar = px.bar(stats, x=group_col, y='승인금액', text_auto=',.0f',
                             color=group_col, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # --- 하단 통계 표 (요청하신 정렬 기능 적용) ---
        st.subheader("📋 데이터 요약 및 상세 내역")
        tab1, tab2 = st.tabs(["항목별 요약표", "개별 영수증 내역"])
        
        with tab1:
            # 1. 먼저 그룹화하여 합계 계산
            summary = filtered_df.groupby(group_col)['승인금액'].agg(['sum', 'count', 'mean']).reset_index()
            summary.columns = [group_col, '총합계', '건수', '평균']
            
            # 2. ★중요★ 숫자 상태일 때 '총합계' 기준 내림차순으로 먼저 정렬!
            summary = summary.sort_values(by='총합계', ascending=False)
            
            # 3. 정렬이 끝난 후 보기 좋게 '원'과 콤마 붙이기
            summary_display = summary.copy()
            summary_display['총합계'] = summary_display['총합계'].map('{:,.0f}원'.format)
            summary_display['평균'] = summary_display['평균'].map('{:,.0f}원'.format)
            
            st.dataframe(summary_display, use_container_width=True)
            
        with tab2:
            st.dataframe(filtered_df, use_container_width=True)

    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
else:
    st.info("시트 주소를 입력해주세요.")
