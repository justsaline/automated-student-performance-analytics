import pandas as pd

def subject_summary(df):
    summary = df.groupby('subject').agg(students = ('reg_no', 'nunique'), avg_marks = ('marks', 'mean'), avg_attendance = ('attendance', 'mean')).reset_index()
    return summary

def attendance_summary(df):
    summary = df.groupby('subject').agg(avg_attendance = ('attendance', 'mean'), attendance_records = ('attendance', 'count')).reset_index()
    return summary

def student_summary(df):
    summary = (
        df.groupby('reg_no')
        .agg(
            student_name=('student_name', 'first'),
            class_=('class', 'first'),
            term=('term', 'first'),
            subjects_taken=('subject', 'nunique'),
            avg_marks=('marks', 'mean'),
            avg_attendance=('attendance', 'mean')
        ).reset_index()
    )
    return summary

def at_risk_students(df,marks_threshold=40,attendance_threshold=75):

    stats = student_summary(df)

    at_risk = stats[(stats['avg_marks'] < marks_threshold) | (stats['avg_attendance'] < attendance_threshold)]
    return at_risk