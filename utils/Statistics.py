from streamlit_echarts import st_echarts
import streamlit as st
import pandas as pd

def plot_echarts(df, x_axis, y_axis, plot_type):
    """Genera un grafico ECharts in base al tipo selezionato."""
    options = {
        "title": {"text": f"{plot_type} Chart"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": df[x_axis].tolist()},
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": y_axis,
                "type": plot_type,
                "data": df[y_axis].tolist(),
                "smooth": True if plot_type == "line" else False,
            }
        ],
    }
    st_echarts(options=options, height="500px")

def Statistics(df_list, filenames):
    """Visualizza dataset individuali e permette il merge con ECharts."""
    st.subheader("📈 Data Plotting")
    show_individual_plots = True
    
    # Bottone per attivare il Merge
    if st.button("🔄 Merge Datasets"):
        show_individual_plots = False

    if show_individual_plots:
        # Visualizzazione singoli dataset
        for idx, df in enumerate(df_list):
            st.caption(f"**Dataset {idx + 1} - {filenames[idx]}**")
            col1, col2, col3 = st.columns([1, 1, 1])
            col4, col5 = st.columns([1, 2])
            
            with col1:
                x_axis = st.selectbox(f"X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
            with col2:
                y_axis = st.selectbox(f"Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
            with col3:
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["line", "bar", "scatter", "pie", "radar", "heatmap"], key=f"plot_type_{idx}")
            with col4:
                st.dataframe(df)
            with col5:
                if not df.empty:
                    plot_echarts(df, x_axis, y_axis, plot_type)
    else:
        # Sezione Merge
        st.subheader("📊 Merge Multiple Datasets")
        selected_datasets = st.multiselect("Seleziona i dataset da unire", filenames, default=filenames)
        
        if selected_datasets:
            merged_dfs = [df_list[filenames.index(name)] for name in selected_datasets]
            common_columns = set(merged_dfs[0].columns)
            for df in merged_dfs[1:]:
                common_columns.intersection_update(df.columns)
            
            if common_columns:
                x_axis = st.selectbox("Seleziona la colonna X comune", list(common_columns))
                y_axes = []
                for idx, df in enumerate(merged_dfs):
                    y_axis = st.selectbox(f"Seleziona colonna Y per {selected_datasets[idx]}", df.columns.tolist(), key=f"y_axis_merge_{idx}")
                    y_axes.append((df, y_axis, selected_datasets[idx]))
                
                plot_type = st.selectbox("Scegli il tipo di grafico", ["line", "bar", "scatter", "pie", "radar", "heatmap"], key="plot_type_merge")
                
                options = {
                    "title": {"text": "Grafico combinato"},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": merged_dfs[0][x_axis].tolist()},
                    "yAxis": {"type": "value"},
                    "legend": {"data": [name for _, _, name in y_axes]},
                    "series": [
                        {
                            "name": name,
                            "type": plot_type,
                            "data": df[y_axis].tolist(),
                            "smooth": True if plot_type == "line" else False
                        } for df, y_axis, name in y_axes
                    ]
                }
                st_echarts(options=options, height="500px")
            else:
                st.warning("I dataset selezionati non hanno colonne in comune, impossibile fare il merge.")
        else:
            st.info("Seleziona almeno un dataset per procedere.")
