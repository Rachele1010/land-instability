import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

def convert_unix_to_datetime(df):
    """Converte colonne con timestamp Unix in formato leggibile."""
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and (df[col].between(1e9, 2e9)).all():
            df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

import uuid  # Importiamo il modulo per generare chiavi uniche

def plot_echarts(df_list, x_axes, y_axes, dataset_names, plot_type):
    """Genera un grafico ECharts con più dataset senza richiedere colonne comuni."""
    
    options = {
        "title": {"text": f"{plot_type.capitalize()} Chart"},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": dataset_names},
        "xAxis": [
            {"type": "category", "data": df[x].astype(str).tolist(), "name": dataset_names[i]}
            for i, (df, x) in enumerate(zip(df_list, x_axes))
        ],
        "yAxis": {"type": "value"},
        "series": [
            {"name": dataset_names[i], "type": plot_type, "data": df[y].tolist(), "smooth": True if plot_type == "line" else False}
            for i, (df, y) in enumerate(zip(df_list, y_axes))
        ],
    }
    
    # Creazione di una chiave univoca con uuid
    unique_key = f"echarts_{plot_type}_{'_'.join(dataset_names)}_{uuid.uuid4().hex}"
    
    st_echarts(options=options, height="500px", key=unique_key)

def Statistics(df_list, filenames):
    """Gestisce la visualizzazione e il merge dei dataset."""

    # Inizializza lo stato della modalità di visualizzazione
    if "plot_mode" not in st.session_state:
        st.session_state["plot_mode"] = "single"

    st.subheader("📈 Data Plotting")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Single Plot"):
            st.session_state["plot_mode"] = "single"
    with col2:
        if st.button("🔄 Merge Plot"):
            st.session_state["plot_mode"] = "merge"

    # ---- Modalità Single Plot ----
    if st.session_state["plot_mode"] == "single":
        for idx, df in enumerate(df_list):
            df = convert_unix_to_datetime(df)  # Conversione timestamp Unix
            st.caption(f"**Dataset {idx + 1} - {filenames[idx]}**")
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                x_axis = st.selectbox(f"X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
            with col2:
                y_axis = st.selectbox(f"Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
            with col3:
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["line", "bar", "scatter", "pie", "heatmap", "radar"], key=f"plot_type_{idx}")

            st.dataframe(df)

            if not df.empty:
                plot_echarts([df], [x_axis], [y_axis], [filenames[idx]], plot_type)

    # ---- Modalità Merge Plot ----
    elif st.session_state["plot_mode"] == "merge":
        st.subheader("📊 Merge Multiple Datasets")
        selected_datasets = st.multiselect("Seleziona i dataset da plottare insieme", filenames, default=filenames)

        if selected_datasets:
            df_list_selected = [convert_unix_to_datetime(df_list[filenames.index(name)]) for name in selected_datasets]
            x_axes = []
            y_axes = []

            col1, col2, col3 = st.columns(3)

            with col1:
                for i, name in enumerate(selected_datasets):
                    x_axes.append(st.selectbox(f"X Axis per {name}", df_list_selected[i].columns.tolist(), key=f"x_axis_merge_{i}"))
            with col2:
                for i, name in enumerate(selected_datasets):
                    y_axes.append(st.selectbox(f"Y Axis per {name}", df_list_selected[i].columns.tolist(), key=f"y_axis_merge_{i}"))
            with col3:
                plot_type = st.selectbox("Scegli il tipo di grafico", ["line", "bar", "scatter", "pie", "heatmap", "radar"], key="plot_type_merge")

            # Mostra il grafico unificato
            plot_echarts(df_list_selected, x_axes, y_axes, selected_datasets, plot_type)




