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

    ## 🏆 메인 가설: "탐색 피로도(Search Fatigue)의 역설"

    > **"풍부한 검색 결과는 유저의 콘텐츠 선택의 어려움을 가중시키고 탐색 피로도를 높이며, 특정 임계점을 넘은 탐색 시간은 구독 해지의 결정적 신호(Red Flag)가 될 것이다."**
    
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
    tab1, tab2, tab3 = st.tabs(["📊 결과 수 구간별 클릭률", "📉 탐색 마찰 지수", "💡 인사이트 & 액션플랜"])

    with tab1:
        st.subheader("결과 수 구간별 클릭률 (CTR by Result Count)")
        st.markdown("**의미:** 결과 수가 31개 이상일 때 클릭률이 실제로 급감하는지 확인")
        st.markdown("**계산:** (해당 구간의 클릭 수 / 해당 구간의 총 검색 수) * 100 ")
        
        # tab2의 px.line과 유사하게 px.bar 생성
        fig1 = px.bar(df_p1, x='Range', y='CTR', text='CTR',
                      title="31개 이상일 때 클릭률 급감 없이 일정 유지 (41-50개 구간 최고)",
                      labels={'CTR': 'Click Rate (CTR) %', 'Range': '결과 수 구간'})
        
        # 막대 위 텍스트 서식 지정 및 색상 설정 (첨부된 원본 그래프와 유사한 톤)
        fig1.update_traces(texttemplate='%{text}%', textposition="outside", marker_color='#6088A5')
        
        # 임계점 (Threshold 30) 빨간 점선 추가 ('21-30개'와 '31-40개' 사이인 x축 3.5 위치)
        fig1.add_vline(x=3.5, line_width=2, line_dash="dash", line_color="red", annotation_text="Threshold (30)")
        
        # y축 범위를 0~100%로 설정하여 여백 확보
        fig1.update_layout(yaxis_range=[0, 100])
        
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("탐색 마찰 지수 (Search Friction Index)")
        st.markdown("**의미:** 결과 1개를 탐색하는 데 걸리는 시간")
        st.markdown("**계산:** 평균 탐색 시간(duration) / 결과 수(results_returned)")
        
        fig2 = px.line(df_p1[df_p1['Range'] != '0개'], x='Range', y='Friction', text='Friction', markers=True,
                       title="결과가 많을수록 1개당 탐색 시간 급감 (Skimming 효과)",
                       labels={'Friction': '초/결과', 'Range': '결과 수 구간'})
        fig2.update_traces(line_color='purple', textposition="top right")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.success("""
        - ✅ 가설: 검색 결과 수가 많을 수록 검색 소요 시간은 늘어나지만, 클릭률은 감소할 것이다.
        - ✅ 판단 결과: 거짓 (False)
        """)
        st.markdown("""
        * **현상:** 검색 결과가 50개 이상이어도 사용자는 포기하지 않고 '빠른 스캔(Skimming)'으로 효율적 탐색을 수행함.
        * **문제점:** 상위 1~3위(Top 3) 클릭 점유율이 29.4%로 낮음 (일반적으로 과반수여야 함).
         * **인사이트:** 상단 콘텐츠 클릭 집중도를 50~60%로 향상할 수 있도록 랭킹 알고리즘 개선 필요.
        * **액션 플랜:**
            1. **시멘틱 검색 도입:** 단순 키워드 매칭이 아닌 '맥락'과 '의도' 기반 상단 노출.
            2. **개인화 가중치:** 사용자 개인 취향(시청 이력) 반영하여 상단 재배열.
            3. **UI 개선:** 검색 정확도가 높은 결과에 '슈퍼 베스트 매치' 배지로 시각적 강조 및 미리보기 자동 재생 적용.
        * **기대 효과:**
            1. **클릭률 향상:** 상위 1~3위(Top 3) 클릭 점유율 29.4%를 50-60%로 향상으로 신뢰도 개선.
            2. **검색 실패 감소:** 정확한 단어를 몰라도 맥락을 통한 검색으로 검색 실패율 감소.
            3. **검색 만족도 상승:** 넷플릭스의 검색 만족도 상승으로 브랜드 충성도 강화.
        """)

