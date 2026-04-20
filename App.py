import streamlit as st
import pandas as pd
import os
from src.data_cleaning import load_data, load_excel_sheets, clean_data, normalize_columns, detect_subject_columns, compute_percentage_column
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

# show a notice if data is already loaded
if st.session_state.get("data_ready", False):
    st.success("✅ Data already loaded — navigate to the summary pages or re-upload below to reset.")

uploaded_file = st.file_uploader("Upload student data (CSV or Excel)", type = ['csv', 'xlsx'])

if uploaded_file is not None:
    st.session_state.uploaded_file_bytes = uploaded_file.read()
    st.session_state.uploaded_file_name = uploaded_file.name
    uploaded_file.seek(0)
    try:
        st.session_state.raw_df = load_data(uploaded_file)
        st.session_state.data_ready = False
        
        if uploaded_file.name.lower().endswith(".xlsx"):
            uploaded_file.seek(0)
            xl = pd.ExcelFile(uploaded_file)
            st.session_state.excel_sheet_names = xl.sheet_names
        else:
            st.session_state.excel_sheet_names = []
            
    except ValueError as e:
        st.error(str(e))
        st.stop()
        
if "raw_df" not in st.session_state:
    st.info("Please upload a CSV or Excel file to continue.")
    st.stop()
    
raw_df = st.session_state.raw_df

import io
if uploaded_file is None and st.session_state.get("uploaded_file_bytes"):
    uploaded_file = io.BytesIO(st.session_state.uploaded_file_bytes)
    uploaded_file.name = st.session_state.uploaded_file_name

source_name = os.path.splitext(uploaded_file.name)[0] if uploaded_file is not None else "Unknown"

section_header("Your Data")
st.dataframe(raw_df.head(5), use_container_width=True, hide_index=True)

# multi-sheet selection for excel files
if st.session_state.get("excel_sheet_names"):
    all_sheets = st.session_state.excel_sheet_names
    
    if len(all_sheets) > 1:
        with st.container(border=True):
            st.subheader("📄 Sheet Selection")
            st.caption(
                "Multiple sheets detected. By default only the first sheet is loaded. "
                "Select additional sheets to merge them — useful when each sheet represents a different term or semester. "
                "If a sheet has no term column, the sheet name will be used as the term automatically."
            )
            _sheet_default = st.session_state.get("selected_sheets") or [all_sheets[0]]
            selected_sheets = st.multiselect(
                "Select sheets to include",
                options=all_sheets,
                default=_sheet_default,
                key="selected_sheets"
            )
            if not selected_sheets:
                st.warning("⚠️ Please select at least one sheet.")
    else:
        selected_sheets = all_sheets
        st.session_state.selected_sheets = selected_sheets
else:
    selected_sheets = []
    st.session_state.selected_sheets = selected_sheets

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
marks_range = MARKS_MAX
st.session_state.max_marks = marks_range

# detect subjects early for the auto-mode info banner
auto_detected_subjects = []
if mode == "auto":
    try:
        all_auto_subjects = list(detect_subject_columns(normalize_columns(raw_df)))
        
        current_selected = st.session_state.get("selected_sheets", [])
        excel_sheet_names = st.session_state.get("excel_sheet_names", [])
        
        if excel_sheet_names and len(current_selected) > 1 and uploaded_file is not None:
            try:
                uploaded_file.seek(0)
                for sheet in current_selected[1:]:
                    try:
                        extra_df = pd.read_excel(uploaded_file, sheet_name=sheet)
                        uploaded_file.seek(0)
                        extra_subjects = detect_subject_columns(normalize_columns(extra_df))
                        for s in extra_subjects:
                            if s not in all_auto_subjects:
                                all_auto_subjects.append(s)
                    except Exception:
                        pass
            except Exception:
                pass
        
        auto_detected_subjects = all_auto_subjects
        
    except Exception:
        auto_detected_subjects = []

    if auto_detected_subjects:
        st.info(
            f"**Auto mode** — {len(auto_detected_subjects)} subject column(s) detected across all selected sheets: "
            + ", ".join(f"`{s}`" for s in auto_detected_subjects)
        )

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


# Determine which subjects are known at this point for the UI
ui_subjects = subject_columns if mode == "manual" else auto_detected_subjects

