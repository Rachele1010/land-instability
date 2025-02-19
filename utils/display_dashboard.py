import streamlit as st
import pandas as pd
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
import plotly.express as px
import plotly.graph_objects as go

def map_combined_datasets(dataframes, filenames=None):
    """
    Mappa più dataset con coordinate e popups, garantendo che tutti i punti vengano plottati correttamente.
    """
    if filenames is None:
        filenames = [f"Dataset {i+1}" for i in range(len(dataframes))]

    if not dataframes:
        st.error("❌ Nessun dataset disponibile.")
        return

    col1, col2 = st.columns([3, 1])  
    colors = ["red", "blue", "green", "purple", "orange", "pink"]

    with col2:
        st.subheader("📂 Dataset Caricati")

        # Creazione di selectbox per ogni dataset
        lat_columns = []
        lon_columns = []
        
        for i, df in enumerate(dataframes):
            if df is None or df.empty:
                st.warning(f"⚠ Il dataset '{filenames[i]}' è vuoto.")
                continue
            
            lat_col = st.selectbox(f"Colonna latitudine ({filenames[i]})", df.columns, key=f"lat_{i}")
            lon_col = st.selectbox(f"Colonna longitudine ({filenames[i]})", df.columns, key=f"lon_{i}")

            lat_columns.append(lat_col)
            lon_columns.append(lon_col)

    with col1:
        st.subheader("🗺 Data Mapping")

        fig = go.Figure()
        all_latitudes = []
        all_longitudes = []

        for i, (df, filename) in enumerate(zip(dataframes, filenames)):
            try:
                # Recupera le colonne selezionate correttamente
                lat_col = lat_columns[i]
                lon_col = lon_columns[i]

                if lat_col and lon_col and lat_col in df.columns and lon_col in df.columns:
                    df_map = df[[lat_col, lon_col]].dropna().copy()
                    df_map.columns = ["lat", "lon"]
                    df_map["file"] = filename

                    df_map["lat"] = pd.to_numeric(df_map["lat"], errors="coerce")
                    df_map["lon"] = pd.to_numeric(df_map["lon"], errors="coerce")
                    df_map = df_map.dropna()

                    if df_map.empty:
                        st.warning(f"⚠ '{filename}' non ha dati validi dopo il cleaning.")
                        continue

                    all_latitudes.extend(df_map["lat"].tolist())
                    all_longitudes.extend(df_map["lon"].tolist())

                    # Aggiunta punti alla mappa
                    fig.add_trace(go.Scattermapbox(
                        lat=df_map["lat"],
                        lon=df_map["lon"],
                        mode="markers",
                        marker=dict(size=15, color=colors[i % len(colors)]),
                        name=filename,
                        text=[f"{filename}<br>({lat}, {lon})" for lat, lon in zip(df_map["lat"], df_map["lon"])]
                    ))

            except Exception as e:
                st.warning(f"⚠ Errore con '{filename}': {e}")

        if not all_latitudes or not all_longitudes:
            st.warning("❌ Nessun dato valido per visualizzare la mappa.")
            return

        # Centro dinamico della mappa
        center_lat = sum(all_latitudes) / len(all_latitudes)
        center_lon = sum(all_longitudes) / len(all_longitudes)

        # Configura la mappa con zoom automatico e legenda
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=6  
            ),
            legend=dict(title="Legenda"),
            height=800
        )

        st.plotly_chart(fig, use_container_width=True)


def display_dashboard():
    """Dashboard per la gestione dei file con Drag & Drop."""
    st.header("📊 Data Analysis and Plotting")

    # Sidebar con file uploader
    st.sidebar.header("📂 Upload Files")
    uploaded_files = st.sidebar.file_uploader(
        "Drag & Drop your CSV files here", type=['csv', 'xlsx', 'txt'], accept_multiple_files=True
    )

    if not uploaded_files:
        st.sidebar.info("No files uploaded yet.")
        return
    
    df_list = []
    for uploaded_file in uploaded_files:
        df = load_file(uploaded_file)  # Carica il file
        if df is not None:
            df = process_file(df)  # Elabora i dati
            df_list.append(df)

    for idx, df in enumerate(df_list):
        st.subheader(f"Dataset {idx + 1} - {uploaded_files[idx].name}")

        col1, col2, col3 = st.columns([1, 1, 1])
        col4, col5 = st.columns([1, 2])

        with col1:
            x_axis = st.selectbox(f"X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
        with col2:
            y_axis = st.selectbox(f"Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
        with col3:
            plot_type = st.selectbox(f"Plot Type {idx + 1}", [
                "Basic Scatter", "Basic Bar", "Basic Line", "Mixed Line and Bar", 
                "Calendar Heatmap", "DataZoom"
            ], key=f"plot_type_{idx}")

        with col4:
            st.dataframe(df)
        with col5:
            if not df.empty:
                create_and_render_plot(df, x_axis, y_axis, plot_type)

    map_combined_datasets(df_list)
