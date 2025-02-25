import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

def plot_echarts(df, x_axis, y_axes, plot_type):
    """Genera un grafico ECharts con più variabili e legenda."""
    if x_axis not in df.columns or any(y not in df.columns for y in y_axes):
        st.warning("❗ Alcune colonne selezionate non esistono nel dataset.")
        return  
    
    df = df[[x_axis] + y_axes].dropna()
    df[x_axis] = df[x_axis].astype(str)
    
    options = {
        "title": {"text": f"{plot_type.capitalize()} Chart"},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": y_axes},
        "xAxis": {"type": "category", "data": df[x_axis].tolist()},
        "yAxis": {"type": "value"},
        "series": [
            {"name": y, "type": plot_type, "data": df[y].tolist(), "smooth": True if plot_type == "line" else False}
            for y in y_axes
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
                plot_echarts(df, x_axis, [y_axis], plot_type)
    else:
        st.subheader("📊 Merge Multiple Datasets")
        selected_datasets = st.multiselect("Seleziona i dataset da unire", filenames, default=filenames)
        if selected_datasets:
            merged_dfs = [df_list[filenames.index(name)] for name in selected_datasets]
            common_columns = set(merged_dfs[0].columns)
            for df in merged_dfs[1:]:
                common_columns.intersection_update(df.columns)
            if common_columns:
                x_axis = st.selectbox("Seleziona la colonna X comune", list(common_columns), key="merge_x_axis")
                y_axes = [st.selectbox(f"Colonna Y per {selected_datasets[idx]}", df.columns.tolist(), key=f"y_axis_merge_{idx}") for idx, df in enumerate(merged_dfs)]
                plot_type = st.selectbox("Scegli il tipo di grafico", ["line", "bar", "scatter"], key="plot_type_merge")
                if st.button("📊 Genera Grafico Merge"):
                    merged_df = pd.concat([df.set_index(x_axis)[y].rename(name) for df, y, name in zip(merged_dfs, y_axes, selected_datasets)], axis=1).reset_index()
                    st.dataframe(merged_df)
                    plot_echarts(merged_df, x_axis, merged_df.columns[1:].tolist(), plot_type)
            else:
                st.warning("⚠️ I dataset selezionati non hanno colonne in comune.")
        else:
            st.info("ℹ️ Seleziona almeno un dataset per procedere.")