with st.container(border=True):
    st.subheader("📐 Max Marks Configuration")
    st.caption(
        "If some subjects have different maximum marks (e.g. lab subjects out of 50), configure them here. "
        "All analytics will use percentage scores internally."
    )

    if mode == "manual":
        global_max = marks_range
    else:
        global_max = st.number_input(
            "Global maximum marks",
            min_value=1,
            value=100,
            key="global_max_auto"
        )

    st.session_state.max_marks = int(global_max)

    diff_max_marks = st.radio(
        "Do any subjects have a different maximum marks?",
        options=["No — all subjects share the same max marks", "Yes — configure per subject"],
        key="diff_max_marks_radio"
    ) == "Yes — configure per subject"

    st.session_state.diff_max_marks = diff_max_marks
    max_marks_config_valid = True

    if not diff_max_marks:
        st.session_state.max_marks_config = int(global_max)

    else:
        if not ui_subjects:
            st.warning(
                "⚠️ Subject columns are not yet known. "
                "Please complete the mapping above first (manual mode) or upload a file (auto mode)."
            )
            max_marks_config_valid = False
            st.session_state.max_marks_config = {}
        else:
            st.markdown("**Select subjects with non-standard maximum marks:**")
            st.caption(
                "Only subjects selected here will show a configuration input. "
                "All other subjects automatically use the global max set above."
            )

            non_standard_subjects = st.multiselect(
                "Subjects with different max marks",
                options=ui_subjects,
                key="non_standard_subjects_select"
            )

            per_subject_config = {}

            if non_standard_subjects:
                st.markdown("**Configure max marks for selected subjects:**")
                st.caption(f"Defaults are set to global max ({int(global_max)}). Only change what differs.")

                chunks = [non_standard_subjects[i:i+3] for i in range(0, len(non_standard_subjects), 3)]
                for chunk in chunks:
                    cols = st.columns(len(chunk))
                    for col, subj in zip(cols, chunk):
                        with col:
                            val = st.number_input(
                                f"`{subj}`",
                                min_value=1,
                                value=int(global_max),
                                step=1,
                                key=f"max_marks_subj_{subj}"
                            )
                            per_subject_config[subj] = int(val)

            for subj in ui_subjects:
                if subj not in per_subject_config:
                    per_subject_config[subj] = int(global_max)

            st.session_state.max_marks_config = per_subject_config
            st.session_state.max_marks = 100


run_cleaning = st.button("🚀 Run Data Cleaning", disabled=not max_marks_config_valid)
st.markdown("<br>", unsafe_allow_html=True) 

if run_cleaning:
    try:
        extra_dfs = []
        selected_sheets = st.session_state.get("selected_sheets", [])
        excel_sheet_names = st.session_state.get("excel_sheet_names", [])
        
        if excel_sheet_names and len(selected_sheets) > 1 and uploaded_file is not None:
            uploaded_file.seek(0)
            sheet_data = load_excel_sheets(uploaded_file, selected_sheets)
            first_sheet_name = selected_sheets[0]
            extra_sheet_data = [(name, df) for name, df in sheet_data if name != first_sheet_name]
            extra_dfs = [df for _, df in extra_sheet_data]
        
        if excel_sheet_names and selected_sheets:
            source_name = selected_sheets[0]

        if mode == "auto":
            with st.spinner('Scanning data structures...'):
                time.sleep(2)
            cleaned_df, report = clean_data(
                raw_df,
                mode="auto",
                marks_range=st.session_state.max_marks,
                extra_dfs=extra_dfs if extra_dfs else None,
                source_name=source_name
            )
        else:
            with st.spinner('Scanning data structures...'):
                time.sleep(2)
            cleaned_df, report = clean_data(
                raw_df,
                mode="manual",
                manual_mapping=manual_mapping,
                subject_columns=subject_columns,
                marks_range=marks_range,
                extra_dfs=extra_dfs if extra_dfs else None,
                source_name=source_name
            )
            
    except Exception as e:
        st.error(str(e))
        st.stop()


    max_marks_config = st.session_state.get("max_marks_config", st.session_state.get("max_marks", 100))
    cleaned_df = compute_percentage_column(cleaned_df, max_marks_config)

    st.session_state.long_df = cleaned_df
    st.session_state.cleaning_report = report
    st.session_state.data_ready = True
    st.session_state.pass_mark = pass_mark
    st.session_state.attendance_threshold = attendance_threshold
    st.success("Data Cleaned Successfully ✅")

from src.ui_components import inject_font, page_header, section_header, render_cleaning_report

if "cleaning_report" in st.session_state:
    render_cleaning_report(st.session_state.cleaning_report)