import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid
import re
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file

def sanitize_filename(filename):
    """Rimuove caratteri speciali e spazi, rendendo il nome del file sicuro per Streamlit."""
    return re.sub(r'\W+', '_', filename)

def map_combined_datasets(dataframes, filenames=None):
    if filenames is None:
        filenames = [f"Dataset {i+1}" for i in range(len(dataframes))]
    
    if not dataframes:
        st.error("❌ Nessun dataset disponibile.")
        return

    col1, col2 = st.columns([3, 1])
    colors = ["red", "blue", "green", "purple", "orange", "pink"]
    default_center = {"lat": 41.8719, "lon": 12.5674}  # Coordinate di default (Italia)
    
    # Varianti di nomi di colonne per latitudine e longitudine
    coordinate_variants = {
        "lat": ["lat", "latitude", "Latitudine", "y"],
        "lon": ["lon", "longitude", "Longitudine", "x"]
    }

    with col2:
        lat_columns, lon_columns = [], []
        for i, df in enumerate(dataframes):
            if df is None or df.empty:
                st.warning(f"⚠ Il dataset '{filenames[i]}' è vuoto.")
                continue

            detected_lat_col = next((col for col in coordinate_variants["lat"] if col in df.columns), None)
            detected_lon_col = next((col for col in coordinate_variants["lon"] if col in df.columns), None)
            
            with st.expander(f"File: {filenames[i]}"):
                safe_filename = sanitize_filename(filenames[i])  
                unique_id = uuid.uuid4().hex  # UUID per rendere la chiave unica

                # Seleziona la colonna di latitudine
                lat_col = st.selectbox(
                    f"Latitudine ({filenames[i]})",
                    df.columns,
                    index=df.columns.get_loc(detected_lat_col) if detected_lat_col in df.columns else 0,
                    key=f"lat_{safe_filename}_{i}_{unique_id}"  # Aggiungi UUID
                )
                
                # Seleziona la colonna di longitudine
                lon_col = st.selectbox(
                    f"Longitudine ({filenames[i]})",
                    df.columns,
                    index=df.columns.get_loc(detected_lon_col) if detected_lon_col in df.columns else 1,
                    key=f"lon_{safe_filename}_{i}_{unique_id}"  # Aggiungi UUID
                )
            
            lat_columns.append(lat_col)
            lon_columns.append(lon_col)

    with col1:
        st.subheader("🗺 Data Mapping")

        fig = go.Figure()
        all_latitudes, all_longitudes = [], []
        first_valid_center = None

        for i, (df, filename) in enumerate(zip(dataframes, filenames)):
            try:
                lat_col, lon_col = lat_columns[i], lon_columns[i]

                if lat_col in df.columns and lon_col in df.columns:
                    df_map = df.dropna(subset=[lat_col, lon_col]).copy()
                    df_map["lat"] = pd.to_numeric(df_map[lat_col], errors="coerce")
                    df_map["lon"] = pd.to_numeric(df_map[lon_col], errors="coerce")
                    df_map = df_map.dropna()

                    if df_map.empty:
                        st.warning(f"⚠ '{filename}' non ha dati validi dopo il cleaning.")
                        continue

                    all_latitudes.extend(df_map["lat"].tolist())
                    all_longitudes.extend(df_map["lon"].tolist())

                    if first_valid_center is None and not df_map.empty:
                        first_valid_center = {"lat": df_map["lat"].iloc[0], "lon": df_map["lon"].iloc[0]}

                    popup_info = df_map.apply(lambda row: "<br>".join([f"<b>{col}</b>: {row[col]}" for col in df.columns]), axis=1)

                    fig.add_trace(go.Scattermapbox(
                        lat=df_map["lat"], lon=df_map["lon"],
                        mode="markers", marker=dict(size=15, color=colors[i % len(colors)]),
                        name=filename, hoverinfo="text", text=popup_info
                    ))

            except Exception as e:
                st.warning(f"⚠ Errore con '{filename}': {e}")

        if not all_latitudes or not all_longitudes:
            st.warning("❌ Nessun dato valido per visualizzare la mappa.")
            return

        center_lat, center_lon = (first_valid_center or default_center).values()

        fig.update_layout(
            autosize=True,
            mapbox=dict(style="open-street-map", center=dict(lat=center_lat, lon=center_lon), zoom=6),
            height=800, margin={"r":0, "t":0, "l":0, "b":0}
        )

        st.plotly_chart(fig, use_container_width=True)

def display_dashboard():
    st.sidebar.header("📂 Upload Files")
    uploaded_files = st.sidebar.file_uploader("Carica i tuoi file CSV/XLSX", type=['csv', 'xlsx', 'txt'], accept_multiple_files=True)

    if not uploaded_files:
        st.sidebar.info("No files uploaded yet.")
        return

    df_list, filenames = [], []
    for uploaded_file in uploaded_files:
        df = load_file(uploaded_file)
        if df is not None:
            df = process_file(df)
            df_list.append(df)
            filenames.append(uploaded_file.name)

    tab1, tab2 = st.tabs(["🌍 Map Generator", "📊 Statistics"])

    with tab1:
        map_combined_datasets(df_list, filenames)

    with tab2:
        for i, df in enumerate(df_list):
            st.subheader(f"📈 Dataset {i+1} - {filenames[i]}")
            x_axis = st.selectbox("X Axis", df.columns, key=f"x_{i}")
            y_axis = st.selectbox("Y Axis", df.columns, key=f"y_{i}")
            create_and_render_plot(df, x_axis, y_axis, "Basic Line")


