import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Page Configuration and CSS for a Hyper-Compact Layout ---
st.set_page_config(layout="wide")

# This CSS is the key to removing all extra space.
st.markdown("""
    <style>
        /* Reduce top padding of the whole page */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        /* Reduce space above the main title */
        h1 {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
            font-size: 2.5rem !important;
        }
        /* Make plot titles smaller and remove bottom margin */
        h3 {
            font-size: 1.2rem !important;
            margin-top: 1rem !important;
            margin-bottom: 0rem !important; /* CRITICAL: removes space below title */
        }
        /* This targets the container for elements in a column and removes the gap */
        .st-emotion-cache-z5fcl4 {
             gap: 0rem !important; /* CRITICAL: removes the vertical gap between plots */
        }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

df = load_data("enriched_data_logical_cleaned.csv")

# --- Sidebar Filters ---
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

# --- Main Page Title ---
st.title("\U0001F30E Global Cholera Tracker")

# --- Layout Columns ---
left_col, right_col = st.columns([3, 2])

# --- Left Column (Map and Trend Line with NO gap) ---
# --- Left Column (MODIFIED to match the style of the Malaria dashboard) ---
with left_col:
    # --- Choropleth Map (Bigger) ---
    # The subheader is removed, and the title is now INSIDE the plot, like the Malaria code.
    map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    if not map_df.empty and map_df["Number of reported cases of cholera"].sum() > 0:
        map_df["Log_Cases"] = np.log10(map_df["Number of reported cases of cholera"] + 1)
    else:
        map_df["Log_Cases"] = 0

    fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                            color="Log_Cases", color_continuous_scale="Reds",
                            # 1. ADDED: Internal title to match Malaria style
                            title="Reported Cholera Cases (Log Scale)")
    
    # 2. MODIFIED: Height and margins now match the Malaria map exactly
    fig_map.update_layout(height=400, margin=dict(t=30, b=10))
    st.plotly_chart(fig_map, use_container_width=True)


    # --- Line Chart: Cholera Over Time (Smaller) ---
    # The subheader is removed, and the title is now INSIDE the plot.
    trend = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    fig_trend = px.line(trend, x="Year", y="Number of reported cases of cholera", markers=True,
                        # 1. ADDED: Internal title to match Malaria style
                        title="Cholera Cases Over Time")

    # 2. MODIFIED: Height and margins now match the Malaria trend line exactly
    fig_trend.update_layout(height=200, margin=dict(t=30, b=10))
    st.plotly_chart(fig_trend, use_container_width=True)



# --- Right Column (Bar and Box Plots) ---
with right_col:
    # Cases by Gender and Vaccination Status
    st.subheader("Cases by Gender and Vaccination Status")
    stacked_bar = filtered_df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
    fig_bar = px.bar(stacked_bar, x="Gender", y="Number of reported cases of cholera", color="Vaccinated_Against_Cholera",
                     barmode="stack")
    fig_bar.update_layout(height=190, margin=dict(l=0, r=10, t=0, b=0))
    st.plotly_chart(fig_bar, use_container_width=True)

    # Age Distribution by Sanitation Level
    st.subheader("Age Distribution by Sanitation Level")
    box_data = filtered_df[["Sanitation_Level", "Age"]].dropna()
    fig_box = px.box(box_data, x="Sanitation_Level", y="Age", color="Sanitation_Level")
    fig_box.update_layout(height=190, showlegend=True, margin=dict(l=0, r=10, t=0, b=0))
    st.plotly_chart(fig_box, use_container_width=True)
