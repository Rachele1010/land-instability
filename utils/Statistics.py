import streamlit as st
import pandas as pd
import plotly.graph_objects as go  
import plotly.express as px  
from utils.plotting import create_and_render_plot  
from utils.utils import convert_unix_to_datetime, compute_autocorrelation,  compute_cross_correlation, calcola_statistiche, aggrega_dati_temporali

# Funzione principale per la visualizzazione e analisi dei dataset
def Statistics(df_list, filenames):
    if "show_individual_plots" not in st.session_state:
        st.session_state["show_individual_plots"] = True
    if "show_merge_multiple_dataset" not in st.session_state:
        st.session_state["show_merge_multiple_dataset"] = False
    if "show_autocorrelation" not in st.session_state:
        st.session_state["show_autocorrelation"] = False
    if "show_cross_correlation" not in st.session_state:
        st.session_state["show_cross_correlation"] = False
    if "show_pivot" not in st.session_state:
        st.session_state["show_distribution_data"] = False
        
        st.subheader("📈 Data Plotting")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📊 Single Plot"):
            st.session_state["show_individual_plots"] = True
            st.session_state["show_merge_multiple_dataset"] = False
            st.session_state["show_autocorrelation"] = False
            st.session_state["show_cross_correlation"] = False
    with col2:
        if st.button("🔄 Merge Datasets"):
            st.session_state["show_individual_plots"] = False
            st.session_state["show_merge_multiple_dataset"] = True
            st.session_state["show_autocorrelation"] = False
            st.session_state["show_cross_correlation"] = False
    with col3:
        if st.button("📈 Autocorrelation"):
            st.session_state["show_individual_plots"] = False
            st.session_state["show_merge_multiple_dataset"] = False
            st.session_state["show_autocorrelation"] = True
            st.session_state["show_cross_correlation"] = False
    with col4:
        if st.button("🔀 Cross-Correlation"):
            st.session_state["show_individual_plots"] = False
            st.session_state["show_merge_multiple_dataset"] = False
            st.session_state["show_autocorrelation"] = False
            st.session_state["show_cross_correlation"] = True
    with col5:
        if st.button("🔄 Distribution Data"):
            st.session_state["show_distribution_data"] = True
            st.session_state["show_individual_plots"] = False
            st.session_state["show_merge_multiple_dataset"] = False
            st.session_state["show_autocorrelation"] = False
            st.session_state["show_cross_correlation"] = False

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
                plot_type = st.selectbox(f"Plot Type {idx + 1}", ["Basic Scatter", "Basic Bar", "Basic Line", "Mixed Line and Bar", 
                                         "Calendar Heatmap", "DataZoom"], key=f"plot_type_{idx}")

            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(df)
            with col2:
                create_and_render_plot(df, x_axis, y_axis, plot_type)

    # Sezione per Merge Datasets (UNICO GRAFICO)
    elif st.session_state["show_merge_multiple_dataset"]:
        st.subheader("📊 Merge Multiple Datasets in One Plot")
        
        selected_datasets = st.multiselect("Seleziona i dataset", filenames, default=filenames)

        if selected_datasets:
            fig = go.Figure()  # Unico grafico

            x_axes, y_axes, second_y_axes, plot_types = {}, {}, {}, {}

            col1, col2, col3, col4 = st.columns(4)

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
                    selected_plot_type = st.selectbox(f"Plot Type ({dataset_name})", 
                                        ["Scatter", "Bar", "Line"], 
                                        key=f"plot_type_{i}")
                    plot_types[dataset_name] = selected_plot_type

            with col4:
                for i, dataset_name in enumerate(selected_datasets):
                    second_y_axes[dataset_name] = st.checkbox(f"Secondo asse Y? ({dataset_name})", key=f"secondary_y_{i}")

            for dataset_name in selected_datasets:
                df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                
                if dataset_name in x_axes and dataset_name in y_axes:
                    trace_kwargs = {
                        "x": df[x_axes[dataset_name]],
                        "y": df[y_axes[dataset_name]],
                        "name": dataset_name,
                        "yaxis": "y2" if second_y_axes.get(dataset_name, False) else "y1"
                    }
                    
                    if plot_types[dataset_name] == "Scatter":
                        fig.add_trace(go.Scatter(mode='lines+markers', **trace_kwargs))
                    elif plot_types[dataset_name] == "Bar":
                        fig.add_trace(go.Bar(**trace_kwargs))
                    elif plot_types[dataset_name] == "Line":
                        fig.add_trace(go.Scatter(mode='lines', **trace_kwargs))

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

    elif st.session_state["show_autocorrelation"]:
        st.subheader("📈 Autocorrelation Analysis")
    
        # Selezione dataset
        selected_datasets = st.multiselect("Seleziona i dataset", filenames, default=filenames)
    
        if selected_datasets:
            fig = go.Figure()
            y_axis_1, y_axis_2, plot_types, max_lag_values = {}, {}, {}, {}
    
            # UI con 4 colonne: Y1, Y2 (opzionale), tipo di grafico, lag
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
            with col1:
                for i, dataset_name in enumerate(selected_datasets):
                    df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                    y_axis_1[dataset_name] = st.selectbox(f"Primary Y Axis ({dataset_name})", df.columns.tolist(), key=f"y_axis1_{i}")
    
            with col2:
                for i, dataset_name in enumerate(selected_datasets):
                    df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                    y_axis_2[dataset_name] = st.selectbox(f"Secondary Y Axis (opzionale) ({dataset_name})", ["None"] + df.columns.tolist(), key=f"y_axis2_{i}")
    
            with col3:
                for i, dataset_name in enumerate(selected_datasets):
                    plot_types[dataset_name] = st.selectbox(f"Plot Type ({dataset_name})", ["Basic Scatter", "Basic Bar", "Basic Line", "Mixed Line and Bar", 
                                         "Calendar Heatmap", "DataZoom"], key=f"plot_type_{i}")
    
            with col4:
                for i, dataset_name in enumerate(selected_datasets):
                    max_lag_values[dataset_name] = st.slider(f"Lag ({dataset_name})", min_value=1, max_value=100, value=50, key=f"lag_{i}")
    
            # Creazione del grafico
            for dataset_name in selected_datasets:
                df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                
                # Prima variabile Y
                lags, autocorr_values = compute_autocorrelation(df, y_axis_1[dataset_name], max_lag_values[dataset_name])
                fig.add_trace(go.Scatter(
                    x=lags, y=autocorr_values,
                    mode="lines+markers" if plot_types[dataset_name] == "Scatter" else "lines",
                    name=f"{dataset_name} - {y_axis_1[dataset_name]}",
                    yaxis="y1"
                ))
    
                # Seconda variabile Y (se selezionata)
                if y_axis_2[dataset_name] != "None":
                    lags, autocorr_values = compute_autocorrelation(df, y_axis_2[dataset_name], max_lag_values[dataset_name])
                    fig.add_trace(go.Scatter(
                        x=lags, y=autocorr_values,
                        mode="lines+markers" if plot_types[dataset_name] == "Scatter" else "lines",
                        name=f"{dataset_name} - {y_axis_2[dataset_name]}",
                        yaxis="y2"
                    ))
    
            # Layout con secondo asse Y
            fig.update_layout(
                title="Autocorrelation for Multiple Datasets",
                xaxis=dict(title="Lag"),
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
    elif st.session_state["show_cross_correlation"]:
        st.subheader("🔀 Cross-Correlation Analysis")
        
        selected_datasets = st.multiselect("Seleziona i dataset", filenames, default=filenames)
    
        if selected_datasets:
            fig = go.Figure()
            y_axis_1, y_axis_2, plot_types, max_lag_values = {}, {}, {}, {}
    
            # UI con 4 colonne: Y1, Y2 (opzionale), tipo di grafico, lag
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
            with col1:
                for i, dataset_name in enumerate(selected_datasets):
                    df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                    y_axis_1[dataset_name] = st.selectbox(f"Primary Y Axis ({dataset_name})", df.columns.tolist(), key=f"y_axis1_{dataset_name}")
    
            with col2:
                for i, dataset_name in enumerate(selected_datasets):
                    df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                    y_axis_2[dataset_name] = st.selectbox(f"Secondary Y Axis ({dataset_name})", df.columns.tolist(), key=f"y_axis2_{dataset_name}")
    
            with col3:
                for i, dataset_name in enumerate(selected_datasets):
                    plot_types[dataset_name] = st.selectbox(f"Plot Type ({dataset_name})", ["Scatter", "Bar", "Line"], key=f"plot_type_{dataset_name}")
    
            with col4:
                for i, dataset_name in enumerate(selected_datasets):
                    max_lag_values[dataset_name] = st.slider(f"Lag ({dataset_name})", min_value=1, max_value=100, value=50, key=f"lag_{dataset_name}")
    
            # Iteriamo sui dataset selezionati
            for dataset_name in selected_datasets:
                df = convert_unix_to_datetime(df_list[filenames.index(dataset_name)])
                var1 = y_axis_1[dataset_name]  # Ora è definito
                var2 = y_axis_2[dataset_name]  # Ora è definito
                max_lag = max_lag_values[dataset_name]
    
                lags, cross_corr_values = compute_cross_correlation(df, var1, var2, max_lag)
                if lags:
                    fig.add_trace(go.Scatter(x=lags, y=cross_corr_values, mode="lines+markers", name=f"{dataset_name}: {var1} vs {var2}"))
    
            fig.update_layout(title="Cross-Correlation", xaxis_title="Lag", yaxis_title="Cross-Correlation Value")
            st.plotly_chart(fig, use_container_width=True)
    
    elif st.session_state["show_distribution_data"]:
        st.subheader("Distribution Data")
        selected_files = st.multiselect("Select file", filenames)

        for idx, dataset_name in enumerate(filenames):
            if dataset_name not in selected_files:
                continue
    
            df = df_list[idx]
            df = convert_unix_to_datetime(df)
    
            if df is not None:
                #st.write(f"### 📊 Statistiche per {dataset_name}")
                stats_df = calcola_statistiche(df)
    
                # Visualizzazione delle metriche per ogni variabile
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
                # Visualizzazione delle metriche per ogni variabile
                for _, row in stats_df.iterrows():
                    with col1:
                        with st.container():
                            st.write(f"**Variable:** {row['Variabile']}")
                        with col2:
                            st.metric(label="Conteggio", value=row['Counting'])
                        if row['Somma'] != 'N/A':
                            with col3:
                                st.metric(label="Somma", value=row['Sum'])
                            with col4:  
                                st.metric(label="Media", value=row['Mean'])
                            with col5:
                                st.metric(label="Minimo", value=row['Minimum'])
                            with col6:
                                st.metric(label="Massimo", value=row['Max'])
                            with col7:    
                                st.metric(label="Mediana", value=row['Median'])
                        st.markdown("---")
    
                # Selezione di una colonna datetime se disponibile
                colonne_datetime = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
                if len(colonne_datetime) > 0:
                    colonna_data = st.selectbox(f"Select datatime {dataset_name}", colonne_datetime)
                    # Selezione della variabile da plottare
                    col1, col2 = st.columns([1,4])
                    variabili_numeriche = df.select_dtypes(include=['number']).columns
                    with col1:
                        if len(variabili_numeriche) > 0:
                            variabile_plot = st.selectbox(f"Select variable {dataset_name}", variabili_numeriche)
                            aggregazioni = aggrega_dati_temporali(df, colonna_data, variabile_plot)
        
                        # Visualizzazione dei grafici per ogni aggregazione temporale
                    with col2:
                        for periodo, agg_df in aggregazioni.items():
                            st.write(f"#### Plot {periodo} by {dataset_name}")
                            fig = px.bar(agg_df, x=agg_df.index, y=agg_df.values, title=f"{periodo} Aggregate")
                            st.plotly_chart(fig)
                        else:
                            st.warning(f"⚠️ No available numeric variables for plotting in {dataset_name}.")
                    else:
                        st.warning(f"⚠️ No datatime on {dataset_name}.")
    
