import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="7_안산시 동별 성비 차이 분석", layout="wide")

st.title("⚖️ 안산시 동별 성비(남녀 인구) 차이 분석")
st.markdown("전체 인구수 대비 남녀 인구수의 격차(절댓값 차이 및 비율)가 가장 큰 곳과 작은 곳을 그래프로 비교 분석합니다.")

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
    return pivot_df

try:
    data_df = load_and_process_sex_ratio()

    # 3. [최상단 배치] 조회 조건 설정
    st.markdown("### 🔍 조회 조건 설정")
    col_year_sel, col_dong_sel = st.columns(2) # 화면을 가로로 2개 분할
    
    with col_year_sel:
        # 연도 선택 드롭다운 (최신 연도인 2025년이 기본값)
        available_years = sorted(data_df['연도'].unique(), reverse=True)
        selected_year = st.selectbox("📅 조회 연도 선택", available_years, index=0)
    
    # 선택된 연도 데이터 미리 필터링
    year_df = data_df[data_df['연도'] == selected_year].copy()
    
    with col_dong_sel:
        # 선택된 연도 내에 존재하는 동 리스트 정렬 후 드롭다운 제공
        dong_list = sorted(year_df['동이름'].unique())
        selected_dong = st.selectbox("🏘️ 개별 조회할 동 선택", dong_list)

    st.markdown("---") # 구분선

    # 4. [신규 추가] 연도 선택 시 나타나는 성비 차이 극과 극 그래프 (상위 5 vs 하위 5)
    st.subheader(f"📊 {selected_year}년 전체 인구 대비 성비 격차 비율(%) 비교 그래프")
    st.markdown("* 비율(%)이 높을수록 남녀 불균형이 심한 동이며, 낮을수록 남녀 성비가 균등한 동입니다.")

    # 격차 비율 기준으로 전체 동 정렬
    sorted_df = year_df.sort_values(by='성비_격차비율(%)', ascending=False)
    
    # 그래프 시각화를 위해 상위 5개(가장 큰 곳)와 하위 5개(가장 작은 곳) 추출 및 결합
    largest_5 = sorted_df.head(5).copy()
    largest_5['구분'] = '격차 가장 큰 곳 (불균형)'
    
    smallest_5 = sorted_df.tail(5).iloc[::-1].copy() # 가장 균등한 곳부터 역순 정렬
    smallest_5['구분'] = '격차 가장 작은 곳 (균등)'
    
    plot_comparison_df = pd.concat([largest_5, smallest_5])

    # Plotly 그룹형 막대그래프 생성
    fig_comp = px.bar(
        plot_comparison_df,
        x='동이름',
        y='성비_격차비율(%)',
        color='구분',
        barmode='group',
        text_auto='.2f',  # 소수점 둘째자리까지 막대 위에 표시
        labels={'동이름': '행정동', '성비_격차비율(%)': '성비 격차 비율 (%)', '구분': '그룹 분류'},
        color_discrete_map={'격차 가장 큰 곳 (불균형)': '#d62728', '격차 가장 작은 곳 (균등)': '#2ca02c'} # 불균형은 빨강, 균등은 초록
    )
    
    fig_comp.update_layout(
        xaxis_title="행정동",
        yaxis_title="성비 격차 비율 (%)",
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) # 범례를 상단 가로형으로 배치
    )
    fig_comp.update_traces(textposition='outside', cliponaxis=False)
    
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")

    # 5. 개별 동 성비 격차 상세 조회 결과 출력
    st.subheader(f"🏘️ {selected_year}년 [{selected_dong}] 성비 격차 상세 결과")
    
    # 선택된 동 데이터 추출
    dong_data = year_df[year_df['동이름'] == selected_dong].iloc[0]
    
    # 메트릭(지표) 카드 시각화
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label="총 인구수", value=f"{int(dong_data['남+여']):,} 명")
    c2.metric(label="남자 인구수", value=f"{int(dong_data['남']):,} 명")
    c3.metric(label="여자 인구수", value=f"{int(dong_data['여']):,} 명")
    
    diff_val = int(dong_data['성비_인구차이'])
    ratio_val = dong_data['성비_격차비율(%)']
    status = "남자가 더 많음 🔵" if dong_data['남'] > dong_data['여'] else ("여자가 더 많음 🔴" if dong_data['남'] < dong_data['여'] else "남녀 완벽 균등 ⚪")
    
    c4.metric(label="남녀 격차 비율", value=f"{ratio_val:.2f} %", delta=f"{diff_val:,} 명 차이", delta_color="off")
    
    st.info(f"💡 **{selected_dong}**은(는) **{selected_year}년** 기준 **{status}** 상태이며, 전체 인구수 대비 약 **{ratio_val:.2f}%**의 성별 편차가 존재합니다.")

    # 선택한 동의 연도별 성비 변화 트렌드 라인 차트
    st.caption(f"📈 {selected_dong}의 연도별 남녀 인구 추이 트렌드 (2016년 ~ 2025년)")
    dong_trend = data_df[data_df['동이름'] == selected_dong].sort_values(by='연도')
    
    plot_data = []
    for _, r in dong_trend.iterrows():
        plot_data.append({'연도': r['연도'], '성별': '남성 인구', '인구수': r['남']})
        plot_data.append({'연도': r['연도'], '성별': '여성 인구', '인구수': r['여']})
    plot_df = pd.DataFrame(plot_data)
    
    fig_line = px.line(
        plot_df, 
        x='연도', 
        y='인구수', 
        color='성별', 
        markers=True,
        color_discrete_map={'남성 인구': '#1f77b4', '여성 인구': '#e377c2'}, # 남성 파랑, 여성 핑크
        height=300
    )
    fig_line.update_layout(margin=dict(l=20, r=20, t=10, b=10))
    st.plotly_chart(fig_line, use_container_width=True)

except FileNotFoundError:
    st.error("🚨 `population.csv` 파일을 찾을 수 없습니다. 전처리 파일을 먼저 생성해 주세요.")
