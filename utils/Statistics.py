import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

def convert_unix_to_datetime(df):
    """Converte automaticamente colonne Unix timestamp in datetime se rilevate."""
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].min() > 1e9 and df[col].max() < 1e12:  # Verifica formato Unix timestamp
                df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

def Statistics(df_list, filenames):
    """
    Funzione per visualizzare i dataset separati e fornire un'opzione di merge con grafici ECharts.
    """
    st.subheader("📈 Data Plotting")
    show_individual_plots = True
    
    # Bottone per attivare il Merge
    if st.button("🔄 Merge Datasets"):
        show_individual_plots = False  

    if show_individual_plots:
        # ---- Grafici individuali ----
        for idx, df in enumerate(df_list):
            df = convert_unix_to_datetime(df)  # Converte eventuali date in Unix
            st.caption(f"**Dataset {idx + 1} - {filenames[idx]}**")
            col1, col2, col3 = st.columns([1, 1, 1])
            col4, col5 = st.columns([1, 2])
            
            with col1:
                x_axis = st.selectbox(f"X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
            with col2:
                y_axis = st.selectbox(f"Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
            with col3:
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["Line", "Bar", "Scatter"], key=f"plot_type_{idx}")
            with col4:
                st.dataframe(df)
            with col5:
                if not df.empty:
                    options = {
                        "title": {"text": filenames[idx]},
                        "tooltip": {"trigger": "axis"},
                        "xAxis": {"type": "category", "data": df[x_axis].tolist()},
                        "yAxis": {"type": "value"},
                        "series": [{"name": y_axis, "type": plot_type.lower(), "data": df[y_axis].tolist()}]
                    }
                    st_echarts(options=options, height="400px")

    else:
        # ---- Merge ----
        st.subheader("📊 Merge Multiple Datasets")
        selected_datasets = st.multiselect("Seleziona i dataset da unire", filenames, default=filenames)

        if selected_datasets:
            merged_dfs = [convert_unix_to_datetime(df_list[filenames.index(name)]) for name in selected_datasets]

            # Trova colonne comuni
            common_columns = set(merged_dfs[0].columns)
            for df in merged_dfs[1:]:
                common_columns.intersection_update(df.columns)

            if common_columns:
                st.write("### Selezione delle Variabili per Ogni Dataset")
                x_axis = st.selectbox("Seleziona la colonna X comune", list(common_columns))

                y_axes = {}
                for idx, df in enumerate(merged_dfs):
                    y_axes[selected_datasets[idx]] = st.selectbox(
                        f"Seleziona colonna Y per {selected_datasets[idx]}", df.columns.tolist(), key=f"y_axis_merge_{idx}"
                    )

                selected_plot_type = st.selectbox("Scegli il tipo di grafico", ["Line", "Bar", "Scatter"])

                # Creazione del grafico con ECharts
                options = {
                    "title": {"text": "Grafico combinato"},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": merged_dfs[0][x_axis].tolist()},
                    "yAxis": {"type": "value"},
                    "legend": {"data": list(y_axes.keys())},
                    "series": [
                        {
                            "name": dataset_name,
                            "type": selected_plot_type.lower(),
                            "data": df[y_axis].tolist(),
                            "smooth": True
                        } for dataset_name, y_axis in y_axes.items()
                    ]
                }
                st_echarts(options=options, height="500px")
            else:
                st.warning("I dataset selezionati non hanno colonne in comune, impossibile fare il merge.")
        else:
            st.info("Seleziona almeno un dataset per procedere.")


