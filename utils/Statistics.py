import streamlit as st
import pandas as pd
import plotly.express as px  
from utils.plotting import create_and_render_plot

# Funzione per convertire timestamp Unix in datetime
def convert_unix_to_datetime(df):
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].between(1e9, 2e9).all():
            df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

# Funzione per calcolare l'autocorrelazione
def compute_autocorrelation(df, column):
    if column not in df.columns:
        st.error(f"❌ Errore: La colonna '{column}' non esiste nel DataFrame.")
        return None

    autocorr_values = [df[column].autocorr(lag) for lag in range(1, min(len(df), 50))]
    lags = list(range(1, len(autocorr_values) + 1))

    fig = px.line(x=lags, y=autocorr_values, markers=True, title=f"Autocorrelation Plot - {column}")
    fig.update_xaxes(title="Lag")
    fig.update_yaxes(title="Autocorrelation Coefficient")
    
    return fig

# Funzione principale per la visualizzazione e analisi dei dataset
def Statistics(df_list, filenames):
    if "show_individual_plots" not in st.session_state:
        st.session_state["show_individual_plots"] = True

    st.subheader("📈 Data Plotting")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Single Plot"):
            st.session_state["show_individual_plots"] = True
    with col2:
        if st.button("🔄 Merge Datasets"):
            st.session_state["show_individual_plots"] = False
    with col3:
        if st.button("📈 Autocorrelation"):
            st.session_state["show_individual_plots"] = None  # Modalità autocorrelazione

    # Sezione per i singoli grafici
    if st.session_state["show_individual_plots"] is True:
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

    # Sezione per Merge Datasets
    elif st.session_state["show_individual_plots"] is False:
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
                plot_type = st.selectbox("Plot Type", ["Basic Scatter", "Basic Bar", "Basic Line", "Mixed Line and Bar", 
                                                       "Calendar Heatmap", "DataZoom"], key="plot_type_merge")

            # Creazione grafico per dataset uniti
            for i in range(len(selected_datasets)):
                create_and_render_plot(df_list_selected[i], x_axes[i], y_axes[i], plot_type)

    # Sezione per l'Autocorrelazione
    elif st.session_state["show_individual_plots"] is None:
        st.subheader("📊 Autocorrelation Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_datasets = st.multiselect("Seleziona i dataset", filenames, default=filenames)

        if selected_datasets:
            df_list_selected = [convert_unix_to_datetime(df_list[filenames.index(name)]) for name in selected_datasets]
            selected_columns = {}

            with col2:
                for i, name in enumerate(selected_datasets):
                    selected_columns[name] = st.multiselect(f"Seleziona le colonne ({name})", 
                                                            df_list_selected[i].columns.tolist(), 
                                                            key=f"autocorr_cols_{i}")
            
            with col3:
                max_lag = st.slider("Seleziona il massimo lag", min_value=1, max_value=50, value=20)

            for i, name in enumerate(selected_datasets):
                df = df_list_selected[i]
                for col in selected_columns[name]:
                    fig = compute_autocorrelation(df, col)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
