import streamlit as st
import pandas as pd
import uuid
from streamlit_echarts import st_echarts
from demo_echarts import ST_DEMOS  # Solo ECharts
from utils.plotting import create_and_render_plot

# Funzione per convertire timestamp Unix in datetime
def convert_unix_to_datetime(df):
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].between(1e9, 2e9).all():
            df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

# Funzione principale per la visualizzazione dei dataset
def Statistics(df_list, filenames):
    if "show_individual_plots" not in st.session_state:
        st.session_state["show_individual_plots"] = True

    st.subheader("📈 Data Plotting")

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
                # Selezione del grafico disponibile tra le demo di ECharts
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["Basic Scatter", "Basic Bar", "Basic Line", "Mixed Line and Bar", 
                                                                  "Calendar Heatmap", "DataZoom", "Pie Chart"], key=f"plot_type_{idx}")

            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(df)
            with col2:
                create_and_render_plot(df, x_axis, y_axis, plot_type)

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
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["Basic Scatter", "Basic Bar", "Basic Line", "Mixed Line and Bar", 
                                                                  "Calendar Heatmap", "DataZoom", "Pie Chart"], key=f"plot_type_{idx}_merge")

            create_and_render_plot(df, x_axis, y_axis, plot_type)











