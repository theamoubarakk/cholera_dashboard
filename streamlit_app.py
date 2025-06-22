import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# Ensure correct dtypes
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce").fillna(0)
df["Number of reported deaths from cholera"] = pd.to_numeric(df["Number of reported deaths from cholera"], errors="coerce").fillna(0)
df["Cholera case fatality rate"] = pd.to_numeric(df["Cholera case fatality rate"], errors="coerce")

def compute_fatality(row):
    if pd.isna(row["Cholera case fatality rate"]):
        cases = row["Number of reported cases of cholera"]
        deaths = row["Number of reported deaths from cholera"]
        return round(deaths / cases, 4) if cases > 0 else 0
    return row["Cholera case fatality rate"]

df["Cholera case fatality rate"] = df.apply(compute_fatality, axis=1)
df["Log_Cases"] = np.log10(df["Number of reported cases of cholera"] + 1)

# Sidebar filters
with st.sidebar:
    st.header("\U0001F5FA\ufe0f Filters")
    countries = st.multiselect("Select Countries", sorted(df["Country"].unique()), default=None)
    year_range = st.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
    gender = st.multiselect("Select Gender", df["Gender"].unique(), default=list(df["Gender"].unique()))
    urban = st.radio("Urban or Rural", ["Both", "Urban", "Rural"], index=0)
    access_water = st.multiselect("Access to Clean Water", df["Access_to_Clean_Water"].unique())
    vaccinated = st.multiselect("Vaccinated Against Cholera", df["Vaccinated_Against_Cholera"].unique())

# Apply filters
filtered_df = df[df["Year"].between(*year_range)]
if countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(countries)]
if gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender)]
if urban != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == urban]
if access_water:
    filtered_df = filtered_df[filtered_df["Access_to_Clean_Water"].isin(access_water)]
if vaccinated:
    filtered_df = filtered_df[filtered_df["Vaccinated_Against_Cholera"].isin(vaccinated)]

# Layout
st.title("\U0001F30D Global Cholera Tracker")
st.markdown("Use the filters on the left to explore **reported cholera cases** across countries and time.")

# Row 1
col1, col2 = st.columns([1.3, 1])

# Choropleth map
with col1:
    st.subheader("Reported Cholera Cases (Log Scale)")
    map_df = filtered_df.groupby("Country", as_index=False)["Log_Cases"].mean()
    fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                            color="Log_Cases", color_continuous_scale="OrRd",
                            labels={"Log_Cases": "Log_Cases"})
    fig_map.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

# Sanitation level bar chart
with col2:
    st.subheader("Deaths by Sanitation Level")
    bar_san = filtered_df.groupby("Sanitation_Level")["Number of reported deaths from cholera"].sum().reset_index()
    fig_bar_san = px.bar(bar_san, x="Sanitation_Level", y="Number of reported deaths from cholera", color="Sanitation_Level")
    fig_bar_san.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_bar_san, use_container_width=True)

# Row 2
col3, col4 = st.columns(2)

# Donut: Access to Clean Water
with col1:
    donut1 = filtered_df["Access_to_Clean_Water"].value_counts().reset_index()
    donut1.columns = ["Access_to_Clean_Water", "Count"]

    fig_donut1 = px.pie(
        donut1,
        values="Count",
        names="Access_to_Clean_Water",
        hole=0.5,
        title="Access to Clean Water",
        color_discrete_sequence=px.colors.sequential.Blues
    )
    st.plotly_chart(fig_donut1, use_container_width=True)


# Donut: Vaccinated
with col2:
    donut2 = filtered_df["Vaccinated_Against_Cholera"].value_counts().reset_index()
    donut2.columns = ["Vaccinated_Against_Cholera", "Count"]

    fig_donut2 = px.pie(
        donut2,
        values="Count",
        names="Vaccinated_Against_Cholera",
        hole=0.5,
        title="Vaccinated Against Cholera",
        color_discrete_sequence=px.colors.sequential.Greens
    )
    st.plotly_chart(fig_donut2, use_container_width=True)


# Row 3
col5, col6 = st.columns(2)

# Boxplot: Age by Urban/Rural
with col5:
    st.subheader("Age Distribution by Location")
    fig_box = px.box(filtered_df, x="Urban_or_Rural", y="Age", color="Urban_or_Rural")
    fig_box.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_box, use_container_width=True)

# Stacked bar: Gender vs WHO Region deaths
with col6:
    st.subheader("Cholera Deaths by Gender and Region")
    stacked = filtered_df.groupby(["WHO Region", "Gender"])["Number of reported deaths from cholera"].sum().reset_index()
    fig_stacked = px.bar(stacked, x="WHO Region", y="Number of reported deaths from cholera", color="Gender", barmode="stack")
    fig_stacked.update_layout(height=350)
    st.plotly_chart(fig_stacked, use_container_width=True)
