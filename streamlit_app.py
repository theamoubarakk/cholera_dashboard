import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# --- Page Configuration (Set this at the top) ---
st.set_page_config(layout="wide") # Use the full page width for a better layout

# Load the dataset (update path if needed)
# To avoid reloading data on every interaction, use st.cache_data
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

df = load_data("enriched_data_logical_cleaned.csv")

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

# Apply filters only if selections are made
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

# --- Main Page Title ---
st.title("\U0001F30E Global Cholera Tracker")
st.markdown("Use the filters on the left to explore reported cholera cases across countries and time.")

# --- NEW LAYOUT SECTION ---
# Create two main columns. The right column is wider to hold the map.
# The ratio [2, 3] gives 2/5 of the space to the left and 3/5 to the right.
left_col, right_col = st.columns([2, 3])

# --- Populate the Left Column ---
# The bar chart and box plot will be stacked vertically here.
with left_col:
    # Cases by Gender and Vaccination Status
    st.subheader("Cases by Demographics")
    stacked_bar = filtered_df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
    fig_bar = px.bar(stacked_bar, x="Gender", y="Number of reported cases of cholera", color="Vaccinated_Against_Cholera",
                     barmode="stack", title="Cases by Gender and Vaccination Status")
    fig_bar.update_layout(height=300) # Adjust height for a compact view
    st.plotly_chart(fig_bar, use_container_width=True)

    # Age Distribution by Sanitation Level
    st.subheader("Age & Sanitation")
    box_data = filtered_df[["Sanitation_Level", "Age"]].dropna()
    fig_box = px.box(box_data, x="Sanitation_Level", y="Age", color="Sanitation_Level",
                     title="Age Distribution by Sanitation Level")
    fig_box.update_layout(height=300, showlegend=False) # Adjust height
    st.plotly_chart(fig_box, use_container_width=True)


# --- Populate the Right Column ---
# The map and the trend line will be stacked vertically here.
with right_col:
    # Choropleth Map (Larger)
    map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    # Handle cases where all filtered data might be zero
    if not map_df.empty and map_df["Number of reported cases of cholera"].sum() > 0:
        map_df["Log_Cases"] = np.log10(map_df["Number of reported cases of cholera"] + 1)
    else:
        map_df["Log_Cases"] = 0 # Assign zero if no data

    fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                            color="Log_Cases", color_continuous_scale="Reds",
                            title="Reported Cholera Cases (Log Scale)")
    # Make the map taller to dominate the view
    fig_map.update_layout(height=450, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    # Line Chart: Cholera Over Time (Smaller, below the map)
    trend = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    fig_trend = px.line(trend, x="Year", y="Number of reported cases of cholera", markers=True,
                        title="Cholera Cases Over Time")
    # Make the trend chart shorter
    fig_trend.update_layout(height=250)
    st.plotly_chart(fig_trend, use_container_width=True)
