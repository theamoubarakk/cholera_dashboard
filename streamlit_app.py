import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

import streamlit as st
import plotly.express as px

# Clean layout CSS
st.markdown("""
    <style>
        section[data-testid="stSidebar"] > div {
            padding: 0.5rem;
        }
        .map-title {
            margin-bottom: -10px;
        }
        .element-container {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🌍 Global Cholera Tracker")

# MAIN LAYOUT
col_left, col_right = st.columns([1.1, 1.9])  # More space for the right side (Map + Trend)

with col_left:
    st.plotly_chart(gender_vaccine_fig.update_layout(height=220, margin=dict(t=30, b=0, l=0, r=0)), use_container_width=True)
    st.plotly_chart(age_sanitation_fig.update_layout(height=220, margin=dict(t=20, b=0, l=0, r=0)), use_container_width=True)
    st.plotly_chart(correlation_fig.update_layout(height=220, margin=dict(t=20, b=0, l=0, r=0)), use_container_width=True)

with col_right:
    st.markdown("<h4 class='map-title'>Reported Cholera Cases (Log Scale)</h4>", unsafe_allow_html=True)
    st.plotly_chart(world_map_fig.update_layout(height=320, margin=dict(t=10, b=10, l=0, r=0)), use_container_width=True)
    st.markdown("<div style='margin-top: -20px'></div>", unsafe_allow_html=True)
    st.plotly_chart(trend_over_time_fig.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0)), use_container_width=True)
