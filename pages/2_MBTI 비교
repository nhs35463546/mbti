import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MBTI별 국가 비교", page_icon="⚖️", layout="wide")

st.title("⚖️ MBTI별 국가 비교 분석")

@st.cache_data
def load_data():
    return pd.read_csv("countries_mbti.csv")

try:
    df = load_data()
    mbti_types = sorted(list(df.columns[1:])) # Country 컬럼 제외한 MBTI 목록
    
    # 1. MBTI 유형 선택 및 차트 노출 국가 수 조절 슬라이더
    col1, col2 = st.columns([2, 3])
    with col1:
        selected_mbti = st.selectbox("비교할 MBTI 유형을 선택하세요:", mbti_types)
    with col2:
        top_n = st.slider("차트에 표시할 상위 국가 수를 선택하세요:", min_value=5, max_value=50, value=15)
    
    # 2. 선택한 MBTI 기준 비율 내림차순 정렬
    comparison_df = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=False)
    top_countries = comparison_df.head(top_n)
    
    # 1위 국가 정보 추출
    highest_country = comparison_df.iloc[0]['Country']
    highest_val = comparison_df.iloc[0][selected_mbti]
    
    # 3. 하이라이트 메시지 출력
    st.info(f"💡 **{selected_mbti}** 유형의 비율이 전 세계에서 가장 높은 국가는 **{highest_country}**입니다. (비율: {highest_val:.2%})")
    
    # 4. Plotly 바 차트 시각화
    fig = px.bar(
        top_countries,
        x='Country',
        y=selected_mbti,
        title=f"📊 전 세계 {selected_mbti} 유형 비율 상위 {top_n}개국 비교",
        labels={'Country': '국가', selected_mbti: f'{selected_mbti} 비율'},
        color=selected_mbti,
        color_continuous_scale='plasma'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. 전체 국가 순위 테이블 출력
    st.subheader(f"🏆 전체 국가별 {selected_mbti} 비율 순위")
    st.dataframe(comparison_df.reset_index(drop=True).style.format({selected_mbti: '{:.4%}'}))

except FileNotFoundError:
    st.error("❌ `countries_mbti.csv` 파일을 찾을 수 없습니다.")
