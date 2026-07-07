import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="7_안산시 동별 성비 차이 분석", layout="wide")

st.title("⚖️ 안산시 동별 성비(남녀 인구) 차이 분석")
st.markdown("전체 인구수 대비 남녀 인구수의 격차 비율(%)이 가장 큰 곳과 작은 곳을 그래프로 비교 분석합니다.")

# 2. 데이터 불러오기 및 성비 차이 계산 변환
@st.cache_data
def load_and_process_sex_ratio():
    df = pd.read_csv("population.csv")
    # 시각화 가독성을 위해 동 이름만 추출
    df['동이름'] = df['행정구역'].apply(lambda x: x.split()[-1] if isinstance(x, str) else x)
    
    # 롱 포맷 데이터를 계산하기 쉽게 와이드 포맷으로 임시 변환
    pivot_df = df.pivot_table(index=['행정구역', '동이름', '연도'], columns='구분', values='인구수').reset_index()
    
    # 성비 차이 지표 계산
    # 1) 절대적인 수치 차이: |남 - 여|
    pivot_df['성비_인구차이'] = (pivot_df['남'] - pivot_df['여']).abs()
    # 2) 전체 인구수 대비 성비 격차 비율 (%): (|남 - 여| / 총인구) * 100
    pivot_df['성비_격차비율(%)'] = pivot_df.apply(
        lambda r: (abs(r['남'] - r['여']) / r['남+여'] * 100) if r['남+여'] > 0 else 0, axis=1
    )
    
    # 남자가 더 많은지 여자가 더 많은지 상태 텍스트 라벨 추가
    def get_gender_status(row):
        if row['남'] > row['여']:
            return "남자가 더 많음 🔵"
        elif row['여'] > row['남']:
            return "여자가 더 많음 🔴"
        else:
            return "남녀 균등 ⚪"
            
    pivot_df['성별우세'] = pivot_df.apply(get_gender_status, axis=1)
    return pivot_df

try:
    data_df = load_and_process_sex_ratio()

    # 3. [최상단 배치] 조회 조건 설정 (동 선택 창 제거, 연도 선택만 유지)
    st.markdown("### 🔍 조회 조건 설정")
    
    # 연도 선택 드롭다운 (최신 연도인 2025년이 기본값)
    available_years = sorted(data_df['연도'].unique(), reverse=True)
    selected_year = st.selectbox("📅 조회 연도 선택", available_years, index=0)
    
    # 선택된 연도 데이터 필터링
    year_df = data_df[data_df['연도'] == selected_year].copy()

    st.markdown("---") # 구분선

    # 4. 연도 선택 시 나타나는 성비 차이 극과 극 그래프 (상위 5 vs 하위 5)
    st.subheader(f"📊 {selected_year}년 전체 인구 대비 성비 격차 비율(%) 비교 그래프")
    st.markdown("* 비율(%)이 높을수록 남녀 불균형이 심한 동이며, 낮을수록 남녀 성비가 균등한 동입니다.")

    # 격차 비율 기준으로 전체 동 정렬
    sorted_df = year_df.sort_values(by='성비_격차비율(%)', ascending=False)
    
    # 그래프 시각화를 위해 상위 5개(가장 큰 곳)와 하위 5개(가장 작은 곳) 추출 및 결합
    largest_5 = sorted_df.head(5).copy()
    largest_5['그룹'] = '격차 가장 큰 곳 (불균형)'
    
    smallest_5 = sorted_df.tail(5).iloc[::-1].copy() # 가장 균등한 곳부터 역순 정렬
    smallest_5['그룹'] = '격차 가장 작은 곳 (균등)'
    
    plot_comparison_df = pd.concat([largest_5, smallest_5])
    
    # 그래프 x축이나 텍스트 레이블에 남자가 많은지 여자가 많은지 직관적으로 명시하기 위해 새로운 컬럼 생성
    # 예시: "원곡동 (남 많음)", "고잔동 (여 많음)"
    def make_label(row):
        status_short = "(남)" if "남자가" in row['성별우세'] else ("(여)" if "여자가" in row['성별우세'] else "")
        return f"{row['동이름']} {status_short}"
        
    plot_comparison_df['동이름_성별'] = plot_comparison_df.apply(make_label, axis=1)

    # Plotly 그룹형 막대그래프 생성
    fig_comp = px.bar(
        plot_comparison_df,
        x='동이름_성별',
        y='성비_격차비율(%)',
        color='그룹',
        barmode='group',
        text='성비_격차비율(%)', # 텍스트로 비율 직접 매핑
        hover_data={'동이름': True, '남': ':,', '여': ':,', '성별우세': True, '성비_격차비율(%)': ':.2f%'}, # 마우스 올렸을 때 디테일 정보
        labels={'동이름_성별': '행정동 (우세 성별)', '성비_격차비율(%)': '성비 격차 비율 (%)', '그룹': '그룹 분류'},
        color_discrete_map={'격차 가장 큰 곳 (불균형)': '#d62728', '격차 가장 작은 곳 (균등)': '#2ca02c'} # 불균형 빨강, 균등 초록
    )
    
    # 막대 위 텍스트 서식 지정 (소수점 둘째자리 + % 기호)
    fig_comp.update_traces(
        texttemplate='%{text:.2f}%', 
        textposition='outside', 
        cliponaxis=False
    )
    
    fig_comp.update_layout(
        xaxis_title="행정동 (남: 남자 더 많음 / 여: 여자 더 많음)",
        yaxis_title="성비 격차 비율 (%)",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) # 범례 상단 배치
    )
    
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")

    # 5. 하단에 텍스트 리스트 형태로도 깔끔하게 성별 우세 정보 요약 출력
    col_large, col_small = st.columns(2)
    
    with col_large:
        st.markdown("🔺 **성비 격차가 가장 큰 동 TOP 5 상세**")
        for i, (_, row) in enumerate(largest_5.iterrows(), 1):
            st.write(f"{i}위. **{row['동이름']}** — ✨ **{row['성별우세']}** (남: {row['남']:,}명 / 여: {row['여']:,}명)")

    with col_small:
        st.markdown("🟢 **성비 격차가 가장 작은(균등한) 동 TOP 5 상세**")
        for i, (_, row) in enumerate(smallest_5.iterrows(), 1):
            st.write(f"{i}위. **{row['동이름']}** — ✨ **{row['성별우세']}** (남: {row['남']:,}명 / 여: {row['여']:,}명)")

except FileNotFoundError:
    st.error("🚨 `population.csv` 파일을 찾을 수 없습니다. 전처리 파일을 먼저 생성해 주세요.")
