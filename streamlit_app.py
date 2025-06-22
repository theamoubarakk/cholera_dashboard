import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("enriched_data_logical_cleaned.csv")
df["Number of reported cases of cholera"] = pd.to_numeric(df["Number of reported cases of cholera"], errors="coerce").fillna(0)
df["Number of reported deaths from cholera"] = pd.to_numeric(df["Number of reported deaths from cholera"], errors="coerce").fillna(0)
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

# Compute fatality rate if missing
df["Cholera case fatality rate"] = df.apply(
    lambda row: round(row["Number of reported deaths from cholera"] / row["Number of reported cases of cholera"], 4)
    if pd.isna(row["Cholera case fatality rate"]) and row["Number of reported cases of cholera"] > 0
    else row["Cholera case fatality rate"],
    axis=1
)

# Fill missing
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].fillna(df[col].mode()[0])
    else:
        df[col] = df[col].fillna(0)

# Create age groups
df["Age_Group"] = pd.cut(df["Age"], bins=[0, 18, 35, 50, 65, 100], labels=["0-18", "19-35", "36-50", "51-65", "66+"])

# Title
st.markdown("<h1 style='text-align:center;'>🌍 Global Cholera Tracker</h1>", unsafe_allow_html=True)

# Map
map_df = df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
map_df["Log_Cases"] = map_df["Number of reported cases of cholera"].apply(lambda x: np.log10(x) if x > 0 else 0)
fig_map = px.choropleth(map_df, locations="Country", locationmode="country names",
                        color="Log_Cases", title="Reported Cholera Cases (Log Scale)",
                        color_continuous_scale="OrRd")

# Line chart
time_df = df.groupby("Year")["Number of reported cases of cholera"].sum().reset_index()
fig_trend = px.line(time_df, x="Year", y="Number of reported cases of cholera", markers=True,
                    title="Cholera Cases Over Time")

# Heatmap
# Heatmap: Cholera Cases by Gender and Age
heatmap_data = filtered_df.groupby(['Gender', 'Age'])['Number of reported cases of cholera'].sum().reset_index()
heatmap_pivot = heatmap_data.pivot(index='Gender', columns='Age', values='Number of reported cases of cholera').fillna(0)

fig_heatmap = px.imshow(
    heatmap_pivot.values,
    labels=dict(x="Age", y="Gender", color="Cholera Cases"),
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    color_continuous_scale="Reds"
)
fig_heatmap.update_layout(title="Cholera Cases by Gender and Age")

# Correlation bar
numeric_df = df.select_dtypes(include=[np.number])
corrs = numeric_df.corr()["Number of reported cases of cholera"].drop("Number of reported cases of cholera")
top_corrs = corrs.sort_values(key=abs, ascending=False).head(10)
corr_df = pd.DataFrame({"Feature": top_corrs.index, "Correlation": top_corrs.values})
fig_corr = px.bar(corr_df, x="Correlation", y="Feature", orientation='h',
                  title="Top Correlating Features with Cholera Cases")

# Layout
col1, col2 = st.columns([1, 1])
with col1:
    st.plotly_chart(fig_map, use_container_width=True)
with col2:
    st.plotly_chart(fig_trend, use_container_width=True)

col3, col4 = st.columns([1, 1])
with col3:
    st.plotly_chart(fig_heatmap, use_container_width=True)
with col4:
    st.plotly_chart(fig_corr, use_container_width=True)
