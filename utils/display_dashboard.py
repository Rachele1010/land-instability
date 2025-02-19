import streamlit as st
import pandas as pd
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file

def visualization_section(df):
    """Handles the display of data table, map, and coordinate correction."""
    if df is None or df.empty:
        st.warning("No data available for visualization.")
        return

    col1, col2, col3 = st.columns([1, 2, 1])  # 3 colonne: tabella | mappa | modifica coordinate

    with col1:
        st.subheader("Data Table")
        st.dataframe(df)

    with col2:
        st.subheader("Data Mapping")

        # Dropdown per selezionare le colonne delle coordinate
        lat_col = st.selectbox("Select Latitude Column", df.columns, key="lat_select")
        lon_col = st.selectbox("Select Longitude Column", df.columns, key="lon_select")

        # Verifica che le colonne siano valide
        if lat_col and lon_col:
            try:
                df_map = df[[lat_col, lon_col]].dropna()

                # Converti le colonne in float, ignorando errori
                df_map["lat"] = pd.to_numeric(df_map[lat_col], errors="coerce")
                df_map["lon"] = pd.to_numeric(df_map[lon_col], errors="coerce")

                # Rimuovi eventuali valori NaN generati dalla conversione
                df_map = df_map.dropna()

                if not df_map.empty:
                    st.map(df_map[["lat", "lon"]])
                else:
                    st.warning("No valid latitude/longitude data to display on the map.")
            except Exception as e:
                st.error(f"Error processing map data: {e}")

    with col3:
        st.subheader("Edit Point Coordinates")

        # Seleziona un punto da correggere
        point_id = st.selectbox("Select a point to edit", df.index, key="point_select")

        if point_id is not None:
            try:
                old_lat, old_lon = df.at[point_id, lat_col], df.at[point_id, lon_col]

                new_lat = st.number_input("New Latitude", value=float(old_lat), format="%.6f", key="new_lat")
                new_lon = st.number_input("New Longitude", value=float(old_lon), format="%.6f", key="new_lon")

                if st.button("Update Coordinates", key="update_btn"):
                    df.at[point_id, lat_col] = new_lat
                    df.at[point_id, lon_col] = new_lon
                    st.success(f"Updated point {point_id}: ({new_lat}, {new_lon})")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Error updating coordinates: {e}")


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
