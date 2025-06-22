import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Load the dataset (update path if needed)
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# --- Sidebar Filters ---
st.sidebar.title("Filters")
countries = st.sidebar.multiselect("Select Countries", sorted(df["Country"].dropna().unique()))
year_range = st.sidebar.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
genders = st.sidebar.multiselect("Select Gender", df["Gender"].dropna().unique(), default=list(df["Gender"].dropna().unique()))
location = st.sidebar.radio("Urban or Rural", ["Both", "Urban", "Rural"], index=0)
water_access = st.sidebar.selectbox("Access to Clean Water", ["Both", "Yes", "No"])
vaccinated = st.sidebar.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"])

# --- Filter Data ---
filtered_df = df.copy()

if countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(countries)]
filtered_df = filtered_df[(filtered_df["Year"] >= year_range[0]) & (filtered_df["Year"] <= year_range[1])]
if genders:
    filtered_df = filtered_df[filtered_df["Gender"].isin(genders)]
if location != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == location]
if water_access != "Both":
    filtered_df = filtered_df[filtered_df["Access_to_Clean_Water"] == water_access]
if vaccinated != "Both":
    filtered_df = filtered_df[filtered_df["Vaccinated_Against_Cholera"] == vaccinated]

# --- Layout: Title ---
st.title("\U0001F30E Global Cholera Tracker")
st.markdown("Use the filters on the left to explore reported cholera cases across countries and time.")

# --- Layout Columns ---
col1, col2 = st.columns([1, 1])

# --- Choropleth Map (Top Right) ---
with col1:
    map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    map_df["Log_Cases"] = np.log10(map_df["Number of reported cases of cholera"] + 1)
    fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                            color="Log_Cases", color_continuous_scale="Reds",
                            title="Reported Cholera Cases (Log Scale)")
    fig_map.update_layout(height=300)
    st.plotly_chart(fig_map, use_container_width=True)

# --- Line Chart: Cholera Over Time ---
with col2:
    trend = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    fig_trend = px.line(trend, x="Year", y="Number of reported cases of cholera", markers=True,
                        title="Cholera Cases Over Time")
    fig_trend.update_layout(height=250)
    st.plotly_chart(fig_trend, use_container_width=True)

# --- Left Column for 2 stacked plots ---
left1, left2 = st.columns([1, 1])

with left1:
    stacked_bar = filtered_df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
    fig_bar = px.bar(stacked_bar, x="Gender", y="Number of reported cases of cholera", color="Vaccinated_Against_Cholera",
                     barmode="stack", title="Cases by Gender and Vaccination Status")
    fig_bar.update_layout(height=280)
    st.plotly_chart(fig_bar, use_container_width=True)

with left2:
    box_data = filtered_df[["Sanitation_Level", "Age"]].dropna()
    fig_box = px.box(box_data, x="Sanitation_Level", y="Age", color="Sanitation_Level",
                     title="Age Distribution by Sanitation Level")
    fig_box.update_layout(height=280, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)
