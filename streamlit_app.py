import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Page Configuration and Custom CSS ---
st.set_page_config(layout="wide")

# VITAL: Inject CSS to reduce top padding of the main page and titles
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem; /* Reduce top padding */
        }
        .st-emotion-cache-18ni7ap { /* Specific selector for main container */
            padding-top: 1rem;
        }
        h1 {
            padding-top: 0rem; /* Reduce padding above the main title */
        }
        h3 {
            padding-top: 0rem; /* Reduce padding above subheaders */
            padding-bottom: 0rem; /* Reduce padding below subheaders */
        }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

df = load_data("enriched_data_logical_cleaned.csv")

# --- Sidebar Filters ---
# The sidebar code remains unchanged
with st.sidebar:
    st.title("Filters")
    countries = st.multiselect("Select Countries", sorted(df["Country"].dropna().unique()))
    year_range = st.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
    genders = st.multiselect("Select Gender", df["Gender"].dropna().unique(), default=list(df["Gender"].dropna().unique()))
    location = st.radio("Urban or Rural", ["Both", "Urban", "Rural"], index=0)
    water_access = st.selectbox("Access to Clean Water", ["Both", "Yes", "No"])
    vaccinated = st.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"])

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

# --- Main Page Title (Now closer to the top) ---
st.title("\U0001F30E Global Cholera Tracker")
st.markdown("Use the filters on the left to explore reported cholera cases across countries and time.")

# --- Layout Columns ---
left_col, right_col = st.columns([2, 3])

# --- Left Column ---
with left_col:
    # Cases by Gender and Vaccination Status
    st.subheader("Cases by Gender and Vaccination Status")
    stacked_bar = filtered_df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
    # MODIFIED: Removed the title from inside the plot
    fig_bar = px.bar(stacked_bar, x="Gender", y="Number of reported cases of cholera", color="Vaccinated_Against_Cholera",
                     barmode="stack")
    # MODIFIED: Reduced margins to remove whitespace
    fig_bar.update_layout(height=280, margin=dict(l=0, r=10, t=10, b=0))
    st.plotly_chart(fig_bar, use_container_width=True)

    # Age Distribution by Sanitation Level
    st.subheader("Age Distribution by Sanitation Level")
    box_data = filtered_df[["Sanitation_Level", "Age"]].dropna()
    # MODIFIED: Removed the title from inside the plot
    fig_box = px.box(box_data, x="Sanitation_Level", y="Age", color="Sanitation_Level")
    # MODIFIED: Reduced margins and removed legend
    fig_box.update_layout(height=280, showlegend=False, margin=dict(l=0, r=10, t=10, b=0))
    st.plotly_chart(fig_box, use_container_width=True)

# --- Right Column ---
with right_col:
    # Choropleth Map
    # MODIFIED: Placed the title outside the plot using st.subheader
    st.subheader("Reported Cholera Cases (Log Scale)")
    map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    if not map_df.empty and map_df["Number of reported cases of cholera"].sum() > 0:
        map_df["Log_Cases"] = np.log10(map_df["Number of reported cases of cholera"] + 1)
    else:
        map_df["Log_Cases"] = 0

    # MODIFIED: Removed the title from inside the plot
    fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                            color="Log_Cases", color_continuous_scale="Reds")
    # MODIFIED: Set margins to 0 to bring the map right up to the title
    fig_map.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    # Line Chart: Cholera Over Time
    # MODIFIED: Placed the title outside the plot
    st.subheader("Cholera Cases Over Time")
    trend = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    # MODIFIED: Removed the title from inside the plot
    fig_trend = px.line(trend, x="Year", y="Number of reported cases of cholera", markers=True)
    # MODIFIED: Set margins to push the chart up
    fig_trend.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_trend, use_container_width=True)
