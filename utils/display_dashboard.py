import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file

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

    coordinate_variants = {
        "lat": ["lat", "latitude", "Latitudine", "y", "Y"],
        "lon": ["lon", "longitude", "Longitudine", "x", "X"]
    }

    with col2:
        st.subheader("📂 Datasets")
        lat_columns = []
        lon_columns = []
        
        for i, df in enumerate(dataframes):
            if df is None or df.empty:
                st.warning(f"⚠ Il dataset '{filenames[i]}' is empty.")
                continue
            
            detected_lat_col = next((col for col in coordinate_variants["lat"] if col in df.columns), None)
            detected_lon_col = next((col for col in coordinate_variants["lon"] if col in df.columns), None)

            if detected_lat_col is None:
                detected_lat_col = "y" if "y" in df.columns else "Y" if "Y" in df.columns else None
            if detected_lon_col is None:
                detected_lon_col = "x" if "x" in df.columns else "X" if "X" in df.columns else None

            if detected_lat_col is None or detected_lon_col is None:
                st.warning(f"⚠ Dataset '{filenames[i]}' hasn't lat and lon.")
                continue
            
            with st.expander(f"File: {filenames[i]}"):
                lat_col = st.selectbox(f"Seleziona colonna latitudine", df.columns, index=df.columns.get_loc(detected_lat_col), key=f"lat_{i}")
                lon_col = st.selectbox(f"Seleziona colonna longitudine", df.columns, index=df.columns.get_loc(detected_lon_col), key=f"lon_{i}")
            
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



def display_dashboard():
    st.header("Data Analysis and Plotting")
    st.write("Here you can upload and view your data on map and plot." 
             " Use the side window to upload your files and on the dashboard will appear the various products: **🌍 Map Generator** and **📊 Statistics**."
             " Choose the chart format, correlate and implement simple expeditious analysis. There is no data loading limit. ")
    st.sidebar.header("📂 Upload Files")
    uploaded_files = st.sidebar.file_uploader("Drag & Drop your CSV files here", type=['csv', 'xlsx', 'txt'], accept_multiple_files=True)

    if not uploaded_files:
        st.sidebar.info("No files uploaded yet.")
        return
    
    df_list = []
    filenames = []

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
    st.subheader("📈 Data Plotting")

    # Opzione per selezionare più dataset per merge
    selected_datasets = st.multiselect("Seleziona i dataset da unire", filenames, default=filenames)

    if selected_datasets:
        merged_dfs = [df_list[filenames.index(name)] for name in selected_datasets]

        # Verifica che abbiano almeno una colonna in comune
        common_columns = set(merged_dfs[0].columns)
        for df in merged_dfs[1:]:
            common_columns.intersection_update(df.columns)

        if common_columns:
            x_axis = st.selectbox("Seleziona la colonna X comune", list(common_columns))
            y_axes = []
            for idx, df in enumerate(merged_dfs):
                y_axis = st.selectbox(f"Seleziona colonna Y per {selected_datasets[idx]}", df.columns.tolist(), key=f"y_axis_{idx}")
                y_axes.append((df, y_axis, selected_datasets[idx]))  # Salviamo anche il nome del dataset

            # Creare un grafico combinato
            fig = go.Figure()
            for df, y_axis, name in y_axes:
                fig.add_trace(go.Scatter(x=df[x_axis], y=df[y_axis], mode='lines+markers', name=name))

            fig.update_layout(title="Grafico combinato", xaxis_title=x_axis, yaxis_title="Valori")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("I dataset selezionati non hanno colonne in comune, impossibile fare il merge.")
    else:
        st.info("Seleziona almeno un dataset per procedere.")

