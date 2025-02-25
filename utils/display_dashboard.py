import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
from utils.map_combined_datasets import map_combined_datasets

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
    
