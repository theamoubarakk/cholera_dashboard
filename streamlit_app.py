import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("enriched_data_logical.csv")
df["Country"] = df["Country"].str.strip()

# Aggregate cholera cases by country
map_df = df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()

# Convert to numeric (some values may be strings)
map_df["Number of reported cases of cholera"] = pd.to_numeric(
    map_df["Number of reported cases of cholera"], errors="coerce"
).fillna(0).clip(upper=1_000_000)

# Create choropleth map
fig = px.choropleth(
    map_df,
    locations="Country",
    locationmode="country names",
    color="Number of reported cases of cholera",
    title="Global Cholera Cases Map",
    color_continuous_scale="OrRd",
    template="plotly_white",
    hover_name="Country"
)

fig.update_geos(
    projection_type="natural earth",
    showcountries=True,
    showcoastlines=True,
    showland=True,
    fitbounds="locations"
)

# Display map in Streamlit
st.set_page_config(layout="wide")
st.title("🗺️ Global Cholera Tracker")
st.plotly_chart(fig, use_container_width=True)
