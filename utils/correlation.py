import streamlit as st
import pandas as pd
import io
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
import streamlit as st
import streamlit as st
import pandas as pd
import plotly.express as px

import streamlit as st
import pandas as pd
import plotly.express as px

def map_combined_datasets(dataframes):
    """
    Funzione per mappare più dataset combinati con colonne di latitudine e longitudine,
    includendo il rilevamento automatico e la modifica delle coordinate.
    """
    combined_df = pd.DataFrame(columns=['lat', 'lon', 'info'])
    col1, col2 = st.columns([3, 1])  # Mappa | Modifica coordinate

    with col1:
        st.subheader("🗺 Data Mapping")

        for df in dataframes:
            if df is not None:
                # Auto-detect delle colonne lat/lon/x/y
                possible_lat_cols = [col for col in df.columns if any(x in col.lower() for x in ["lat", "x"])]
                possible_lon_cols = [col for col in df.columns if any(x in col.lower() for x in ["lon", "y"])]
                
                # Seleziona le colonne migliori se disponibili
                lat_col = possible_lat_cols[0] if possible_lat_cols else None
                lon_col = possible_lon_cols[0] if possible_lon_cols else None

                st.write(f"Detected lat_col: {lat_col}, lon_col: {lon_col}")  # Debugging line

                if lat_col and lon_col:
                    # Prepara il DataFrame per la mappa
                    df_map = df[[lat_col, lon_col]].dropna()
                    df_map.columns = ["lat", "lon"]
                    df['info'] = df.iloc[:, 0].astype(str)  # Usa la prima colonna come info per pop-up
                    
                    # Verifica se le colonne "lat", "lon", e "info" sono nel DataFrame
                    if 'lat' in df.columns and 'lon' in df.columns and 'info' in df.columns:
                        # Aggiungi le colonne 'lat', 'lon', 'info' al DataFrame combinato, solo se esistono
                        combined_df = pd.concat([combined_df, df[['lat', 'lon', 'info']]], ignore_index=True)
                    else:
                        st.warning("Required columns 'lat', 'lon', and 'info' are missing from the dataset.")
                    
                    # Pulisci e verifica che lat e lon siano numerici
                    combined_df['lat'] = pd.to_numeric(combined_df['lat'], errors='coerce')
                    combined_df['lon'] = pd.to_numeric(combined_df['lon'], errors='coerce')
                    
                    # Rimuovi righe con lat/lon non numerici
                    combined_df = combined_df.dropna(subset=['lat', 'lon'])
                    
                    # Visualizza il DataFrame per il debug
                    st.write("Combined DataFrame:", combined_df.head())
                    st.write("DataFrame columns:", combined_df.columns)
                    st.write("DataFrame dtypes:", combined_df.dtypes)

                    # Visualizza la mappa combinata se ci sono coordinate
                    if not combined_df.empty:
                        fig = px.scatter_mapbox(
                            combined_df, 
                            lat="lat", lon="lon", 
                            hover_name="info",  # Mostra le info come pop-up
                            zoom=5, 
                            height=500
                        )
                        fig.update_layout(mapbox_style="carto-positron")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No valid latitude/longitude data to display on the map.")
                else:
                    st.warning("No valid coordinate columns found for mapping.")
        
        # Visualizza la mappa combinata se ci sono coordinate
        if not combined_df.empty:
            fig = px.scatter_mapbox(
                combined_df, 
                lat="lat", lon="lon", 
                hover_name="info",  # Mostra le info come pop-up
                zoom=5, 
                height=500
            )
            fig.update_layout(mapbox_style="carto-positron")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No valid latitude or longitude data available for map display.")

def correlation():
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
        # Usa la funzione di caricamento e elaborazione dei file
        df = load_file(uploaded_file)  # Carica il file
        if df is not None:
            df = process_file(df)  # Elabora i dati
            df_list.append(df)

    # Creazione dinamica dei controlli e dei grafici
    for idx, df in enumerate(df_list):
        st.subheader(f"Dataset {idx + 1} - {uploaded_files[idx].name}")

        col1, col2, col3 = st.columns([1, 1, 1])  # Tre colonne per X, Y, tipo di grafico
        col4, col5 = st.columns([1, 2])  # Colonne per tabella e grafico

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
            st.dataframe(df)  # Mostra la tabella
        with col5:
            if not df.empty:
                create_and_render_plot(df, x_axis, y_axis, plot_type)  # Mostra il grafico

    # Mappatura combinata di tutti i dataset caricati
    st.subheader("🌍 Combined Map")
    map_combined_datasets(df_list)
