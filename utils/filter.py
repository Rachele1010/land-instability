import streamlit as st
import pandas as pd

def dynamic_filter_and_operations(dataframes, file_options):
    """
    Funzione per applicare filtri dinamici sui dataframe selezionati
    e effettuare operazioni sui dati filtrati.
    
    Args:
        dataframes (dict): Dizionario che associa i file ai dataframe.
        file_options (list): Lista delle opzioni di file per il caricamento.
    
    Returns:
        pd.DataFrame: Il dataframe filtrato.
    """
    
    st.sidebar.markdown("##### Dynamic Filter Data")
    
    # Seleziona il dataset
    selected_dataset = st.sidebar.selectbox("Select dataset", file_options)
    
    # Recupera il dataframe corrispondente
    if selected_dataset in dataframes:
        selected_df = dataframes[selected_dataset]
        
        # Se il dataframe non è vuoto, mostra le colonne per il filtro
        if not selected_df.empty:
            column_to_filter = st.sidebar.selectbox("Select column to filter", selected_df.columns.tolist())
            
            # Selezione del tipo di filtro
            filter_type = st.sidebar.radio("Select filter type", ["Range", "Exact", "Contains"])
            
            # Filtro per intervallo di valori (solo per colonne numeriche)
            if filter_type == "Range" and pd.api.types.is_numeric_dtype(selected_df[column_to_filter]):
                min_value = selected_df[column_to_filter].min()
                max_value = selected_df[column_to_filter].max()
                range_values = st.sidebar.slider(
                    "Select range",
                    min_value=float(min_value),
                    max_value=float(max_value),
                    value=(float(min_value), float(max_value))
                )
                selected_df = selected_df[(selected_df[column_to_filter] >= range_values[0]) & (selected_df[column_to_filter] <= range_values[1])]
            
            # Filtro per valore esatto (solo per colonne di tipo stringa)
            elif filter_type == "Exact" and selected_df[column_to_filter].dtype == 'object':
                exact_value = st.text_input("Enter exact value")
                if exact_value:
                    selected_df = selected_df[selected_df[column_to_filter] == exact_value]
            
            # Filtro per contenuto (solo per colonne di tipo stringa)
            elif filter_type == "Contains" and selected_df[column_to_filter].dtype == 'object':
                keyword = st.text_input("Enter keyword")
                if keyword:
                    selected_df = selected_df[selected_df[column_to_filter].str.contains(keyword, case=False, na=False)]
        
        # Filtro per data
        st.sidebar.markdown("##### Filter Data by Date")
        data_to_filter = st.sidebar.selectbox("Select date column", selected_df.columns.tolist())
        
        if pd.api.types.is_datetime64_any_dtype(selected_df[data_to_filter]):
            selected_df[data_to_filter] = pd.to_datetime(selected_df[data_to_filter], errors='coerce')
            min_date = selected_df[data_to_filter].min()
            max_date = selected_df[data_to_filter].max()
            date_range = st.sidebar.date_input(
                "Select date range",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
            
            if date_range:
                selected_df = selected_df[
                    (selected_df[data_to_filter] >= pd.to_datetime(date_range[0])) & 
                    (selected_df[data_to_filter] <= pd.to_datetime(date_range[1]))
                ]
        else:
            st.sidebar.warning("La colonna selezionata non è di tipo datetime.")
        
        # Operazioni sui dati filtrati
        st.sidebar.markdown("### Operations")
        use_operations = st.sidebar.checkbox("Enable operations")
        
        if use_operations:
            selected_column = st.sidebar.selectbox("Select a column", selected_df.columns.tolist(), key="operation_column")
            operation = st.sidebar.selectbox("Select an operation", ["Count", "Sum", "Mean"], key="operation_type")
            
            if operation == "Count":
                result = selected_df[selected_column].count()
            elif operation == "Sum":
                result = selected_df[selected_column].sum()
            elif operation == "Mean":
                result = selected_df[selected_column].mean()
            
            st.sidebar.write(f"Result of {operation} on {selected_column}: {result}")
        
        return selected_df
    else:
        st.sidebar.warning("No data available for the selected dataset.")
        return None
