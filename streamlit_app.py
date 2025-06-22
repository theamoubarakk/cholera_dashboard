import numpy as np
import streamlit as st


with st.container():
    # Aggregate and convert
    map_df = df.groupby("Country")["Number of reported cases of cholera"].sum().reset_index()
    map_df["Number of reported cases of cholera"] = pd.to_numeric(
        map_df["Number of reported cases of cholera"], errors="coerce"
    ).fillna(0)

    # Apply log scale for color clarity
    map_df["Log_Cases"] = np.log1p(map_df["Number of reported cases of cholera"])

    fig = px.choropleth(
        map_df,
        locations="Country",
        locationmode="country names",
        color="Log_Cases",
        hover_name="Country",
        hover_data={"Log_Cases": False, "Number of reported cases of cholera": True},
        title="Global Cholera Cases (Log Scale)",
        color_continuous_scale="OrRd",
        template="plotly_white"
    )

    fig.update_geos(
        projection_type="natural earth",
        showcountries=True,
        showcoastlines=True,
        showland=True,
        fitbounds="locations"
    )

    st.plotly_chart(fig, use_container_width=True)
