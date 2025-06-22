
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("enriched_data_logical.csv")

st.set_page_config(layout="wide")
st.title("🌍 Cholera Dashboard - Global Trends and Risk Factors")

# Sidebar Filters
with st.sidebar:
    st.header("🔍 Filters")
    countries = st.multiselect("Select Countries", df["Country"].unique(), default=["Nigeria", "India", "United States"])
    years = st.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
    gender = st.multiselect("Gender", df["Gender"].unique(), default=list(df["Gender"].unique()))
    urban_rural = st.radio("Urban or Rural", ["Urban", "Rural", "Both"], index=2)
    vaccinated = st.multiselect("Vaccinated Against Cholera", df["Vaccinated_Against_Cholera"].unique(), default=["Yes", "No"])

# Apply filters
filtered_df = df[
    (df["Country"].isin(countries)) &
    (df["Year"].between(years[0], years[1])) &
    (df["Gender"].isin(gender)) &
    (df["Vaccinated_Against_Cholera"].isin(vaccinated))
]

if urban_rural != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == urban_rural]

# Layout with no scrolling
col1, col2 = st.columns(2)

# Map: Cholera cases by country
with col1:
    map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    map_fig = px.choropleth(map_df, locations="Country", locationmode="country names",
                            color="Number of reported cases of cholera",
                            title="Cholera Cases by Country", color_continuous_scale="Reds")
    st.plotly_chart(map_fig, use_container_width=True)

# Bar: Deaths by sanitation level
with col2:
    bar_df = filtered_df.groupby("Sanitation_Level")["Number of reported deaths from cholera"].sum().reset_index()
    bar_fig = px.bar(bar_df, x="Sanitation_Level", y="Number of reported deaths from cholera", 
                     title="Deaths by Sanitation Level", color="Sanitation_Level")
    st.plotly_chart(bar_fig, use_container_width=True)

# Second row
col3, col4 = st.columns(2)

# Box plot: Age by access to clean water
with col3:
    box_fig = px.box(filtered_df, x="Access_to_Clean_Water", y="Age", color="Access_to_Clean_Water",
                     title="Age Distribution by Access to Clean Water")
    st.plotly_chart(box_fig, use_container_width=True)

# Stacked bar: Deaths by gender and urban/rural
with col4:
    stack_df = filtered_df.groupby(["Gender", "Urban_or_Rural"])["Number of reported deaths from cholera"].sum().reset_index()
    stack_fig = px.bar(stack_df, x="Gender", y="Number of reported deaths from cholera", color="Urban_or_Rural",
                       title="Cholera Deaths by Gender and Location", barmode="stack")
    st.plotly_chart(stack_fig, use_container_width=True)

# Line chart: Cholera cases over time
line_df = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
line_fig = px.line(line_df, x="Year", y="Number of reported cases of cholera", markers=True,
                   title="Trend of Cholera Cases Over Time")
st.plotly_chart(line_fig, use_container_width=True)
