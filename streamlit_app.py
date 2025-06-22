import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Load and clean data
df = pd.read_csv("enriched_data_logical.csv")
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce")

# Sidebar filters (optional enhancement)
with st.sidebar:
    st.title("Filters")
    country_list = df["Country"].dropna().unique().tolist()
    st.multiselect("Select Countries", options=country_list)
    st.slider("Select Year Range", min_value=int(df["Year"].min()), max_value=int(df["Year"].max()), value=(2000, 2016))
    st.multiselect("Select Gender", ["Male", "Female"], default=["Male", "Female"])
    st.radio("Urban or Rural", ["Both", "Urban", "Rural"], index=0)
    st.selectbox("Access to Clean Water", ["Both", "Yes", "No"])
    st.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"])

# Inject CSS for styling
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        h1 {
            font-size: 32px !important;
        }
        h2, h3, h4 {
            font-size: 18px !important;
            margin-bottom: 0.2rem;
        }
        .element-container {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }
        .map-title {
            margin-bottom: -12px;
        }
    </style>
""", unsafe_allow_html=True)

# Page title
st.title("🌍 Global Cholera Tracker")
st.markdown("Use the filters on the left to explore reported cholera cases across countries and time.")

# Create charts
gender_vaccine_fig = px.bar(
    df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index(),
    x="Gender", y="Number of reported cases of cholera", color="Vaccinated_Against_Cholera",
    barmode="stack", title="Cases by Gender and Vaccination Status"
)

age_sanitation_fig = px.box(
    df, x="Sanitation_Level", y="Age", color="Sanitation_Level",
    title="Age Distribution by Sanitation Level"
)

trend_df = df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
trend_over_time_fig = px.line(
    trend_df, x="Year", y="Number of reported cases of cholera", title="Cholera Cases Over Time"
)

map_df = df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
map_df["Log_Cases"] = np.log10(map_df["Number of reported cases of cholera"] + 1)
world_map_fig = px.choropleth(
    map_df, locations="Country", locationmode="country names", color="Log_Cases",
    color_continuous_scale="Reds", title="Reported Cholera Cases (Log Scale)"
)

# Layout: 3 small left charts, 2 larger right charts
col1, col2 = st.columns([1.1, 1.9])

with col1:
    st.plotly_chart(gender_vaccine_fig.update_layout(height=210, margin=dict(t=30, b=0, l=0, r=0)), use_container_width=True)
    st.plotly_chart(age_sanitation_fig.update_layout(height=210, margin=dict(t=20, b=0, l=0, r=0)), use_container_width=True)
    # Optional: insert a 3rd chart here (e.g. sanitation-vaccination)
    st.empty()  # placeholder

with col2:
    st.markdown("<h4 class='map-title'>Reported Cholera Cases (Log Scale)</h4>", unsafe_allow_html=True)
    st.plotly_chart(world_map_fig.update_layout(height=330, margin=dict(t=10, b=10, l=0, r=0)), use_container_width=True)
    st.markdown("<div style='margin-top: -20px'></div>", unsafe_allow_html=True)
    st.plotly_chart(trend_over_time_fig.update_layout(height=270, margin=dict(t=10, b=0, l=0, r=0)), use_container_width=True)

