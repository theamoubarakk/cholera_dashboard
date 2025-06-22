import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# Convert fatality rate to numeric
if df['Cholera case fatality rate'].dtype == object:
    df['Cholera case fatality rate'] = pd.to_numeric(df['Cholera case fatality rate'], errors='coerce').fillna(0)

# Sidebar filters
st.sidebar.header("\U0001F50D Filters")
countries = st.sidebar.multiselect("Select Countries", sorted(df['Country'].unique()))
year_range = st.sidebar.slider("Select Year Range", int(df['Year'].min()), int(df['Year'].max()), (2000, 2016))
genders = st.sidebar.multiselect("Select Gender", df['Gender'].unique(), default=df['Gender'].unique())
location_type = st.sidebar.radio("Urban or Rural", ["Both"] + df['Urban_or_Rural'].unique().tolist())
water_access = st.sidebar.selectbox("Access to Clean Water", ["Both"] + df['Access_to_Clean_Water'].unique().tolist())
vaccinated = st.sidebar.selectbox("Vaccinated Against Cholera", ["Both"] + df['Vaccinated_Against_Cholera'].unique().tolist())

# Filter data
filtered_df = df[df['Year'].between(*year_range)]
if countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
if genders:
    filtered_df = filtered_df[filtered_df['Gender'].isin(genders)]
if location_type != "Both":
    filtered_df = filtered_df[filtered_df['Urban_or_Rural'] == location_type]
if water_access != "Both":
    filtered_df = filtered_df[filtered_df['Access_to_Clean_Water'] == water_access]
if vaccinated != "Both":
    filtered_df = filtered_df[filtered_df['Vaccinated_Against_Cholera'] == vaccinated]

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 Global Cholera Tracker")
st.markdown("Use the filters on the left to explore **reported cholera cases** across countries and time.")

# Choropleth map
df_map = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
df_map["Log_Cases"] = df_map["Number of reported cases of cholera"].apply(lambda x: 0 if x == 0 else round(np.log10(x), 1))
fig_map = px.choropleth(df_map, locations="Country", locationmode="country names",
                        color="Log_Cases", color_continuous_scale="OrRd",
                        title="Reported Cholera Cases (Log Scale)")

# Line chart: Trend over time
df_trend = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
fig_line = px.line(df_trend, x="Year", y="Number of reported cases of cholera",
                   title="Cholera Cases Over Time", markers=True)

# Stacked bar: Gender × Vaccination
bar_data = filtered_df.groupby(["Gender", "Vaccinated_Against_Cholera"])["Number of reported cases of cholera"].sum().reset_index()
fig_bar = px.bar(bar_data, x="Gender", y="Number of reported cases of cholera", color="Vaccinated_Against_Cholera",
                 barmode="stack", title="Cases by Gender and Vaccination Status")

# Boxplot: Age by Sanitation Level
fig_box = px.box(filtered_df, x="Sanitation_Level", y="Age", color="Sanitation_Level",
                 title="Age Distribution by Sanitation Level")

# Layout for single-page view
col1, col2 = st.columns([1, 1])
with col1:
    st.plotly_chart(fig_map, use_container_width=True)
with col2:
    st.plotly_chart(fig_line, use_container_width=True)

col3, col4 = st.columns([1, 1])
with col3:
    st.plotly_chart(fig_bar, use_container_width=True)
with col4:
    st.plotly_chart(fig_box, use_container_width=True)
