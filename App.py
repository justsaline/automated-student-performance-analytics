import streamlit as st
import pandas as pd
from src.data_cleaning import load_data, clean_data
from src.schema import ID_COLUMNS, MARKS_MAX, PASS_MARK
from src.ui_components import inject_font, page_header, section_header
import time

st.set_page_config(
    page_title="Lume/upload",
    page_icon="assets/icon.png",
    layout="wide"
)
st.logo("assets/logo.png", icon_image="assets/icon.png")
inject_font()
page_header(
    label="Academic Analytics",
    title="Student Performance Analysis",
    subtitle="Upload a student dataset to clean, analyse and visualise academic performance."
)

if "data_ready" not in st.session_state:
    st.session_state.data_ready = False
    
uploaded_file = st.file_uploader("Upload student data (CSV or Excel)", type = ['csv', 'xlsx'])

if uploaded_file is not None:
    try: 
        st.session_state.raw_df = load_data(uploaded_file)
    except ValueError as e:
        st.error(str(e))
        st.stop()
        
if "raw_df" not in st.session_state:
    st.info("Please upload a CSV or Excel file to continue.")
    st.stop()
    
raw_df = st.session_state.raw_df

section_header("Your Data")
st.dataframe(raw_df.head(5), use_container_width=True, hide_index=True)

with st.container(border=True):
    st.subheader("⚙️ Cleaning Mode")
    st.caption("Choose how columns should be interpreted. Auto tries to detect columns automatically. Manual lets you define mappings yourself.")

    mode = st.radio(
        "Select Mode", 
        options=["Auto", "Manual"],
        horizontal=True,
        label_visibility="collapsed"
    )
mode = mode.lower()

manual_mapping = None
subject_columns = None
pass_mark = PASS_MARK
attendance_threshold = 75

if mode == "manual":
    st.markdown("### 🧩 Manual Column Mapping")
    st.info("Map your dataset columns to canonical column names. Only map what exists in your file.")

    st.markdown("#### ⚙️ Validation Settings")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            marks_range = st.number_input("Enter maximum marks for validation:", min_value=1, value=MARKS_MAX)
        with col2:
            pass_mark = st.number_input("Pass mark", min_value=1, value=PASS_MARK)
        with col3:
            attendance_threshold = st.number_input("Attendance threshold (%)", min_value=1, max_value=100, value=75)

    st.markdown("#### 🔄 Dataset Mapping")
    with st.container(border=True):
        map_cols = st.columns(2)
        
        manual_mapping = {}
        current_id_selections = {
            col: st.session_state.get(f"map_{col}", "-- Not Present --")
            for col in ID_COLUMNS
        }

        for i, canonical_col in enumerate(ID_COLUMNS):
            
            used_by_others = {
                v for k, v in current_id_selections.items()
                if v != "-- Not Present --" and k != canonical_col
            }
            
            available_options = [
                col for col in raw_df.columns
                if col not in used_by_others
            ]
            
            with map_cols[i % 2]:
                selected_col = st.selectbox(
                    f"Map **{canonical_col}** to:",
                    options=["-- Not Present --"] + available_options,
                    key=f"map_{canonical_col}"
                )

            if selected_col != "-- Not Present --":
                manual_mapping[canonical_col] = selected_col

    st.markdown("#### 📚 Subject Columns")
    with st.container(border=True):
        
        used_columns = {
            st.session_state.get(f"map_{col}")
            for col in ID_COLUMNS
            if st.session_state.get(f"map_{col}") != "-- Not Present --"
        }
        
        subject_columns = st.multiselect(
            "Select subject columns (marks columns)",
            options=[col for col in raw_df.columns if col not in used_columns]
        )

    if not manual_mapping or not subject_columns:
        st.warning("⚠️ Manual mode requires column mapping and subject selection.")

run_cleaning = st.button("🚀 Run Data Cleaning")
st.markdown("<br>", unsafe_allow_html=True) 

if run_cleaning:
    try:
        if mode == "auto":
            with st.spinner('Scanning data structures...'):
                time.sleep(2)
            cleaned_df, report = clean_data(raw_df, mode = "auto", marks_range = MARKS_MAX)
        else:
            with st.spinner('Scanning data structures...'):
                time.sleep(2)
            cleaned_df, report = clean_data(raw_df, mode = "manual",
                                            manual_mapping = manual_mapping,
                                            subject_columns = subject_columns, marks_range = marks_range)
            
    except Exception as e:
        st.error(str(e))
        st.stop()
    
    st.session_state.long_df = cleaned_df
    st.session_state.cleaning_report = report
    st.session_state.data_ready = True
    st.session_state.pass_mark = pass_mark
    st.session_state.attendance_threshold = attendance_threshold
    st.success("Data Cleaned Successfully")

from src.ui_components import inject_font, page_header, section_header, render_cleaning_report

if "cleaning_report" in st.session_state:
    render_cleaning_report(st.session_state.cleaning_report)