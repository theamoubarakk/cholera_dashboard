import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Load dataset
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# Fill and calculate missing values
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce").fillna(0)
df["Number of reported deaths from cholera"] = pd.to_numeric(df["Number of reported deaths from cholera"], errors="coerce").fillna(0)

def compute_fatality(row):
    if pd.isna(row["Cholera case fatality rate"]):
        cases = row["Number of reported cases of cholera"]
        deaths = row["Number of reported deaths from cholera"]
        return round(deaths / cases, 4) if cases > 0 else 0
    return row["Cholera case fatality rate"]

df["Cholera case fatality rate"] = df.apply(compute_fatality, axis=1)

# Sidebar filters
st.sidebar.header("🔎 Filters")
countries = st.sidebar.multiselect("Select Countries", sorted(df["Country"].dropna().unique()))
years = st.sidebar.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
genders = st.sidebar.multiselect("Select Gender", df["Gender"].dropna().unique(), default=list(df["Gender"].dropna().unique()))
location = st.sidebar.radio("Urban or Rural", ["Both", "Urban", "Rural"], index=0)
water = st.sidebar.selectbox("Access to Clean Water", ["Both", "Yes", "No"])
vax = st.sidebar.selectbox("Vaccinated Against Cholera", ["Both", "Yes", "No"])

# Apply filters
filtered_df = df[(df["Year"] >= years[0]) & (df["Year"] <= years[1])]

if countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(countries)]
if genders:
    filtered_df = filtered_df[filtered_df["Gender"].isin(genders)]
if location != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == location]
if water != "Both":
    filtered_df = filtered_df[filtered_df["Access_to_Clean_Water"] == water]
if vax != "Both":
    filtered_df = filtered_df[filtered_df["Vaccinated_Against_Cholera"] == vax]

# MAIN TITLE
st.markdown("## 🌍 Global Cholera Tracker")
st.markdown("Use the filters on the left to explore **reported cholera cases** across countries and time.")

# Map
map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
map_df["Log_Cases"] = map_df["Number of reported cases of cholera"].apply(lambda x: 0 if x <= 0 else round(np.log10(x), 1))

fig_map = px.choropleth(map_df,
                        locations="Country",
                        locationmode="country names",
                        color="Log_Cases",
                        color_continuous_scale="OrRd",
                        title="Reported Cholera Cases (Log Scale)")
fig_map.update_layout(height=400)

# Bar: Sanitation Level
bar1 = filtered_df.groupby("Sanitation_Level")["Number of reported deaths from cholera"].sum().reset_index()
fig_bar1 = px.bar(bar1, x="Sanitation_Level", y="Number of reported deaths from cholera",
                  color="Sanitation_Level", title="Deaths by Sanitation Level")
fig_bar1.update_layout(height=300)

# Donuts
donut1 = filtered_df["Access_to_Clean_Water"].value_counts().reset_index()
fig_donut1 = px.pie(donut1, values="Access_to_Clean_Water", names="index", hole=0.5,
                    color_discrete_sequence=px.colors.sequential.Blues)
fig_donut1.update_layout(title="Access to Clean Water", height=300)

donut2 = filtered_df["Vaccinated_Against_Cholera"].value_counts().reset_index()
fig_donut2 = px.pie(donut2, values="Vaccinated_Against_Cholera", names="index", hole=0.5,
                    color_discrete_sequence=px.colors.sequential.Greens)
fig_donut2.update_layout(title="Vaccinated Against Cholera", height=300)

# Box: Age Distribution
fig_box = px.box(filtered_df, x="Urban_or_Rural", y="Age", color="Urban_or_Rural",
                 title="Age Distribution by Location")
fig_box.update_layout(height=300)

# Grouped Bar: Deaths by Gender & Region
bar2 = filtered_df.groupby(["WHO Region", "Gender"])["Number of reported deaths from cholera"].sum().reset_index()
fig_grouped = px.bar(bar2, x="WHO Region", y="Number of reported deaths from cholera", color="Gender",
                     barmode="group", title="Cholera Deaths by Gender and Region")
fig_grouped.update_layout(height=300)

# LAYOUT 3x2
col1, col2 = st.columns([2, 1])
col1.plotly_chart(fig_map, use_container_width=True)
col2.plotly_chart(fig_bar1, use_container_width=True)

col3, col4 = st.columns(2)
col3.plotly_chart(fig_donut1, use_container_width=True)
col4.plotly_chart(fig_donut2, use_container_width=True)

col5, col6 = st.columns(2)
col5.plotly_chart(fig_box, use_container_width=True)
col6.plotly_chart(fig_grouped, use_container_width=True)
