import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# Sidebar filters
st.sidebar.header("🔎 Filters")
countries = st.sidebar.multiselect("Select Countries", options=df["Country"].unique())
years = st.sidebar.slider("Select Year Range", min_value=int(df["Year"].min()), max_value=int(df["Year"].max()), value=(2000, 2016))
genders = st.sidebar.multiselect("Select Gender", options=df["Gender"].dropna().unique())
urban_rural = st.sidebar.radio("Urban or Rural", options=["Both", "Urban", "Rural"])
water = st.sidebar.selectbox("Access to Clean Water", options=["All", "Yes", "No"])
vax = st.sidebar.selectbox("Vaccinated Against Cholera", options=["All", "Yes", "No"])

# Apply filters
filtered_df = df[
    (df["Year"] >= years[0]) & (df["Year"] <= years[1])
]

if countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(countries)]
if genders:
    filtered_df = filtered_df[filtered_df["Gender"].isin(genders)]
if urban_rural != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == urban_rural]
if water != "All":
    filtered_df = filtered_df[filtered_df["Access_to_Clean_Water"] == water]
if vax != "All":
    filtered_df = filtered_df[filtered_df["Vaccinated_Against_Cholera"] == vax]

# Map
map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
map_df["Log_Cases"] = map_df["Number of reported cases of cholera"].apply(lambda x: 0 if x <= 0 else round(np.log10(x), 1))
map_fig = px.choropleth(map_df, locations="Country", locationmode="country names",
                        color="Log_Cases", color_continuous_scale="OrRd",
                        title="Reported Cholera Cases (Log Scale)")
map_fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=350)

# Bar: Deaths by Sanitation
bar1 = px.bar(filtered_df.groupby("Sanitation_Level")["Number of reported deaths from cholera"].sum().reset_index(),
              x="Sanitation_Level", y="Number of reported deaths from cholera",
              title="Deaths by Sanitation Level", color="Sanitation_Level", height=300)

# Donut: Access to Clean Water
donut1 = filtered_df["Access_to_Clean_Water"].value_counts().reset_index()
fig_donut1 = px.pie(donut1, names="index", values="Access_to_Clean_Water",
                    hole=0.5, title="Access to Clean Water", color_discrete_sequence=px.colors.sequential.Blues)
fig_donut1.update_traces(textinfo='percent+label')

# Donut: Vaccinated
donut2 = filtered_df["Vaccinated_Against_Cholera"].value_counts().reset_index()
fig_donut2 = px.pie(donut2, names="index", values="Vaccinated_Against_Cholera",
                    hole=0.5, title="Vaccinated Against Cholera", color_discrete_sequence=px.colors.sequential.Greens)
fig_donut2.update_traces(textinfo='percent+label')

# Grouped Bar: Gender × WHO Region
grouped = filtered_df.groupby(["WHO Region", "Gender"])["Number of reported deaths from cholera"].sum().reset_index()
grouped_bar = px.bar(grouped, x="WHO Region", y="Number of reported deaths from cholera", color="Gender",
                     barmode="group", title="Cholera Deaths by Gender and Region", height=300)

# Layout on a single page
st.markdown("## 🌍 Global Cholera Tracker")
st.markdown("Use the filters on the left to explore **reported cholera cases** across countries and time.")

col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(map_fig, use_container_width=True)
with col2:
    st.plotly_chart(bar1, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_donut1, use_container_width=True)
with col4:
    st.plotly_chart(fig_donut2, use_container_width=True)

st.plotly_chart(grouped_bar, use_container_width=True)
