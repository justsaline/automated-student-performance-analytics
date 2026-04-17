import streamlit as st
from src.analytics import rank_students, at_risk_students, subject_summary
from src.visualizations import subject_performance_heatmap, top_students_bar, at_risk_scatter
from src.schema import PASS_MARK
from src.ui_components import inject_font, page_header, render_sidebar

st.set_page_config(
    page_title="Lume/Total Summary",
    page_icon="assets/icon.png",
    layout="wide"
)
side_context = render_sidebar()
inject_font()
page_header(
    label="Academic Analytics",
    title="Total Summary",
    subtitle="Cohort-level performance overview across all students and subjects."
)

if not st.session_state.get("data_ready", False):
    st.warning("Please upload and process data on the main page first.")
    st.stop()
    
filtered_df = st.session_state.long_df
if filtered_df.empty:
    st.warning("No data found for the selected filter. Try a different combination.")
    st.stop()

groupable_columns = [
    col for col in filtered_df.columns
    if col not in ["marks", "marks_pct", "reg_no", "student_name", "subject", "attendance"]
]

st.divider()
st.markdown("### 🎛️ Filter Cohort")

with st.container(border=True):
    st.caption(
        "This page provides a high-level overview of student performance across the entire dataset, "
        "highlighting academic trends, attendance patterns, and overall rankings. Attendance is recorded "
        "at student level and is uniform across subjects in this dataset."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        group_by = st.selectbox(
            "Group By",
            options=["All"] + groupable_columns,
            key="total_group_by"
        )

    filtered_df = st.session_state.long_df.copy()

    with col2:
        if group_by != "All":
            options_list = sorted(filtered_df[group_by].dropna().unique())
            selected_value = st.selectbox(
                f"Select specific {group_by}",
                options=options_list,
                key="total_group_value"
            )
            if selected_value in options_list:
                filtered_df = filtered_df[filtered_df[group_by] == selected_value]
            else:
                selected_value = "All Terms"
        else:
            st.selectbox("Select specific group", ["Not applicable"], disabled=True)
            selected_value = "All Terms"

    with side_context:
        if 'long_df' in st.session_state:
            st.markdown("### SYSTEM CONTEXT")
            with st.container(border=True):
                st.markdown(f"**Students:** `{filtered_df['reg_no'].nunique()}`")
                st.markdown(f"**Total Records:** `{len(filtered_df)}`")
                st.markdown(f"**Active Group:** `{group_by}`")
                st.markdown(f"**Active Term:** `{selected_value}`")
    total_students = filtered_df['reg_no'].nunique()
    avg_marks = filtered_df['marks_pct'].mean()
    avg_attendance = filtered_df['attendance'].mean()

st.markdown("### 📌 Cohort Overview")
st.caption("These metrics summarize the overall academic and attendance performance of all students in the dataset.")

c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.metric("Total Students", total_students)

with c2:
    with st.container(border=True):
        st.metric("Average Marks (%)", f"{avg_marks:.1f}%")

with c3:
    with st.container(border=True):
        st.metric("Average Attendance", f"{avg_attendance:.2f}%")


st.divider()

if group_by != "All":
    st.info(f"Showing results for {group_by} = {selected_value}")
else:
    st.info("Showing results for entire dataset")

st.markdown("### 📚 Subject-wise Performance Distribution")

col_chart, col_table = st.columns([6, 4], gap="large")

with col_chart:
    heatmap_fig = subject_performance_heatmap(filtered_df)
    heatmap_fig.update_layout(coloraxis_showscale=False, title_text="")
    st.plotly_chart(heatmap_fig, use_container_width=True)

with col_table:
    with st.container(border=True):
        st.markdown("**ℹ️ About Subject Summary**")
        st.caption(
            "This table summarizes the number of students and average marks for each subject. "
            "It helps identify subjects with high or low performance across the cohort."
        )
        
        sub_df = subject_summary(filtered_df)
        display_sub_df = sub_df[["subject", "students", "avg_marks"]].copy()
        display_sub_df["avg_marks"] = display_sub_df["avg_marks"].round(1).astype(str) + "%"
        display_sub_df = display_sub_df.rename(columns={"subject": "Subject", "students": "Students", "avg_marks": "Avg Marks (%)"})
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(
            display_sub_df,
            use_container_width=True,
            hide_index=True
        )

st.divider()

st.markdown("### 🏆 Top Ranked Students")
st.caption("Ranks are computed using dense ranking, so students with the same average marks share the same rank.")

rank_df = rank_students(filtered_df)
top_df = rank_df.head(10)

tab_top10, tab_full = st.tabs(["📊 Top 10 Overview", "📋 Full Cohort Rankings"])

with tab_top10:
    col_chart, col_table = st.columns([6, 4], gap="large")
    
    with col_chart:
        fig = top_students_bar(rank_df, top_n=10)
        fig.update_layout(coloraxis_showscale=False) 
        st.plotly_chart(fig, use_container_width=True)
        
    with col_table:
        with st.container(border=True):
            st.markdown("**ℹ️ Top 10 List**")
            
            display_df = top_df[["rank", "reg_no", "student_name", "avg_marks"]].copy()
            display_df["avg_marks"] = display_df["avg_marks"].round(1).astype(str) + "%"
            display_df = display_df.rename(columns={"rank": "Rank", "reg_no": "Reg No", "student_name": "Student", "avg_marks": "Avg Marks (%)"})
            
            st.dataframe(
                display_df,
                use_container_width=True, 
                height=350, 
                hide_index=True
            )

with tab_full:
    st.dataframe(
        rank_df[["rank", "reg_no", "student_name", "avg_marks", "avg_attendance"]]
        .rename(columns={"rank": "Rank", "reg_no": "Reg No", "student_name": "Student", "avg_marks": "Avg Marks (%)", "avg_attendance": "Avg Attendance (%)"})
        .assign(**{"Avg Marks (%)": lambda d: d["Avg Marks (%)"].round(1).astype(str) + "%",
                   "Avg Attendance (%)": lambda d: d["Avg Attendance (%)"].round(1).astype(str) + "%"}),
        use_container_width=True,
        height=500,
        hide_index=True
    )

pass_mark = st.session_state.get("pass_mark", PASS_MARK)
attendance_threshold = st.session_state.get("attendance_threshold", 75)
at_risk_df = at_risk_students(filtered_df, pass_mark,attendance_threshold).reset_index()

st.divider()

st.markdown("### ⚠️ At-Risk Students")
st.markdown(f"**Students At Risk:** `{len(at_risk_df)}`")

if not at_risk_df.empty:
    tab_chart, tab_table = st.tabs(["📈 Visualization", "📋 Detailed List"])
    
    with tab_chart:
        fig = at_risk_scatter(at_risk_df, pass_mark=pass_mark, attendance_threshold=attendance_threshold)
        fig.update_layout(title_text="")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab_table:
        st.caption("Students listed below have been identified as at-risk based on low average marks or attendance.")
        
        display_risk_df = at_risk_df[["reg_no", "student_name", "avg_marks", "avg_attendance"]].copy()
        display_risk_df["avg_marks"] = display_risk_df["avg_marks"].round(1).astype(str) + "%"
        display_risk_df["avg_attendance"] = display_risk_df["avg_attendance"].round(1).astype(str) + "%"
        display_risk_df = display_risk_df.rename(columns={"reg_no": "Reg No", "student_name": "Student", "avg_marks": "Avg Marks (%)", "avg_attendance": "Avg Attendance (%)"})
        
        st.dataframe(
            display_risk_df,
            use_container_width=True,
            hide_index=True
        )
else:
    st.success("No at-risk students detected.")
    
st.markdown(
    "<p style='text-align: center; color: gray;'>End of summary</p>",
    unsafe_allow_html=True)