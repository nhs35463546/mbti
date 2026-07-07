import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="7_안산시 동별 성비 차이 분석", layout="wide")

st.title("⚖️ 안산시 동별 성비(남녀 인구) 차이 분석")
st.markdown("전체 인구수 대비 남녀 인구수의 격차(절댓값 차이 및 비율)가 가장 큰 곳과 작은 곳을 분석합니다.")

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

    # 3. [최상단 배치] 조회 조건 설정 (연도 선택 후 동 선택)
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
        selected_dong = st.selectbox("🏘️ 조회할 동 선택", dong_list)

    st.markdown("---") # 구분선

    # 4. 개별 동 성비 격차 상세 조회 결과 출력
    st.subheader(f"📈 {selected_year}년 {selected_dong} 성비 격차 상세 결과")
    
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
    st.caption(f"📊 {selected_dong}의 연도별 남녀 인구 추이 트렌드 (2016년 ~ 2025년)")
    dong_trend = data_df[data_df['동이름'] == selected_dong].sort_values(by='연도')
    
    plot_data = []
    for _, r in dong_trend.iterrows():
        plot_data.append({'연도': r['연도'], '성별': '남성 인구', '인구수': r['남']})
        plot_data.append({'연도': r['연도'], '성별': '여성 인구', '인구수': r['여']})
    plot_df = pd.DataFrame(plot_data)
    
    fig = px.line(
        plot_df, 
        x='연도', 
        y='인구수', 
        color='성별', 
        markers=True,
        color_discrete_map={'남성 인구': '#1f77b4', '여성 인구': '#e377c2'}, # 남성 파랑, 여성 핑크
        height=300
    )
    fig.update_layout(margin=dict(l=20, r=20, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 5. 하단 배치: 해당 연도의 성비 격차 비율(%) 기준 극과 극 요약 (가장 큰 동 3 vs 가장 작은 동 3)
    st.subheader(f"📊 {selected_year}년 안산시 성비 격차 극과 극 요약 (전체 인구수 대비 비율 기준)")
    
    # 격차 비율 기준으로 전체 동 정렬
    sorted_df = year_df.sort_values(by='성비_격차비율(%)', ascending=False)
    
    largest_3 = sorted_df.head(3)
    smallest_3 = sorted_df.tail(3).iloc[::-1]  # 가장 균등한 곳부터 보이게 반전

    col_large, col_small = st.columns(2)
    
    with col_large:
        st.markdown("🔴 **성비 차이가 가장 큰 동 TOP 3** (남녀 불균형 상위)")
        for i, (_, row) in enumerate(largest_3.iterrows(), 1):
            gender_dominant = "남초" if row['남'] > row['여'] else "여초"
            st.caption(f"{i}위. **{row['동이름']}** : 격차 {row['성비_격차비율(%)']:.2f}% (남 {row['남']:,}명 / 여 {row['여']:,}명 — _{gender_dominant}_)")

    with col_small:
        st.markdown("🟢 **성비 차이가 가장 작은 동 TOP 3** (남녀 비율 가장 균등)")
        for i, (_, row) in enumerate(smallest_3.iterrows(), 1):
            st.caption(f"{i}위. **{row['동이름']}** : 격차 {row['성비_격차비율(%)']:.2f}% (남 {row['남']:,}명 / 여 {row['여']:,}명)")

except FileNotFoundError:
    st.error("🚨 `population.csv` 파일을 찾을 수 없습니다. 전처리 파일을 먼저 생성해 주세요.")
