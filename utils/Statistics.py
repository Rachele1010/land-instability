import streamlit as st
import pandas as pd
import plotly.graph_objects as go  
from utils.plotting import create_and_render_plot  

# Funzione per convertire timestamp Unix in datetime
def convert_unix_to_datetime(df):
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].between(1e9, 2e9).all():
            df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

# Funzione principale per la visualizzazione e analisi dei dataset
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

    # Sezione per i singoli grafici
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
                plot_type = st.selectbox(f"Plot Type {idx + 1}", 
                                         ["Basic Scatter", "Basic Bar", "Basic Line", 
                                          "Mixed Line and Bar", "Calendar Heatmap", "DataZoom"], 
                                         key=f"plot_type_{idx}")

            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(df)
            with col2:
                create_and_render_plot(df, x_axis, y_axis, plot_type)

    # Sezione per Merge Datasets (UNICO GRAFICO)
    else:
        st.subheader("📊 Merge Multiple Datasets in One Plot")
        
        selected_datasets = st.multiselect("Seleziona i dataset", filenames, default=filenames)

        if selected_datasets:
            fig = go.Figure()  # Unico grafico

            x_axes, y_axes, second_y_axes = {}, {}, {}

            col1, col2, col3 = st.columns(3)

            with col1:
                for i, dataset_name in enumerate(selected_datasets):
                    df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                    x_axes[dataset_name] = st.selectbox(f"X Axis ({dataset_name})", df.columns.tolist(), key=f"x_axis_merge_{i}")

            with col2:
                for i, dataset_name in enumerate(selected_datasets):
                    df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                    y_axes[dataset_name] = st.selectbox(f"Y Axis ({dataset_name})", df.columns.tolist(), key=f"y_axis_merge_{i}")

            with col3:
                for i, dataset_name in enumerate(selected_datasets):
                    second_y_axes[dataset_name] = st.checkbox(f"Secondo asse Y? ({dataset_name})", key=f"secondary_y_{i}")

            # Aggiunta dei dati nel grafico unico
            for dataset_name in selected_datasets:
                df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                
                fig.add_trace(go.Scatter(
                    x=df[x_axes[dataset_name]],
                    y=df[y_axes[dataset_name]],
                    mode='lines+markers',
                    name=dataset_name,
                    yaxis="y2" if second_y_axes[dataset_name] else "y1"  
                ))

            # Layout del grafico con doppio asse Y
            fig.update_layout(
                title="Merged Datasets",
                xaxis=dict(title="X Axis"),
                yaxis=dict(title="Primary Y Axis"),
                yaxis2=dict(
                    title="Secondary Y Axis",
                    overlaying='y',
                    side='right',
                    showgrid=False  
                ),
                legend=dict(title="Datasets")
            )

            st.plotly_chart(fig, use_container_width=True)

