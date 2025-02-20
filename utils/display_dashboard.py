import streamlit as st
import pandas as pd
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
import plotly.express as px
import plotly.graph_objects as go

def map_combined_datasets(dataframes, filenames=None):
    """
    Mappa più dataset con coordinate e popups, centrando la mappa sui dati caricati o sull'Italia di default.
    """
    if filenames is None:
        filenames = [f"Dataset {i+1}" for i in range(len(dataframes))]

    if not dataframes:
        st.error("❌ Nessun dataset disponibile.")
        return

    col1, col2 = st.columns([3, 1])
    colors = ["red", "blue", "green", "purple", "orange", "pink"]
    
    # Centro predefinito: Italia
    default_center = {"lat": 41.8719, "lon": 12.5674}  

    with col2:
        st.subheader("📂 Dataset Caricati")
        lat_columns = []
        lon_columns = []
        info_columns = []  # Colonne aggiuntive per il popup
        
        for i, df in enumerate(dataframes):
            if df is None or df.empty:
                st.warning(f"⚠ Il dataset '{filenames[i]}' è vuoto.")
                continue
            
            lat_col = st.selectbox(f"Colonna latitudine ({filenames[i]})", df.columns, key=f"lat_{i}")
            lon_col = st.selectbox(f"Colonna longitudine ({filenames[i]})", df.columns, key=f"lon_{i}")
            info_col = st.multiselect(f"Seleziona colonne info ({filenames[i]})", df.columns, key=f"info_{i}")

            lat_columns.append(lat_col)
            lon_columns.append(lon_col)
            info_columns.append(info_col)
    
    with col1:
        st.subheader("🗺 Data Mapping")

        fig = go.Figure()
        all_latitudes = []
        all_longitudes = []
        first_valid_center = None  # Per salvare il primo dataset valido

        for i, (df, filename) in enumerate(zip(dataframes, filenames)):
            try:
                lat_col = lat_columns[i]
                lon_col = lon_columns[i]
                info_col = info_columns[i]

                if lat_col and lon_col and lat_col in df.columns and lon_col in df.columns:
                    df_map = df.dropna(subset=[lat_col, lon_col]).copy()
                    df_map["lat"] = pd.to_numeric(df_map[lat_col], errors="coerce")
                    df_map["lon"] = pd.to_numeric(df_map[lon_col], errors="coerce")
                    df_map = df_map.dropna()

                    if df_map.empty:
                        st.warning(f"⚠ '{filename}' non ha dati validi dopo il cleaning.")
                        continue

                    all_latitudes.extend(df_map["lat"].tolist())
                    all_longitudes.extend(df_map["lon"].tolist())

                    # Imposta il centro della mappa con il primo dataset valido
                    if first_valid_center is None and not df_map.empty:
                        first_valid_center = {
                            "lat": df_map["lat"].iloc[0], 
                            "lon": df_map["lon"].iloc[0]
                        }

                    # Crea popup con le colonne selezionate
                    popup_info = df_map.apply(lambda row: "<br>".join([f"<b>{col}</b>: {row[col]}" for col in info_col]), axis=1)

                    # Aggiunta punti alla mappa
                    fig.add_trace(go.Scattermapbox(
                        lat=df_map["lat"],
                        lon=df_map["lon"],
                        mode="markers",
                        marker=dict(size=15, color=colors[i % len(colors)]),
                        name=filename,
                        hoverinfo="text",
                        text=popup_info  
                    ))
            
            except Exception as e:
                st.warning(f"⚠ Errore con '{filename}': {e}")

        if not all_latitudes or not all_longitudes:
            st.warning("❌ Nessun dato valido per visualizzare la mappa.")
            return

        # Determina il centro della mappa
        if first_valid_center:
            center_lat = first_valid_center["lat"]
            center_lon = first_valid_center["lon"]
        else:
            center_lat, center_lon = default_center["lat"], default_center["lon"]

        # Configura la mappa con zoom automatico
        fig.update_layout(
            autosize=True,
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=6
            ),
            legend=dict(title="Legenda"),
            height=800,
            margin={"r":0,"t":0,"l":0,"b":0}  # Rimuove margini bianchi
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
