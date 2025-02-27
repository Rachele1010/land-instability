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
        st.error(f"❌ Errore: La colonna '{column}' non esiste nel DataFrame.")
        return None
    autocorr_values = [df[column].autocorr(lag) for lag in range(1, min(len(df), max_lag))]
    lags = list(range(1, len(autocorr_values) + 1))
    return lags, autocorr_values
    
def compute_cross_correlation(df, column1, column2, max_lag=50):
    if column1 not in df.columns or column2 not in df.columns:
        st.error("❌ Errore: Una delle colonne selezionate non esiste nel DataFrame.")
        return None
    cross_corr_values = [df[column1].corr(df[column2].shift(lag)) for lag in range(1, min(len(df), max_lag))]
    lags = list(range(1, len(cross_corr_values) + 1))
    return lags, cross_corr_values

# Funzione per calcolare le statistiche
def calcola_statistiche(df):
    stats = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            stats.append({
                'Variabile': col,
                'Conteggio': df[col].count(),
                'Somma': df[col].sum(),
                'Media': df[col].mean(),
                'Minimo': df[col].min(),
                'Massimo': df[col].max(),
                'Mediana': df[col].median()
            })
        else:
            stats.append({
                'Variabile': col,
                'Conteggio': df[col].count(),
                'Somma': 'N/A',
                'Media': 'N/A',
                'Minimo': 'N/A',
                'Massimo': 'N/A',
                'Mediana': 'N/A'
            })
    return pd.DataFrame(stats)

# Funzione per aggregare dati temporali
def aggrega_dati_temporali(df, colonna_data, colonna_valore):
    df = df.set_index(colonna_data)
    aggregazioni = {
        'Annuale': df[colonna_valore].resample('Y').sum(),
        'Mensile': df[colonna_valore].resample('M').sum(),
        'Stagionale': df[colonna_valore].resample('Q').sum(),
        'Semestrale': df[colonna_valore].resample('6M').sum()
    }
    return aggregazioni
