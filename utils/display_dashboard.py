import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_echarts import st_echarts
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
from utils.map_combined_datasets import map_combined_datasets

def display_dashboard():
    st.header("Data Analysis and Plotting")
    st.write("Here you can upload and view your data on a map and plot." 
             " Use the side window to upload your files, and the dashboard will display the various products: **🌍 Map Generator** and **📊 Statistics**."
             " Choose the chart format, correlate, and implement simple analyses. There is no data loading limit.")

    # Upload dei file
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

        # ---- Struttura originale ----
        for idx, df in enumerate(df_list):
            st.caption(f"**Dataset {idx + 1} - {filenames[idx]}**")
            col1, col2, col3 = st.columns([1, 1, 1])
            col4, col5 = st.columns([1, 2])
            
            with col1:
                x_axis = st.selectbox(f"X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
            with col2:
                y_axis = st.selectbox(f"Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
            with col3:
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["Basic Scatter", "Basic Bar", "Basic Line", "Mixed Line and Bar", "Calendar Heatmap", "DataZoom"], key=f"plot_type_{idx}")
            with col4:
                st.dataframe(df)
            with col5:
                if not df.empty:
                    create_and_render_plot(df, x_axis, y_axis, plot_type)

        # ---- Bottone per Merge ----
        st.divider()
        if st.button("🔄 Merge Datasets"):
            st.subheader("📊 Merge Multiple Datasets")

            # Selezione dei dataset
            selected_datasets = st.multiselect("Seleziona i dataset da unire", filenames, default=filenames)

            if selected_datasets:
                merged_dfs = [df_list[filenames.index(name)] for name in selected_datasets]

                # Trova colonne comuni
                common_columns = set(merged_dfs[0].columns)
                for df in merged_dfs[1:]:
                    common_columns.intersection_update(df.columns)

                if common_columns:
                    x_axis = st.selectbox("Seleziona la colonna X comune", list(common_columns))
                    y_axes = []
                    for idx, df in enumerate(merged_dfs):
                        y_axis = st.selectbox(f"Seleziona colonna Y per {selected_datasets[idx]}", df.columns.tolist(), key=f"y_axis_merge_{idx}")
                        y_axes.append((df, y_axis, selected_datasets[idx]))

                    # Creazione del grafico con ECharts
                    options = {
                        "title": {"text": "Grafico combinato"},
                        "tooltip": {"trigger": "axis"},
                        "xAxis": {"type": "category", "data": merged_dfs[0][x_axis].tolist()},
                        "yAxis": {"type": "value"},
                        "legend": {"data": [name for _, _, name in y_axes]},
                        "series": [
                            {
                                "name": name,
                                "type": "line",
                                "data": df[y_axis].tolist(),
                                "smooth": True
                            } for df, y_axis, name in y_axes
                        ]
                    }
                    st_echarts(options=options, height="500px")
                else:
                    st.warning("I dataset selezionati non hanno colonne in comune, impossibile fare il merge.")
            else:
                st.info("Seleziona almeno un dataset per procedere.")
