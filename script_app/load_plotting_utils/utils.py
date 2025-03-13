import streamlit as st
import pandas as pd
import plotly.graph_objects as go  
import plotly.express as px  
from script_app.load_plotting_utils.plotting import create_and_render_plot  

# Funzione per convertire timestamp Unix in datetime
import pandas as pd

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
        elif pd.api.types.is_string_dtype(df[col]):
            # Verifica se la colonna è nel formato YYYYMMDD
            if df[col].str.match(r'^\d{8}$').all():
                df[col] = pd.to_datetime(df[col], format='%Y%m%d')
            # Verifica se la colonna è nel formato YYYY-MM-DD
            elif df[col].str.match(r'^\d{4}-\d{2}-\d{2}$').all():
                df[col] = pd.to_datetime(df[col], format='%Y-%m-%d')
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

import pandas as pd

def aggrega_datos_time(df, colonna_data, colonna_valore):
    # Assicura che la colonna datetime sia nel formato corretto
    df[colonna_data] = pd.to_datetime(df[colonna_data], errors='coerce')
    
    # Rimuove eventuali righe con date nulle
    df = df.dropna(subset=[colonna_data])
    
    # Imposta la colonna datetime come indice
    df = df.set_index(colonna_data)
    
    # Riempie eventuali NaN nella colonna di valore
    df[colonna_valore] = df[colonna_valore].fillna(0)
    
    # Mappa le stagioni
    stagioni = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn"
    }
    
    df['Season'] = df.index.month.map(stagioni)
    
    # Mantiene l'ordine corretto delle stagioni
    stagioni_ordine = pd.CategoricalDtype(["Winter", "Spring", "Summer", "Autumn"], ordered=True)
    df['Season'] = df['Season'].astype(stagioni_ordine)

    # Aggregazione per stagione
    agg_stagioni = df.groupby('Season')[colonna_valore].count()

    # Debug per controllare la struttura dei dati
    print("Aggregazioni Stagionali:")
    print(agg_stagioni)

    aggregazioni = {
        'Annually': df[colonna_valore].resample('YE').count(),
        'Monthly': df[colonna_valore].resample('ME').count(),
        'Seasonality': agg_stagioni,
        'Six-monthly': df[colonna_valore].resample('6M').count()
    }
    
    return aggregazioni
