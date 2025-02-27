import streamlit as st
import pandas as pd
import io

# Funzione per rilevare automaticamente il separatore di colonna
def detect_separator(uploaded_file):
    """Rileva il separatore delle colonne in un file CSV o TXT."""
    first_line = io.StringIO(uploaded_file.getvalue().decode("utf-8")).readline()
    possible_separators = [';', ',', '\t', ' ']  # Punto e virgola, virgola, tabulazione, spazio
    separator_counts = {sep: first_line.count(sep) for sep in possible_separators}
    return max(separator_counts, key=separator_counts.get) if max(separator_counts.values()) > 0 else ','

# Funzione per caricare il file in base all'estensione
@st.cache_data
def load_file(uploaded_file, decimal_sep):
    """Carica un file CSV, TXT o Excel e rileva il separatore."""
    try:
        if uploaded_file.name.endswith(('.csv', '.txt')):
            sep = detect_separator(uploaded_file)
            df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")), sep=sep, decimal=decimal_sep)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, decimal=decimal_sep)
        else:
            st.error("Formato file non supportato")
            return None
        return df
    except pd.errors.ParserError as e:
        st.error(f"Errore di parsing del file: {e}")
        return None
    except Exception as e:
        st.error(f"Errore generico nel caricamento del file: {e}")
        return None

# Funzione per inferire e convertire le date nel DataFrame
def infer_and_parse_dates(df):
    """Rileva e converte le colonne di tipo data."""
    date_formats = ['%d/%m/%Y %H:%M:%S', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']  # Possibili formati di data
    for col in df.columns:
        if df[col].dtype == 'object':  # Se la colonna è testuale, proviamo a convertirla in datetime
            for date_format in date_formats:
                try:
                    temp_col = pd.to_datetime(df[col], format=date_format, errors='coerce')
                    if temp_col.notna().sum() > 0:  # Se almeno un valore è valido, assegniamo la colonna
                        df[col] = temp_col
                        break
                except Exception:
                    continue
    return df

# Funzione per convertire i numeri con virgola decimale in float
def convert_decimal(df, decimal_sep):
    """Converte i numeri con il separatore decimale scelto dall'utente."""
    if decimal_sep == ',':
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = df[col].str.replace(',', '.', regex=False).astype(float)
            except ValueError:
                continue  # Se la conversione non è possibile, ignora la colonna
    return df

# Funzione per elaborare il dataset
def process_file(df, decimal_sep):
    """Elabora il dataset: conversione numeri e date."""
    df = infer_and_parse_dates(df)
    df = convert_decimal(df, decimal_sep)
    return df

# Funzione per caricare e visualizzare il file
def load_and_display_file(uploaded_file, decimal_sep):
    """Carica, elabora e visualizza il file con il separatore decimale scelto."""
    try:
        file_name = uploaded_file.name  # Nome del file caricato

        # Se il file non è già stato caricato nella sessione, caricalo e memorizzalo
        if file_name not in st.session_state:
            df = load_file(uploaded_file, decimal_sep)
            if df is not None:
                df = process_file(df, decimal_sep)  # Elabora il dataset
                st.session_state[file_name] = df  # Memorizza il dataframe

        # Recupera il dataframe dalla sessione e visualizzalo
        df = st.session_state.get(file_name)
        if df is not None:
            st.subheader(f"📂 File: {file_name}")  # Mostra il nome del file
            st.dataframe(df)  # Visualizza il DataFrame
            return df

        return None
    except pd.errors.ParserError as e:
        st.error(f"Errore durante il parsing del file CSV: {e}")
    except Exception as e:
        st.error(f"Errore generico: {e}")

# 🔹 Interfaccia utente Streamlit
st.title("📊 Caricamento e Analisi Dataset")

# Caricamento del file
uploaded_file = st.file_uploader("Carica il tuo file (CSV, TXT, Excel)", type=["csv", "txt", "xlsx"])

# Opzione per scegliere il separatore decimale
decimal_sep = st.radio("🔢 Seleziona il separatore decimale", ('.', ','), index=0)

# Se un file è stato caricato, elaboralo e visualizzalo
if uploaded_file is not None:
    load_and_display_file(uploaded_file, decimal_sep)
else:
    st.info("📂 Nessun file caricato.")


