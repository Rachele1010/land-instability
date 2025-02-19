import streamlit as st
import pandas as pd
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file

import streamlit as st
import pandas as pd

def visualization_section(df):
    """Handles the display of data table, map, and coordinate correction."""
    if df is None or df.empty:
        st.warning("No data available for visualization.")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Table")
        st.dataframe(df)

    with col2:
        st.subheader("Data Mapping")

        # Cerca colonne con lat/lon o x/y
        lat_col = [col for col in df.columns if "lat" in col.lower()]
        lon_col = [col for col in df.columns if "lon" in col.lower()]

        if not lat_col or not lon_col:
            lat_col = [col for col in df.columns if col.lower() in ["x"]]
            lon_col = [col for col in df.columns if col.lower() in ["y"]]

        # Se troviamo coordinate valide
        if lat_col and lon_col:
            lat_col, lon_col = lat_col[0], lon_col[0]
            df_map = df[[lat_col, lon_col]].dropna()
            df_map.columns = ['lat', 'lon']
            st.map(df_map)

            # Seleziona un punto da correggere
            st.subheader("Edit Point Coordinates")
            point_id = st.selectbox("Select a point to edit", df.index)

            if point_id is not None:
                old_lat, old_lon = df.at[point_id, lat_col], df.at[point_id, lon_col]

                new_lat = st.number_input("New Latitude", value=old_lat, format="%.6f")
                new_lon = st.number_input("New Longitude", value=old_lon, format="%.6f")

                if st.button("Update Coordinates"):
                    df.at[point_id, lat_col] = new_lat
                    df.at[point_id, lon_col] = new_lon
                    st.success(f"Updated point {point_id}: ({new_lat}, {new_lon})")
                    st.experimental_rerun()

        else:
            st.write("No valid coordinate columns ('lat/lon' or 'x/y') found for mapping.")


    st.subheader("Data Plotting")
    col1, col2, col3 = st.columns(3)
    with col1:
        x_axis = st.selectbox("Select X axis", df.columns.tolist(), key=f"x_axis_{df.shape}")
    with col2:
        y_axis = st.selectbox("Select Y axis", df.columns.tolist(), key=f"y_axis_{df.shape}")
    with col3:
        plot_type = st.selectbox("Select plot type", [
            "Basic Scatter", "Basic Bar", "Basic Line", "Mixed Line and Bar", 
            "Calendar Heatmap", "DataZoom"
        ], key=f"plot_type_{df.shape}")
    if x_axis and y_axis and plot_type:
        create_and_render_plot(df, x_axis, y_axis, plot_type)

def display_dashboard():
    #st.header("File Upload and Management")
    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, type=['csv', 'xlsx', 'txt'])
    if uploaded_files:
        for uploaded_file in uploaded_files:
            df = load_file(uploaded_file)
            if df is not None:
                df = process_file(df)  # Elabora i dati prima di passarlo alla visualizzazione
                st.subheader(f"File: {uploaded_file.name}")
                visualization_section(df)

# Esegui la dashboard
display_dashboard()