# --- 2단계: 이탈의 임계점 분석 ---
elif selection == "2단계: 이탈의 임계점 분석":
    st.header("Phase 2: 이탈의 임계점 (Tipping Point) 분석")

    # 데이터 생성
    data_p2 = {
        'Group': ['Immediate Exit', 'Quick Scan', 'Standard Browse', 'Deep Consideration', 'Decision Fatigue'],
        'Churn_Rate(%)': [13.74, 14.63, 14.69, 15.72, 15.36],
        'Abandon_Rate': [51.14, 51.31, 50.75, 52.15, 51.62],
        'Churn_in_Abandon': [14.07, 14.36, 15.06, 15.87, 15.33]
    }
    df_p2 = pd.DataFrame(data_p2)

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 사용자 그룹별 검색 포기율 분석", "📊 검색 포기자 내 이탈률 분석", "💡 인사이트 & 액션플랜"])

    with tab1:
        st.subheader("사용자 그룹별 검색 포기율")

        # 📌 설명을 그래프 밖으로 분리
        st.markdown("""
        - **전체 검색 포기율**: 검색의 절반 이상이 아무 클릭 없이 종료 → 검색 포기는 매우 흔한 행동
        - 수치 차이 작음 → “포기율이 높다/낮다”로 결론 내리면 안됨 → **포기의 ‘맥락’(행동 특징)을 봐야함**
         1) **Deep Consideration(28-48초)**: 미결정 포기. 콘텐츠에 대한 기대는 유지, 다음 세션 재시도 가능성 높음(회복 가능성 높음)
         2) **Decision Fatigue(48초 이상)**: 피로 기반 포기. 일부 세션은 ‘진성 포기자’로 전이되며 장기 이탈 위험이 급격히 증가     
        """)
        st.markdown("---")

        colors = ['gray', 'gray', 'gray', '#E9967A', '#D32F2F']

        fig3 = px.bar(
            df_p2,
            x='Group',
            y='Abandon_Rate',
            text='Abandon_Rate',
            title="Search Abandonment Rate by User Group",
            color='Group',
            color_discrete_sequence=colors
        )

        fig3.update_traces(
            texttemplate='%{text:.2f}%',
            textposition='outside'
        )

        fig3.update_layout(
            showlegend=False,
            yaxis_range=[50, 53],
            xaxis_title="User Group",
            yaxis_title="Abandonment Rate (%)",
            margin=dict(t=60, b=40)
        )

        fig3.add_hline(
            y=51.19,
            line_dash="dash",
            line_color="blue",
            annotation_text="Overall Average (51.19%)",
            annotation_position="top right"
        )

        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader("검색 포기자 내 이탈률")

        st.markdown("""
        1) **무클릭 종료**: 즉각적인 이탈 신호는 아님
        2) **Deep Consideration(28-48초)**: 좌절감+기대 붕괴. 이탈 위험이 실제로 ‘행동으로 처음 드러나는 지점'
        3) **Decision Fatigue(48초 이상)**: 이미 관여도 높은 유저만 남아 있음. ‘즉시 이탈’이 아니라 ‘장기 전이 위험’ 상태
        """)
        st.markdown("---")

        colors = ['gray', 'gray', 'gray', '#D32F2F', '#E9967A']

        fig_abandon = px.bar(
            df_p2,
            x='Group',
            y='Churn_in_Abandon',
            text='Churn_in_Abandon',
            title="Churn Rate among Search Abandoners",
            color='Group',
            color_discrete_sequence=colors
        )

        fig_abandon.update_traces(
            texttemplate='%{text:.2f}%',
            textposition='outside'
        )

        fig_abandon.update_layout(
            showlegend=False,
            yaxis_range=[13, 17],
            xaxis_title="User Group",
            yaxis_title="Churn Rate (%)",
            margin=dict(t=60, b=40)   # ✅ 겹침 방지
        )

        fig_abandon.add_hline(
            y=14.94,
            line_dash="dash",
            line_color="blue",
            annotation_text="Overall Avg (14.94%)",
            annotation_position="top right"
        )

        st.plotly_chart(fig_abandon, use_container_width=True)

    with tab3:
        st.subheader("💡 비즈니스 인사이트 & 액션플랜")
        st.markdown("""
        * **현상:** 
            1. 검색 포기율은 ‘문제 지표’가 아님(평균 51.19%). 무클릭 종료는 예외가 아니라 기본 상태
            2. 검색 포기 맥락상 Decision Fatigue(51.62%)은 장기 이탈 위험 높은 위험군 
            3. 이탈은 ‘Deep Consideration’에서 이미 시작되며, 특히 검색 포기자 중 이탈률 가장 높음(15.87%). 이 구간부터 집중적인 케어 필요
        * **액션 플랜:**
            1. **Decision Fatigue 관리:** 강요하지 않고 "다음에 이어보기", "찜하기" 유도하여 세션 종료 경험 개선
            2. **Deep Consideration 조기 개입:** 30초 경과 시 "지금 인기 있는 콘텐츠" 팝업 제안
        """)

