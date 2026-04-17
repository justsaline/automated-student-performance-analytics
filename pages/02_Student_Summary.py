import pandas as pd
import streamlit as st
from src.ui_components import inject_font, page_header, render_sidebar
from src.analytics import (
    student_overview,
    student_strengths_weaknesses,
)
from src.schema import PASS_MARK
from src.visualizations import (
    student_subject_marks_bar,
    student_marks_distribution,
    performance_category_donut,
)

st.set_page_config(
    page_title="Lume/Student Summary",
    page_icon="assets/icon.png",
    layout="wide"
)

side_context = render_sidebar()
inject_font()
page_header(
    label="Academic Analytics",
    title="Student Summary",
    subtitle="Individual academic performance breakdown by subject and term."
)

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

st.markdown("### 👤 Student Profile Selection")

with st.container(border=True):
    col_student, col_term = st.columns([2, 1])
    
    with col_student:
        selected_label = st.selectbox(
            "Select a student",
            options=list(student_label_map.keys()),
            key="student_selector"
        )

    selected_reg_no = student_label_map[selected_label]
    student_terms = (
        long_df[long_df["reg_no"] == selected_reg_no]["term"]
        .dropna()
        .unique()
    )

    with col_term:
        selected_term = st.selectbox(
            "Select Term",
            options=["All Terms"] + sorted(list(student_terms)),
            key="student_term_selector"
        )

with side_context:
    if 'long_df' in st.session_state:
        st.markdown("### STUDENT CONTEXT")
        with st.container(border=True):
            st.markdown(f"**Name:** `{selected_label.split(' - ')[1]}`")
            st.markdown(f"**ID:** `{selected_reg_no}`")
            st.markdown(f"**Viewing:** `{selected_term}`")
        st.divider()

student_df = long_df[long_df["reg_no"] == selected_reg_no]

if selected_term != "All Terms":
    student_df = student_df[student_df["term"] == selected_term]

overview = student_overview(student_df, selected_reg_no)
attendance = overview["avg_attendance"]

if pd.isna(attendance):
    attendance_display = "Not Available"
else:
    attendance_display = f"{attendance:.2f}%"

# Build student_perf with both marks (raw) and marks_pct for different chart uses
if selected_term == "All Terms":
    student_perf = (
        student_df
        .groupby("subject", as_index=False)
        .agg(marks=("marks", "mean"), marks_pct=("marks_pct", "mean"))
        .sort_values("subject")
    )
else:
    student_perf = student_df[["subject", "marks", "marks_pct"]].sort_values("subject")

perf_dict = student_strengths_weaknesses(student_df, selected_reg_no)

c1, c2, c3 = st.columns(3)

avg_marks = overview['avg_marks']  # now pct-based from analytics

with c1:
    with st.container(border=True):
        st.metric("Average Marks (%)", f"{avg_marks:.1f}%" if avg_marks is not None and not pd.isna(avg_marks) else "N/A") 
        
with c2:
    with st.container(border=True):
        st.metric("Overall Attendance", attendance_display)
        
with c3:
    with st.container(border=True):
        st.metric("Subjects Taken", overview["subjects_taken"])
st.divider()

st.markdown("### 📊 Subject-wise Performance")
st.caption(f"Showing performance for: {selected_term}")

if student_perf.empty or student_perf['marks'].isna().all():
    st.info("No mark data available for this student.")
else:
    col_chart, col_table = st.columns([6, 4], gap="large")
    
    with col_chart:
        bar_chart = student_subject_marks_bar(student_perf)
        bar_chart.update_layout(title_text="")
        st.plotly_chart(bar_chart, use_container_width=True)
        
    with col_table:
        with st.container(border=True):
            st.markdown("**ℹ️ About Subject Marks**")
            st.caption(
                "Raw score alongside percentage (normalised to 0–100 across all subjects). "
                "The bar chart and analytics use the percentage scale."
            )
            
            display_perf_df = student_perf[["subject", "marks", "marks_pct"]].copy()
            display_perf_df["marks"] = display_perf_df["marks"].round(1)
            display_perf_df["marks_pct"] = display_perf_df["marks_pct"].round(1).astype(str) + "%"
            display_perf_df = display_perf_df.rename(columns={
                "subject": "Subject",
                "marks": "Raw Score",
                "marks_pct": "Score (%)"
            })
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(
                display_perf_df,
                use_container_width=True,
                hide_index=True
            )
st.divider()

# bucket subjects into pct ranges
bins = [0, 40, 60, 75, 100]
labels = ["0–40", "41–60", "61–75", "76–100"]

