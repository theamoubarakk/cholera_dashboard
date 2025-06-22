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
                        title="Cholera Cases Over Time",
                    color_discrete_sequence=['red'])

    # 2. MODIFIED: Height and margins now match the Malaria trend line exactly
    fig_trend.update_layout(height=180, margin=dict(t=30, b=10))
    st.plotly_chart(fig_trend, use_container_width=True)



# --- Right Column (NEW, INTERESTING GRAPHS) ---
with right_col:

    # --- GRAPH 1: Cholera Cases by WHO Region Over Time ---
    st.subheader("Regional Contribution to Cholera Cases")
    
    # Prepare data: Group by Year and WHO Region, summing the cases
    regional_trend = filtered_df.groupby(['Year', 'WHO Region'])['Number of reported cases of cholera'].sum().reset_index()
    
    fig_regional = px.area(regional_trend, 
                           x="Year", 
                           y="Number of reported cases of cholera", 
                           color="WHO Region",color_discrete_sequence=px.colors.sequential.Reds_r,
                        )
                           
    fig_regional.update_layout(height=145, margin=dict(l=0, r=10, t=30, b=0))
    st.plotly_chart(fig_regional, use_container_width=True)


    # --- GRAPH 2: Fatality Rate by Sanitation and Water Access ---
    st.subheader("How Environment Affects Fatality Rate")
    
    # Clean the fatality rate data (remove potential infinite values)
    filtered_df['Cholera case fatality rate'] = pd.to_numeric(filtered_df['Cholera case fatality rate'], errors='coerce')
    filtered_df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Prepare data: Group by Sanitation and Water Access, calculating the *mean* fatality rate
    fatality_data = filtered_df.groupby(['Sanitation_Level', 'Access_to_Clean_Water'])['Cholera case fatality rate'].mean().reset_index().dropna()
    
    fig_fatality = px.bar(fatality_data, 
                          x="Sanitation_Level", 
                          y="Cholera case fatality rate", 
                          color="Sanitation_Level",
                          facet_col="Access_to_Clean_Water", # Creates side-by-side charts,
                          category_orders={"Sanitation_Level": ["Low", "Medium", "High"]}, color_discrete_map={
                              "Low": "#FFA07A",      # Light Red (LightSalmon)
                              "Medium": "#E6443E",   # Medium Red
                              "High": "#B22222" ) # Ensure correct order

    fig_fatality.update_layout(height=145, margin=dict(l=0, r=10, t=30, b=0))
    st.plotly_chart(fig_fatality, use_container_width=True)


    # --- GRAPH 3 (Optional third graph): Age Distribution in Urban vs. Rural areas ---
    st.subheader("Age Distribution by Location")
    
    # # Prepare data: simply select the needed columns and drop missing values
    age_location_data = filtered_df[['Urban_or_Rural', 'Age']].dropna()
    
    fig_violin = px.violin(age_location_data, 
                            x='Urban_or_Rural', 
                            y='Age', 
                            color='Urban_or_Rural',
                            box=True, # Show a box plot inside the violin
                            points=False, # Hide individual data points for a cleaner look
                           color_discrete_map={
                                "Urban": "#E6443E",    # Medium Red
                                "Rural": "#B22222"     # Dark Red
                            } )
                         
    fig_violin.update_layout(height=145, margin=dict(l=0, r=10, t=30, b=0))
    st.plotly_chart(fig_violin, use_container_width=True)
