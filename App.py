import streamlit as st
import pandas as pd
from src.data_cleaning import load_data, clean_data
from src.schema import ID_COLUMNS, MARKS_MAX, PASS_MARK

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500&display=swap');
    p, h1, h2, h3, h4, h5, h6, label, button, input, textarea, 
    .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader,
    .stRadio, .stSelectbox, .stMultiSelect, .stNumberInput,
    .stDataFrame, .stMetric, .stExpander {
        font-family: 'Outfit', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Automated Student Performance Analysis")
st.caption("Upload student data to begin analysis.")

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

st.subheader("Preview of Uploaded Data")
st.dataframe(raw_df.head(5), width = "stretch")

st.subheader("⚙️ Cleaning Mode")

mode = st.radio(
    "Choose how columns should be interpreted",
    options=["Auto", "Manual"],
    index=0,
    help="Auto tries to detect columns automatically. Manual lets you define mappings yourself."
)

mode = mode.lower()

manual_mapping = None
subject_columns = None
pass_mark = PASS_MARK
attendance_threshold = 75

if mode == "manual":
    st.markdown("### 🧩 Manual Column Mapping")

    st.info(
        "Map your dataset columns to canonical column names. "
        "Only map what exists in your file."
    )
    
    marks_range = st.number_input(
        "Enter maximum marks for validation:")
    pass_mark = st.number_input("Pass mark", min_value=1, value=PASS_MARK)
    attendance_threshold = st.number_input("Attendance threshold (%)", min_value=1, max_value=100, value=75)

    manual_mapping = {}
    current_id_selections = {
        col: st.session_state.get(f"map_{col}", "-- Not Present --")
        for col in ID_COLUMNS}

    for canonical_col in ID_COLUMNS:
        
        used_by_others = {
        v for k, v in current_id_selections.items()
        if v != "-- Not Present --" and k != canonical_col}
        
        available_options = [
        col for col in raw_df.columns
        if col not in used_by_others]
        
        selected_col = st.selectbox(
            f"Map **{canonical_col}** to:",
            options=["-- Not Present --"] + available_options,
            key=f"map_{canonical_col}"
        )

        if selected_col != "-- Not Present --":
            manual_mapping[canonical_col] = selected_col
            
    used_columns = {
    st.session_state.get(f"map_{col}")
    for col in ID_COLUMNS
    if st.session_state.get(f"map_{col}") != "-- Not Present --"}
    
    st.divider()
            
    st.markdown("### 📚 Subject Columns")

    subject_columns = st.multiselect(
        "Select subject columns (marks columns)",
        options=[col for col in raw_df.columns if col not in used_columns]
    )

    if not manual_mapping or not subject_columns:
        st.warning("Manual mode requires column mapping and subject selection.")

run_cleaning = st.button("🚀 Run Data Cleaning")
st.divider()

if run_cleaning:
    try:
        if mode == "auto":
            cleaned_df, report = clean_data(raw_df, mode = "auto", marks_range = MARKS_MAX)
        else:
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

    with st.expander("🧹 Data Cleaning Summary", expanded=True):
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