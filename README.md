# Automated Student Performance Analysis

## Introduction

The Automated Student Performance Analysis system is a web-based analytical application developed using Streamlit and Python. The objective of this project is to provide an end-to-end data processing and analysis pipeline for academic datasets that are often inconsistent, manually maintained, and structurally ambiguous.

Educational institutions frequently store student records in spreadsheet format with varying column names, inconsistent attendance formats, embedded text inside numeric fields, and duplicate records. These inconsistencies make analytical reporting difficult and error-prone. This application addresses those challenges by standardizing, validating, restructuring, and analyzing raw student performance data through a reproducible and transparent pipeline.

The system is modular in design and separates responsibilities into data loading, cleaning, analytics computation, and visualization layers.

---

## System Architecture

The application is structured as a multi-page Streamlit application with modular backend components:

- `app.py` – Main interface for data upload and cleaning execution  
- `data_cleaning.py` – Complete preprocessing and validation pipeline  
- `analytics.py` – Aggregation, ranking, and risk detection logic  
- `visualizations.py` – Plotly-based visualization generation  
- `schema.py` – Canonical schema definitions and system constants  
- `1_total_summary.py` – Cohort-level dashboard  
- `2_student_summary.py` – Individual student-level dashboard  

This separation ensures maintainability, scalability, and clarity of logic.

---

## Input Data Requirements

The system accepts the following file formats:

- CSV (.csv)
- Excel (.xlsx)

The uploaded file must contain student-level data in wide format, where each row represents a student and each subject is represented as a separate column containing marks.

A typical dataset structure is as follows:

| Reg No | Student Name | Class | Term | Attendance | Math | Physics | Chemistry |
|--------|-------------|-------|------|------------|------|---------|----------|

The system expects identification-related columns along with subject columns containing marks.

---

## Canonical Schema Assumptions

Internally, the application standardizes all data into a canonical structure to ensure consistent processing. The expected identification columns are:

- reg_no  
- student_name  
- class  
- term  
- attendance  

Subject columns are automatically identified or manually selected and later transformed into two analytical columns:

- subject  
- marks  

After preprocessing, the dataset is reshaped into long format, where each row represents a single (student, subject) record. This format enables grouping, aggregation, ranking, and visualization.

---

## Data Cleaning and Preprocessing Pipeline

The cleaning pipeline is executed sequentially and is fully automated unless manual mapping is selected.

### Column Normalization

In automatic mode, column names are standardized by converting them to lowercase, trimming whitespace, and resolving naming inconsistencies using an alias mapping system. For example, variations such as “Roll No”, “Registration Number”, or “Roll Number” are mapped to the canonical column name `reg_no`. This reduces dependency on strict column naming conventions.

If the automatic detection does not correctly interpret the dataset, manual mode allows users to explicitly map dataset columns to canonical names and manually select subject columns.

### Wide to Long Transformation

Once identification and subject columns are finalized, the dataset is reshaped using a melt operation. Subject columns are converted into row-level entries, producing a structured dataset where each row corresponds to a student’s performance in a specific subject.

### Marks Cleaning

The marks column undergoes numeric extraction using regular expressions. Any textual noise (e.g., “78 marks”, “90/100”) is cleaned by extracting valid numeric values. Invalid or non-numeric entries are converted to missing values and reported in the cleaning summary.

Marks are assumed to lie within the range 0–100.

### Attendance Cleaning

Attendance values are standardized to percentage format. The system handles:

- Values already in percentage form (e.g., 82, 75%)
- Decimal values representing proportions (e.g., 0.85 converted to 85%)

Invalid or non-numeric attendance values are removed and reported.

### Row Validation and Deduplication

Rows are removed if:

- Registration number or subject is missing  
- Both marks and attendance are missing  
- Duplicate records exist for the same (reg_no, subject, term)  

Duplicate detection ensures that repeated entries do not distort aggregate calculations. A cleaning report summarizes rows before cleaning, rows after cleaning, invalid entries removed, and duplicates detected.

---

## Analytical Features

Once cleaned, the dataset becomes available for analytical processing.

### Subject-Level Summary

