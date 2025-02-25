import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts
import numpy as np
def plot_echarts(df, x_axis, y_axis, plot_type):
    """Genera e mostra un grafico ECharts con i dati forniti."""
    
    # Controlla se y_axis è una colonna valida
    if y_axis not in df.columns or not isinstance(df[y_axis], pd.Series):
        st.warning(f"❗ Colonna '{y_axis}' non valida, impossibile generare il grafico.")
        return  # Esci senza errore se y_axis non è valido

    # Seleziona solo le colonne necessarie ed elimina valori NaN
    df = df[[x_axis, y_axis]].dropna()

    # Converte X in stringa per evitare problemi con l'asse X
    df[x_axis] = df[x_axis].astype(str)

    # Converte la colonna Y in numerico, sostituendo errori con NaN
    df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')

    # Rimuove righe con NaN dopo la conversione
    df = df.dropna()

    # Se il DataFrame è vuoto dopo la pulizia, esci senza errore
    if df.empty:
        st.warning(f"❗ Nessun dato valido per il grafico '{plot_type}' con X='{x_axis}' e Y='{y_axis}'.")
        return

    # Configurazione del grafico
    options = {
        "title": {"text": f"{plot_type.capitalize()} Chart"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": df[x_axis].tolist()},
        "yAxis": {"type": "value"},
        "series": [{
            "name": y_axis,
            "type": plot_type,
            "data": df[y_axis].tolist(),
            "smooth": True if plot_type == "line" else False,
        }],
    }

    # Mostra il grafico con Streamlit-ECharts
    try:
        st_echarts(options=options, height="500px")
    except Exception as e:
        st.error(f"❌ Errore durante la creazione del grafico: {e}")

def Statistics(df_list, filenames):
    """Visualizza dataset individuali e permette il merge con ECharts."""
    
    st.subheader("📈 Data Plotting")
    show_individual_plots = True

    if st.button("🔄 Merge Datasets"):
        show_individual_plots = False

    if show_individual_plots:
        for idx, df in enumerate(df_list):
            st.caption(f"**Dataset {idx + 1} - {filenames[idx]}**")

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
        st.subheader("📊 Merge Multiple Datasets")
        selected_datasets = st.multiselect("Seleziona i dataset da unire", filenames, default=filenames)

        if selected_datasets:
            merged_dfs = [df_list[filenames.index(name)] for name in selected_datasets]
            common_columns = set(merged_dfs[0].columns)

            for df in merged_dfs[1:]:
                common_columns.intersection_update(df.columns)

            if common_columns:
                x_axis = st.selectbox("Seleziona la colonna X comune", list(common_columns), key="merge_x_axis")
                y_axes = []

                for idx, df in enumerate(merged_dfs):
                    y_axis = st.selectbox(f"Colonna Y per {selected_datasets[idx]}", df.columns.tolist(), key=f"y_axis_merge_{idx}")
                    y_axes.append((df, y_axis, selected_datasets[idx]))

                plot_type = st.selectbox("Scegli il tipo di grafico", ["line", "bar", "scatter"], key="plot_type_merge")

                col1, col2 = st.columns([1, 2])
                with col1:
                    merged_df = pd.concat([df.set_index(x_axis)[y_axis].rename(name) for df, y_axis, name in y_axes], axis=1).reset_index()
                    st.dataframe(merged_df)
                with col2:
                    for name in merged_df.columns[1:]:
                        plot_echarts(merged_df, x_axis, name, plot_type)
            else:
                st.warning("⚠️ I dataset selezionati non hanno colonne in comune, impossibile fare il merge.")
        else:
            st.info("ℹ️ Seleziona almeno un dataset per procedere.")



