from streamlit_echarts import st_echarts
import streamlit as st
import pandas as pd

def convert_unix_to_datetime(df):
    """Converte le colonne con timestamp Unix in formato leggibile."""
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):  # Verifica se la colonna è numerica
            if df[col].min() > 1_000_000_000:  # Probabile Unix timestamp in secondi
                df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

def plot_echarts(df, x_axis, y_axis, plot_type):
    """Genera un grafico ECharts, gestendo eventuali problemi di dati."""
    if df.empty or x_axis not in df.columns or y_axis not in df.columns:
        st.error(f"Errore: Colonne non valide. x_axis: {x_axis}, y_axis: {y_axis}")
        return

    # Rimuovere eventuali valori NaN prima di passare i dati
    df = df[[x_axis, y_axis]].dropna()

    options = {
        "title": {"text": f"{plot_type.capitalize()} Chart"},
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

            df = convert_unix_to_datetime(df)  # Convertiamo Unix time se presente

            col1, col2, col3 = st.columns([1, 1, 1])
            col4, col5 = st.columns([1, 2])

            with col1:
                x_axis = st.selectbox(f"X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
            with col2:
                y_axis = st.selectbox(f"Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
            with col3:
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["line", "bar", "scatter"], key=f"plot_type_{idx}")
            with col4:
                st.dataframe(df)
            with col5:
                if not df.empty:
                    plot_echarts(df, x_axis, y_axis, plot_type)
    else:
        # Sezione Merge
        st.subheader("📊 Merge Multiple Datasets")

        # Selezione dataset da unire
        selected_datasets = st.multiselect("Seleziona i dataset da unire", filenames, default=filenames)

        if selected_datasets:
            merged_dfs = [convert_unix_to_datetime(df_list[filenames.index(name)]) for name in selected_datasets]
            common_columns = set(merged_dfs[0].columns)

            for df in merged_dfs[1:]:
                common_columns.intersection_update(df.columns)

            if common_columns:
                x_axis = st.selectbox("Seleziona la colonna X comune", list(common_columns), key="merge_x_axis")

                y_axes = []
                for idx, df in enumerate(merged_dfs):
                    y_axis = st.selectbox(f"Seleziona colonna Y per {selected_datasets[idx]}", df.columns.tolist(), key=f"y_axis_merge_{idx}")
                    y_axes.append((df, y_axis, selected_datasets[idx]))

                plot_type = st.selectbox("Scegli il tipo di grafico", ["line", "bar", "scatter"], key="plot_type_merge")

                # Creiamo un dataframe unificato basato sulla colonna X comune
                merged_df = pd.concat([df.set_index(x_axis)[y_axis].rename(name) for df, y_axis, name in y_axes], axis=1)
                merged_df = merged_df.reset_index()

                st.dataframe(merged_df)  # Mostra il dataset unito
                for name in merged_df.columns[1:]:
                    plot_echarts(merged_df, x_axis, name, plot_type)
            else:
                st.warning("I dataset selezionati non hanno colonne in comune, impossibile fare il merge.")
        else:
            st.info("Seleziona almeno un dataset per procedere.")

