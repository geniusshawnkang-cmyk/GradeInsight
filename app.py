
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Grade Insight",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Grade Insight")
st.subheader("Personal Academic Performance Analyzer")
st.write("나의 학업 성취도를 분석하고 학습 방향을 찾아보세요.")

st.divider()

# 성적 데이터 저장 공간

# 성적 데이터 저장 공간
FILE_PATH = "grades.csv"

if "grades" not in st.session_state:
    try:
        st.session_state.grades = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        st.session_state.grades = pd.DataFrame(
            columns=["과목", "평가 유형", "평가명", "평가 날짜", "점수", "만점", "환산 점수"]
        )


st.sidebar.title("메뉴")
menu = st.sidebar.radio(
    "원하는 기능을 선택하세요.",
    ["대시보드", "성적 입력", "성적 분석", "학습 진단"]
)

# 성적 입력
if menu == "성적 입력":
    st.header("📝 성적 입력")
    st.write("시험과 수행평가 결과를 기록해 보세요.")

    with st.form("grade_form"):
        subject = st.selectbox(
            "과목",
            ["국어", "수학", "영어", "통합사회", "통합과학", "한국사", "기타"]
        )

        evaluation = st.selectbox(
            "평가 유형",
            ["지필평가", "수행평가"]
        )

        name = st.text_input("평가명", placeholder="예: 1학기 중간고사")

        date = st.date_input("평가 날짜")

        col1, col2 = st.columns(2)

        score = col1.number_input(
            "획득 점수",
            min_value=0.0,
            value=80.0
        )

        maximum = col2.number_input(
            "만점",
            min_value=1.0,
            value=100.0
        )

        submitted = st.form_submit_button("성적 등록")

        if submitted:
            if not name.strip():
                st.warning("평가명을 입력해 주세요.")
            elif score > maximum:
                st.warning("획득 점수는 만점을 초과할 수 없습니다.")
            else:
                new_grade = pd.DataFrame([{
                    "과목": subject,
                    "평가 유형": evaluation,
                    "평가명": name,
                    "평가 날짜": str(date),
                    "점수": score,
                    "만점": maximum,
                    "환산 점수": round(score / maximum * 100, 2)
                }])               
                st.session_state.grades = pd.concat(
                    [st.session_state.grades, new_grade],
                    ignore_index=True
                )

                st.session_state.grades.to_csv(FILE_PATH, index=False)

                st.success("성적이 등록되었습니다!")

    st.divider()
    st.subheader("등록된 성적")

    if not st.session_state.grades.empty:
        st.dataframe(
            st.session_state.grades,
            use_container_width=True
        )
    else:
        st.info("아직 등록된 성적이 없습니다.")

        
# 대시보드
elif menu == "대시보드":
    st.header("나의 학업 대시보드")

    grades = st.session_state.grades

    col1, col2, col3 = st.columns(3)

    col1.metric("등록 과목", f"{grades['과목'].nunique()}개")
    
    if not grades.empty:
        col2.metric(
            "전체 평균",
            f"{grades['환산 점수'].mean():.1f}점"
        )
    else:
        col2.metric("전체 평균", "0점")

    col3.metric("등록 평가", f"{len(grades)}개")

    if grades.empty:
        st.info("왼쪽 메뉴에서 성적을 먼저 입력해 주세요.")
    else:
        st.subheader("최근 등록된 성적")
        st.dataframe(grades.tail(5), use_container_width=True)

# 성적 분석

elif menu == "성적 분석":
    st.header("📈 성적 분석")

    grades = st.session_state.grades

    if grades.empty:
        st.info("성적을 먼저 입력해 주세요.")

    else:
        # 과목별 평균 계산
        st.subheader("1. 과목별 평균")

        subject_avg = grades.groupby("과목")["환산 점수"].mean().reset_index()

        subject_avg.columns = ["과목", "평균 점수"]

        st.dataframe(
            subject_avg.round(2),
            use_container_width=True
        )

        # 과목별 평균 그래프
        fig1 = px.bar(
            subject_avg,
            x="과목",
            y="평균 점수",
            title="과목별 평균 점수",
            text_auto=".1f",
            range_y=[0, 100]
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.divider()

        # 평가 유형별 평균
        st.subheader("2. 평가 유형별 평균")

        type_avg = grades.groupby("평가 유형")["환산 점수"].mean().reset_index()

        type_avg.columns = ["평가 유형", "평균 점수"]

        st.dataframe(
            type_avg.round(2),
            use_container_width=True
        )

        fig2 = px.bar(
            type_avg,
            x="평가 유형",
            y="평균 점수",
            title="지필평가와 수행평가 평균 비교",
            text_auto=".1f",
            range_y=[0, 100]
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # 과목별 성적 변화 추이
        st.subheader("3. 과목별 성적 변화 추이")

        subjects = grades["과목"].unique().tolist()

        selected_subject = st.selectbox(
            "분석할 과목 선택",
            subjects
        )

        trend_data = grades[
            grades["과목"] == selected_subject
        ].copy()

        trend_data["평가 날짜"] = pd.to_datetime(
            trend_data["평가 날짜"]
        )

        trend_data = trend_data.sort_values("평가 날짜")

        fig3 = px.line(
            trend_data,
            x="평가 날짜",
            y="환산 점수",
            markers=True,
            title=f"{selected_subject} 성적 변화 추이",
            range_y=[0, 100],
            hover_data=["평가명"]
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # 전체 성적 데이터
        st.subheader("4. 전체 성적 기록")
        st.dataframe(grades, use_container_width=True)

# 학습 진단
elif menu == "학습 진단":
    st.header("📊 학습 진단")

    grades = st.session_state.grades

    if grades.empty:
        st.info("성적을 먼저 입력해 주세요.")

    else:
        subject_avg = grades.groupby("과목")["환산 점수"].mean().reset_index()

        st.subheader("과목별 학습 상태")

        for _, row in subject_avg.iterrows():
            subject = row["과목"]
            average = row["환산 점수"]

            if average >= 90:
                status = "우수"
                message = "현재 좋은 성취도를 보이고 있습니다."

            elif average >= 80:
                status = "양호"
                message = "꾸준한 학습으로 성취도를 높여 보세요."

            else:
                status = "보완 필요"
                message = "관련 개념을 다시 학습하고 부족한 부분을 확인해 보세요."

            st.write(f"**{subject} | {average:.1f}점 | {status}**")
            st.progress(float(average) / 100)
            st.caption(message)

        st.divider()

        st.subheader("전체 학습 결과")

        overall_avg = subject_avg["환산 점수"].mean()

        st.metric("전체 과목 평균", f"{overall_avg:.1f}점")

        best_subject = subject_avg.loc[
            subject_avg["환산 점수"].idxmax()
        ]

        st.success(
            f"평균이 가장 높은 과목은 {best_subject['과목']}입니다."
        )