import pandas as pd
import streamlit as st

from src.analytics import (
    student_overview,
    student_subject_analysis,
    student_strengths_weaknesses,
)

from src.visualizations import (
    student_subject_marks_bar,
    student_marks_distribution,
    performance_category_donut,
)

st.set_page_config(page_title="Student Summary", layout="wide")

st.title("👤 Student Summary")

if not st.session_state.get("data_ready", False):
    st.warning("Please upload and process data on the main page first.")
    st.stop()
    
long_df = st.session_state.long_df

student_ids = (
    long_df[["reg_no", "student_name"]]
    .drop_duplicates()
    .sort_values("reg_no"))

student_label_map = {
    f"{row.reg_no} - {row.student_name}": row.reg_no
    for _, row in student_ids.iterrows()
    }

selected_label = st.selectbox(
    "Select a student",
    options=list(student_label_map.keys()))

selected_reg_no = student_label_map[selected_label]

overview = student_overview(long_df, selected_reg_no)
attendance = overview["avg_attendance"]

if pd.isna(attendance):
    attendance_display = "Not Available"
else:
    attendance_display = f"{attendance:.2f}%"
student_perf = student_subject_analysis(long_df, selected_reg_no)
perf_dict = student_strengths_weaknesses(long_df, selected_reg_no)

c1, c2, c3 = st.columns(3)

c1.metric("Average Marks", f"{overview['avg_marks']:.2f}")
c2.metric("Overall Attendance",attendance_display)
c3.metric("Subjects Taken", overview["subjects_taken"])

st.divider()

st.subheader("📊 Subject-wise Performance")

col1, col2 = st.columns([2, 1])
with col1:
    bar_chart = student_subject_marks_bar(student_perf)
    st.plotly_chart(bar_chart, use_container_width = True)
with col2:
    with st.expander("ℹ️ About Subject Marks Bar Chart", expanded=True):
        st.markdown(
            "This bar chart displays the marks obtained by the selected student in each subject. "
            "It provides a clear visual representation of their performance across different subjects."
        )
        st.dataframe(
            student_perf,
            use_container_width = True,
            hide_index = True
        )
st.divider()
dist_fig = student_marks_distribution(student_perf)
st.plotly_chart(dist_fig, use_container_width = True)

st.divider()

st.subheader("Performance Category")

perf_fig = performance_category_donut(perf_dict)
st.plotly_chart(perf_fig, use_container_width = True)