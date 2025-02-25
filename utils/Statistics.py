from streamlit_echarts import st_echarts
import streamlit as st
import pandas as pd

def convert_unix_to_datetime(df):
    """Converte colonne Unix timestamp in formato data leggibile."""
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):  # Controlla se è numerica
            if df[col].min() > 1_000_000_000:  # Probabile Unix time in secondi
                df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

def plot_echarts(df, x_axis, y_axis_list, plot_type):
    """Genera un grafico ECharts con più serie."""
    
    # Creiamo il dizionario di opzioni per il grafico
    options = {
        "title": {"text": "Grafico"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": df[x_axis].tolist()},
        "yAxis": {"type": "value"},
        "legend": {"data": y_axis_list},
        "series": [
            {
                "name": y_axis,
                "type": plot_type,
                "data": df[y_axis].tolist(),
                "smooth": True if plot_type == "line" else False
            } for y_axis in y_axis_list
        ],
    }
    st_echarts(options=options, height="500px")

def Statistics(df_list, filenames):
    """Visualizza dataset e permette il merge con selezione colonne."""
    st.subheader("📈 Data Plotting")

    # Bottone per attivare il Merge
    merge_mode = st.checkbox("🔄 Merge Datasets")

    if not merge_mode:
        # Visualizzazione dataset individuali
        for idx, df in enumerate(df_list):
            st.caption(f"**Dataset {idx + 1} - {filenames[idx]}**")

            df = convert_unix_to_datetime(df)  # Convertiamo Unix time se presente

            # Posizioniamo i select box in colonna
            st.write(f"**Selezione Variabili per {filenames[idx]}**")
            x_axis = st.selectbox(f"X Axis ({filenames[idx]})", df.columns.tolist(), key=f"x_axis_{idx}")
            y_axis = st.selectbox(f"Y Axis ({filenames[idx]})", df.columns.tolist(), key=f"y_axis_{idx}")
            plot_type = st.selectbox(f"Tipo di Grafico ({filenames[idx]})", ["line", "bar", "scatter"], key=f"plot_type_{idx}")

            st.dataframe(df)
            
            if not df.empty:
                plot_echarts(df, x_axis, [y_axis], plot_type)

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
                plot_echarts(merged_df, x_axis, merged_df.columns[1:].tolist(), plot_type)

            else:
                st.warning("I dataset selezionati non hanno colonne in comune, impossibile fare il merge.")
        else:
            st.info("Seleziona almeno un dataset per procedere.")
