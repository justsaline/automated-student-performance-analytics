import streamlit as st
import pandas as pd
from src.data_cleaning import load_data, clean_data, normalize_columns, detect_subject_columns, compute_percentage_column
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

# ── Data-already-loaded indicator ────────────────────────────────────────────
if st.session_state.get("data_ready", False):
    st.success("✅ Data already loaded — navigate to the summary pages or re-upload below to reset.")

uploaded_file = st.file_uploader("Upload student data (CSV or Excel)", type = ['csv', 'xlsx'])

if uploaded_file is not None:
    try: 
        st.session_state.raw_df = load_data(uploaded_file)
        # Reset ready flag when a new file is uploaded
        st.session_state.data_ready = False
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
marks_range = MARKS_MAX
st.session_state.max_marks = marks_range

# ── Detect subject columns for auto mode (for UI purposes only) ───────────────
auto_detected_subjects = []
if mode == "auto":
    try:
        auto_detected_subjects = detect_subject_columns(normalize_columns(raw_df))
    except Exception:
        auto_detected_subjects = []

    if auto_detected_subjects:
        st.info(
            f"**Auto mode** — {len(auto_detected_subjects)} subject column(s) detected: "
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

# ── Per-subject max marks configuration ──────────────────────────────────────
# Determine which subjects are known at this point for the UI
ui_subjects = subject_columns if mode == "manual" else auto_detected_subjects

with st.container(border=True):
    st.subheader("📐 Max Marks Configuration")
    st.caption("If some subjects have different maximum marks (e.g. lab subjects out of 50), configure them here. All analytics will use percentage scores internally.")

    diff_max_marks = st.radio(
        "Do your subjects have different maximum marks?",
        options=["No — all subjects share the same max marks", "Yes — configure per subject"],
        key="diff_max_marks_radio"
    ) == "Yes — configure per subject"

    st.session_state.diff_max_marks = diff_max_marks

    max_marks_config_valid = True  # used to gate the Run button

    if not diff_max_marks:
        # Single global max — already captured in marks_range for manual mode; default 100 for auto
        global_max = marks_range if mode == "manual" else st.number_input(
            "Global maximum marks", min_value=1, value=100, key="global_max_auto"
        )
        st.session_state.max_marks_config = int(global_max)
        st.session_state.max_marks = int(global_max)
    else:
        # Per-subject inputs
        if not ui_subjects:
            st.warning("⚠️ Subject columns are not yet known. Please complete the mapping above first (manual mode) or upload a file (auto mode).")
            max_marks_config_valid = False
            st.session_state.max_marks_config = {}
        else:
            st.markdown("Enter the maximum marks for each subject:")
            per_subject_config = {}
            missing_any = False

            # Render in rows of 3
            subjects_chunked = [ui_subjects[i:i+3] for i in range(0, len(ui_subjects), 3)]
            for chunk in subjects_chunked:
                cols = st.columns(len(chunk))
                for col, subj in zip(cols, chunk):
                    with col:
                        val = st.number_input(
                            f"`{subj}`",
                            min_value=1,
                            value=100,
                            step=1,
                            key=f"max_marks_subj_{subj}"
                        )
                        per_subject_config[subj] = int(val)

            if missing_any:
                st.warning("⚠️ Please enter max marks for all subjects before running.")
                max_marks_config_valid = False

            st.session_state.max_marks_config = per_subject_config
            # Store a representative global max for legacy uses
            st.session_state.max_marks = 100

# ── Run button ────────────────────────────────────────────────────────────────
run_cleaning = st.button("🚀 Run Data Cleaning", disabled=not max_marks_config_valid)
st.markdown("<br>", unsafe_allow_html=True) 

if run_cleaning:
    try:
        if mode == "auto":
            with st.spinner('Scanning data structures...'):
                time.sleep(2)
            cleaned_df, report = clean_data(raw_df, mode="auto", marks_range=st.session_state.max_marks)
        else:
            with st.spinner('Scanning data structures...'):
                time.sleep(2)
            cleaned_df, report = clean_data(raw_df, mode="manual",
                                            manual_mapping=manual_mapping,
                                            subject_columns=subject_columns,
                                            marks_range=marks_range)
            
    except Exception as e:
        st.error(str(e))
        st.stop()

    # Compute marks_pct column using per-subject or global config
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