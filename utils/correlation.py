import streamlit as st
import pandas as pd
import io
from utils.plotting import create_and_render_plot

def map_combined_datasets(dataframes):
    """
    Funzione per mappare più dataset combinati con colonne di latitudine e longitudine.
    """
    combined_df = pd.DataFrame(columns=['lat', 'lon'])

    for df in dataframes:
        if df is not None:
            lat_col = [col for col in df.columns if "lat" in col.lower()]
            lon_col = [col for col in df.columns if "lon" in col.lower()]
            if lat_col and lon_col:
                df = df.rename(columns={lat_col[0]: 'lat', lon_col[0]: 'lon'})
                combined_df = pd.concat([combined_df, df[['lat', 'lon']]], ignore_index=True)

    if not combined_df.empty:
        st.map(combined_df)
    else:
        st.warning("No valid latitude or longitude data available for map display.")

def correlation():
    """Dashboard per la gestione dei file con Drag & Drop."""
    st.set_page_config(layout="wide")  # Imposta il layout a tutta pagina
    st.header("📊 Data Analysis and Plotting")

    # Sidebar con file uploader
    st.sidebar.header("📂 Upload Files")
    uploaded_files = st.sidebar.file_uploader(
        "Drag & Drop your CSV files here", type=["csv"], accept_multiple_files=True
    )

    if not uploaded_files:
        st.sidebar.info("No files uploaded yet.")
        return
    
    df_list = []
    for uploaded_file in uploaded_files:
        df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
        df_list.append(df)

    # Creazione dinamica dei controlli e dei grafici
    for idx, df in enumerate(df_list):
        st.subheader(f"Dataset {idx + 1} - {uploaded_files[idx].name}")

        col1, col2, col3 = st.columns([1, 1, 1])  # Tre colonne per X, Y, tipo di grafico
        col4, col5 = st.columns([1, 2])  # Colonne per tabella e grafico

        with col1:
            x_axis = st.selectbox(f"🛠️ X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
        with col2:
            y_axis = st.selectbox(f"📈 Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
        with col3:
            plot_type = st.selectbox(f"🎨 Plot Type {idx + 1}", [
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

