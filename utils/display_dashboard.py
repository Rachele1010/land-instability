import streamlit as st
import pandas as pd
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
import plotly.express as px

def map_combined_datasets(dataframes, filenames=None):
    """
    Mappa più dataset con coordinate, rilevando automaticamente lat/lon o x/y.
    Mostra tutti i punti nella stessa mappa.
    """
    if filenames is None:
        filenames = [f"Dataset {i+1}" for i in range(len(dataframes))]

    combined_df = pd.DataFrame(columns=['lat', 'lon', 'file'])

    col1, col2 = st.columns([3, 1])  # Layout: Mappa a sinistra, selectbox a destra

    selected_columns = {}  # Dizionario per salvare le colonne selezionate

    with col2:  # Selezione delle coordinate
        st.subheader("📂 Dataset Caricati")

        if not dataframes:
            st.error("❌ Nessun dataset disponibile.")
            return
        
        for i, (df, filename) in enumerate(zip(dataframes, filenames)):
            if df is None or df.empty:
                st.warning(f"⚠ Il dataset '{filename}' è vuoto.")
                continue

            # Auto-detect colonne per latitudine e longitudine
            possible_lat_cols = [col for col in df.columns if any(x in col.lower() for x in ["lat", "x"])]
            possible_lon_cols = [col for col in df.columns if any(x in col.lower() for x in ["lon", "y"])]

            if not possible_lat_cols or not possible_lon_cols:
                st.warning(f"⚠ Nessuna colonna lat/lon o x/y trovata in '{filename}'.")
                continue

            # Selezione manuale delle colonne
            lat_col = st.selectbox(f"Colonna di latitudine per {filename}", possible_lat_cols, key=f"lat_{i}")
            lon_col = st.selectbox(f"Colonna di longitudine per {filename}", possible_lon_cols, key=f"lon_{i}")

            # Salva le colonne selezionate
            selected_columns[filename] = (lat_col, lon_col)

            # Prepara il DataFrame per la mappa
            df_map = df[[lat_col, lon_col]].dropna().copy()
            df_map.columns = ["lat", "lon"]
            df_map["file"] = filename  # Usa il nome del file per il popup

            # Aggiungi al dataset combinato
            combined_df = pd.concat([combined_df, df_map], ignore_index=True)

    with col1:  # Mostra la mappa con tutti i dataset combinati
        st.subheader("🗺 Data Mapping")

        if not combined_df.empty:
            fig = px.scatter_mapbox(
                combined_df, 
                lat="lat", lon="lon", 
                hover_name="file",  # Mostra il nome del file nel popup
                zoom=5, 
                height=800
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("❌ Nessun dato valido per visualizzare la mappa.")
