import streamlit as st
from src.analytics import rank_students, at_risk_students, subject_summary
from src.visualizations import subject_performance_heatmap, top_students_bar, at_risk_scatter
from src.schema import PASS_MARK

st.set_page_config(
    page_title="Total Summary",
    layout="wide")

st.title("📊 Total Summary")
st.caption(
    "This page provides a high-level overview of student performance across the entire dataset, "
    "highlighting academic trends, attendance patterns, and overall rankings. Attendance is recorded at student level and is uniform across subjects in this dataset.")


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

st.markdown(
    "### 📌 Cohort Overview\n"
    "These metrics summarize the overall academic and attendance performance of all students in the dataset.")


st.divider()

st.subheader("📚 Subject-wise performance Distribution")

col1, col2 = st.columns([2, 1])
with col1:
    heatmap_fig = subject_performance_heatmap(long_df)
    st.plotly_chart(heatmap_fig, use_container_width=True)
    sub_df = subject_summary(long_df)
with col2:
    with st.expander("ℹ️ About Subject Summary Table", expanded=True):
        st.markdown(
            "This table summarizes the number of students and average marks for each subject. "
            "It helps identify subjects with high or low performance across the cohort."
        )
        st.dataframe(
            sub_df[["subject", "students","avg_marks"]], use_container_width=True, hide_index=True
        )

st.divider()

st.subheader("🏆 Top Ranked Students")
st.caption(
    "Ranks are computed using dense ranking, so students with the same average marks share the same rank.")

rank_df = rank_students(long_df)
top_df = rank_df.head(10)

col3, col4 = st.columns([2, 1])
with col3:
    fig = top_students_bar(rank_df, top_n=10)
    st.plotly_chart(fig, use_container_width=True)
with col4:
    with st.expander("ℹ️ List of Top Students", expanded=True):
        st.dataframe(
            top_df[["rank", "reg_no", "student_name", "avg_marks"]],
            use_container_width=True, height = 300, hide_index=True
        )

with st.expander("📋 View Full Student Rankings"):
    st.dataframe(
        rank_df[
            ["rank", "reg_no", "student_name", "avg_marks", "avg_attendance"]
        ],
        use_container_width=True,
        height=400
    )

at_risk_df = at_risk_students(long_df, PASS_MARK).reset_index()

st.divider()

st.subheader("⚠️ At-Risk Students")
st.write("Students At Risk: ", len(at_risk_df))
if not at_risk_df.empty:
    fig = at_risk_scatter(at_risk_df)
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("📋 View At-Risk Students Details"):
        st.caption("Students listed below have been identified as at-risk based on low average marks or attendance.")
        st.dataframe(
            at_risk_df[
                ["reg_no", "student_name", "avg_marks", "avg_attendance"]
            ],
            use_container_width=True
        )
else:
    st.success("No at-risk students detected.")
    
st.markdown(
    "<p style='text-align: center; color: gray;'>End of summary</p>",
    unsafe_allow_html=True)