import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load cleaned dataset
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# Handle missing and incorrect types
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce").fillna(0)
df["Number of reported deaths from cholera"] = pd.to_numeric(df["Number of reported deaths from cholera"], errors="coerce").fillna(0)

# Fix fatality rate
def compute_fatality(row):
    if pd.isna(row["Cholera case fatality rate"]):
        cases = row["Number of reported cases of cholera"]
        deaths = row["Number of reported deaths from cholera"]
        return round(deaths / cases, 4) if cases > 0 else 0
    return row["Cholera case fatality rate"]
df["Cholera case fatality rate"] = df.apply(compute_fatality, axis=1)

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_countries = st.sidebar.multiselect("Select Countries", sorted(df["Country"].dropna().unique()))
year_range = st.sidebar.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
selected_gender = st.sidebar.multiselect("Select Gender", df["Gender"].dropna().unique(), default=df["Gender"].dropna().unique())
urban_filter = st.sidebar.radio("Urban or Rural", ["Both", "Urban", "Rural"])
water_filter = st.sidebar.selectbox("Access to Clean Water", ["Both", "Yes", "No"])
vaccine_filter = st.sidebar.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"])

# Apply filters
filtered_df = df[
    (df["Year"] >= year_range[0]) & 
    (df["Year"] <= year_range[1]) & 
    (df["Gender"].isin(selected_gender))
]
if selected_countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_countries)]
if urban_filter != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == urban_filter]
if water_filter != "Both":
    filtered_df = filtered_df[filtered_df["Access_to_Clean_Water"] == water_filter]
if vaccine_filter != "Both":
    filtered_df = filtered_df[filtered_df["Vaccinated_Against_Cholera"] == vaccine_filter]

# Layout
st.markdown("## 🌍 Global Cholera Tracker")
st.markdown("Use the filters on the left to explore **reported cholera cases** across countries and time.")

# -------- ROW 1: MAP & BAR --------
col1, col2 = st.columns([1.3, 1])

# Map
with col1:
    map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    map_df["Log_Cases"] = map_df["Number of reported cases of cholera"].apply(lambda x: np.log10(x + 1))
    st.markdown("#### Reported Cholera Cases (Log Scale)")
    map_fig = px.choropleth(map_df, locations="Country", locationmode="country names",
                            color="Log_Cases", color_continuous_scale="OrRd")
    st.plotly_chart(map_fig, use_container_width=True)

# Bar: Sanitation Level
with col2:
    st.markdown("#### Deaths by Sanitation Level")
    bar_df = filtered_df.groupby("Sanitation_Level")["Number of reported deaths from cholera"].sum().reset_index()
    fig_bar = px.bar(bar_df, x="Sanitation_Level", y="Number of reported deaths from cholera", color="Sanitation_Level")
    st.plotly_chart(fig_bar, use_container_width=True)

# -------- ROW 2: DONUTS --------
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### Access to Clean Water")
    donut1 = filtered_df["Access_to_Clean_Water"].value_counts().reset_index()
    donut1.columns = ["Access", "Count"]
    fig_donut1 = px.pie(donut1, values="Count", names="Access", hole=0.55,
                        color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig_donut1, use_container_width=True)

with col4:
    st.markdown("#### Vaccinated Against Cholera")
    donut2 = filtered_df["Vaccinated_Against_Cholera"].value_counts().reset_index()
    donut2.columns = ["Vaccinated", "Count"]
    fig_donut2 = px.pie(donut2, values="Count", names="Vaccinated", hole=0.55,
                        color_discrete_sequence=px.colors.sequential.Greens)
    st.plotly_chart(fig_donut2, use_container_width=True)

# -------- ROW 3: BOXPLOT & REGION --------
col5, col6 = st.columns(2)

with col5:
    st.markdown("#### Age Distribution by Location")
    fig_age = px.box(filtered_df, x="Urban_or_Rural", y="Age", color="Urban_or_Rural")
    st.plotly_chart(fig_age, use_container_width=True)

with col6:
    st.markdown("#### Cholera Deaths by Gender and Region")
    reg_df = filtered_df.groupby(["WHO Region", "Gender"])["Number of reported deaths from cholera"].sum().reset_index()
    fig_deaths = px.bar(reg_df, x="WHO Region", y="Number of reported deaths from cholera",
                        color="Gender", barmode="group")
    st.plotly_chart(fig_deaths, use_container_width=True)
