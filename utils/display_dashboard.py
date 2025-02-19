import streamlit as st
import pandas as pd
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
import plotly.express as px

import streamlit as st
import pandas as pd
import plotly.express as px

def map_combined_datasets(dataframes, filenames=None):
    """
    Mappa più dataset con coordinate e permette la selezione di un file per correggere le coordinate.
    """
    if filenames is None:
        filenames = [f"Dataset {i+1}" for i in range(len(dataframes))]

    combined_df = pd.DataFrame(columns=['lat', 'lon', 'file'])

    col1, col2 = st.columns([3, 1])  # Layout: Mappa a sinistra, selezione dataset a destra

    with col2:  
        st.subheader("📂 Dataset Caricati")

        if not dataframes:
            st.error("❌ Nessun dataset disponibile.")
            return
        
        # Seleziona quale file correggere
        file_to_edit_index = st.selectbox(
            "Seleziona il dataset da modificare", 
            range(len(filenames)), 
            format_func=lambda i: filenames[i]
        )

        df_to_edit = dataframes[file_to_edit_index]
        filename_to_edit = filenames[file_to_edit_index]

        if df_to_edit is None or df_to_edit.empty:
            st.warning(f"⚠ Il dataset '{filename_to_edit}' è vuoto.")
            return

        # Rimuove spazi e caratteri speciali dai nomi delle colonne
        df_to_edit.columns = df_to_edit.columns.str.strip().str.replace(r"[^\w\s]", "", regex=True)

        # Selezione manuale delle colonne per il dataset scelto
        lat_col = st.selectbox(f"Colonna latitudine ({filename_to_edit})", df_to_edit.columns, key=f"lat_{file_to_edit_index}")
        lon_col = st.selectbox(f"Colonna longitudine ({filename_to_edit})", df_to_edit.columns, key=f"lon_{file_to_edit_index}")

    with col1:  
        st.subheader("🗺 Data Mapping")

        # Combina tutti i dataset nella mappa
        for i, (df, filename) in enumerate(zip(dataframes, filenames)):
            try:
                df.columns = df.columns.str.strip().str.replace(r"[^\w\s]", "", regex=True)
                lat_col = st.session_state.get(f"lat_{i}")
                lon_col = st.session_state.get(f"lon_{i}")

                if lat_col and lon_col and lat_col in df.columns and lon_col in df.columns:
                    df_map = df[[lat_col, lon_col]].dropna().copy()
                    df_map.columns = ["lat", "lon"]
                    df_map["file"] = filename
                    combined_df = pd.concat([combined_df, df_map], ignore_index=True)
            except Exception as e:
                st.warning(f"⚠ Errore con '{filename}': {e}")

        # Mostra la mappa con tutti i dati
        if not combined_df.empty:
            fig = px.scatter_mapbox(
                combined_df, 
                lat="lat", lon="lon", 
                hover_name="file",  
                zoom=5, 
                height=800
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
