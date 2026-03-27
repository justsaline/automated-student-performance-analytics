import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Lume/About | Student Performance Analysis",
    layout="wide", page_icon="assets/icon.png"
)
st.logo("assets/logo.png", icon_image="assets/icon.png")

_, content, _ = st.columns([1, 3, 1])

with content:
    st.title("About the System")
    st.markdown(
        "Automated Student Performance Analysis is an analytical framework "
        "designed to transform fragmented academic records into standardized, "
        "actionable insights through automated data processing and visualization."
    )

    st.divider()

    st.header("Objective")
    st.markdown(
        "Academic data often lacks structural consistency. This application "
        "automates the extraction, cleaning, and normalization of student datasets, "
        "allowing educators to focus on intervention rather than manual data entry."
    )

    st.divider()

    st.header("Key Capabilities")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Data Normalization**")
            st.caption(
                "Automated detection and cleaning of CSV/Excel files, "
                "handling inconsistent naming and missing values."
            )
            
        with st.container(border=True):
            st.markdown("**Individual Diagnostics**")
            st.caption(
                "Granular breakdown of strengths and weaknesses "
                "per student across different assessment terms."
            )

    with col2:
        with st.container(border=True):
            st.markdown("**Cohort Analytics**")
            st.caption(
                "High-level overview of subject-wise distributions, "
                "attendance correlations, and academic trends."
            )
            
        with st.container(border=True):
            st.markdown("**Risk Identification**")
            st.caption(
                "Automated flagging of students based on custom "
                "academic performance and attendance thresholds."
            )

    st.divider()

    st.header("Data Requirements")
    st.markdown(
        "To ensure accurate processing, uploaded datasets should include "
        "the following primary identifiers:"
    )

    spec_data = {
        "Field": ["Identifier", "Full Name", "Group", "Term", "Attendance"],
        "Description": ["Registration or Roll Number", "Legal Student Name", "Class or Grade Level", "Semester or Assessment Period", "Percentage or Decimal Format"]
    }
    st.table(pd.DataFrame(spec_data))

    st.markdown("**Subject Mapping**")
    st.markdown(
        "The system utilizes a wide-to-long transformation logic. This allows "
        "users to include any number of subjects (e.g., Mathematics, Science, "
        "Arts) without pre-configuring the schema."
    )

    st.divider()

    st.header("Processing Logic")
    
    st.markdown("**Heuristic Column Detection**")
    st.markdown(
        "The system cross-references header aliases to map user data to internal "
        "logic, reducing the need for manual column renaming."
    )

    st.markdown("**Validation Pipeline**")
    st.markdown(
        "Data passes through a strict cleaning pipeline that removes "
        "non-numeric artifacts, normalizes attendance to a 100-point scale, "
        "and eliminates duplicate records."
    )

    st.divider()

    st.header("Navigation")
    st.markdown("- [Data Upload and Configuration](/)")
    st.markdown("- [Cohort Performance Summary](/Total_Summary)")
    st.markdown("- [Individual Student Analytics](/Student_Summary)")

    st.markdown(
        "<p style='text-align:center; color: gray; margin-top: 4rem; font-size: 0.8rem;'>"
        "Automated Student Performance Analysis System v1.0</p>",
        unsafe_allow_html=True
    )