For each subject, the system computes:

- Number of unique students  
- Average marks  
- Average attendance  

This provides a subject-wise overview of cohort performance.

### Student-Level Summary

For each student, the system calculates:

- Total subjects taken  
- Average marks across subjects  
- Average attendance  

This supports individual academic evaluation.

### Ranking Mechanism

Students are ranked using dense ranking based on average marks. If multiple students share identical averages, they receive the same rank, and ranking numbers are assigned consecutively without gaps.

### At-Risk Student Detection

A student is classified as at-risk if:

- Their average marks are below the defined passing mark (default: 35), or  
- Their average attendance falls below the defined threshold (default: 75%).  

This dual-condition system ensures that both academic performance and participation are considered.

### Strength and Weakness Classification

At the individual level, subject performance is categorized as:

- Strengths: marks ≥ 75  
- Average: marks between 40 and 74  
- Weaknesses: marks < 40  

This classification provides intuitive academic profiling.

---

## Visualization Layer

All visualizations are implemented using Plotly and integrated within Streamlit dashboards.

The cohort-level dashboard includes:

- Subject performance heatmap  
- Top-ranked students bar chart  
- At-risk scatter plot  
- Subject summary table  

The student-level dashboard includes:

- Subject-wise marks bar chart  
- Marks distribution histogram  
- Performance category donut chart  

These visualizations transform tabular data into interpretable insights.

---

### Cohort Filtering and Dynamic Segmentation
---

The Total Summary dashboard includes an interactive filtering mechanism that allows users to dynamically refine the dataset before performing analysis. This feature enables selective cohort analysis without modifying the original uploaded file.

Users can filter the dataset based on available attributes such as:

- Class
- Term
- Or other categorical identifiers present in the dataset

When a filter is applied, all summary metrics, rankings, visualizations, and at-risk detection logic are recalculated in real time based only on the filtered subset of students.

This ensures that:

- Aggregate statistics reflect only the selected subgroup
- Rankings are computed within the filtered cohort
- Heatmaps show subject distribution specific to the filtered data
- At-risk identification is contextually accurate for that segment

The filtering system operates on the cleaned long-format dataset stored in session state. Since filtering is applied after the preprocessing stage, it does not affect data integrity or cleaning logic. Instead, it acts as a dynamic analytical layer on top of validated data.

This design supports exploratory analysis use cases such as:

- Comparing performance across different classes
- Analyzing term-wise performance differences
- Identifying high-risk groups within specific academic segments
- Evaluating subject difficulty within smaller cohorts

By integrating filtering directly into the dashboard layer, the system enhances interactivity while preserving a reproducible preprocessing pipeline.

---

## Ambiguity Resolution Strategy

The system explicitly addresses real-world data ambiguity through:

- Alias-based column normalization  
- Regex-based numeric extraction  
- Automatic decimal-to-percentage attendance conversion  
- Controlled duplicate removal  
- Manual override mode for non-standard datasets  

By combining automation with optional manual control, the system balances robustness and flexibility.

---

## Assumptions and Limitations

The application assumes:

- Marks are out of 100  
- Attendance is percentage-based  
- Attendance is uniform per student per term  
- The dataset represents a single academic term  

Current limitations include:

- No support for grade-based (A/B/C) systems  
- No multi-term longitudinal comparison  
- No predictive modeling component  
- No automated anomaly detection beyond validation rules  

These limitations can be extended in future iterations.

---

## Technologies Used

- Python  
- Pandas  
- Streamlit  
- Plotly  

---

## Running the Application

Install dependencies and launch the application using:

    pip install -r requirements.txt
    streamlit run app.py

The application will open in a browser interface where datasets can be uploaded and analyzed interactively.

---

## Academic Relevance

This project demonstrates applied knowledge in:

- Data cleaning and preprocessing  
- Schema normalization  
- Handling ambiguity in real-world datasets  
- Data reshaping techniques (wide-to-long transformation)  
- Exploratory Data Analysis (EDA)  
- Dashboard-based reporting  
- Modular software architecture  

It reflects practical implementation of data analytics concepts in an educational domain setting.

---

End of Documentation