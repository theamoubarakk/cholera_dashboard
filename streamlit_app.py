import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Load CSV
df = pd.read_csv("enriched_data_logical.csv")

# Fix missing values and column names
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce").fillna(0)
df["Log_Cases"] = df["Number of reported cases of cholera"].apply(lambda x: np.log10(x) if x > 0 else 0)

# Sidebar filters
st.sidebar.header("Filters")
countries = st.sidebar.multiselect("Select Countries", options=df["Country"].unique())
years = st.sidebar.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
genders = st.sidebar.multiselect("Select Gender", options=df["Gender"].dropna().unique(), default=list(df["Gender"].dropna().unique()))
urban_rural = st.sidebar.radio("Urban or Rural", ["Both", "Urban", "Rural"])
clean_water = st.sidebar.selectbox("Access to Clean Water", ["Both", "Yes", "No"])
vaccinated = st.sidebar.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"])

# Filtering
filtered_df = df.copy()
filtered_df = filtered_df[filtered_df["Year"].between(years[0], years[1])]
if countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(countries)]
if genders:
    filtered_df = filtered_df[filtered_df["Gender"].isin(genders)]
if urban_rural != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == urban_rural]
if clean_water != "Both":
    filtered_df = filtered_df[filtered_df["Access_to_Clean_Water"] == clean_water]
if vaccinated != "Both":
    filtered_df = filtered_df[filtered_df["Vaccinated_Against_Cholera"] == vaccinated]

# Title
st.markdown("<h2 style='text-align:center;'>🌍 Global Cholera Tracker</h2>", unsafe_allow_html=True)

# Layout: Map top-right, Trend below it, others on left
col_left, col_right = st.columns([1, 1.2])

with col_right:
    st.markdown("<h4>Reported Cholera Cases (Log Scale)</h4>", unsafe_allow_html=True)
    fig_map = px.choropleth(filtered_df, locations="Country", locationmode="country names",
                            color="Log_Cases", hover_name="Country",
                            color_continuous_scale="Reds")
    fig_map.update_layout(height=320, margin=dict(t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("<h4>Cholera Cases Over Time</h4>", unsafe_allow_html=True)
    trend_df = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    fig_trend = px.line(trend_df, x="Year", y="Number of reported cases of cholera", markers=True)
    fig_trend.update_layout(height=220, margin=dict(t=10, b=10))
    st.plotly_chart(fig_trend, use_container_width=True)

with col_left:
    st.markdown("<h4>Cases by Gender and Vaccination Status</h4>", unsafe_allow_html=True)
    bar_df = filtered_df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
    fig_bar = px.bar(bar_df, x="Gender", y="Number of reported cases of cholera", color="Vaccinated_Against_Cholera",
                     barmode="stack", height=250)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<h4>Age Distribution by Sanitation Level</h4>", unsafe_allow_html=True)
    fig_box = px.box(filtered_df, x="Sanitation_Level", y="Age", color="Sanitation_Level")
    fig_box.update_layout(height=250)
    st.plotly_chart(fig_box, use_container_width=True)