# --- 3단계: 실패 극복 효과 측정 ---
    # --- 3단계: 실패 극복 효과 측정 ---
elif selection == "3단계: 실패 극복 효과 측정":
    st.subheader("Phase 3: 실패 극복 효과 측정 (Recovery Analysis)")
    st.markdown("---")
    st.subheader("📊 분석 결과")
    res_col1, res_col2 = st.columns([3, 2])

    with res_col1:
        df_recovery = pd.DataFrame({
            '그룹명': ['방치 그룹 (Abandon)', '복구 그룹 (Recovery)'],
            '구독 유지율 (%)': [82.05, 89.86]
        })
        fig_rec = px.bar(
            df_recovery, x='그룹명', y='구독 유지율 (%)', text='구독 유지율 (%)',
            color='그룹명', color_discrete_map={'방치 그룹 (Abandon)': '#564d4d', '복구 그룹 (Recovery)': '#E50914'}
        )
        fig_rec.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_rec.update_layout(yaxis=dict(range=[70, 100]), showlegend=False)
        st.plotly_chart(fig_rec, use_container_width=True)

    with res_col2:
        st.markdown("""
        **[수치 해석]**
        - **복구 그룹(추천 클릭):** 구독 유지율 **89.86%**
        - **방치 그룹(미클릭 이탈):** 구독 유지율 **82.05%**
        
        **[결론]**
        단순 유지율 차이는 7.81%p이나, **상대적 비율로 환산 시 추천 클릭이 유저의 구독 유지 가능성을 약 9.52% 높이는 효과**가 있음을 실증함. 
        이는 검색 실패 상황에서도 추천 시스템이 유저의 부정적 경험을 효과적으로 상쇄하고 있음을 의미함.
        """)

    st.markdown("---")

    # 4, 5, 6. 인사이트 / 액션플랜 / 기대효과 (탭 구조)
    st.subheader("💡 전략적 제언")
    tab_insight, tab_action, tab_effect = st.tabs(["💡 비즈니스 인사이트", "🛠️ 액션 플랜", "📈 기대 효과"])

    with tab_insight:
        st.markdown("""
        - **기회 영역의 발견:** 검색 실패(0건)는 단순한 서비스 오류가 아니라, 유저의 새로운 니즈를 파악하고 **'개인화된 대안'을 제시할 수 있는 강력한 마케팅 접점**임.
        - **이탈 방어의 핵심:** 추천 클릭 한 번이 유저를 방치했을 때보다 10% 가까운 잔존 가치를 창출하므로, 0건 검색 페이지의 최적화가 필수적임.
        """)

    with tab_action:
        st.markdown("""
        **1. '결과 없음' 페이지 UI/UX 전면 개편**
        - '검색 결과가 없습니다' 문구 최소화 및 유저 취향 기반 **'초개인화 대안 콘텐츠'**를 상단에 배치.
        
        **2. 검색 실패 로그 기반 콘텐츠 수급(IP) 전략**
        - 결과가 0건인 검색어(Query)를 전수 분석하여, 유저가 원하지만 현재 없는 콘텐츠의 라이선스 구매 혹은 오리지널 제작의 우선순위 지표로 활용.
        """)

    with tab_effect:
        st.success("""
        - **정량적 효과:** 현재 48.68%인 복구율을 UI 개선을 통해 60% 이상으로 끌어올릴 경우, 추가적인 구독 이탈 방어 매출 창출 가능.
        - **정성적 효과:** 검색 실패라는 부정적 경험을 '새로운 콘텐츠 발견'이라는 긍정적 경험으로 전환하여 브랜드 로열티 강화.
        """)