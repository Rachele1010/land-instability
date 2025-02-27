import streamlit as st
import pandas as pd
import io

# Funzione per rilevare il separatore nel file
def detect_separator(uploaded_file):
    """Detects the column separator in a CSV or TXT file."""
    first_line = io.StringIO(uploaded_file.getvalue().decode("utf-8")).readline()
    possible_separators = [';', ',', '\t', ' ']  # Punto e virgola, virgola, tabulazione, spazio
    separator_counts = {sep: first_line.count(sep) for sep in possible_separators}
    return max(separator_counts, key=separator_counts.get) if max(separator_counts.values()) > 0 else ','

# Funzione per caricare il file
@st.cache_data
def load_file(uploaded_file, decimal_sep):
    """Carica un file e rileva il separatore per CSV/TXT."""
    if uploaded_file.name.endswith(('.csv', '.txt')):
        sep = detect_separator(uploaded_file)
        try:
            df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")), sep=sep, decimal=decimal_sep)
            return df
        except pd.errors.ParserError as e:
            st.error(f"Errore di parsing del file: {e}")
            return None
    elif uploaded_file.name.endswith('.xlsx'):
        return pd.read_excel(uploaded_file, decimal=decimal_sep)
    else:
        st.error("Formato file non supportato")
        return None

# Funzione per convertire il separatore decimale
def convert_decimal(df, decimal_sep):
    """Converte i numeri con il separatore decimale scelto dall'utente."""
    if decimal_sep == ',':
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.replace(',', '.')
        df = df.apply(pd.to_numeric, errors='ignore')  # Converti in numerico se possibile
    return df

# Funzione per elaborare il dataset
def process_file(df, decimal_sep):
    """Elabora il dataset, convertendo numeri e date."""
    df = convert_decimal(df, decimal_sep)
    return df

# Interfaccia utente
uploaded_file = st.file_uploader("Carica il tuo file (CSV, TXT, Excel)", type=["csv", "txt", "xlsx"])

if uploaded_file is not None:
    # Opzione per selezionare il separatore decimale
    decimal_sep = st.radio("Seleziona il separatore decimale", ('.', ','), index=0)

    df = load_file(uploaded_file, decimal_sep)
    
    if df is not None:
        df = process_file(df, decimal_sep)
        st.subheader(f"Anteprima del file: {uploaded_file.name}")
        st.dataframe(df)

