import streamlit as st
import pandas as pd
import io
import re
# Funzione per rilevare il separatore in un file CSV o TXT
# Funzione per standardizzare il separatore
def normalize_separator(text):
    """Sostituisce i separatori misti con una virgola e rimuove spazi superflui"""
    text = re.sub(r'\s*[,;]\s*', ',', text)  # Converte ", ", "; ", ";" in ","
    text = re.sub(r'\s+', ' ', text).strip()  # Rimuove spazi multipli
    return text
# Funzione per caricare il file in base all'estensione
@st.cache_data
def load_file(uploaded_file):
    """Carica un file CSV o TXT con separatori misti e normalizza i dati."""
    if uploaded_file.name.endswith(('.csv', '.txt')):
        try:
            # Legge il contenuto del file
            raw_text = uploaded_file.getvalue().decode("utf-8")

            # Normalizza i separatori
            normalized_text = normalize_separator(raw_text)

            # Converte in DataFrame
            df = pd.read_csv(io.StringIO(normalized_text), sep=',', engine='python')

            # Controlla se il dataframe è vuoto
            if df.empty:
                st.error("❌ Il dataset è vuoto dopo il caricamento. Controlla il file e il separatore.")
                return None

            # Mostra un'anteprima per debugging
            st.write(df.head())

            return df

        except pd.errors.ParserError as e:
            st.error(f"❌ Errore di parsing: {e}")
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

# Funzione per elaborare i dati del DataFrame
def process_file(df):
    """Elabora i dati del DataFrame."""
    df = infer_and_parse_dates(df)
    #df = convert_decimal_comma(df, decimal_sep)
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
        st.error(f"Error file CSV: {e}")
    except Exception as e:
        st.error(f"Error: {e}")

# Interfaccia utente
uploaded_file = st.file_uploader("Upload your file (CSV, TXT, Excel)", type=["csv", "txt", "xlsx"])

if uploaded_file is not None:
    load_and_display_file(uploaded_file)
else:
    st.info("No file.")


