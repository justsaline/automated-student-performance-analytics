import pandas as pd
import plotly.express as px
from src.schema import MARKS_MIN, MARKS_MAX,ATTENDANCE_MIN, ATTENDANCE_MAX,PASS_MARK

def student_subject_marks_bar(student_subject_df):
    fig = px.bar(student_subject_df, x='subject', y='marks',
                 text='marks', title = 'Student Subject Marks',
                 labels = {'marks': 'Marks', 'subject': 'Subject'},
                 color = 'subject')
    
    fig.update_traces(texttemplate="%{text:.2f}")
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis_range = [0,100], showlegend = False)
    return fig

def student_marks_distribution(student_subject_df):
    fig = px.histogram(
        student_subject_df,
        x="marks",
        nbins=5,
        title="Marks Distribution",
        labels={"marks": "Marks"},
    )

    fig.add_vline(
        x=PASS_MARK,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Pass Mark ({PASS_MARK})",
        annotation_position="top"
    )

    fig.update_layout(
        xaxis_range=[0, 100],
        yaxis_title="Number of Subjects",
        bargap=0.25,
        height=350
    )
    return fig

def performance_category_donut(perf_dict):
    df = pd.DataFrame({
        'category': ["Strengths", "Average", "Weaknesses"],
        'count': [
            len(perf_dict['strengths']),
            len(perf_dict['average']),
            len(perf_dict['weaknesses'])
        ]
    })
    color_map = {
        "Strengths": "#2ECC71",     # Green
        "Average": "#F1C40F",       # Amber
        "Weaknesses": "#E74C3C"     # Red
    }
    fig = px.pie(
        df,
        names='category',
        values='count',
        hole=0.5,
        title='Performance Breakdown',
        color='category',
        color_discrete_map=color_map
    )
    fig.update_layout(height=350)
    return fig

def subject_performance_heatmap(cleaned_df):
    df = cleaned_df.copy()

    df = df.dropna(subset=["marks", "subject", "reg_no"])

    bins = [0, 40, 60, 75, 90, 100]
    labels = ["0–40", "41–60", "61–75", "76–90", "91–100"]

    df["score_band"] = pd.cut(
        df["marks"],
        bins=bins,
        labels=labels,
        include_lowest=True)

    heatmap_df = (
        df.groupby(["score_band", "subject"])["reg_no"]
        .nunique()
        .reset_index(name="student_count"))

    pivot_df = heatmap_df.pivot(
        index="score_band",
        columns="subject",
        values="student_count"
    ).fillna(0)

    fig = px.imshow(
        pivot_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Viridis",
        labels={
            "x": "Subject",
            "y": "Score Range",
            "color": "Number of Students"
        })
    fig.update_layout(
        title="Subject-wise Performance Distribution",)

    return fig

def top_students_bar(rank_df, top_n=10):
    df = rank_df.head(top_n).copy()
    df = df.sort_values("avg_marks")
    
    fig = px.bar(df, x='avg_marks', y = 'student_name',
                 orientation = 'h', text = "avg_marks", 
                title = f'Top {top_n} Students by Average Marks',
                labels = {'avg_marks': 'Average Marks', 'student_name': 'Student'},
                color="avg_marks",color_continuous_scale="Tealgrn")

    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        xaxis_range=[0, 100],
        height=380,
        showlegend=False,
        yaxis_title=None,
    )

    return fig
    
def at_risk_scatter(at_risk_df, attendance_threshold = 75):
    fig = px.scatter(at_risk_df, x='avg_attendance', y='avg_marks',
                    hover_data=['student_name', 'reg_no'],
                    labels={
                    "avg_attendance": "Average Attendance (%)",
                    "avg_marks": "Average Marks"
                    },
                    title="At-Risk Students: Marks vs Attendance")
    fig.add_vline(
    x=attendance_threshold,
    line_dash="dash",
    line_color="orange",
    annotation_text=f"Attendance Threshold ({attendance_threshold}%)",
    annotation_position="top right"
    )
    fig.add_hline(
    y=PASS_MARK,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Passing Mark ({PASS_MARK})",
    annotation_position="top right"
    )

    fig.update_layout(
        xaxis_range=[ATTENDANCE_MIN, ATTENDANCE_MAX],
        yaxis_range=[MARKS_MIN, MARKS_MAX],
        height=380
    )

    return fig