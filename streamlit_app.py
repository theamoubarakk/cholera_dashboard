import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load the dataset
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# --- Data Cleaning ---
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce").fillna(0)
df["Number of reported deaths from cholera"] = pd.to_numeric(df["Number of reported deaths from cholera"], errors="coerce").fillna(0)

# Compute fatality rate if missing
def compute_fatality(row):
    if pd.isna(row["Cholera case fatality rate"]):
        cases = row["Number of reported cases of cholera"]
        deaths = row["Number of reported deaths from cholera"]
        return round(deaths / cases, 4) if cases > 0 else 0
    return row["Cholera case fatality rate"]
df["Cholera case fatality rate"] = df.apply(compute_fatality, axis=1)

# --- Sidebar Filters ---
st.sidebar.header("Filters")
countries = st.sidebar.multiselect("Select Countries", options=df["Country"].dropna().unique())
year_range = st.sidebar.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
genders = st.sidebar.multiselect("Select Gender", ["Male", "Female"], default=["Male", "Female"])
urban_rural = st.sidebar.radio("Urban or Rural", ["Both", "Urban", "Rural"])
access_clean = st.sidebar.selectbox("Access to Clean Water", ["Both", "Yes", "No"])
vaccinated = st.sidebar.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"])

# --- Filter Data ---
filtered = df[
    (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1]) &
    (df["Gender"].isin(genders))
]
if countries: filtered = filtered[filtered["Country"].isin(countries)]
if urban_rural != "Both": filtered = filtered[filtered["Urban_or_Rural"] == urban_rural]
if access_clean != "Both": filtered = filtered[filtered["Access_to_Clean_Water"] == access_clean]
if vaccinated != "Both": filtered = filtered[filtered["Vaccinated_Against_Cholera"] == vaccinated]

# --- Map ---
map_df = filtered.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
map_df["Log_Cases"] = map_df["Number of reported cases of cholera"].apply(lambda x: np.log10(x) if x > 0 else 0)
fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                        color="Log_Cases", title="Reported Cholera Cases (Log Scale)",
                        color_continuous_scale="OrRd")

# --- Time Series ---
trend = filtered.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
fig_trend = px.line(trend, x="Year", y="Number of reported cases of cholera", markers=True,
                    title="Cholera Cases Over Time")

# --- Stacked Bar: Gender × Vaccinated ---
stacked = filtered.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
fig_stacked = px.bar(stacked, x="Gender", y="Number of reported cases of cholera",
                     color="Vaccinated_Against_Cholera", barmode="stack",
                     title="Cases by Gender and Vaccination Status")

# --- Boxplot: Age vs Sanitation Level ---
fig_box = px.box(filtered, x="Sanitation_Level", y="Age", title="Age Distribution by Sanitation Level")

# --- Layout on 1 Page ---
st.set_page_config(layout="wide")
st.title("🌍 Global Cholera Tracker")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_map, use_container_width=True)
with col2:
    st.plotly_chart(fig_trend, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_stacked, use_container_width=True)
with col4:
    st.plotly_chart(fig_box, use_container_width=True)
