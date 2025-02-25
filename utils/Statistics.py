import streamlit as st
import pandas as pd
import uuid
from streamlit_echarts import st_echarts
from streamlit_pyecharts import st_pyecharts
from demo_echarts import ST_DEMOS
from demo_pyecharts import ST_PY_DEMOS

# Funzione per convertire timestamp Unix in datetime
def convert_unix_to_datetime(df):
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].between(1e9, 2e9).all():
            df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

# Funzione per generare le opzioni dei grafici con ECharts
def get_chart_options(plot_type, df_list, x_axes, y_axes, dataset_names):
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

# Funzione per generare i grafici con ECharts
def plot_echarts(df_list, x_axes, y_axes, dataset_names, plot_type):
    options = get_chart_options(plot_type, df_list, x_axes, y_axes, dataset_names)
    unique_key = f"echarts_{plot_type}_{uuid.uuid4().hex}"
    st_echarts(options=options, height="500px", key=unique_key)

# Funzione principale per la visualizzazione dei dataset
def Statistics(df_list, filenames):
    if "show_individual_plots" not in st.session_state:
        st.session_state["show_individual_plots"] = True

    st.subheader("📈 Data Plotting")

    # Selezione API tra ECharts e PyeCharts (questa volta GLOBALE, non per ogni dataset)
    api_options = ("echarts", "pyecharts")
    selected_api = st.selectbox("Scegli l'API preferita:", api_options)

    # Selezione del grafico disponibile tra le demo
    page_options = list(ST_PY_DEMOS.keys()) if selected_api == "pyecharts" else list(ST_DEMOS.keys())
    selected_page = st.selectbox("Scegli un esempio di grafico", page_options)
    demo, url = ST_DEMOS[selected_page] if selected_api == "echarts" else ST_PY_DEMOS[selected_page]

    # Pulsanti di scelta tra "Single Plot" e "Merge Plot"
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Single Plot"):
            st.session_state["show_individual_plots"] = True
    with col2:
        if st.button("🔄 Merge Datasets"):
            st.session_state["show_individual_plots"] = False

    if st.session_state["show_individual_plots"]:
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
                    if selected_api == "echarts":
                        plot_echarts([df], [x_axis], [y_axis], [filenames[idx]], plot_type)
                    else:
                        st_pyecharts(demo())

    else:
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

            if selected_api == "echarts":
                plot_echarts(df_list_selected, x_axes, y_axes, selected_datasets, plot_type)
            else:
                st_pyecharts(demo())

    # Eseguire il grafico della demo selezionata
    demo()







