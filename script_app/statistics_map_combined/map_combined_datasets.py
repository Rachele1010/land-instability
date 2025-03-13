import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from script_app.load_plotting_utils.plotting import create_and_render_plot
from script_app.load_plotting_utils.load import load_file, process_file

def map_combined_datasets(dataframes, filenames=None):
    """
    Mappa più dataset con coordinate e popups, centrando la mappa sui dati caricati o sull'Italia di default.
    """
    if filenames is None:
        filenames = [f"Dataset {i+1}" for i in range(len(dataframes))]

    if not dataframes:
        st.error("❌ No available datasets.")
        return

    col1, col2 = st.columns([5, 1])
    colors = ["red", "blue", "green", "purple", "orange", "pink"]
    
    default_center = {"lat": 41.8719, "lon": 12.5674}  # Centro Italia

    coordinate_keywords = {
        "lat": ["lat", "latitude", "y", "_latitude"],  # parole chiave per latitudine
        "lon": ["lon", "longitude", "x", "_longitude"]  # parole chiave per longitudine
    }

    with col2:
        st.subheader("📂 Datasets")
        lat_columns = []
        lon_columns = []
        
        for i, df in enumerate(dataframes):
            if df is None or df.empty:
                st.warning(f"⚠ Dataset '{filenames[i]}' is empty.")
                continue

            # Convertiamo tutto in minuscolo per ignorare maiuscole/minuscole
            df.columns = df.columns.str.strip().str.lower()

            detected_lat_col = None
            detected_lon_col = None

            # Cerchiamo colonne contenenti "lat" e "lon"
            for col in df.columns:
                if any(keyword in col for keyword in coordinate_keywords["lat"]):
                    detected_lat_col = col
                if any(keyword in col for keyword in coordinate_keywords["lon"]):
                    detected_lon_col = col

            if detected_lat_col is None or detected_lon_col is None:
                st.warning(f"⚠ Dataset '{filenames[i]}' hasn't lat and lon.")
                continue

            with st.expander(f"File: {filenames[i]}"):
                lat_col = st.selectbox(f"Select latitude", df.columns, index=df.columns.get_loc(detected_lat_col), key=f"lat_{i}")
                lon_col = st.selectbox(f"Select longitude", df.columns, index=df.columns.get_loc(detected_lon_col), key=f"lon_{i}")
            
            lat_columns.append(lat_col)
            lon_columns.append(lon_col)
    
    with col1:
        st.subheader("🗺 Data Mapping")
        fig = go.Figure()
        all_latitudes = []
        all_longitudes = []
        first_valid_center = None  

        for i, (df, filename) in enumerate(zip(dataframes, filenames)):
            try:
                lat_col = lat_columns[i]
                lon_col = lon_columns[i]

                if lat_col and lon_col and lat_col in df.columns and lon_col in df.columns:
                    df_map = df.dropna(subset=[lat_col, lon_col]).copy()
                    df_map["lat"] = pd.to_numeric(df_map[lat_col], errors="coerce")
                    df_map["lon"] = pd.to_numeric(df_map[lon_col], errors="coerce")
                    df_map = df_map.dropna()

                    if df_map.empty:
                        st.warning(f"⚠ '{filename}' no valid data after cleaning.")
                        continue

                    all_latitudes.extend(df_map["lat"].tolist())
                    all_longitudes.extend(df_map["lon"].tolist())

                    if first_valid_center is None and not df_map.empty:
                        first_valid_center = {"lat": df_map["lat"].iloc[0], "lon": df_map["lon"].iloc[0]}

                    popup_info = df_map.apply(lambda row: "<br>".join([f"<b>{col}</b>: {row[col]}" for col in df.columns]), axis=1)

                    fig.add_trace(go.Scattermapbox(
                        lat=df_map["lat"],
                        lon=df_map["lon"],
                        mode="markers",
                        marker=dict(size=15, color=colors[i % len(colors)]),
                        name=filename,
                        hoverinfo="text",
                        text=popup_info
                    ))
            
            except Exception as e:
                st.warning(f"⚠ Error '{filename}': {e}")

        if not all_latitudes or not all_longitudes:
            st.warning("❌ No valid data to display the map.")
            return

        center_lat = first_valid_center["lat"] if first_valid_center else default_center["lat"]
        center_lon = first_valid_center["lon"] if first_valid_center else default_center["lon"]

        fig.update_layout(
            autosize=True,
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=5
            ),
            legend=dict(title="Legenda", x=1.05, y=0.9),
            height=800,
            margin={"r":0,"t":0,"l":0,"b":0}
        )

        st.plotly_chart(fig, use_container_width=True)
