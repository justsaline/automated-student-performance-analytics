import streamlit as st
import pandas as pd
from src.data_cleaning import load_data, clean_data
from src.schema import CANONICAL_COLUMNS, ID_COLUMNS


st.set_page_config(page_title="Automated Student Performance Analysis", layout="wide")

st.title("Automated Student Performance Analysis")
st.caption("Upload student data to begin analysis.")

if "data_ready" not in st.session_state:
    st.session_state.data_ready = False
    
uploaded_file = st.file_uploader("Upload student data (CSV or Excel)", type = ['csv', 'xlsx'])

if uploaded_file is None:
    st.info("Please upload a CSV or Excel file to continue.")
    st.stop()
    
try:
    raw_df = load_data(uploaded_file)
except ValueError as e:
    st.error(str(e))
    st.stop()
    
st.session_state.raw_df = raw_df

st.subheader("Preview of Uploaded Data")
st.dataframe(raw_df.head(), width = "stretch")

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

if mode == "manual":
    st.markdown("### 🧩 Manual Column Mapping")

    st.info(
        "Map your dataset columns to canonical column names. "
        "Only map what exists in your file."
    )
    
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
        

st.divider()

run_cleaning = st.button("🚀 Run Data Cleaning")

if run_cleaning:
    try:
        if mode == "auto":
            cleaned_df, report = clean_data(raw_df, mode = "auto")
        else:
            cleaned_df, report = clean_data(raw_df, mode = "manual", manual_mapping = manual_mapping, subject_columns = subject_columns)
            
    except Exception as e:
        st.error(str(e))
        st.stop()
    
    st.session_state.long_df = cleaned_df
    st.session_state.cleaning_report = report
    st.session_state.data_ready = True
    st.success("Data Cleaned Successfully")