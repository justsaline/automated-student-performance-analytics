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
st.markdown("<br><br>", unsafe_allow_html=True) 

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

if "cleaning_report" in st.session_state:
    report = st.session_state.cleaning_report

    rows_before = report["rows_before"]
    rows_after = report["rows_after"]
    rows_dropped = report["rows_dropped"]
    marks_after = report["marks_after"]
    invalid_marks = report["invalid_marks"]
    duplicate_rows = report["duplicate_rows_detected"]
    attendance_after = report["attendance_after"]
    invalid_attendance = report["invalid_attendance"]

    total_marks = marks_after + invalid_marks
    marks_pct = round((marks_after / total_marks * 100)) if total_marks > 0 else 0
    invalid_marks_pct = round((invalid_marks / total_marks * 100)) if total_marks > 0 else 0
    rows_dropped_pct = round((rows_dropped / rows_before * 100), 1) if rows_before > 0 else 0
    rows_retained_pct = round((rows_after / rows_before * 100)) if rows_before > 0 else 0

    with st.container(border=True):
        st.markdown(f"""<center><h2 style="font-size:24px; font-weight:500; color:var(--color-text-primary); margin:0 0 -25px;">Cleaning Report</h2></center>""", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"""
        <style>
        .section-label {{ font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-text-tertiary); margin: 0 0 10px; }}
        .stat-card {{ background: rgba(255,255,255,0.06); border: 0.5px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px 16px; }}
        .stat-val {{ font-size: 26px; font-weight: 500; color: var(--color-text-primary); margin: 2px 0 0; line-height: 1.1; }}
        .stat-label {{ font-size: 12px; color: var(--color-text-secondary); margin: 0; }}
        .bar-bg {{ height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; margin-top: 10px; overflow: hidden; }}
        .bar-fill {{ height: 6px; border-radius: 3px; }}
        .badge {{ display: inline-block; font-size: 11px; font-weight: 500; padding: 2px 8px; border-radius: 99px; margin-top: 6px; }}
        .grid3 {{ display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 10px; }}
        .grid2 {{ display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 10px; }}
        </style>

        <div style="background: var(--color-background-primary); border: 0.5px solid var(--color-border-tertiary); border-radius: 12px; padding: 20px 22px;">

          <p class="section-label">Row overview</p>
          <div class="grid3" style="margin-bottom:16px;">
            <div class="stat-card">
              <p class="stat-label">Rows before</p>
              <p class="stat-val">{rows_before:,}</p>
            </div>
            <div class="stat-card">
              <p class="stat-label">Rows after</p>
              <p class="stat-val" style="color:var(--color-text-success)">{rows_after:,}</p>
              <div class="bar-bg"><div class="bar-fill" style="width:{rows_retained_pct}%;background:#639922"></div></div>
            </div>
            <div class="stat-card">
              <p class="stat-label">Rows dropped</p>
              <p class="stat-val" style="color:var(--color-text-danger)">{rows_dropped:,}</p>
              <span class="badge" style="background:#FCEBEB;color:#A32D2D;">{rows_dropped_pct}% of total</span>
            </div>
          </div>

          <p class="section-label">Marks</p>
          <div class="grid2" style="margin-bottom:16px;">
            <div class="stat-card">
              <p class="stat-label">Valid marks</p>
              <p class="stat-val" style="color:var(--color-text-success)">{marks_after:,}</p>
              <div class="bar-bg"><div class="bar-fill" style="width:{marks_pct}%;background:#639922"></div></div>
            </div>
            <div class="stat-card">
              <p class="stat-label">Invalid removed</p>
              <p class="stat-val" style="color:var(--color-text-danger)">{invalid_marks:,}</p>
              <span class="badge" style="background:#FCEBEB;color:#A32D2D;">{invalid_marks_pct}% of entries</span>
            </div>
          </div>

          <p class="section-label">Attendance & duplicates</p>
          <div class="grid3">
            <div class="stat-card">
              <p class="stat-label">Valid attendance</p>
              <p class="stat-val" style="color:var(--color-text-success)">{attendance_after:,}</p>
            </div>
            <div class="stat-card">
              <p class="stat-label">Invalid removed</p>
              <p class="stat-val" style="color:var(--color-text-danger)">{invalid_attendance:,}</p>
            </div>
            <div class="stat-card">
              <p class="stat-label">Duplicates found</p>
              <p class="stat-val" style="color:var(--color-text-warning)">{duplicate_rows:,}</p>
            </div>
          </div>

        </div>
        """, unsafe_allow_html=True)