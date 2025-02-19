import streamlit as st
import pandas as pd
import io
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
import plotly.express as px

def map_combined_datasets(dataframes, filenames):
    """
    Funzione per mappare più dataset con colonne di latitudine e longitudine,
    includendo il rilevamento automatico delle coordinate e un popup con il nome del file.
    
    Args:
        dataframes (list of pd.DataFrame): Lista di DataFrame caricati.
        filenames (list of str): Lista di nomi dei file corrispondenti ai DataFrame.
    """
    combined_df = pd.DataFrame(columns=['lat', 'lon', 'info'])

    col1, col2 = st.columns([3, 1])  # Colonna sinistra per la mappa, destra per la selezione del file

    with col1:
        st.subheader("🗺 Mappa dei Dati")

        for i, df in enumerate(dataframes):
            if df is not None:
                # Auto-detect delle colonne per le coordinate (lat/lon oppure x/y)
                possible_lat_cols = [col for col in df.columns if any(x in col.lower() for x in ["lat", "x"])]
                possible_lon_cols = [col for col in df.columns if any(x in col.lower() for x in ["lon", "y"])]

                lat_col = possible_lat_cols[0] if possible_lat_cols else None
                lon_col = possible_lon_cols[0] if possible_lon_cols else None

                if lat_col and lon_col:
                    df_map = df[[lat_col, lon_col]].dropna().copy()
                    df_map.columns = ["lat", "lon"]  # Rinomina per uniformità
                    df_map['info'] = filenames[i]  # Assegna il nome del file come info per il popup

                    # Verifica che lat e lon siano numerici
                    df_map['lat'] = pd.to_numeric(df_map['lat'], errors='coerce')
                    df_map['lon'] = pd.to_numeric(df_map['lon'], errors='coerce')

                    # Rimuove righe con valori NaN nelle coordinate
                    df_map = df_map.dropna(subset=['lat', 'lon'])

                    # Unisce al DataFrame combinato
                    combined_df = pd.concat([combined_df, df_map], ignore_index=True)

        # Visualizza la mappa solo se ci sono dati validi
        if not combined_df.empty:
            fig = px.scatter_mapbox(
                combined_df, 
                lat="lat", lon="lon", 
                hover_name="info",  # Mostra il nome del file nel popup
                zoom=5, 
                height=500
            )
            fig.update_layout(mapbox_style="carto-positron")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nessun dato valido disponibile per la visualizzazione.")

    with col2:
        st.subheader("📂 Seleziona un Dataset")
        if filenames:
            selected_file = st.selectbox("Scegli il dataset da visualizzare", filenames)
            index = filenames.index(selected_file)
            st.dataframe(dataframes[index])  # Mostra il DataFrame selezionato



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
    map_combined_datasets(df_list)
