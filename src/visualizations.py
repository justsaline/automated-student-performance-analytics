import pandas as pd
import plotly.express as px

def student_subject_marks_bar(student_subject_df):
    fig = px.bar(student_subject_df, x='subject', y='marks',
                 text='marks', title = 'Student Subject Marks',
                 labels = {'marks': 'Marks', 'subject': 'Subject'},
                 color = 'subject')
    
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis_range = [0,100], showlegend = False, height = 400)
    return fig

def student_marks_distribution(student_subject_df):
    fig = px.histogram(student_subject_df, x='marks', nbins = 5,
                       title = 'Marks distribution',
                       labels = {'marks':'Marks'})
    fig.update_layout(xaxis_range = [0,100], height = 350)
    return fig

def performance_category_donut(perf_dict):
    df = pd.DataFrame({
        'category': ["Strengths", "Average", "Weaknesses"],
        'count': [len(perf_dict['strengths']),
                  len(perf_dict['average']),
                  len(perf_dict['weaknesses'])]
        })
    fig = px.pie(df, names='category', values='count', hole = 0.5, title = 'Performance Breakdown')
    fig.update_layout(height = 350)
    
    return fig