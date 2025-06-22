import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Custom CSS to reduce padding and white space
st.markdown("""
    <style>
        /* Sidebar tweaks */
        section[data-testid="stSidebar"] > div {
            padding: 1rem 0.5rem;
        }
        .sidebar-content {
            font-size: 0.85rem;
        }

        /* Map title spacing fix */
        .map-title {
            margin-bottom: -12px;
        }

        /* Global plot container padding fix */
        .plot-container {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title & Description
st.title("🌍 Global Cholera Tracker")
st.markdown("Use the filters on the left to explore reported cholera cases across countries and time.")

# Sidebar filters – keep them compact
with st.sidebar:
    st.markdown("### Filters", help="Filter cholera data by year, gender, region, etc.")
    
    countries = st.multiselect("Select Countries", options=country_list, key="countries")
    year_range = st.slider("Select Year Range", 1949, 2016, (2000, 2016), key="years")
    gender = st.multiselect("Select Gender", ["Male", "Female"], default=["Male", "Female"], key="gender")
    urban = st.radio("Urban or Rural", ["Both", "Urban", "Rural"], index=0, key="urban")
    water = st.selectbox("Access to Clean Water", ["Both", "Yes", "No"], index=0, key="water")
    vaccine = st.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"], index=0, key="vaccine")

# Main dashboard layout
col1, col2 = st.columns([1.3, 1.7])

with col1:
    st.plotly_chart(gender_vaccine_fig, use_container_width=True)
    st.plotly_chart(age_sanitation_fig, use_container_width=True)

with col2:
    st.markdown("<h4 class='map-title'>Reported Cholera Cases (Log Scale)</h4>", unsafe_allow_html=True)
    st.plotly_chart(world_map_fig.update_layout(height=420), use_container_width=True)

    # Move line chart upward by reducing vertical gap
    st.markdown("<div style='margin-top: -30px'></div>", unsafe_allow_html=True)
    st.plotly_chart(trend_over_time_fig.update_layout(height=250), use_container_width=True)
