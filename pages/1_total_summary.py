import streamlit as st
from src.analytics import subject_summary, rank_students, attendance_summary
from src.visualizations import subject_performance_heatmap

st.set_page_config(
    page_title="Total Summary",
    layout="wide")

st.title("📊 Total Summary")

if not st.session_state.get("data_ready", False):
    st.warning("Please upload and process data on the main page first.")
    st.stop()
    
long_df = st.session_state.long_df

total_students = long_df['reg_no'].nunique()
avg_marks = long_df['marks'].mean()
avg_attendance = long_df['attendance'].mean()

c1,c2,c3 = st.columns(3)

c1.metric("Total Students", total_students)
c2.metric("Average Marks", f"{avg_marks: .2f}")
c3.metric("Average Attendance", f"{avg_attendance: .2f}")
st.caption(
    "Attendance is recorded at student level and is uniform across subjects in this dataset.")

st.divider()

st.subheader("📚 Subject-wise performance Distribution")

heatmap_fig = subject_performance_heatmap(long_df)
st.plotly_chart(heatmap_fig, use_container_width = True)

st.divider()

st.subheader("🏆 Top Ranked Students")

ranking_df = rank_students(long_df).head(10).reset_index()
st.dataframe(ranking_df, use_container_width = True)