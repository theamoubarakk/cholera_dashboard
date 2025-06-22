import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load your dataset
df = pd.read_csv("enriched_data_logical.csv")
df["Country"] = df["Country"].str.strip()

# Fix common country naming issues
df["Country"] = df["Country"].replace({
    "United States of America": "United States",
    "Côte d’Ivoire": "Ivory Coast",
    "Russian Federation": "Russia",
    "Viet Nam": "Vietnam",
    "Syrian Arab Republic": "Syria",
    "Democratic Republic of the Congo": "DR Congo"
})

st.set_page_config(layout="wide")
st.title("🌍 Cholera Dashboard - Global Trends and Risk Factors")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    all_countries = df["Country"].dropna().unique().tolist()
    default_countries = [c for c in ["Nigeria", "India", "United States"] if c in all_countries]
    countries = st.multiselect("Select Countries", all_countries, default=default_countries)
    
    years = st.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2016))
    gender = st.multiselect("Gender", df["Gender"].unique(), default=list(df["Gender"].unique()))
    urban_rural = st.radio("Urban or Rural", ["Urban", "Rural", "Both"], index=2)
    vaccinated = st.multiselect("Vaccinated Against Cholera", df["Vaccinated_Against_Cholera"].unique(), default=["Yes", "No"])

# Filter dataset
filtered_df = df[
    (df["Country"].isin(countries)) &
    (df["Year"].between(years[0], years[1])) &
    (df["Gender"].isin(gender)) &
    (df["Vaccinated_Against_Cholera"].isin(vaccinated))
]
if urban_rural != "Both":
    filtered_df = filtered_df[filtered_df["Urban_or_Rural"] == urban_rural]

# Layout
col1, col2 = st.columns(2)

# ✅ Choropleth map using GeoPandas + Matplotlib
with col1:
    map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    map_df["Number of reported cases of cholera"] = pd.to_numeric(map_df["Number of reported cases of cholera"], errors="coerce").fillna(0).clip(upper=1_000_000)

    # Load country boundaries from public GeoJSON
    world = gpd.read_file("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson")
    merged = world.merge(map_df, how="left", left_on="NAME", right_on="Country")
    merged["Number of reported cases of cholera"] = merged["Number of reported cases of cholera"].fillna(0)

    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    merged.plot(
        column="Number of reported cases of cholera",
        cmap="Reds",
        linewidth=0.8,
        ax=ax,
        edgecolor="0.8",
        legend=True,
        legend_kwds={"label": "Cholera Cases", "orientation": "vertical"}
    )
    ax.set_title("Cholera Burden by Country", fontsize=16)
    ax.axis("off")
    st.pyplot(fig)

# Bar chart: deaths by sanitation level
with col2:
    bar_df = filtered_df.groupby("Sanitation_Level")["Number of reported deaths from cholera"].sum().reset_index()
    bar_df["Number of reported deaths from cholera"] = pd.to_numeric(bar_df["Number of reported deaths from cholera"], errors="coerce").fillna(0)

    st.bar_chart(
        data=bar_df.set_index("Sanitation_Level"),
        use_container_width=True
    )

# Second row
col3, col4 = st.columns(2)

# Box plot: age vs. clean water access
with col3:
    import seaborn as sns
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=filtered_df, x="Access_to_Clean_Water", y="Age", ax=ax)
    ax.set_title("Age Distribution by Access to Clean Water")
    st.pyplot(fig)

# Stacked bar: gender vs. urban/rural deaths
with col4:
    stacked_df = filtered_df.groupby(["Gender", "Urban_or_Rural"])["Number of reported deaths from cholera"].sum().unstack().fillna(0)
    st.bar_chart(stacked_df)

# Line chart: cases over time
line_df = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
line_df["Number of reported cases of cholera"] = pd.to_numeric(line_df["Number of reported cases of cholera"], errors="coerce").fillna(0)

st.line_chart(
    data=line_df.set_index("Year"),
    use_container_width=True
)
