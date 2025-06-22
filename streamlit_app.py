import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------
# ✅ Load cleaned data
# ----------------------------
df = pd.read_csv("enriched_data_logical_cleaned.csv")
df["Country"] = df["Country"].str.strip()
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce").fillna(0)

# ----------------------------
# ✅ Streamlit setup
# ----------------------------
st.set_page_config(layout="wide")
st.title("🌍 Global Cholera Tracker")
st.markdown("Use the filters on the left to explore **reported cholera cases** across countries and time.")

# ----------------------------
# ✅ Sidebar filters
# ----------------------------
st.sidebar.header("🔍 Filters")

selected_countries = st.sidebar.multiselect(
    "Select Countries", sorted(df["Country"].unique()), default=sorted(df["Country"].unique())
)

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=(2000, 2016)
)

selected_genders = st.sidebar.multiselect(
    "Select Gender", df["Gender"].unique(), default=list(df["Gender"].unique())
)

selected_urban_rural = st.sidebar.radio(
    "Urban or Rural", ["Both", "Urban", "Rural"], index=0
)

selected_water = st.sidebar.multiselect(
    "Access to Clean Water", df["Access_to_Clean_Water"].unique(), default=list(df["Access_to_Clean_Water"].unique())
)

selected_vaccine = st.sidebar.multiselect(
    "Vaccinated Against Cholera", df["Vaccinated_Against_Cholera"].unique(), default=list(df["Vaccinated_Against_Cholera"].unique())
)

selected_sanitation = st.sidebar.multiselect(
    "Sanitation Level", df["Sanitation_Level"].unique(), default=list(df["Sanitation_Level"].unique())
)

# ----------------------------
# ✅ Apply filters to dataset
# ----------------------------
filtered_df = df[
    (df["Country"].isin(selected_countries)) &
    (df["Year"].between(year_range[0], year_range[1])) &
    (df["Gender"].isin(selected_genders)) &
    (df["Access_to_Clean_Water"].isin(selected_water)) &
    (df["Vaccinated_Against_Cholera"].isin(selected_vaccine)) &
    (df["Sanitation_Level"].isin(selected_sanitation))
]

if selected_urban_rural != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == selected_urban_rural]

# ----------------------------
# ✅ Create map data
# ----------------------------
map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
map_df["Log_Cases"] = np.log1p(map_df["Number of reported cases of cholera"])

# ----------------------------
# ✅ Draw interactive map
# ----------------------------
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

st.plotly_chart(fig, use_container_width=True)
