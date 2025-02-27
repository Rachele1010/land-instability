import streamlit as st
import pandas as pd
import plotly.express as px  # Per il grafico di autocorrelazione
from utils.plotting import create_and_render_plot

# Funzione per calcolare l'autocorrelazione
def compute_autocorrelation(df, column):
    if column not in df.columns:
        st.error(f"❌ Errore: La colonna '{column}' non esiste nel DataFrame.")
        return None

    autocorr_values = [df[column].autocorr(lag) for lag in range(1, min(len(df), 50))]
    lags = list(range(1, len(autocorr_values) + 1))

    fig = px.line(x=lags, y=autocorr_values, markers=True, title="Autocorrelation Plot")
    fig.update_xaxes(title="Lag")
    fig.update_yaxes(title="Autocorrelation Coefficient")
    
    return fig

# Modifica della funzione Statistics
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
        autocorr_button = st.button("📈 Autocorrelation")  # Nuovo pulsante

    if st.session_state["show_individual_plots"]:
        for idx, df in enumerate(df_list):
            df = df.copy()
            st.caption(f"**Dataset {idx + 1} - {filenames[idx]}**")

            col1, col2, col3 = st.columns(3)
            with col1:
                x_axis = st.selectbox(f"X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
            with col2:
                y_axis = st.selectbox(f"Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
            with col3:
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["Basic Scatter", "Basic Bar", "Basic Line", 
                                                                  "Mixed Line and Bar", "Calendar Heatmap", "DataZoom"], 
                                         key=f"plot_type_{idx}")

            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(df)
            with col2:
                create_and_render_plot(df, x_axis, y_axis, plot_type)

            # Se l'utente ha premuto il pulsante "Autocorrelation"
            if autocorr_button:
                st.subheader(f"Autocorrelation Analysis - {filenames[idx]}")
                autocorr_col = st.selectbox(f"Seleziona la colonna per l'autocorrelazione ({filenames[idx]})", 
                                            df.columns.tolist(), key=f"autocorr_col_{idx}")
                
                fig = compute_autocorrelation(df, autocorr_col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
