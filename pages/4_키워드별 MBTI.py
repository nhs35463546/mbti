import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="키워드별 MBTI 매칭", page_icon="✨", layout="wide")

st.title("✨ 키워드별 MBTI 그룹 분석")
st.markdown("성향 키워드를 선택하면 관련된 **4가지 MBTI 유형**과 전 세계 국가 데이터 기준 **평균 분포 비율**을 확인하실 수 있습니다.")

# 키워드별 MBTI 4개 매칭 사전 정의
KEYWORD_MBTI_MAP = {
    "낭만적 (외교관형)": {
        "types": ["INFJ", "INFP", "ENFJ", "ENFP"],
        "desc": "진정성 있고 이상적인 관계를 추구하며, 타인에 대한 공감 능력이 뛰어난 낭만주의자 그룹입니다."
    },
    "수호적 (관리자형)": {
        "types": ["ISTJ", "ISFJ", "ESTJ", "ESFJ"],
        "desc": "질서와 규칙을 존중하며, 책임감이 강하고 조직이나 가정을 안정적으로 이끄는 수호자 그룹입니다."
    },
    "이성적 (분석가형)": {
        "types": ["INTJ", "INTP", "ENTJ", "ENTP"],
        "desc": "논리와 지적인 호기심을 바탕으로 시스템을 분석하고 전략적인 해결책을 찾아내는 이성주의자 그룹입니다."
    },
    "창조적 (탐험가형)": {
        "types": ["ISTP", "ISFP", "ESTP", "ESFP"],
        "desc": "예술적 감각이나 뛰어난 실천력을 바탕으로, 현재를 즐기며 도전을 두려워하지 않는 창조적 탐험가 그룹입니다."
    }
}

@st.cache_data
def load_data():
    return pd.read_csv("countries_mbti.csv")

try:
    df = load_data()
    
    # 1. 키워드 선택 드롭다운
    selected_keyword = st.selectbox(
        "관심 있는 성향 키워드를 선택하세요:", 
        list(KEYWORD_MBTI_MAP.keys())
    )
    
    # 선택된 그룹 정보 추출
    group_info = KEYWORD_MBTI_MAP[selected_keyword]
    target_mbtis = group_info["types"]
    
    # 2. 그룹 설명 안내 박스
    st.info(f"💡 **{selected_keyword}** 유형은 **{', '.join(target_mbtis)}** 입니다.\n\n_{group_info['desc']}_")
    
    # 3. 데이터 분석: 선택된 4개 MBTI의 전 세계 평균 비율 계산
    # 국가(Country) 열을 제외한 MBTI 열들의 평균을 구합니다.
    global_means = df.drop(columns=['Country']).mean()
    
    # 선택된 4개 유형만 필터링하여 데이터프레임 생성
    group_means_df = pd.DataFrame({
        'MBTI 유형': target_mbtis,
        '전 세계 평균 비율': [global_means[mbti] for mbti in target_mbtis]
    }).sort_values(by='전 세계 평균 비율', ascending=False)
    
    # 4. 시각화 그래프 배치
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Plotly 막대 차트
        fig = px.bar(
            group_means_df,
            x='MBTI 유형',
            y='전 세계 평균 비율',
            title=f"📊 {selected_keyword} 그룹 내 유형별 전 세계 평균 분포",
            labels={'전 세계 평균 비율': '평균 비율'},
            color='MBTI 유형',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        # 퍼센트 포맷팅 적용
        fig.update_layout(yaxis_tickformat='.2%')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # 데이터 상세 표
        st.subheader("📋 상세 비율 데이터")
        st.markdown("데이터에 등록된 전 세계 모든 국가의 평균값입니다.")
        st.dataframe(
            group_means_df.reset_index(drop=True).style.format({'전 세계 평균 비율': '{:.4%}'}),
            use_container_width=True
        )

except FileNotFoundError:
    st.error("❌ `countries_mbti.csv` 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요.")
