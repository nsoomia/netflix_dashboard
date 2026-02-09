import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 기본 설정
st.set_page_config(page_title="넷플릭스 검색 UX 분석 리포트", layout="wide")

st.title("📊 검색 UX/UI 개선을 위한 데이터 분석 리포트")
st.markdown("---")

# 사이드바 네비게이션
st.sidebar.title("분석 단계 (Phases)")
selection = st.sidebar.radio("이동할 단계를 선택하세요:", 
    ["Overview", "1단계: 선택의 과부하 검증", "2단계: 이탈의 임계점 분석", "3단계: 실패 극복 효과 측정"])

# --- Overview 페이지 ---
if selection == "Overview":
    st.header("📌 프로젝트 개요")
    st.markdown("""
    본 대시보드는 검색 서비스의 사용자 행동 데이터를 기반으로 '선택의 과부하', '이탈 임계점', '추천의 효과'를 검증한 결과를 시각화하였습니다.
    
    ### 🎯 주요 분석 목표
    1. **Choice Overload**: 검색 결과가 많으면 클릭률이 떨어지는가?
    2. **Churn Tipping Point**: 검색 시간이 길어지면 언제 이탈하는가?
    3. **Recovery Analysis**: 검색 실패(0건) 시 추천 시스템은 효과가 있는가?
    """)
    st.info("왼쪽 사이드바에서 각 분석 단계를 선택하여 상세 결과를 확인하세요.")

# --- 1단계: 선택의 과부하 검증 ---
elif selection == "1단계: 선택의 과부하 검증":
    st.header("Phase 1: 선택의 과부하 (Choice Overload) 검증")
    
    # 데이터 생성 (Word 파일 기반)
    data_p1 = {
        'Range': ['0개', '1-10개', '11-20개', '21-30개', '31-40개', '41-50개', '51개 이상'],
        'CTR': [48.7, 47.6, 47.7, 49.7, 48.5, 51.3, 48.7],
        'Duration': [18.40, 19.07, 18.96, 19.07, 19.28, 18.85, 19.03],
        'Friction': [0, 5.56, 1.27, 0.75, 0.55, 0.42, 0.26]
    }
    df_p1 = pd.DataFrame(data_p1)

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 결과 수에 따른 변화", "📉 탐색 마찰 지수", "💡 인사이트 & 액션플랜"])

    with tab1:
        st.subheader("검색 결과 수에 따른 클릭률(CTR) 및 소요 시간")
        
        # 이중 축 차트 생성
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Bar: 클릭률
        fig1.add_trace(
            go.Bar(x=df_p1['Range'], y=df_p1['CTR'], name="클릭률(%)", marker_color='#89CFF0', opacity=0.7),
            secondary_y=False
        )
        
        # Line: 소요 시간
        fig1.add_trace(
            go.Scatter(x=df_p1['Range'], y=df_p1['Duration'], name="평균 검색 시간(초)", mode='lines+markers', line=dict(color='#D32F2F', width=3)),
            secondary_y=True
        )

        fig1.update_layout(title_text="결과 수가 늘어도 시간과 클릭률은 일정함 (가설 기각)", hovermode="x unified")
        fig1.update_yaxes(title_text="클릭률 (%)", secondary_y=False, range=[0, 60])
        fig1.update_yaxes(title_text="평균 검색 시간 (초)", secondary_y=True, range=[18, 20])
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("탐색 마찰 지수 (Search Friction Index)")
        st.markdown("**의미:** 결과 1개를 탐색하는 데 걸리는 시간")
        
        fig2 = px.line(df_p1[df_p1['Range'] != '0개'], x='Range', y='Friction', text='Friction', markers=True,
                       title="결과가 많을수록 1개당 탐색 시간 급감 (Skimming 효과)",
                       labels={'Friction': '초/결과', 'Range': '결과 수 구간'})
        fig2.update_traces(line_color='purple', textposition="top right")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.success("✅ 판단 결과: 거짓 (False)")
        st.markdown("""
        * **현상:** 검색 결과가 50개 이상이어도 사용자는 포기하지 않고 **'빠른 스캔(Skimming)'**으로 효율적 탐색을 수행함.
        * **문제점:** 상위 1~3위(Top 3) 클릭 점유율이 29.4%로 낮음 (일반적으로 과반수여야 함).
        * **액션 플랜:**
            1. **시멘틱 검색 도입:** 단순 키워드 매칭이 아닌 '맥락'과 '의도' 기반 상단 노출.
            2. **개인화 가중치:** 사용자 취향(시청 이력) 반영하여 상단 재배열.
            3. **UI 개선:** Top 1 결과에 '슈퍼 베스트 매치' 배지 및 미리보기 자동 재생 적용.
        """)

