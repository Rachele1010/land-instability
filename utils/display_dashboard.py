import streamlit as st
import pandas as pd
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file

def map_combined_datasets(dataframes, filenames=None):
    """
    Mappa più dataset con coordinate, rilevando automaticamente lat/lon o x/y.
    Mostra un popup con il nome del file e permette di selezionare manualmente le coordinate nella colonna destra.
    """
    if filenames is None:
        filenames = [f"Dataset {i+1}" for i in range(len(dataframes))]

    combined_df = pd.DataFrame(columns=['lat', 'lon', 'file'])
    col1, col2 = st.columns([3, 1])  # Layout: Mappa a sinistra, selectbox a destra

    with col2:  # Colonna per selezione dataset e coordinate
        st.subheader("📂 Dataset Caricati")
        
        if not dataframes:
            st.error("❌ Nessun dataset disponibile.")
            return

        dataset_index = st.selectbox("Seleziona il dataset", range(len(filenames)), format_func=lambda i: filenames[i])
        df = dataframes[dataset_index]
        filename = filenames[dataset_index]

        if df is None or df.empty:
            st.warning("⚠ Il dataset selezionato è vuoto.")
            return

        # Auto-detect colonne per latitudine e longitudine
        possible_lat_cols = [col for col in df.columns if any(x in col.lower() for x in ["lat", "x"])]
        possible_lon_cols = [col for col in df.columns if any(x in col.lower() for x in ["lon", "y"])]

        if not possible_lat_cols or not possible_lon_cols:
            st.warning(f"⚠ Nessuna colonna lat/lon o x/y trovata in '{filename}'.")
            return

        # Selezione manuale delle colonne
        lat_col = st.selectbox("Seleziona la colonna di latitudine", possible_lat_cols, key=f"lat_{filename}")
        lon_col = st.selectbox("Seleziona la colonna di longitudine", possible_lon_cols, key=f"lon_{filename}")

    with col1:  # Colonna per la mappa
        st.subheader("🗺 Data Mapping")

        # Prepara il DataFrame per la mappa
        df_map = df[[lat_col, lon_col]].dropna().copy()
        df_map.columns = ["lat", "lon"]
        df_map["file"] = filename  # Usa il nome del file come info per il popup

        # Aggiungi al dataset combinato
        combined_df = pd.concat([combined_df, df_map], ignore_index=True)

        # Mostra la mappa con popups
        if not combined_df.empty:
            fig = px.scatter_mapbox(
                combined_df, 
                lat="lat", lon="lon", 
                hover_name="file",  # Mostra il nome del file nel popup
                zoom=5, 
                height=500
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("❌ Nessun dato valido per visualizzare la mappa.")


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
