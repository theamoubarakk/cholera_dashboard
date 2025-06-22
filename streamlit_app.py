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


# --- Right Column (ADVANCED VISUALIZATIONS) ---
with right_col:
    
    # --- Data Cleaning (Important First Step) ---
    # Convert numeric columns, coercing errors to NaN (Not a Number)
    numeric_cols = ['Number of reported cases of cholera', 'Cholera case fatality rate']
    for col in numeric_cols:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
    
    # Remove rows where these critical values are missing
    clean_df = filtered_df.dropna(subset=numeric_cols)


    # --- CHART 1: Population Pyramid of Cases by Region and Gender ---
    st.subheader("Cholera Cases by Region and Gender")
    
    # Prepare data for the pyramid
    pyramid_data = clean_df.groupby(['WHO Region', 'Gender'])['Number of reported cases of cholera'].sum().reset_index()
    
    # Key step for pyramid: make one gender's values negative
    pyramid_data['Cases'] = pyramid_data.apply(
        lambda row: -row['Number of reported cases of cholera'] if row['Gender'] == 'Male' else row['Number of reported cases of cholera'],
        axis=1
    )
    
    fig_pyramid = px.bar(pyramid_data, 
                         y='WHO Region', 
                         x='Cases', 
                         color='Gender',
                         orientation='h',
                         barmode='relative',
                         color_discrete_map={'Female': '#E6443E', 'Male': '#FFA07A'},
                         labels={'Cases': 'Number of Reported Cases'})
                         
    # Customize layout for pyramid look
    fig_pyramid.update_layout(
        xaxis=dict(
            tickformat=',.0f',
            tickvals=[-5000000, -2500000, 0, 2500000, 5000000],
            ticktext=['5M', '2.5M', '0', '2.5M', '5M']
        ),
        yaxis_autorange='reversed',
        height=220, 
        margin=dict(l=0, r=10, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_pyramid, use_container_width=True)


    # --- CHART 2: Factor Importance (Average Fatality Rate) ---
    st.subheader("Factors Affecting Fatality Rate")
    
    factors = ['WHO Region', 'Urban_or_Rural', 'Sanitation_Level', 'Access_to_Clean_Water', 'Vaccinated_Against_Cholera']
    factor_fatality_list = []

    for factor in factors:
        # Calculate mean fatality rate for each category in the factor
        grouped = clean_df.groupby(factor)['Cholera case fatality rate'].mean().reset_index()
        grouped.rename(columns={factor: 'Category'}, inplace=True)
        grouped['Factor'] = factor
        factor_fatality_list.append(grouped)

    # Combine all factors into one DataFrame
    all_factors_df = pd.concat(factor_fatality_list).dropna()
    all_factors_df = all_factors_df.sort_values('Cholera case fatality rate', ascending=True)

    fig_factors = px.bar(all_factors_df,
                         x='Cholera case fatality rate',
                         y='Category',
                         color='Cholera case fatality rate',
                         color_continuous_scale='Reds',
                         orientation='h',
                         labels={'Category': 'Factor Category', 'Cholera case fatality rate': 'Avg. Fatality Rate (%)'})
    
    fig_factors.update_layout(height=200, margin=dict(l=0, r=10, t=10, b=0), coloraxis_showscale=False)
    st.plotly_chart(fig_factors, use_container_width=True)


    # --- CHART 3: Heatmap of Fatality Rate by Region and Sanitation ---
    st.subheader("Fatality Rate: Region vs. Sanitation")
    
    # Create a pivot table to structure the data for the heatmap
    heatmap_data = clean_df.pivot_table(
        values='Cholera case fatality rate',
        index='WHO Region',
        columns='Sanitation_Level',
        aggfunc='mean'
    ).reindex(columns=['Low', 'Medium', 'High']) # Ensure logical column order

    fig_heatmap = px.imshow(heatmap_data,
                            labels=dict(x="Sanitation Level", y="WHO Region", color="Avg. Fatality Rate"),
                            color_continuous_scale='Reds')

    fig_heatmap.update_layout(height=180, margin=dict(l=0, r=10, t=10, b=0))
    st.plotly_chart(fig_heatmap, use_container_width=True)
