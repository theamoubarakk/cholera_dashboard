import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Load cleaned data
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# Preprocess: convert log cases for map
df_map = df.copy()
df_map["Log_Cases"] = df_map["Number of reported cases of cholera"].apply(lambda x: np.log10(x) if x > 0 else 0)

# Sidebar filters
st.sidebar.header("\ud83d\udd0d Filters")

countries = st.sidebar.multiselect("Select Countries", options=sorted(df["Country"].unique()))
year_range = st.sidebar.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
gender = st.sidebar.multiselect("Select Gender", options=df["Gender"].unique(), default=list(df["Gender"].unique()))
ur = st.sidebar.radio("Urban or Rural", options=["Both", "Urban", "Rural"], index=0)
water = st.sidebar.selectbox("Access to Clean Water", options=["Both", "Yes", "No"])
vacc = st.sidebar.selectbox("Vaccinated Against Cholera", options=["Both", "Yes", "No"])

# Apply filters
filtered_df = df.copy()
if countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(countries)]
filtered_df = filtered_df[(filtered_df["Year"] >= year_range[0]) & (filtered_df["Year"] <= year_range[1])]
if gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender)]
if ur != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == ur]
if water != "Both":
    filtered_df = filtered_df[filtered_df["Access_to_Clean_Water"] == water]
if vacc != "Both":
    filtered_df = filtered_df[filtered_df["Vaccinated_Against_Cholera"] == vacc]

# Layout
col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown("### Reported Cholera Cases (Log Scale)")
    fig_map = px.choropleth(df_map, locations="Country", locationmode="country names",
                            color="Log_Cases", hover_name="Country",
                            color_continuous_scale="OrRd")
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.markdown("### Cholera Cases Over Time")
    yearly = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    fig_line = px.line(yearly, x="Year", y="Number of reported cases of cholera",
                       markers=True)
    fig_line.update_layout(height=350)
    st.plotly_chart(fig_line, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("### Cases by Gender and Vaccination Status")
    grouped = filtered_df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
    fig_stacked = px.bar(grouped, x="Gender", y="Number of reported cases of cholera",
                         color="Vaccinated_Against_Cholera", barmode="stack")
    fig_stacked.update_layout(height=300)
    st.plotly_chart(fig_stacked, use_container_width=True)

with col4:
    st.markdown("### Age Distribution by Sanitation Level")
    fig_box = px.box(filtered_df, x="Sanitation_Level", y="Age", color="Sanitation_Level")
    fig_box.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# Final row
st.markdown("### Heatmap: Cholera Cases by Gender and Age")
heatmap_data = filtered_df.groupby(["Gender", "Age"])["Number of reported cases of cholera"].sum().reset_index()
heatmap_pivot = heatmap_data.pivot(index="Gender", columns="Age", values="Number of reported cases of cholera")
fig_heatmap = px.imshow(heatmap_pivot, aspect="auto", color_continuous_scale="Blues",
                        labels=dict(x="Age", y="Gender", color="Cases"))
fig_heatmap.update_layout(height=250)
st.plotly_chart(fig_heatmap, use_container_width=True)
