import streamlit as st
import pandas as pd
import io

# Funzione per rilevare il separatore in un file CSV o TXT
def detect_separator(uploaded_file):
    """Detects the column separator in a CSV or TXT file from an uploaded file."""
    first_line = io.StringIO(uploaded_file.getvalue().decode("utf-8")).readline()
    possible_separators = [';', ',', '\t', ' ']  # Punto e virgola, virgola, tabulazione, spazio
    separator_counts = {sep: first_line.count(sep) for sep in possible_separators}
    return max(separator_counts, key=separator_counts.get) if max(separator_counts.values()) > 0 else ','

# Funzione per caricare il file in base al tipo di estensione
@st.cache_data
def load_file(uploaded_file):
    """Carica un file da un oggetto file caricato e rileva il separatore per CSV/TXT."""
    if uploaded_file.name.endswith(('.csv', '.txt')):
        sep = detect_separator(uploaded_file)
        try:
            return pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")), sep=sep)
        except pd.errors.ParserError as e:
            st.error(f"Errore di parsing del file: {e}")
            return None
    elif uploaded_file.name.endswith('.xlsx'):
        return pd.read_excel(uploaded_file)
    else:
        st.error("Formato file non supportato")
        return None

# Funzione per inferire e analizzare le date nel DataFrame
def infer_and_parse_dates(df):
    """Inferisce e analizza le date nel DataFrame."""
    date_formats = ['%d/%m/%Y %H:%M:%S']
    for col in df.columns:
        if df[col].dtype == 'object':
            for date_format in date_formats:
                try:
                    temp_col = pd.to_datetime(df[col], format=date_format, errors='coerce')
                    if temp_col.notna().sum() > 0:
                        df[col] = temp_col
                        break
                except Exception:
                    continue
    return df

# Funzione per convertire i numeri con virgola decimale in float
def convert_decimal_comma(df, decimal_sep=","):
    """Converte i numeri con separatore decimale personalizzato in float."""
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = df[col].str.replace(decimal_sep, '.').astype(float)
            except ValueError:
                continue
    return df

# Funzione per elaborare i dati del DataFrame
def process_file(df, decimal_sep=","):
    """Elabora i dati del DataFrame."""
    df = infer_and_parse_dates(df)
    df = convert_decimal_comma(df, decimal_sep)
    return df

# Funzione per caricare e visualizzare il file
def load_and_display_file(uploaded_file):
    """Carica e visualizza il file."""
    try:
        file_name = uploaded_file.name  # Ottieni il nome del file
        # Se il file non è già stato caricato nella sessione, caricalo e memorizzalo
        if file_name not in st.session_state:
            df = load_file(uploaded_file)  # Carica il file
            if df is not None:
                df = process_file(df)  # Elabora i dati
                st.session_state[file_name] = df  # Memorizza il dataframe in session_state

        # Recupera il dataframe dalla sessione e visualizzalo
        df = st.session_state.get(file_name)
        if df is not None:
            st.subheader(f"File: {file_name}")  # Mostra il nome del file
            st.dataframe(df)  # Mostra il dataframe
            return df

        return None
    except pd.errors.ParserError as e:
        st.error(f"Errore durante il parsing del file CSV: {e}")
    except Exception as e:
        st.error(f"Errore: {e}")

# Interfaccia utente
uploaded_file = st.file_uploader("Carica il tuo file (CSV, TXT, Excel)", type=["csv", "txt", "xlsx"])

if uploaded_file is not None:
    load_and_display_file(uploaded_file)
else:
    st.info("Nessun file caricato.")


