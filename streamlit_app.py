import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import joblib

# --- Page Configuration and CSS ---
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem;
        }
        h1 {
            padding-top: 0rem !important; margin-top: 0rem !important; font-size: 2.5rem !important;
        }
        h3 {
            font-size: 1.15rem !important; margin-top: 1rem !important; margin-bottom: 0.2rem !important; font-weight: 500;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

df = pd.read_csv("enriched_data_logical_cleaned.csv")

# --- Sidebar Filters ---
with st.sidebar:
    st.title("Filters")
    countries = st.multiselect("Select Countries", sorted(df["Country"].dropna().unique()))
    year_range = st.slider("Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (1986, 2016))
    genders = st.multiselect("Select Gender", df["Gender"].dropna().unique(), default=['Male', 'Female'])
    location = st.radio("Urban or Rural", ["Both", "Urban", "Rural"], index=0)
    water_access = st.radio("Access to Clean Water", ["Both", "Yes", "No"], index=0)
    vaccinated = st.radio("Vaccinated Against Cholera", ["Both", "Yes", "No"], index=0)

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
st.title("Cholera Dashboard - Global Trends and Risk Factors")

# --- Layout Columns ---
left_col, right_col = st.columns([3, 2])

# --- CHOLERA FATALITY PREDICTION (Sidebar) ---
import joblib

# Load trained model
model = joblib.load("logreg_model.joblib")

# Sidebar Inputs for Prediction
st.sidebar.header("🔬 Predict Cholera Fatality Risk")

# Collect inputs from user
region = st.sidebar.selectbox("WHO Region", ["Africa", "Americas", "Eastern Mediterranean", "Europe", "South-East Asia", "Western Pacific"])
sanitation = st.sidebar.selectbox("Sanitation Level", ["Low", "Medium", "High"])
urban_rural = st.sidebar.selectbox("Urban or Rural", ["Urban", "Rural"])
water = st.sidebar.selectbox("Access to Clean Water", ["Yes", "No"])
vaccinated = st.sidebar.selectbox("Vaccinated Against Cholera", ["Yes", "No"])
gender = st.sidebar.radio("Gender", ["Male", "Female"])
age = st.sidebar.slider("Age", 0, 100, 30)

# Manually bucket age into categories
if age <= 12:
    age_group = "Child"
elif age <= 18:
    age_group = "Teen"
elif age <= 35:
    age_group = "Young Adult"
elif age <= 50:
    age_group = "Adult"
elif age <= 65:
    age_group = "Middle Age"
else:
    age_group = "Senior"

# All one-hot encoded possible columns (should match training set)
columns = joblib.load("cholera_model_columns.pkl")
user_input = pd.DataFrame([{
    'Sanitation_Level': sanitation,
    'Access_to_Clean_Water': water,
    'Urban_or_Rural': urban_rural,
    'Vaccinated_Against_Cholera': vaccinated,
    'WHO Region': region,
    'Gender': gender,
    'Age_Group': age_group
}])

# One-hot encode and align with training columns
encoded_input = pd.get_dummies(user_input)
encoded_input = encoded_input.reindex(columns=columns, fill_value=0)

# Prediction
pred = model.predict(encoded_input)[0]
prob = model.predict_proba(encoded_input)[0][1]

# Result display
st.sidebar.subheader("Prediction Result")
if pred == 1:
    st.sidebar.error(f"⚠️ High Fatality Risk ({prob*100:.1f}%)")
else:
    st.sidebar.success(f"✅ Low Fatality Risk ({(1-prob)*100:.1f}%)")

# --- Left Column (Map and Trend Line) ---
with left_col:
    st.subheader("Heatmap of Reported Cholera Cases Across the World")
    map_df = filtered_df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    if not map_df.empty and map_df["Number of reported cases of cholera"].sum() > 0:
        map_df["Log_Cases"] = np.log10(map_df["Number of reported cases of cholera"] + 1)
    else:
        map_df["Log_Cases"] = 0

    fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                            color="Log_Cases", color_continuous_scale="Reds")
    fig_map.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("Decades of Cholera: How Cases Have Risen and Fallen Over Time")
    trend = filtered_df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
    fig_trend = px.line(trend, x="Year", y="Number of reported cases of cholera", markers=True,
                        color_discrete_sequence=['#B22222'])
    fig_trend.update_layout(height=155, margin=dict(l=0, r=0, t=0, b=30))
    st.plotly_chart(fig_trend, use_container_width=True)

# --- Right Column ---
with right_col:
    # --- Data Cleaning ---
    numeric_cols = ['Number of reported cases of cholera', 'Cholera case fatality rate']
    for col in numeric_cols:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
    clean_df = filtered_df.dropna(subset=numeric_cols)

    # --- Right Column  ---
with right_col:
    # --- Data Cleaning ---
    numeric_cols = ['Number of reported cases of cholera', 'Cholera case fatality rate']
    for col in numeric_cols:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
    clean_df = filtered_df.dropna(subset=numeric_cols)
    
    # --- CHART: What Makes an Outbreak More Deadly? ---
    st.subheader("Which Living Conditions Increase Risk of Death?")

    factors = ['Urban_or_Rural', 'Sanitation_Level', 'Access_to_Clean_Water', 'Vaccinated_Against_Cholera']
    factor_fatality_list = []

    # Loop through each factor to calculate its average fatality rate and create a clean label
    for factor in factors:
        grouped = clean_df.groupby(factor)['Cholera case fatality rate'].mean().reset_index()
        
        clean_name = factor.replace('_', ' ').replace('Level', '').replace('Against Cholera', '').strip()
        grouped['Display_Label'] = clean_name + ': ' + grouped[factor]
        
        factor_fatality_list.append(grouped[['Display_Label', 'Cholera case fatality rate']])

    # Combine all factors into one DataFrame for plotting
    all_factors_df = pd.concat(factor_fatality_list).dropna()

    # Sorting by fatality rate to rank the factors from most to least deadly
    all_factors_df = all_factors_df.sort_values('Cholera case fatality rate', ascending=True)

    # --- CHART 1: Bar chart ---
    fig_factors = px.bar(all_factors_df,
                         x='Cholera case fatality rate',
                         y='Display_Label',
                         color='Cholera case fatality rate',
                         color_continuous_scale='Reds',
                         orientation='h',
                         labels={'Display_Label': '', 'Cholera case fatality rate': 'Avg. Fatality Rate (%)'})
                         
    # Update layout for a clean look
    fig_factors.update_layout(height=160, # Give this important chart more vertical space
                              margin=dict(l=10, r=10, t=10, b=40), 
                              coloraxis_showscale=False, 
                              yaxis={'title': ''})
                              
    st.plotly_chart(fig_factors, use_container_width=True)

    # --- CHART 2: Heatmap ---
    st.subheader("Sanitation Disparities and Death Rates Across Geographic Zones")
    heatmap_data = clean_df.pivot_table(values='Cholera case fatality rate', index='WHO Region',
                                        columns='Sanitation_Level', aggfunc='mean').reindex(columns=['Low', 'Medium', 'High'])
    fig_heatmap = px.imshow(heatmap_data, labels=dict(x="Sanitation Level", y="", color="Avg. Fatality Rate"),
                            color_continuous_scale='Reds')
    fig_heatmap.update_layout(height=190, margin=dict(l=0, r=10, t=0, b=0))
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # --- CHART 3: REGIONAL CASES BY GENDER ---
    st.subheader("Regional Gender Gaps in Cholera Cases")
    pyramid_data = clean_df.groupby(['WHO Region', 'Gender'])['Number of reported cases of cholera'].sum().reset_index()
    pyramid_data['Cases'] = pyramid_data.apply(
        lambda row: -row['Number of reported cases of cholera'] if row['Gender'] == 'Male' else row['Number of reported cases of cholera'], axis=1)
    fig_pyramid = px.bar(pyramid_data, y='WHO Region', x='Cases', color='Gender',
                         orientation='h', barmode='relative',
                         color_discrete_map={'Female': '#E6443E', 'Male': '#FFA07A'},
                         labels={'Cases': 'Number of Reported Cases', 'WHO Region': ''})
    fig_pyramid.update_layout(
        xaxis=dict(tickformat=',.0f', tickvals=[-50000000, -25000000, 0, 25000000, 50000000],
                   ticktext=['50M', '25M', '0', '25M', '50M']),
        yaxis_autorange='reversed', height=160, margin=dict(l=0, r=10, t=10, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_pyramid, use_container_width=True)