temp_df = student_perf.copy()
temp_df["marks_range"] = pd.cut(
    temp_df["marks_pct"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

range_summary = (
    temp_df.groupby("marks_range", observed=False)["subject"]
    .agg(
        Subjects=lambda x: ", ".join(x),
        Count="count"
    )
    .reindex(labels)
    .reset_index()
)
range_summary["Subjects"] = range_summary["Subjects"].fillna("")
range_summary["Count"] = range_summary["Count"].fillna(0).astype(int)
range_summary.columns = ["Marks Range (%)", "Subjects", "Count"]

col_chart, col_table = st.columns([6, 4], gap="large")

with col_chart:
    if student_perf.empty or student_perf['marks_pct'].isna().all():
        st.info("No mark data available for this student.")
    else:
        pass_mark = st.session_state.get("pass_mark", PASS_MARK)
        dist_fig = student_marks_distribution(student_perf, pass_mark=pass_mark)
        dist_fig.update_layout(title_text="")
        st.plotly_chart(dist_fig, use_container_width=True)

with col_table:
    with st.container(border=True):
        st.markdown("**📌 Marks Range Summary**")
        st.caption(
            "This table shows how the student's subjects are distributed "
            "across different performance ranges."
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(
            range_summary,
            use_container_width=True,
            hide_index=True
        )
        
st.divider()

st.markdown("### 🏆 Performance Category")

total_subjects = (
    len(perf_dict["strengths"])
    + len(perf_dict["average"])
    + len(perf_dict["weaknesses"])
)

strong = len(perf_dict["strengths"])
weak = len(perf_dict["weaknesses"])

if total_subjects == 0:
    insight = "⚪ No subject data available for this student."
elif strong / total_subjects >= 0.6:
    insight = "🟢 The student shows strong overall performance across most subjects."
elif weak / total_subjects >= 0.4:
    insight = "🔴 The student has multiple weak-performing subjects and may need support."
else:
    insight = "🟡 The student's performance is mixed across subjects."
    
st.info(insight)

if student_perf.empty or student_perf['marks'].isna().all():
    st.info("No mark data available for this student.")
else:
    tab_chart, tab_data = st.tabs(["📈 Visualization", "📄 Full Student Details"])

    with tab_chart:
        col_donut, col_details = st.columns([4, 6], gap="large")

        with col_donut:
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            perf_fig = performance_category_donut(perf_dict)
            perf_fig.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                margin=dict(t=50, b=0, l=0, r=0),
                height=300 
            )
            st.plotly_chart(perf_fig, use_container_width=True)

        with col_details:
            with st.container(border=True):
                st.markdown("##### 🔍 Subject Profile Summary")
                st.caption("Classification based on unique subjects across all selected terms.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("🟢 **Strengths**")
                    items = sorted(list(set(perf_dict["strengths"])))
                    if items:
                        for i in items:
                            st.markdown(f"- {i.title()}")
                    else:
                        st.caption("None")

                with c2:
                    st.markdown("🟡 **Average**")
                    items = sorted(list(set(perf_dict["average"])))
                    if items:
                        for i in items:
                            st.markdown(f"- {i.title()}")
                    else:
                        st.caption("None")

                with c3:
                    st.markdown("🔴 **Weaknesses**")
                    items = sorted(list(set(perf_dict["weaknesses"])))
                    if items:
                        for i in items:
                            st.markdown(f"- {i.title()}")
                    else:
                        st.caption("None")

                st.markdown("<br>", unsafe_allow_html=True)

    with tab_data:
        st.caption("This table displays the complete subject-wise academic record for the selected student.")
        
        student_full_df = (
            student_df[student_df["reg_no"] == selected_reg_no]
            .sort_values("subject")
            .reset_index(drop=True)
        )
        
        display_full_df = student_full_df.copy()
        for col in ["marks", "attendance"]:
            if col in display_full_df.columns:
                display_full_df[col] = display_full_df[col].round(2)
        if "marks_pct" in display_full_df.columns:
            display_full_df["marks_pct"] = display_full_df["marks_pct"].round(1).astype(str) + "%"
        display_full_df = display_full_df.rename(columns={
            "reg_no": "Reg No", "student_name": "Student",
            "class": "Class", "term": "Term",
            "attendance": "Attendance (%)", "subject": "Subject",
            "marks": "Raw Score", "marks_pct": "Score (%)"
        })

        st.dataframe(
            display_full_df,
            use_container_width=True,
            hide_index=True
        )

st.divider()
st.markdown(
    "<p style='text-align: center; color: gray;'>End of summary</p>",
    unsafe_allow_html=True
)