# --- 2단계: 이탈의 임계점 분석 ---
elif selection == "2단계: 이탈의 임계점 분석":
    st.header("Phase 2: 이탈의 임계점 (Tipping Point) 분석")

    # 데이터 생성 (Word 파일 기반)
    data_p2 = {
        'Group': ['Immediate Exit (<3s)', 'Quick Scan (3-10s)', 'Standard Browse (10-28s)', 'Deep Consideration (28-48s)', 'Decision Fatigue (≥48s)'],
        'Churn_Rate': [13.74, 14.63, 14.69, 15.72, 15.36],
        'Abandon_Rate': [51.14, 51.31, 50.78, 52.12, 51.62],
        'Churn_in_Abandon': [14.07, 14.36, 15.06, 15.87, 15.33]
    }
    df_p2 = pd.DataFrame(data_p2)

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("사용자 그룹별 이탈률 (Churn Rate)")
        # 컬러 코딩: Deep Consideration 강조
        colors = ['gray'] * 3 + ['red'] + ['salmon']
        
        fig3 = px.bar(df_p2, x='Group', y='Churn_Rate', text='Churn_Rate',
                      title="Deep Consideration (28-48초) 구간에서 이탈률 최대 상승",
                      color='Group', color_discrete_sequence=colors)
        fig3.update_layout(showlegend=False)
        fig3.add_hline(y=14.73, line_dash="dash", annotation_text="전체 평균 (14.73%)")
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("### 🔍 구간 정의")
        st.markdown("""
        - **Deep Consideration (28-48초):** - 🚨 **위험 구간**
          - 고민은 했지만 결정 실패. 
          - 좌절 기반 이탈 발생.
        - **Decision Fatigue (≥48초):** - 피로 기반 포기.
          - 즉시 이탈보다는 장기적 리스크.
        """)

    st.subheader("💡 비즈니스 인사이트 & 액션플랜")
    st.markdown("""
    * **핵심 발견:** 이탈은 '너무 오래 걸려서(Fatigue)'가 아니라, **'고민하다가 실패해서(Deep Consideration)'** 발생한다.
    * **액션 플랜:**
        * **Deep Consideration 조기 개입:** 30초 경과 시 "지금 인기 있는 콘텐츠" 팝업 제안.
        * **Decision Fatigue 관리:** 강요하지 않고 "다음에 이어보기", "찜하기" 유도하여 세션 종료 경험 개선.
    """)

# --- 3단계: 실패 극복 효과 측정 ---
elif selection == "3단계: 실패 극복 효과 측정":
    st.header("Phase 3: 실패를 극복하는 추천의 힘 (Recovery Analysis)")

    # 데이터 생성 (Word 파일 기반)
    st.metric(label="0건 검색 복구율 (Zero-Result Recovery Rate)", value="48.68%")

    col1, col2 = st.columns(2)

    with col1:
        # 데이터 준비
        df_p3 = pd.DataFrame({
            'Status': ['방치 그룹 (No Click)', '복구 그룹 (Click)'],
            'Retention': [82.05, 89.86]
        })
        
        st.subheader("검색 실패(0건) 시 행동에 따른 구독 유지율")
        fig4 = px.bar(df_p3, x='Status', y='Retention', text='Retention', color='Status',
                      color_discrete_map={'방치 그룹 (No Click)': 'gray', '복구 그룹 (Click)': '#E50914'},
                      title="추천 콘텐츠 클릭 시 구독 유지율 +7.81%p 상승")
        fig4.update_yaxes(range=[70, 100])
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        st.markdown("### 📈 데이터 상세")
        st.dataframe(pd.DataFrame({
            '지표': ['전체 결과 0건 검색 수', '추천 클릭 수 (Recovery)', '복구 그룹 유지율', '방치 그룹 유지율', 'Lift (상승분)'],
            '값': ['304건', '148건', '89.86%', '82.05%', '+7.81%p']
        }))

    st.success("💡 결론: 검색 결과가 없어도 추천을 통해 클릭을 유도하면 이탈을 막을 수 있다.")
    st.markdown("""
    * **Action Plan:**
        * **검색 실패 데이터 활용:** 결과 0건 검색어(쿼리)를 분석하여 해당 장르/콘텐츠 라이선스 우선 확보.
        * **페이지 개편:** '검색 결과 없음' 페이지를 '새로운 추천 섹션'으로 전환하여 클릭 유도.
    """)