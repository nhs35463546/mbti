import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="국가별 4대 지표 분석", page_icon="🧠", layout="wide")

st.title("🧠 국가별 MBTI 4대 성향 지표 분석")
st.markdown("선택한 국가의 MBTI 데이터를 바탕으로 **외향/내향(E/I), 직관/감각(N/S), 사고/감정(F/T), 판단/인식(P/J)** 비율을 원형 그래프로 시각화합니다.")

@st.cache_data
def load_data():
    return pd.read_csv("countries_mbti.csv")

try:
    df = load_data()
    countries = sorted(df['Country'].unique())
    
    # 1. 국가 선택 드롭다운
    selected_country = st.selectbox("분석할 국가를 선택하세요:", countries)
    
    # 2. 선택한 국가의 데이터 가져오기
    country_row = df[df['Country'] == selected_country].iloc[0]
    
    # 16개 MBTI 유형 목록
    mbti_types = ['ENFJ', 'ENFP', 'ENTJ', 'ENTP', 'ESFJ', 'ESFP', 'ESTJ', 'ESTP',
                  'INFJ', 'INFP', 'INTJ', 'INTP', 'ISFJ', 'ISFP', 'ISTJ', 'ISTP']
    
    # 각 지표별 수치 초기화
    scores = {'E': 0, 'I': 0, 'N': 0, 'S': 0, 'F': 0, 'T': 0, 'P': 0, 'J': 0}
    
    # 16개 MBTI의 비율을 4대 지표로 누적 합산
    for mbti in mbti_types:
        if mbti in country_row:
            val = country_row[mbti]
            # E/I 구분
            scores[mbti[0]] += val
            # N/S 구분
            scores[mbti[1]] += val
            # F/T 구분
            scores[mbti[2]] += val
            # P/J 구분
            scores[mbti[3]] += val

    # 3. 레이아웃 설정을 통해 2x2 배열로 원형 그래프 배치
    st.subheader(f"📊 {selected_country}의 성향 지표별 비율")
    
    # 두 개의 행(Row) 생성, 각 행마다 두 개의 열(Column) 배치
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    # 공통 그래픽 스타일 함수 정의
    def create_pie_chart(labels, values, title, colors):
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=0,  # 도넛 모양 스타일 (원형을 원하시면 0으로 설정)
            marker=dict(colors=colors),
            textinfo='label+percent',
            hoverinfo='label+percent'
        )])
        fig.update_layout(
            title_text=title,
            title_x=0.3, # 제목 중앙 정렬에 가깝게 조정
            margin=dict(t=40, b=20, l=20, r=20),
            height=300,
            showlegend=False # 그래프 내부에 라벨이 뜨므로 범례는 숨김
        )
        return fig

    # 지표 1: E (외향) vs I (내향)
    with row1_col1:
        fig_ei = create_pie_chart(
            labels=['E (외향)', 'I (내향)'],
            values=[scores['E'], scores['I']],
            title="<b>E (Energy) vs I (Identity)</b>",
            colors=['#FF9999', '#66B3FF']
        )
        st.plotly_chart(fig_ei, use_container_width=True)

    # 지표 2: N (직관) vs S (감각)
    with row1_col2:
        fig_ns = create_pie_chart(
            labels=['N (직관)', 'S (감각)'],
            values=[scores['N'], scores['S']],
            title="<b>N (Information) vs S (Sensation)</b>",
            colors=['#99FF99', '#FFCC99']
        )
        st.plotly_chart(fig_ns, use_container_width=True)

    # 지표 3: F (감정) vs T (사고)
    with row2_col1:
        fig_ft = create_pie_chart(
            labels=['F (감정)', 'T (사고)'],
            values=[scores['F'], scores['T']],
            title="<b>F (Decision) vs T (Thinking)</b>",
            colors=['#FFD700', '#D3D3D3']
        )
        st.plotly_chart(fig_ft, use_container_width=True)

    # 지표 4: P (인식) vs J (판단)
    with row2_col2:
        fig_pj = create_pie_chart(
            labels=['P (인식)', 'J (판단)'],
            values=[scores['P'], scores['J']],
            title="<b>P (Lifestyle) vs J (Judgment)</b>",
            colors=['#C2C2F0', '#FFB3E6']
        )
        st.plotly_chart(fig_pj, use_container_width=True)

except FileNotFoundError:
    st.error("❌ `countries_mbti.csv` 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요.")
