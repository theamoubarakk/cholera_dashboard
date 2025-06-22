import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load data
df = pd.read_csv("enriched_data_logical.csv")

# Sidebar filters
st.sidebar.title("Filters")
countries = st.sidebar.multiselect("Select Countries", options=df["Country"].unique())
year_range = st.sidebar.slider("Select Year Range", min_value=int(df['Year'].min()), max_value=int(df['Year'].max()), value=(2000, 2016))
genders = st.sidebar.multiselect("Select Gender", options=df["Gender"].dropna().unique(), default=df["Gender"].dropna().unique())
area = st.sidebar.radio("Urban or Rural", options=['Both', 'Urban', 'Rural'], index=0)
water = st.sidebar.selectbox("Access to Clean Water", options=['Both', 'Yes', 'No'])
vaccine = st.sidebar.selectbox("Vaccinated Against Cholera", options=['Both', 'Yes', 'No'])

# Filter data
filtered_df = df[
    (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1]) &
    (df["Gender"].isin(genders))
]
if countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(countries)]
if area != 'Both':
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == area]
if water != 'Both':
    filtered_df = filtered_df[filtered_df["Access_to_Clean_Water"] == water]
if vaccine != 'Both':
    filtered_df = filtered_df[filtered_df["Vaccinated_Against_Cholera"] == vaccine]

# Grid layout
col1, col2 = st.columns([1, 1])

# Map
with col2:
    st.markdown("### Reported Cholera Cases (Log Scale)")
    df_map = filtered_df.copy()
    df_map["Log_Cases"] = df_map["Number of reported cases of cholera"].apply(lambda x: 0 if x <= 0 else px.utils.math.log10(x))
    fig_map = px.choropleth(df_map,
        locations="Country",
        locationmode="country names",
        color="Log_Cases",
        color_continuous_scale="Reds",
        title=""
    )
    fig_map.update_layout(height=280, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

# Line chart
with col2:
    st.markdown("### Cholera Cases Over Time")
    line_data = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    fig_line = px.line(line_data, x="Year", y="Number of reported cases of cholera", markers=True)
    fig_line.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_line, use_container_width=True)

# Left column with 3 smaller graphs
with col1:
    st.markdown("### Cases by Gender and Vaccination Status")
    stacked = filtered_df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
    fig_stacked = px.bar(stacked, x="Gender", y="Number of reported cases of cholera", color="Vaccinated_Against_Cholera", barmode="stack")
    fig_stacked.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_stacked, use_container_width=True)

    st.markdown("### Age Distribution by Sanitation Level")
    fig_box = px.box(filtered_df, x="Sanitation_Level", y="Age", color="Sanitation_Level")
    fig_box.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_box, use_container_width=True)
