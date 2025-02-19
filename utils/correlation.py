import streamlit as st
import pandas as pd
import io
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
col1, col2 = st.columns([4, 1])
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
                    
                    # Mostra la mappa
                    if not df_map.empty:
                        st.map(df_map)
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
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No valid latitude or longitude data available for map display.")

    with col2:
        st.subheader("✏️ Edit Point Coordinates")

        for df in dataframes:
            if df is not None:
                # Seleziona il punto da modificare
                point_id = st.selectbox("Select a point to edit", df.index)

                # Auto-detect lat/lon columns for edit
                possible_lat_cols = [col for col in df.columns if any(x in col.lower() for x in ["lat", "x"])]
                possible_lon_cols = [col for col in df.columns if any(x in col.lower() for x in ["lon", "y"])]
                
                lat_col = possible_lat_cols[0] if possible_lat_cols else None
                lon_col = possible_lon_cols[0] if possible_lon_cols else None
                
                if lat_col and lon_col:
                    try:
                        # Permetti di selezionare la colonna corretta se l'auto-detect ha sbagliato
                        lat_col = st.selectbox("Select Latitude Column", df.columns, index=df.columns.get_loc(lat_col))
                        lon_col = st.selectbox("Select Longitude Column", df.columns, index=df.columns.get_loc(lon_col))

                        # Verifica se le colonne selezionate sono numeriche
                        if not pd.api.types.is_numeric_dtype(df[lat_col]) or not pd.api.types.is_numeric_dtype(df[lon_col]):
                            st.warning("Selected columns must be numeric.")
                            st.stop()

                        # Prendi i valori attuali delle coordinate
                        old_lat = float(df.at[point_id, lat_col])
                        old_lon = float(df.at[point_id, lon_col])

                        # Inserisci nuove coordinate
                        new_lat = st.number_input(f"Edit Latitude (Current: {old_lat})", value=old_lat)
                        new_lon = st.number_input(f"Edit Longitude (Current: {old_lon})", value=old_lon)

                        # Salva le modifiche
                        if new_lat != old_lat or new_lon != old_lon:
                            df.at[point_id, lat_col] = new_lat
                            df.at[point_id, lon_col] = new_lon
                            st.success("Coordinates updated successfully!")
                        else:
                            st.info("Coordinates are the same as the current ones.")
                    except Exception as e:
                        st.error(f"❌ Error updating coordinates: {e}")
                else:
                    st.warning("Unable to detect valid coordinate columns for editing.")


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
