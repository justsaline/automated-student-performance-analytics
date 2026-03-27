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