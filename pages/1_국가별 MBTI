import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="국가별 MBTI 현황", page_icon="📍", layout="wide")

st.title("📍 국가별 MBTI 현황 분석")

@st.cache_data
def load_data():
    return pd.read_csv("countries_mbti.csv")

try:
    df = load_data()
    countries = sorted(df['Country'].unique())
    
    # 1. 국가 선택 박스
    selected_country = st.selectbox("분석할 국가를 선택하세요:", countries)
    
    # 2. 선택한 국가의 데이터 추출 및 비율 정렬
    country_data = df[df['Country'] == selected_country].drop(columns=['Country']).iloc[0]
    country_df = pd.DataFrame({
        'MBTI': country_data.index,
        '비율': country_data.values
    }).sort_values(by='비율', ascending=False)
    
    # 주요 특징 (가장 높은 MBTI) 추출
    top_mbti = country_df.iloc[0]['MBTI']
    top_value = country_df.iloc[0]['비율']
    
    # 3. 하이라이트 메시지 출력
    st.success(f"✨ **{selected_country}**에서 가장 높은 비율을 차지하는 MBTI 유형은 **{top_mbti}**입니다. (비율: {top_value:.2%})")
    
    # 4. Plotly를 활용한 인터랙티브 바 차트 시각화
    fig = px.bar(
        country_df, 
        x='MBTI', 
        y='비율', 
        title=f"📊 {selected_country}의 MBTI 유형별 분포 순위",
        labels={'비율': '비율', 'MBTI': 'MBTI 유형'},
        color='비율',
        color_continuous_scale='viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. 상세 데이터 테이블 (퍼센트 포맷팅 적용)
    st.subheader("📋 상세 데이터 순위")
    st.dataframe(country_df.reset_index(drop=True).style.format({'비율': '{:.4%}'}))

except FileNotFoundError:
    st.error("❌ `countries_mbti.csv` 파일을 찾을 수 없습니다.")
