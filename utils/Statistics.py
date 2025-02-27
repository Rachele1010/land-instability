import streamlit as st
import pandas as pd
import plotly.graph_objects as go  
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

    return lags, autocorr_values

# Funzione principale per la visualizzazione e analisi dei dataset
def Statistics(df_list, filenames):
    if "mode" not in st.session_state:
        st.session_state["mode"] = "single"

    st.subheader("📈 Data Plotting")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Single Plot"):
            st.session_state["mode"] = "single"
    with col2:
        if st.button("🔄 Merge Datasets"):
            st.session_state["mode"] = "merge"
    with col3:
        if st.button("📈 Autocorrelation"):
            st.session_state["mode"] = "autocorrelation"

    # Sezione per i singoli grafici
    if st.session_state["mode"] == "single":
        for idx, df in enumerate(df_list):
            df = convert_unix_to_datetime(df)
            st.caption(f"**Dataset {idx + 1} - {filenames[idx]}**")

            col1, col2, col3 = st.columns(3)
            with col1:
                x_axis = st.selectbox(f"X Axis {idx + 1}", df.columns.tolist(), key=f"x_axis_{idx}")
            with col2:
                y_axis = st.selectbox(f"Y Axis {idx + 1}", df.columns.tolist(), key=f"y_axis_{idx}")
            with col3:
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["Scatter", "Bar", "Line"], key=f"plot_type_{idx}")

            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(df)
            with col2:
                create_and_render_plot(df, x_axis, y_axis, plot_type)

    # Sezione per Merge Datasets (UNICO GRAFICO)
    elif st.session_state["mode"] == "merge":
        st.subheader("📊 Merge Multiple Datasets in One Plot")
        selected_datasets = st.multiselect("Seleziona i dataset", filenames, default=filenames)
        
        if selected_datasets:
            fig = go.Figure()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                x_axes = {name: st.selectbox(f"X Axis ({name})", df_list[filenames.index(name)].columns.tolist(), key=f"x_axis_merge_{name}") for name in selected_datasets}
            with col2:
                y_axes = {name: st.selectbox(f"Y Axis ({name})", df_list[filenames.index(name)].columns.tolist(), key=f"y_axis_merge_{name}") for name in selected_datasets}
            with col3:
                plot_types = {name: st.selectbox(f"Plot Type ({name})", ["Scatter", "Bar", "Line"], key=f"plot_type_merge_{name}") for name in selected_datasets}
            
            for name in selected_datasets:
                df = convert_unix_to_datetime(df_list[filenames.index(name)])
                trace_kwargs = {"x": df[x_axes[name]], "y": df[y_axes[name]], "name": name}
                
                if plot_types[name] == "Scatter":
                    fig.add_trace(go.Scatter(mode='lines+markers', **trace_kwargs))
                elif plot_types[name] == "Bar":
                    fig.add_trace(go.Bar(**trace_kwargs))
                elif plot_types[name] == "Line":
                    fig.add_trace(go.Scatter(mode='lines', **trace_kwargs))
            
            fig.update_layout(title="Merged Datasets", xaxis=dict(title="X Axis"), yaxis=dict(title="Y Axis"))
            st.plotly_chart(fig, use_container_width=True)

    # Sezione per Autocorrelazione (UNICO GRAFICO CON PIÙ VARIABILI)
    elif st.session_state["mode"] == "autocorrelation":
        st.subheader("📈 Autocorrelation Analysis")
        selected_datasets = st.multiselect("Seleziona i dataset", filenames, default=filenames)
        
        if selected_datasets:
            fig = go.Figure()
            col1, col2 = st.columns(2)
            
            with col1:
                autocorr_cols = {name: st.selectbox(f"Variabile ({name})", df_list[filenames.index(name)].columns.tolist(), key=f"autocorr_col_{name}") for name in selected_datasets}
            
            for name in selected_datasets:
                df = convert_unix_to_datetime(df_list[filenames.index(name)])
                lags, autocorr_values = compute_autocorrelation(df, autocorr_cols[name])
                fig.add_trace(go.Scatter(x=lags, y=autocorr_values, mode='lines+markers', name=name))
            
            fig.update_layout(title="Autocorrelation Plot", xaxis=dict(title="Lag"), yaxis=dict(title="Autocorrelation Coefficient"))
            st.plotly_chart(fig, use_container_width=True)


