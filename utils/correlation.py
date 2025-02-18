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
    st.header("Data Analysis and Plotting")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    col5, col6 = st.columns([1, 1])
    with col1:
    # Drag & Drop per il caricamento multiplo di file CSV
        uploaded_files = st.file_uploader("Drag & Drop your CSV files here", type=["csv"], accept_multiple_files=True)
        if not uploaded_files:
            st.info("No files uploaded yet.")
            return
        
        df_list = []
    with col5:
        # Caricamento e visualizzazione dei dati
        for uploaded_file in uploaded_files:
            df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
            df_list.append(df)
            st.write(f"### {uploaded_file.name}")
            st.dataframe(df)
   for idx, df in enumerate(df_list):
        with col2:
            x_axis = st.selectbox(f"Select X axis for Dataset {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")

        with col3:
            y_axis = st.selectbox(f"Select Y axis for Dataset {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")

        with col4:
            plot_type = st.selectbox(f"Select plot type for Dataset {idx + 1}", [
                "Basic Scatter", "Basic Bar", "Basic Line", "Mixed Line and Bar", 
                "Calendar Heatmap", "DataZoom"
            ], key=f"plot_type_{idx}")
        with col6:
            if not df.empty:
                create_and_render_plot(df, x_axis, y_axis, plot_type)

    # Mappatura combinata di tutti i dataset caricati
    map_combined_datasets(df_list)
