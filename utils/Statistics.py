import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

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
    st_echarts(options=options, height="500px")

def Statistics(df_list, filenames):
    """Gestisce la visualizzazione e il merge dei dataset."""
    st.subheader("📈 Data Plotting")
    if st.button("🔄 Merge Datasets"):
        show_individual_plots = False
    else:
        show_individual_plots = True
    
    if show_individual_plots:
        for idx, df in enumerate(df_list):
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
    else:
        st.subheader("📊 Merge Multiple Datasets")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            selected_datasets = st.multiselect("Seleziona i dataset da plottare insieme", filenames, default=filenames)
            if selected_datasets:
                df_list_selected = [df_list[filenames.index(name)] for name in selected_datasets]
                with col2:
                    x_axes = [st.selectbox(f"Colonna X per {name}", df.columns.tolist(), key=f"x_axis_merge_{i}") for i, (df, name) in enumerate(zip(df_list_selected, selected_datasets))]
                with col3:
                    y_axes = [st.selectbox(f"Colonna Y per {name}", df.columns.tolist(), key=f"y_axis_merge_{i}") for i, (df, name) in enumerate(zip(df_list_selected, selected_datasets))]
                with col4:
                    plot_type = st.selectbox("Scegli il tipo di grafico", ["line", "bar", "scatter"], key="plot_type_merge")
                if st.button("📊 Genera Grafico Merge"):
                    plot_echarts(df_list_selected, x_axes, y_axes, selected_datasets, plot_type)
            else:
                st.info("ℹ️ Seleziona almeno un dataset per procedere.")
