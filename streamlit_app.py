import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load the dataset
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# Clean and prepare
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce").fillna(0)
df["Number of reported deaths from cholera"] = pd.to_numeric(df["Number of reported deaths from cholera"], errors="coerce").fillna(0)

def compute_fatality(row):
    if pd.isna(row["Cholera case fatality rate"]):
        cases = row["Number of reported cases of cholera"]
        deaths = row["Number of reported deaths from cholera"]
        return round(deaths / cases, 4) if cases > 0 else 0
    return row["Cholera case fatality rate"]
df["Cholera case fatality rate"] = df.apply(compute_fatality, axis=1)

# Streamlit Layout Settings
st.set_page_config(layout="wide")
st.markdown("<h1 style='margin-bottom: 0;'>🌍 Global Cholera Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='margin-top: 0;'>Use the filters on the left to explore <b>reported cholera cases</b> across countries and time.</p>", unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.header("Filters")
countries = st.sidebar.multiselect("Select Countries", options=df["Country"].dropna().unique())
year_range = st.sidebar.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
genders = st.sidebar.multiselect("Select Gender", ["Male", "Female"], default=["Male", "Female"])
urban_rural = st.sidebar.radio("Urban or Rural", ["Both", "Urban", "Rural"])
access_clean = st.sidebar.selectbox("Access to Clean Water", ["Both", "Yes", "No"])
vaccinated = st.sidebar.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"])

# Filter Data
filtered = df[
    (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1]) &
    (df["Gender"].isin(genders))
]
if countries: filtered = filtered[filtered["Country"].isin(countries)]
if urban_rural != "Both": filtered = filtered[filtered["Urban_or_Rural"] == urban_rural]
if access_clean != "Both": filtered = filtered[filtered["Access_to_Clean_Water"] == access_clean]
if vaccinated != "Both": filtered = filtered[filtered["Vaccinated_Against_Cholera"] == vaccinated]

# Graph 1: Map
map_df = filtered.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
map_df["Log_Cases"] = map_df["Number of reported cases of cholera"].apply(lambda x: np.log10(x) if x > 0 else 0)
fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                        color="Log_Cases", title="Reported Cholera Cases (Log Scale)",
                        color_continuous_scale="OrRd")
fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))

# Graph 2: Time Series
trend = filtered.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
fig_trend = px.line(trend, x="Year", y="Number of reported cases of cholera", markers=True,
                    title="Cholera Cases Over Time")
fig_trend.update_layout(margin=dict(l=0, r=0, t=40, b=0))

# Graph 3: Stacked Bar
stacked = filtered.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
fig_stacked = px.bar(stacked, x="Gender", y="Number of reported cases of cholera",
                     color="Vaccinated_Against_Cholera", barmode="stack",
                     title="Cases by Gender and Vaccination Status")
fig_stacked.update_layout(margin=dict(l=0, r=0, t=40, b=0))

# Graph 4: Boxplot
fig_box = px.box(filtered, x="Sanitation_Level", y="Age", title="Age Distribution by Sanitation Level")
fig_box.update_layout(margin=dict(l=0, r=0, t=40, b=0))

# Arrange all charts in a grid (2x2) for no scrolling
top_row = st.columns([1, 1])
bottom_row = st.columns([1, 1])

with top_row[0]:
    st.plotly_chart(fig_map, use_container_width=True)
with top_row[1]:
    st.plotly_chart(fig_trend, use_container_width=True)

with bottom_row[0]:
    st.plotly_chart(fig_stacked, use_container_width=True)
with bottom_row[1]:
    st.plotly_chart(fig_box, use_container_width=True)
