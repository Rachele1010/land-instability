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
        st.subheader("📋 Data Table")
        st.dataframe(df)

    with col2:
        st.subheader("🗺 Data Mapping")

        # Cerca colonne che possono essere usate come coordinate
        possible_lat_cols = [col for col in df.columns if "lat" in col.lower() or col.lower() == "x"]
        possible_lon_cols = [col for col in df.columns if "lon" in col.lower() or col.lower() == "y"]

        # Se non vengono trovate, mostra un errore
        if not possible_lat_cols or not possible_lon_cols:
            st.warning("No valid latitude/longitude columns found in the dataset.")
            return
        
        # Selezione automatica delle colonne
        lat_col = possible_lat_cols[0]
        lon_col = possible_lon_cols[0]

        # Conversione e pulizia dei dati
        df_map = df[[lat_col, lon_col]].dropna()
        df_map["lat"] = pd.to_numeric(df_map[lat_col], errors="coerce")
        df_map["lon"] = pd.to_numeric(df_map[lon_col], errors="coerce")
        df_map = df_map.dropna()

        if not df_map.empty:
            st.map(df_map[["lat", "lon"]])
        else:
            st.warning("No valid latitude/longitude data to display on the map.")

    with col3:
        st.subheader("✏️ Edit Point Coordinates")

        # Seleziona un punto da correggere
        point_id = st.selectbox("Select a point to edit", df.index, key="point_select")

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
