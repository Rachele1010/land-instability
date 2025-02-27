import streamlit as st
import pandas as pd
import plotly.express as px  
from utils.plotting import create_and_render_plot

# Funzione per convertire timestamp Unix in datetime
def convert_unix_to_datetime(df):
    """
    Converte le colonne di un DataFrame da timestamp Unix a datetime (se applicabile).
    """
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].between(1e9, 2e9).all():
            df[col] = pd.to_datetime(df[col], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    return df

# Funzione per calcolare l'autocorrelazione
def compute_autocorrelation(df, column):
    """
    Calcola e visualizza l'autocorrelazione per una colonna specificata.
    """
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

    st.subheader("📈 Data Analysis")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Single Plot"):
            st.session_state["show_individual_plots"] = True
    with col2:
        if st.button("🔄 Merge Datasets"):
            st.session_state["show_individual_plots"] = False

    # Sezione per i singoli grafici
    if st.session_state["show_individual_plots"]:
        for idx, df in enumerate(df_list):
            df = convert_unix_to_datetime(df.copy())  # Applica la conversione ai timestamp

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

    # Sezione per l'Autocorrelazione
    with col3:
        if st.button("📈 Autocorrelation"):
            st.subheader("📊 Autocorrelation Analysis")

            # Scelta multipla dei file
            selected_files = st.multiselect("Seleziona i dataset per l'autocorrelazione", filenames, default=filenames)

            if not selected_files:
                st.warning("⚠️ Seleziona almeno un dataset per continuare.")
                return

            for file in selected_files:
                idx = filenames.index(file)
                df = convert_unix_to_datetime(df_list[idx].copy())  # Conversione timestamp

                st.markdown(f"### 📊 Dataset: {file}")

                # Scelta multipla delle colonne
                selected_columns = st.multiselect(f"Seleziona le colonne per l'autocorrelazione ({file})", 
                                                  df.columns.tolist(), key=f"autocorr_cols_{idx}")

                if not selected_columns:
                    st.warning(f"⚠️ Seleziona almeno una colonna per il dataset {file}.")
                    continue

                for col in selected_columns:
                    fig = compute_autocorrelation(df, col)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
