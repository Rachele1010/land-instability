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
    Mappa più dataset con coordinate, rilevando automaticamente lat/lon o x/y.
    Ogni dataset ha un colore diverso.
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
        
        dataset_index = st.selectbox(
            "Seleziona il dataset per scegliere le coordinate", 
            range(len(filenames)), 
            format_func=lambda i: filenames[i]
        )

        df = dataframes[dataset_index]
        filename = filenames[dataset_index]

        if df is None or df.empty:
            st.warning(f"⚠ Il dataset '{filename}' è vuoto.")
            return

        # Selezione manuale delle colonne lat/lon
        lat_col = st.selectbox(f"Colonna latitudine ({filename})", df.columns, key=f"lat_{dataset_index}")
        lon_col = st.selectbox(f"Colonna longitudine ({filename})", df.columns, key=f"lon_{dataset_index}")

    with col1:  
        st.subheader("🗺 Data Mapping")

        # Unisce i dataset con colori diversi
        for i, (df, filename) in enumerate(zip(dataframes, filenames)):
            try:
                lat_col = st.session_state.get(f"lat_{i}")
                lon_col = st.session_state.get(f"lon_{i}")

                if lat_col and lon_col and lat_col in df.columns and lon_col in df.columns:
                    df_map = df[[lat_col, lon_col]].dropna().copy()
                    df_map.columns = ["lat", "lon"]
                    df_map["file"] = filename
                    combined_df = pd.concat([combined_df, df_map], ignore_index=True)
            except Exception as e:
                st.warning(f"⚠ Errore con '{filename}': {e}")

        # Mostra la mappa con colori diversi per dataset
        if not combined_df.empty:
            fig = px.scatter_mapbox(
                combined_df, 
                lat="lat", lon="lon", 
                color="file",  # Differenzia i punti per dataset
                hover_name="file",  
                zoom=5, 
                height=800
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("❌ Nessun dato valido per visualizzare la mappa.")

    # Mappatura combinata di tutti i dataset caricati
    map_combined_datasets(df_list)
