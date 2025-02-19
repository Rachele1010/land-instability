import streamlit as st
import pandas as pd
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file

def visualization_section(df):
    """Handles the display of data table, map, and coordinate correction."""
    if df is None or df.empty:
        st.warning("No data available for visualization.")
        return

    col1, col2, col3 = st.columns([1, 2, 1])  # Tabella | Mappa | Modifica coordinate

    with col1:
        st.subheader("📋 Data Table")
        st.dataframe(df)

    with col2:
        st.subheader("🗺 Data Mapping")

        # Auto-detect delle colonne lat/lon/x/y
        possible_lat_cols = [col for col in df.columns if any(x in col.lower() for x in ["lat", "x"])]
        possible_lon_cols = [col for col in df.columns if any(x in col.lower() for x in ["lon", "y"])]

        # Seleziona le colonne migliori se disponibili
        lat_col = possible_lat_cols[0] if possible_lat_cols else None
        lon_col = possible_lon_cols[0] if possible_lon_cols else None

        # Controllo se sono state trovate colonne valide
        if lat_col and lon_col:
            df_map = df[[lat_col, lon_col]].dropna()
            df_map.columns = ["lat", "lon"]

            # Mostra la mappa se ci sono coordinate valide
            if not df_map.empty:
                st.map(df_map)
            else:
                st.warning("No valid latitude/longitude data to display on the map.")
        else:
            st.warning("No valid coordinate columns found for mapping.")

    with col3:
        st.subheader("✏️ Edit Point Coordinates")

        if lat_col and lon_col:
            # Permetti di selezionare la colonna corretta se l'auto-detect ha sbagliato
            lat_col = st.selectbox("Select Latitude Column", df.columns, index=df.columns.get_loc(lat_col))
            lon_col = st.selectbox("Select Longitude Column", df.columns, index=df.columns.get_loc(lon_col))

            # Verifica se le colonne selezionate sono numeriche
            if not pd.api.types.is_numeric_dtype(df[lat_col]) or not pd.api.types.is_numeric_dtype(df[lon_col]):
                st.warning("Selected columns must be numeric.")
                return

            # Seleziona il punto da modificare
            point_id = st.selectbox("Select a point to edit", df.index)

            if point_id is not None:
                try:
                    old_lat = float(df.at[point_id, lat_col])
                    old_lon = float(df.at[point_id, lon_col])

                    new_lat = st.number_input(
                        "New Latitude", value=old_lat, format="%.6f", key=f"new_lat_{point_id}"
                    )
                    new_lon = st.number_input(
                        "New Longitude", value=old_lon, format="%.6f", key=f"new_lon_{point_id}"
                    )

                    if st.button("Update Coordinates", key=f"update_btn_{point_id}"):
                        df.at[point_id, lat_col] = new_lat
                        df.at[point_id, lon_col] = new_lon
                        st.success(f"✅ Updated point {point_id}: ({new_lat}, {new_lon})")
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
