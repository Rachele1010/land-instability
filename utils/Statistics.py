import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import uuid

# Funzione per convertire timestamp Unix in datetime
def convert_unix_to_datetime(df):
    """Converte colonne con timestamp Unix in formato leggibile."""
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and (df[col].between(1e9, 2e9)).all():
            df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

# Funzione per generare opzioni dei grafici
def get_chart_options(plot_type, df_list, x_axes, y_axes, dataset_names):
    """Genera le opzioni per il grafico in base al tipo selezionato."""
    options = {
        "title": {"text": f"{plot_type.capitalize()} Chart"},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": dataset_names},
        "xAxis": [{"type": "category", "data": df[x].astype(str).tolist(), "name": dataset_names[i]} for i, (df, x) in enumerate(zip(df_list, x_axes))],
        "yAxis": {"type": "value"},
        "series": []
    }

    for i, (df, y) in enumerate(zip(df_list, y_axes)):
        series_data = {"name": dataset_names[i], "type": plot_type, "data": df[y].tolist()}
        if plot_type == "line":
            series_data["smooth"] = True
        options["series"].append(series_data)

    return options

# Funzione per generare i grafici
def plot_echarts(df_list, x_axes, y_axes, dataset_names, plot_type):
    """Crea un grafico ECharts con identificatori unici per evitare errori."""
    options = get_chart_options(plot_type, df_list, x_axes, y_axes, dataset_names)
    unique_key = f"echarts_{plot_type}_{uuid.uuid4().hex}"
    st_echarts(options=options, height="500px", key=unique_key)

# Funzione principale per gestire i dataset e la visualizzazione
def Statistics(df_list, filenames):
    """Gestisce la visualizzazione e il merge dei dataset."""
    
    # Stato iniziale della vista
    if "show_individual_plots" not in st.session_state:
        st.session_state["show_individual_plots"] = True

    st.subheader("📈 Data Plotting")
    
    # Pulsanti di scelta tra "Single Plot" e "Merge Plot"
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Single Plot"):
            st.session_state["show_individual_plots"] = True
    with col2:
        if st.button("🔄 Merge Datasets"):
            st.session_state["show_individual_plots"] = False

    if st.session_state["show_individual_plots"]:
        # ---- Modalità "Single Plot" ----
        for idx, df in enumerate(df_list):
            df = convert_unix_to_datetime(df)
            st.caption(f"**Dataset {idx + 1} - {filenames[idx]}**")
            col1, col2, col3 = st.columns(3)

            with col1:
                x_axis = st.selectbox(f"X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
            with col2:
                y_axis = st.selectbox(f"Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
            with col3:
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["line", "bar", "scatter", "pie", "heatmap", "radar", "candlestick"], key=f"plot_type_{idx}")

            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(df)
            with col2:
                if not df.empty:
                    plot_echarts([df], [x_axis], [y_axis], [filenames[idx]], plot_type)

    else:
        # ---- Modalità "Merge Datasets" ----
        st.subheader("📊 Merge Multiple Datasets")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            selected_datasets = st.multiselect("Seleziona i dataset", filenames, default=filenames)

        if selected_datasets:
            df_list_selected = [convert_unix_to_datetime(df_list[filenames.index(name)]) for name in selected_datasets]
            x_axes, y_axes = [], []

            with col2:
                for i, name in enumerate(selected_datasets):
                    x_axes.append(st.selectbox(f"X Axis {name}", df_list_selected[i].columns.tolist(), key=f"x_axis_merge_{i}"))
            with col3:
                for i, name in enumerate(selected_datasets):
                    y_axes.append(st.selectbox(f"Y Axis {name}", df_list_selected[i].columns.tolist(), key=f"y_axis_merge_{i}"))
            with col4:
                plot_type = st.selectbox("Scegli il tipo di grafico", ["line", "bar", "scatter", "pie", "heatmap", "radar", "candlestick"], key="plot_type_merge")

            # Creazione del grafico unificato
            plot_echarts(df_list_selected, x_axes, y_axes, selected_datasets, plot_type)





