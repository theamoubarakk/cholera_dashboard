import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Load data
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# Clean & compute
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce").fillna(0)
df["Number of reported deaths from cholera"] = pd.to_numeric(df["Number of reported deaths from cholera"], errors="coerce").fillna(0)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0).astype(int)

df["Cholera case fatality rate"] = df.apply(lambda row: round(row["Number of reported deaths from cholera"] / row["Number of reported cases of cholera"], 4)
                                            if pd.isna(row["Cholera case fatality rate"]) and row["Number of reported cases of cholera"] > 0
                                            else row["Cholera case fatality rate"], axis=1)

# Sidebar filters
st.sidebar.header("Filters")
countries = st.sidebar.multiselect("Select Countries", options=df["Country"].dropna().unique())
year_range = st.sidebar.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
genders = st.sidebar.multiselect("Select Gender", options=df["Gender"].dropna().unique(), default=df["Gender"].dropna().unique())
urban_rural = st.sidebar.radio("Urban or Rural", ["Both", "Urban", "Rural"])
clean_water = st.sidebar.selectbox("Access to Clean Water", ["Both", "Yes", "No"])
vaccinated = st.sidebar.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"])

# Apply filters
filtered_df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
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
st.markdown("<h1 style='text-align:center;'>🌍 Global Cholera Tracker</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align:center;'>Explore trends in cholera cases, deaths, and key demographic factors worldwide</h5>", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([1.2, 1])
with col1:
    df_map = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    df_map["Log_Cases"] = df_map["Number of reported cases of cholera"].apply(lambda x: np.log10(x) if x > 0 else 0)
    fig_map = px.choropleth(df_map, locations="Country", locationmode="country names",
                            color="Log_Cases", title="Reported Cholera Cases (Log Scale)",
                            color_continuous_scale="OrRd")
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    trend = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    fig_trend = px.line(trend, x="Year", y="Number of reported cases of cholera",
                        title="Cholera Cases Over Time", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

col3, col4 = st.columns([1, 1])
with col3:
    stacked = filtered_df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
    fig_stack = px.bar(stacked, x="Gender", y="Number of reported cases of cholera",
                       color="Vaccinated_Against_Cholera", barmode="stack",
                       title="Cases by Gender and Vaccination")
    st.plotly_chart(fig_stack, use_container_width=True)

with col4:
    if "Sanitation_Level" in filtered_df.columns and "Age" in filtered_df.columns:
        fig_box = px.box(filtered_df, x="Sanitation_Level", y="Age",
                         title="Age Distribution by Sanitation Level")
        st.plotly_chart(fig_box, use_container_width=True)
