import streamlit as st
import pandas as pd

def inject_font():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500&display=swap');
        p, h1, h2, h3, h4, h5, h6, label, button, input, textarea, 
        .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader,
        .stRadio, .stSelectbox, .stMultiSelect, .stNumberInput,
        .stDataFrame, .stMetric, .stExpander {
            font-family: 'Outfit', sans-serif !important;
        }
        [class*="material-icons"], [class*="icon"], i {
            font-family: 'Material Icons' !important;
        }
        </style>
    """, unsafe_allow_html=True)
    

def page_header(label, title, subtitle=None):
    subtitle_html = f'<p style="font-size:15px; color:var(--color-text-secondary); margin:0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="padding: 2rem 0 1.5rem;">
        <p style="font-size:13px; font-weight:500; text-transform:uppercase; 
        letter-spacing:0.08em; color:var(--color-text-tertiary); margin:0 0 8px;">
        {label}
        </p>
        <h1 style="font-size:32px; font-weight:500; color:var(--color-text-primary); 
        margin:0 0 8px; line-height:1.2;">
        {title}
        </h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)

def section_header(title):
    st.markdown(f"""
    <div style="padding: 1rem 0 0.5rem;">
        <p style="font-size:11px; font-weight:500; text-transform:uppercase; 
        letter-spacing:0.08em; color:var(--color-text-tertiary); margin:0 0 6px;">
        {title}
        </p>
        <div style="height:1px; background:var(--color-border-tertiary);"></div>
    </div>
    """, unsafe_allow_html=True)
    
def render_sidebar():
    st.logo(
        "assets/logo.png",
        icon_image="assets/icon.png"
    )
    with st.sidebar:
        st.markdown("## ACADEMIC ENGINE")
        st.caption("AUTOMATED PERFORMANCE ANALYSIS")
        st.divider()
        
        context_area = st.container()
        
        st.divider()
        with st.expander("SYSTEM DOCUMENTATION"):
            st.markdown("- **Input:** CSV or Excel\n- **Processing:** Heuristic Mapping\n- **Export:** PDF/CSV Supported")

        st.markdown(
            "<div style='margin-top: 50%; font-size: 0.8rem; color: gray; opacity: 0.6;'>"
            "SYSTEM v1.0.4<br>"
            "BUILT FOR ACADEMIC CLARITY"
            "</div>",
            unsafe_allow_html=True
        )
    return context_area

def render_cleaning_report(report):
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
        st.markdown("<center><h2 style='font-size:24px; font-weight:500; margin:0 0 -25px;'>Cleaning Report</h2></center>", unsafe_allow_html=True)
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
        <div style="padding: 0 4px 25px;">
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