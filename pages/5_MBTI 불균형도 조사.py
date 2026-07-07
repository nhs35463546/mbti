import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="세계 MBTI 불균형도 조사", page_icon="🧮", layout="wide")

st.title("🧮 전 세계 MBTI 불균형도(성향 쏠림) 조사")
st.markdown("""
이 페이지는 통계적 방법(**표준편차**)을 사용하여 어떤 나라가 가장 특정 성향에 치우쳐 있는지, 
혹은 어떤 나라가 16가지 MBTI 유형이 가장 골고루 섞여 있는지 분석합니다.
- **불균형도(표준편차)가 높음**: 특정 MBTI 유형이 압도적으로 많음 (뚜렷한 국가적 개성 또는 집단성)
- **불균형도(표준편차)가 낮음**: 16개 MBTI 유형이 모두 골고루 존재함 (문화적 다양성)
""")

@st.cache_data
def load_data():
    return pd.read_csv("countries_mbti.csv")

try:
    df = load_data()
    
    # 1. 수치 데이터만 추출하여 국가별 표준편차 계산
    mbti_cols = df.columns[1:]
    df_numeric = df[mbti_cols]
    
    # 국가별로 16개 MBTI 비율의 표준편차 계산 후 새로운 컬럼으로 추가
    df['불균형도 (표준편차)'] = df_numeric.std(axis=1)
    
    # 분석에 필요한 컬럼만 정렬
    analysis_df = df[['Country', '불균형도 (표준편차)']].sort_values(by='불균형도 (표준편차)', ascending=False).reset_index(drop=True)
    
    # 2. 상위권(쏠림 국가) 및 하위권(밸런스 국가) 탑 5 추출
    top_unbalanced = analysis_df.head(5)
    top_balanced = analysis_df.tail(5).iloc[::-1] # 역순으로 정렬하여 가장 균형잡힌 곳이 위로 오게
    
    # 3. 하이라이트 대시보드 카드 배치
    col1, col2 = st.columns(2)
    
    with col1:
        st.error(f"🚨 **세계에서 가장 성향 쏠림이 심한 국가 (1위)**")
        most_unbalanced_country = top_unbalanced.iloc[0]['Country']
        st.metric(label=most_unbalanced_country, value="개성/집단주의형", delta=f"지수: {top_unbalanced.iloc[0]['불균형도 (표준편차)']:.4f}")
        st.markdown(f"**{most_unbalanced_country}**은(는) 특정 MBTI를 가진 사람들의 비율이 매우 높아, 국가적 색깔이 아주 뚜렷하거나 집단적 성향이 강할 수 있습니다.")
        
    with col2:
        st.success(f"⚖️ **세계에서 가장 황금 밸런스를 이룬 국가 (1위)**")
        most_balanced_country = top_balanced.iloc[0]['Country']
        st.metric(label=most_balanced_country, value="문화적 다양성형", delta=f"지수: {top_balanced.iloc[0]['불균형도 (표준편차)']:.4f}", delta_color="inverse")
        st.markdown(f"**{most_balanced_country}**은(는) 16가지 성향이 전 세계에서 가장 골고루 분포되어 있어, 다양한 가치관과 개성이 존중받는 환경일 확률이 높습니다.")

    st.markdown("---")
    
    # 4. 시각화 탭 구성
    tab1, tab2 = st.tabs(["📊 불균형도 상/하위국 비교", "🔍 국가별 MBTI 실제 분포 확인"])
    
    with tab1:
        st.subheader("🏆 성향 불균형도 극과 극 비교 (상위 5 vs 하위 5)")
        # 상위 5개와 하위 5개를 합쳐서 그래프 생성
        chart_df = pd.concat([top_unbalanced, top_balanced])
        chart_df['구분'] = ['성향 쏠림 국가(TOP 5)']*5 + ['황금 밸런스 국가(TOP 5)']*5
        
        fig = px.bar(
            chart_df,
            x='Country',
            y='불균형도 (표준편차)',
            color='구분',
            title='전 세계 국가별 MBTI 불균형도 지수 (표준편차 비교)',
            labels={'Country': '국가', '불균형도 (표준편차)': '불균형도 지수 (표준편차)'},
            color_discrete_map={'성향 쏠림 국가(TOP 5)': '#FF4B4B', '황금 밸런스 국가(TOP 5)': '#00A86B'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("🔍 원하는 국가를 선택해 16개 MBTI의 진짜 분포 형태를 비교해보세요!")
        
        # 유저가 직접 두 나라를 골라 분포 그래프를 대조할 수 있는 인터랙티브 기능
        countries = sorted(df['Country'].unique())
        c1, c2 = st.columns(2)
        with c1:
            country_a = st.selectbox("첫 번째 국가 선택:", countries, index=countries.index(most_unbalanced_country))
        with c2:
            country_b = st.selectbox("두 번째 국가 선택:", countries, index=countries.index(most_balanced_country))
            
        # 두 국가의 MBTI 데이터 추출
        data_a = df[df['Country'] == country_a][mbti_cols].melt(var_name='MBTI', value_name='비율')
        data_b = df[df['Country'] == country_b][mbti_cols].melt(var_name='MBTI', value_name='비율')
        data_a['국가'] = country_a
        data_b['국가'] = country_b
        compare_melted = pd.concat([data_a, data_b])
        
        # 라인(선) 그래프로 분포의 '굴곡' 시각화 (쏠린 국가는 요동치고, 밸런스 국가는 완만함)
        fig_compare = px.line(
            compare_melted,
            x='MBTI',
            y='비율',
            color='국가',
            markers=True,
            title=f"📈 {country_a} vs {country_b}의 16개 MBTI 분포도 굴곡 비교",
            labels={'비율': '해당 MBTI가 차지하는 비율'}
        )
        fig_compare.update_layout(yaxis_tickformat='.1%')
        st.plotly_chart(fig_compare, use_container_width=True)
        st.caption("💡 쏠림 지수가 높은 국가는 그래프 선의 위아래 굴곡(높낮이)이 심하고, 밸런스 지수가 높은 국가는 선이 비교적 평평하고 완만하게 나타납니다.")

except FileNotFoundError:
    st.error("❌ `countries_mbti.csv` 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요.")
