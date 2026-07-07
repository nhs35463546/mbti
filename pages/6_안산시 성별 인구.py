import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 (탭 이름을 '6_안산시 성별 인구 상위 TOP 7'로 지정)
st.set_page_config(page_title="6_안산시 성별 인구 상위 TOP 7", layout="wide")

st.title("📊 안산시 동별 성별 인구수 TOP 7 분석")
st.markdown("2016년부터 2025년까지의 데이터를 바탕으로, 성별에 따른 인구 상위 7개 동을 보여줍니다.")

# 2. 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("population.csv")
    # 시각화 가독성을 위해 "경기도 안산시 상록구 사동" -> "사동" 형태로 동 이름만 추출
    df['동이름'] = df['행정구역'].apply(lambda x: x.split()[-1] if isinstance(x, str) else x)
    return df

try:
    df = load_data()

    # 3. 사이드바 컨트롤러 (조건 선택)
    st.sidebar.header("🔍 필터 조건 설정")
    
    # 연도 선택 (가장 최신 연도인 2025년을 기본값으로 설정)
    available_years = sorted(df['연도'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("연도 선택", available_years, index=0)
    
    # 성별 선택
    selected_gender = st.sidebar.radio("성별 선택", ["남", "여"])

    # 4. 데이터 필터링 및 정렬
    filtered_df = df[(df['연도'] == selected_year) & (df['구분'] == selected_gender)]
    top7_df = filtered_df.sort_values(by='인구수', ascending=False).head(7)

    # 5. 메인 화면 시각화
    st.subheader(f"📅 {selected_year}년 기준 [{selected_gender}자] 인구수 상위 7개 동")
    
    if not top7_df.empty:
        # Plotly 막대그래프 생성
        # 남성은 Blues(파란색), 여성은 RdPu(붉은색/분홍색 계열 라즈베리-핑크) 스케일 적용
        fig = px.bar(
            top7_df,
            x='동이름',
            y='인구수',
            text_auto=',',  # 숫자 3자리마다 쉼표 표시
            labels={'동이름': '행정동', '인구수': '인구수 (명)'},
            color='인구수',  # 인구수에 따라 색상 그라데이션 적용
            color_continuous_scale='Blues' if selected_gender == "남" else 'RdPu'
        )
        
        # 그래프 레이아웃 깔끔하게 조정
        fig.update_layout(
            xaxis_title="행정동",
            yaxis_title="인구수 (명)",
            coloraxis_showscale=False,  # 우측 색상 바 숨기기
            height=500
        )
        
        fig.update_traces(
            textposition='outside',  # 막대 바깥쪽에 숫자 표시
            cliponaxis=False
        )
        
        # Streamlit 화면에 그래프 렌더링
        st.plotly_chart(fig, use_container_width=True)
        
        # 6. 하단에 상세 데이터 테이블도 함께 보여주기
        with st.expander("📝 상위 7개 동 상세 데이터 보기"):
            table_df = top7_df[['행정구역', '연도', '구분', '인구수']].reset_index(drop=True)
            table_df.index = table_df.index + 1  # 순위를 1부터 표시
            st.dataframe(table_df, use_container_width=True)
            
    else:
        st.warning("선택한 조건에 해당하는 데이터가 존재하지 않습니다.")

except FileNotFoundError:
    st.error("🚨 `population.csv` 파일을 찾을 수 없습니다. 먼저 `preprocess.py`를 실행하여 전처리를 완료해 주세요.")
