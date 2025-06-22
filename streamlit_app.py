import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------------
# ✅ Load and clean the dataset
# -------------------------------
df = pd.read_csv("enriched_data_logical.csv")
df["Country"] = df["Country"].str.strip()

# Convert cholera case values to numeric and handle errors
df["Number of reported cases of cholera"] = pd.to_numeric(
    df["Number of reported cases of cholera"], errors="coerce"
).fillna(0)

# -------------------------------
# ✅ Page configuration
# -------------------------------
st.set_page_config(layout="wide")
st.title("🌍 Global Cholera Tracker")
st.markdown("This interactive map shows the **total number of reported cholera cases** by country using a logarithmic color scale for clarity.")

# -------------------------------
# ✅ Aggregate cases by country
# -------------------------------
map_df = df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()

# Log-scale transformation for better shading
map_df["Log_Cases"] = np.log1p(map_df["Number of reported cases of cholera"])

# -------------------------------
# ✅ Build interactive choropleth map
# -------------------------------
fig = px.choropleth(
    map_df,
    locations="Country",
    locationmode="country names",
    color="Log_Cases",
    hover_name="Country",
    hover_data={"Number of reported cases of cholera": True, "Log_Cases": False},
    color_continuous_scale="OrRd",
    title="Reported Cholera Cases (Log Scale)",
    template="plotly_white"
)

fig.update_geos(
    projection_type="natural earth",
    showcountries=True,
    showcoastlines=True,
    showland=True,
    fitbounds="locations"
)

# -------------------------------
# ✅ Display the map
# -------------------------------
st.plotly_chart(fig, use_container_width=True)
