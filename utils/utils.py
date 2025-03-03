import streamlit as st
import pandas as pd
import plotly.graph_objects as go  
import plotly.express as px  
from utils.plotting import create_and_render_plot  

# Funzione per convertire timestamp Unix in datetime
def convert_unix_to_datetime(df):
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # Verifica se i valori sono plausibili per timestamp in secondi
            if df[col].between(1e9, 2e9).all():
                df[col] = pd.to_datetime(df[col], unit='s')
            # Verifica se i valori sono plausibili per timestamp in millisecondi
            elif df[col].between(1e12, 2e12).all():
                df[col] = pd.to_datetime(df[col], unit='ms')
    return df

# Funzione per calcolare l'autocorrelazione
def compute_autocorrelation(df, column, max_lag=50):
    if column not in df.columns:
        st.error(f"❌ Error: One of the selected columns does not exist in the DataFrame.")
        return None
    autocorr_values = [df[column].autocorr(lag) for lag in range(1, min(len(df), max_lag))]
    lags = list(range(1, len(autocorr_values) + 1))
    return lags, autocorr_values
    
def compute_cross_correlation(df, column1, column2, max_lag=50):
    if column1 not in df.columns or column2 not in df.columns:
        st.error("❌ Error: One of the selected columns does not exist in the DataFrame.")
        return None
    cross_corr_values = [df[column1].corr(df[column2].shift(lag)) for lag in range(1, min(len(df), max_lag))]
    lags = list(range(1, len(cross_corr_values) + 1))
    return lags, cross_corr_values

# Funzione per calcolare le statistiche
def calcula_statistics(df):
    stats = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            stats.append({
                'Variable': col,
                'Counting': df[col].count(),
                'Sum': df[col].sum(),
                'Mean': df[col].mean(),
                'Minum': df[col].min(),
                'Max': df[col].max(),
                'Median': df[col].median()
            })
        else:
            stats.append({
                'Variable': col,
                'Counting': df[col].count(),
                'Sum': 'N/A',
                'Mean': 'N/A',
                'Minimum': 'N/A',
                'Max': 'N/A',
                'Median': 'N/A'
            })
    return pd.DataFrame(stats)

# Funzione per aggregare dati temporali
import pandas as pd
import streamlit as st

import pandas as pd
import plotly.express as px

def aggrega_datos_time(df, colonna_data, colonna_valore):
    # Assicuriamoci che la colonna_data sia datetime
    df[colonna_data] = pd.to_datetime(df[colonna_data], errors='coerce')
    
    # Controlliamo che la colonna non abbia valori NaT
    df = df.dropna(subset=[colonna_data])
    
    df = df.set_index(colonna_data)
    
    # Mappatura mesi -> stagioni
    stagioni_map = {
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Autumn', 10: 'Autumn', 11: 'Autumn'
    }

    # Creiamo una colonna "Season"
    df['Season'] = df.index.month.map(stagioni_map)

    # Raggruppiamo per stagione e contiamo
    agg_stagioni = df.groupby("Season")[colonna_valore].count().reset_index()

    # Ordinare le stagioni nella sequenza corretta
    stagione_order = ["Winter", "Spring", "Summer", "Autumn"]
    agg_stagioni["Season"] = pd.Categorical(agg_stagioni["Season"], categories=stagione_order, ordered=True)
    agg_stagioni = agg_stagioni.sort_values("Season")

    # Creiamo il grafico
    fig = px.bar(
        agg_stagioni, 
        x="Season", 
        y=colonna_valore, 
        color="Season", 
        title="Seasonal Data Distribution",
        color_discrete_map={
            "Winter": "blue",
            "Spring": "green",
            "Summer": "orange",
            "Autumn": "brown"
        }
    )
    
    # Creiamo il dizionario con tutti i dati aggregati
    aggregazioni = {
        'Annual': df[colonna_valore].resample('YE').count(),
        'Monthly': df[colonna_valore].resample('ME').count(),
        'Seasonal': agg_stagioni.set_index("Season"),
        'Six-monthly': df[colonna_valore].resample('6M').count()
    }

    return aggregazioni, fig  # Restituiamo i dati aggregati e il grafico

