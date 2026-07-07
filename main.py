import streamlit as st
import pandas as pd

# 페이지 레이아웃 및 제목 설정
st.set_page_config(
    page_title="국가별 MBTI 분석 대시보드",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 데이터 분석 대시보드")
st.markdown("""
이 대시보드는 전 세계 여러 국가의 MBTI 유형 분포 데이터를 시각화하고 분석하기 위해 제작되었습니다.
왼쪽 사이드바의 메뉴를 이용해 원하는 분석 페이지로 이동할 수 있습니다.
""")

# 캐싱을 이용해 데이터를 로드 (페이지 이동 시 재로딩 속도 최적화)
@st.cache_data
def load_data():
    return pd.read_csv("countries_mbti.csv")

try:
    df = load_data()
    
    st.header("📊 데이터셋 요약 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="총 수집 국가 수", value=f"{df.shape[0]}개국")
    with col2:
        st.metric(label="분석된 MBTI 유형 수", value=f"{df.shape[1] - 1}개 (기본 16가지)")
        
    st.subheader("👀 데이터 미리보기 (상위 5개국)")
    st.dataframe(df.head())
    
    st.subheader("💡 데이터 구조 설명")
    st.markdown("""
    - **Country**: 데이터가 수집된 국가명입니다.
    - **MBTI 유형 열 (ENFJ ~ ISTP)**: 각 국가 내에서 해당 MBTI 유형이 차지하는 **비율(Proportion)**을 의미합니다.
    - 본 데이터는 세분화되었던 `-A`와 `-T` 성향이 하나의 대표 MBTI 유형으로 통합된 데이터입니다.
    """)

except FileNotFoundError:
    st.error("❌ `countries_mbti.csv` 파일을 찾을 수 없습니다. 파일이 `main.py`와 동일한 폴더에 위치해 있는지 확인해주세요.")
