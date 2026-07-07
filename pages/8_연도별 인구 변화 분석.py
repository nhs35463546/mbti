import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="8_안산시 기간별 인구 변화 분석", layout="wide")

st.title("📉 안산시 기간별 성별 인구 변화량 분석 (1년 단위)")
st.markdown("사용자가 지정한 1년 기간 사이에서 특정 성별의 인구수가 가장 많이 변화한 동을 찾아냅니다.")

# 2. 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("population.csv")
    # 시각화 가독성을 위해 동 이름만 추출
    df['동이름'] = df['행정구역'].apply(lambda x: x.split()[-1] if isinstance(x, str) else x)
    return df

try:
    df = load_data()

    # 3. 사이드바 컨트롤러 (성별 및 1년 단위 기간 선택 드롭다운)
    st.sidebar.header("🔍 분석 조건 설정")
    
    # 성별 선택
    selected_gender = st.sidebar.radio("성별 선택", ["남+여", "남", "여"], index=0)
    
    # 데이터에 존재하는 연도를 바탕으로 "시작연도 - 종료연도" 형태의 1년 단위 기간 리스트 자동 생성
    available_years = sorted(df['연도'].unique())
    period_options = []
    
    for y in available_years:
        if (y + 1) in available_years:
            period_options.append(f"{y} - {y+1}")
            
    # 1년 단위 기간 선택 드롭다운 생성 (기본값은 예시로 들어주신 "2018 - 2019")
    default_idx = period_options.index("2018 - 2019") if "2018 - 2019" in period_options else 0
    selected_period = st.sidebar.selectbox("비교 기간 선택", period_options, index=default_idx)
    
    # 선택된 텍스트에서 시작 연도와 종료 연도 분리 추출
    start_year = int(selected_period.split(" - ")[0])
    end_year = int(selected_period.split(" - ")[1])

    # 4. 두 연도 데이터 필터링 및 변화량 계산
    df_start = df[(df['연도'] == start_year) & (df['구분'] == selected_gender)][['행정구역', '동이름', '인구수']].rename(columns={'인구수': f'인구_{start_year}'})
    df_end = df[(df['연도'] == end_year) & (df['구분'] == selected_gender)][['행정구역', '동이름', '인구수']].rename(columns={'인구수': f'인구_{end_year}'})
    
    # 두 시점의 데이터를 동 기준으로 병합
    merged_df = pd.merge(df_start, df_end, on=['행정구역', '동이름'], how='inner')
    
    # 변화값 계산 (종료연도 인구 - 시작연도 인구)
    merged_df['변화량'] = merged_df[f'인구_{end_year}'] - merged_df[f'인구_{start_year}']
    # 순수한 변화의 크기를 비교하기 위해 절댓값 컬럼 생성
    merged_df['변화량_절댓값'] = merged_df['변화량'].abs()
    
    # 변화 크기(절댓값)가 가장 큰 순서대로 내림차순 정렬
    sorted_df = merged_df.sort_values(by='변화량_절댓값', ascending=False)

    if not sorted_df.empty:
        # 5. 상위 1위 동 요약 메시지 출력
        top_1 = sorted_df.iloc[0]
        direction = "증가 📈" if top_1['변화량'] > 0 else "감소 📉"
        
        st.info(
            f"💡 **{selected_period}** 기간 사이 **[{selected_gender}]** 인구 변화가 가장 컸던 곳은 "
            f"**{top_1['동이름']}**입니다. (총 **{abs(int(top_1['변화량'])):,}명** {direction})"
        )
        
        # 6. 변화량이 가장 큰 상위 7개 동 그래프 시각화
        st.subheader(f"📊 {selected_period} 인구 변화량 TOP 7 동 (성별: {selected_gender})")
        st.markdown(f"* {start_year}년 대비 {end_year}년에 인구가 가장 급격하게 유입(증가)했거나 유출(감소)한 상위 7개 동입니다.")
        
        top7_df = sorted_df.head(7).copy()
        top7_df['상태'] = top7_df['변화량'].apply(lambda x: '인구 증가' if x > 0 else '인구 감소')
        
        # Plotly 막대그래프 생성
        fig = px.bar(
            top7_df,
            x='동이름',
            y='변화량',
            color='상태',
            text_auto=',', 
            labels={'동이름': '행정동', '변화량': '인구 변화량 (명)', '상태': '변화 구분'},
            color_discrete_map={'인구 증가': '#2ca02c', '인구 감소': '#d62728'} 
        )
        
        fig.update_layout(
            xaxis_title="행정동",
            yaxis_title="인구 변화량 (명)",
            height=500
        )
        
        fig.update_traces(
            textposition='outside',
            cliponaxis=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 7. 하단에 상세 비교 데이터 테이블 제공
        with st.expander("📝 전체 동별 상세 데이터 보기 (변화량 큰 순 정렬)"):
            display_df = sorted_df[['행정구역', f'인구_{start_year}', f'인구_{end_year}', '변화량']].reset_index(drop=True)
            display_df.columns = ['행정구역', f'{start_year}년 인구', f'{end_year}년 인구', '인구 변화량']
            
            st.dataframe(
                display_df.style.format({
                    f'{start_year}년 인구': '{:,.0f}',
                    f'{end_year}년 인구': '{:,.0f}',
                    '인구 변화량': '{:+,.0f}'
                }),
                use_container_width=True
            )
            
    else:
        st.warning("선택한 조건에 해당하는 데이터가 존재하지 않습니다.")

except FileNotFoundError:
    st.error("🚨 `population.csv` 파일을 찾을 수 없습니다. 전처리 파일을 먼저 생성해 주세요.")
