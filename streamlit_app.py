import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go  # MOVED TO THE TOP OF THE SCRIPT

# --- Page Configuration and CSS for a Hyper-Compact Layout ---
st.set_page_config(layout="wide")

# This CSS is the key to removing all extra space.
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem;
        }
        h1 {
            padding-top: 0rem !important; margin-top: 0rem !important; font-size: 2.5rem !important;
        }
        h3 {
            font-size: 1.2rem !important; margin-top: 1rem !important; margin-bottom: 0rem !important;
        }
        /* This targets the container for elements in a column and removes the gap */
        div[data-testid="stVerticalBlock"] {
            gap: 0.5rem; /* A small gap is better than zero for readability */
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

# --- UNIFIED LAYOUT STYLE ---
# Both columns now use external subheaders and tight margins for a consistent look.

# --- Left Column (Map and Trend Line) ---
with left_col:
    # --- Choropleth Map (Bigger) ---
    st.subheader("Reported Cholera Cases (Log Scale)") # External title
    map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    if not map_df.empty and map_df["Number of reported cases of cholera"].sum() > 0:
        map_df["Log_Cases"] = np.log10(map_df["Number of reported cases of cholera"] + 1)
    else:
        map_df["Log_Cases"] = 0

    fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                            color="Log_Cases", color_continuous_scale="Reds")
    # Taller map with ZERO TOP MARGIN
    fig_map.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)


    # --- Line Chart: Cholera Over Time (Smaller) ---
    st.subheader("Cholera Cases Over Time") # External title
    trend = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    fig_trend = px.line(trend, x="Year", y="Number of reported cases of cholera", markers=True,
                        color_discrete_sequence=['red'])

    # Shorter trend line with ZERO TOP MARGIN
    fig_trend.update_layout(height=155, margin=dict(l=0, r=0, t=0, b=30))
    st.plotly_chart(fig_trend, use_container_width=True)


# --- Right Column (Three Interesting Graphs) ---
with right_col:
    # --- GRAPH 1: Cholera Cases by WHO Region Over Time ---
    st.subheader("Regional Contribution to Cholera Cases")
    regional_trend = filtered_df.groupby(['Year', 'WHO Region'])['Number of reported cases of cholera'].sum().reset_index()
    fig_regional = px.area(regional_trend, 
                           x="Year", 
                           y="Number of reported cases of cholera", 
                           color="WHO Region",
                           color_discrete_sequence=px.colors.sequential.Reds_r)
    # Balanced height with ZERO TOP MARGIN
    fig_regional.update_layout(height=160, margin=dict(l=0, r=10, t=0, b=0))
    st.plotly_chart(fig_regional, use_container_width=True)


    # --- GRAPH 2: Fatality Rate by Sanitation and Water Access ---
    st.subheader("How Environment Affects Fatality Rate")
    filtered_df['Cholera case fatality rate'] = pd.to_numeric(filtered_df['Cholera case fatality rate'], errors='coerce')
    filtered_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    fatality_data = filtered_df.groupby(['Sanitation_Level', 'Access_to_Clean_Water'])['Cholera case fatality rate'].mean().reset_index().dropna()
    fig_fatality = px.bar(fatality_data, 
                          x="Sanitation_Level", 
                          y="Cholera case fatality rate", 
                          color="Sanitation_Level",
                          facet_col="Access_to_Clean_Water",
                          category_orders={"Sanitation_Level": ["Low", "Medium", "High"]},
                          color_discrete_map={"Low": "#FFA07A", "Medium": "#E6443E", "High": "#B22222"})
    # Balanced height with ZERO TOP MARGIN
    fig_fatality.update_layout(height=160, margin=dict(l=0, r=10, t=0, b=0))
    st.plotly_chart(fig_fatality, use_container_width=True)


    # --- GRAPH 3: Overlaid Histograms ---
    st.subheader("Age Distribution by Location")
    urban_ages = filtered_df[filtered_df['Urban_or_Rural'] == 'Urban']['Age'].dropna()
    rural_ages = filtered_df[filtered_df['Urban_or_Rural'] == 'Rural']['Age'].dropna()
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=urban_ages, name='Urban', marker_color='#E6443E', opacity=0.75))
    fig_hist.add_trace(go.Histogram(x=rural_ages, name='Rural', marker_color='#B22222', opacity=0.75))
    fig_hist.update_layout(
        barmode='overlay',
        xaxis_title_text='Age',
        yaxis_title_text='Count',
        height=160, # Balanced height
        margin=dict(l=0, r=10, t=0, b=0) # ZERO TOP MARGIN
    )
    st.plotly_chart(fig_hist, use_container_width=True)
