import streamlit as st
import pandas as pd
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def map_combined_datasets(dataframes, filenames=None):
    """
    Mappa più dataset con coordinate e popups, mostrando tutti i dati insieme correttamente.
    """
    if filenames is None:
        filenames = [f"Dataset {i+1}" for i in range(len(dataframes))]

    if not dataframes:
        st.error("❌ Nessun dataset disponibile.")
        return

    combined_df = pd.DataFrame(columns=['lat', 'lon', 'file'])
    colors = ["red", "blue", "green", "purple", "orange", "pink"]  # Colori per i dataset

    st.subheader("🗺 Data Mapping")

    fig = go.Figure()
    all_latitudes = []
    all_longitudes = []

    # Iteriamo su tutti i dataset per aggiungerli alla mappa
    for i, (df, filename) in enumerate(zip(dataframes, filenames)):
        try:
            st.write(f"🔍 Dataset: {filename}")  # Debug per vedere i dataset caricati

            lat_col = st.session_state.get(f"lat_{i}")
            lon_col = st.session_state.get(f"lon_{i}")

            if lat_col and lon_col and lat_col in df.columns and lon_col in df.columns:
                df_map = df[[lat_col, lon_col]].dropna().copy()
                df_map.columns = ["lat", "lon"]
                df_map["file"] = filename

                # Conversione forzata a numerico
                df_map["lat"] = pd.to_numeric(df_map["lat"], errors="coerce")
                df_map["lon"] = pd.to_numeric(df_map["lon"], errors="coerce")

                # Controllo per dati validi
                df_map = df_map.dropna()

                if df_map.empty:
                    st.warning(f"⚠ Nessun dato valido in '{filename}'.")
                    continue

                # Aggiunge i dati al dataframe combinato
                combined_df = pd.concat([combined_df, df_map], ignore_index=True)

                all_latitudes.extend(df_map["lat"].tolist())
                all_longitudes.extend(df_map["lon"].tolist())

                # Aggiunge i punti alla mappa
                fig.add_trace(go.Scattermapbox(
                    lat=df_map["lat"],
                    lon=df_map["lon"],
                    mode="markers+text",
                    text=[f"{filename}<br>({lat}, {lon})" for lat, lon in zip(df_map["lat"], df_map["lon"])],  
                    marker=dict(
                        size=15,  # Punti più grandi
                        color=colors[i % len(colors)]
                    ),
                    name=filename
                ))
        except Exception as e:
            st.warning(f"⚠ Errore con '{filename}': {e}")

    # Se non ci sono dati validi, mostra un messaggio di avviso
    if combined_df.empty:
        st.warning("❌ Nessun dato valido per visualizzare la mappa.")
        return

    # Calcoliamo il centro della mappa
    if all_latitudes and all_longitudes:
        center_lat = sum(all_latitudes) / len(all_latitudes)
        center_lon = sum(all_longitudes) / len(all_longitudes)
    else:
        center_lat, center_lon = 0, 0  # Default se i dati non sono validi

    # Configurazione della mappa con zoom automatico
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=6  # Zoom migliorato
        ),
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
