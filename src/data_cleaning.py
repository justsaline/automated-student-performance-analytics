import pandas as pd
from src.schema import ID_COLUMNS, COLUMN_ALIASES

def load_data(uploaded_file):
    if uploaded_file is None:
        raise ValueError("No file uploaded.")
    file_name = uploaded_file.name.lower()
    
    try:
        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.") 
    except Exception as e:
        raise ValueError(f"Failed to read file {e}")
    
    if df.empty:
        raise ValueError("Uploaded file contains no data.")
    if df.columns.size ==0:
        raise ValueError("Uploaded file contains no columns.")
    
    return df

# Normalize column names and rename to canonical names when mode is auto
def normalize_columns(df):
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
    
    column_mapping = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for col in df.columns:
            if col in aliases:
                column_mapping[col] = canonical
    
    df = df.rename(columns = column_mapping)
    return df

# Auto detect subject columns by excluding canonical ID columns
def detect_subject_columns(df):
    id_columns = ID_COLUMNS.copy()

    subject_columns = [col for col in df.columns if col not in id_columns]

    return subject_columns

# When in manual mode apply user provided mapping to rename columns
def apply_manual_column_mapping(df, manual_mapping):
    df = df.copy()
    
    rename_map = {actual: canonical for canonical, actual in manual_mapping.items() if actual in df.columns}
    
    df = df.rename(columns = rename_map)
    return df

# Convert the wide format table to long format by melting subject columns
def reshape_wide_to_long(df, subject_columns):
    
    df = df.copy()
    id_columns = ID_COLUMNS.copy()
    
    long_df = df.melt(id_vars = id_columns, value_vars = subject_columns, var_name = "subject", value_name = "marks")
    
    return long_df

# Clean marks column to ensrure numeric values only and count the chnages
def clean_marks(df):
    df = df.copy()
    
    before_count = df['marks'].notna().sum()
    df['marks'] = df['marks'].astype(str).str.extract(r'(\d+\.?\d*)', expand = False).astype('Float64')
    after_count = df['marks'].notna().sum()
    
    result = {'marks_before': before_count, 'marks_after': after_count, 'invalid_marks': before_count - after_count}
    
    return df, result

# Clean attendance column to ensure numeric values only and count the changes
def clean_attendance(df):
    df = df.copy()
    
    before_count = df['attendance'].notna().sum()
    df['attendance'] = df['attendance'].astype(str).str.extract(r'(\d+\.?\d*)', expand = False).astype('float')
    after_count = df['attendance'].notna().sum()
    
    result = {'attendance_before': before_count, 'attendance_after': after_count, 'invalid_attendance': before_count - after_count}
    
    return df, result

# Drop rows with missing data according to set rules and count the changes
# Rules to drop a row: 
# 1. Missing reg_no or subject -> no identification
# 2. Both marks and attendance are missing -> no useful data
# 3. Duplicate entries for same reg_no and subject -. keep first
def drop_invalid_rows(df):
    df = df.copy()
    
    before_rows = len(df)
    df = df.dropna(subset = ['reg_no', 'subject'])
    df = df[~(df['marks'].isna() & df['attendance'].isna())]
    
    duplicate_key = ['reg_no', 'subject', 'term']

    # Count duplicate groups
    duplicate_groups = df.duplicated(subset=duplicate_key, keep=False)
    duplicate_count = duplicate_groups.sum()

    # Drop exact duplicates (keep first)
    df = df.drop_duplicates(subset=duplicate_key, keep='first')

    after_rows = len(df)

    result = {'rows_before': before_rows, 'rows_after': after_rows, 'rows_dropped': before_rows - after_rows, 'duplicate_rows_detected': int(duplicate_count)}
    
    return df, result

# Main function deciding mode and applying data cleaning steps in order
def clean_data(df, mode = "auto", manual_mapping = None, subject_columns = None):
    
    df = df.copy()
    
    report = {}
    
    #  Conditional processing based on mode with value eror handling
    if mode == "auto":
        df = normalize_columns(df)
        subject_columns = detect_subject_columns(df)
        
    elif mode == "manual":
        if manual_mapping is None or subject_columns is None:
            raise ValueError("Manual mode requires manual_mapping and subject_columns.")
        df = apply_manual_column_mapping(df, manual_mapping)
        
    else:
        raise ValueError("Mode must be either 'auto' or 'manual'.")
    
    df = reshape_wide_to_long(df, subject_columns)
    df, marks_report = clean_marks(df)
    report.update(marks_report)
    df, attendance_report = clean_attendance(df)
    report.update(attendance_report)
    df, drop_report = drop_invalid_rows(df)
    report.update(drop_report)
    
    return  df, report