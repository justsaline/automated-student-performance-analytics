import pandas as pd
from src.schema import PASS_MARK

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
            avg_attendance=('attendance', lambda x: x.mean(skipna=True))
        ).reset_index()
    )
    return summary

def at_risk_students(df,PASS_MARK,attendance_threshold=75):

    stats = student_summary(df)

    at_risk = stats[(stats['avg_marks'] < PASS_MARK) | (stats['avg_attendance'] < attendance_threshold)]
    return at_risk

def rank_students(df):
    
    summary = student_summary(df)
    summary['rank'] = summary['avg_marks'].rank(ascending= False, method='dense').astype(int)
    
    return  summary.sort_values('rank')

def student_subject_analysis(df, reg_no):
    
    student_df = df[df['reg_no'] == reg_no]
    
    if student_df.empty:
        raise ValueError(f"No data found for reg_no: {reg_no}")
    
    student_perf = student_df[['subject', 'marks']].sort_values('subject').reset_index(drop=True)
    
    return student_perf

def student_strengths_weaknesses(df, reg_no):
    
    perf = student_subject_analysis(df, reg_no)
    
    strengths = perf[perf['marks']>=75]['subject'].tolist()
    weaknesses = perf[perf['marks']<40]['subject'].tolist()
    average = perf[(perf['marks'] >= 40) & (perf['marks'] < 75)]['subject'].tolist()
    
    return {'strengths': strengths,'average': average,'weaknesses': weaknesses}

def student_overview(df, reg_no):
    
    summary = student_summary(df)
    
    student = summary[summary['reg_no']==reg_no]
    if student.empty:
        raise ValueError(f"No data found for reg_no: {reg_no}")
    
    return student.iloc[0].to_dict()