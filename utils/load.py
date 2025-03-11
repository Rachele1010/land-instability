import re
import io
import pandas as pd
import streamlit as st

# 🔹 Rimuove il separatore delle migliaia senza toccare i separatori di colonna
def remove_thousands_separator(text):
    """Rimuove la virgola come separatore delle migliaia, senza toccare i separatori di colonna."""
    return re.sub(r'(?<=\d),(?=\d{1,3}(\D|$))', '', text)

# 🔹 Normalizza il separatore senza eliminare i ritorni a capo
def normalize_separator(text):
    """Normalizza i separatori mantenendo le righe separate"""
    text = remove_thousands_separator(text)  # Rimuove il separatore delle migliaia
    text = re.sub(r'\s*,\s*', ',', text)  # Rimuove spazi attorno alle virgole (separatore di colonna)
    text = re.sub(r'\s*;\s*', ';', text)  # Rimuove spazi attorno ai punti e virgola
    text = re.sub(r'\s*[,;]\s*', ',', text)  # Sostituisce punto e virgola e virgole con un'unica virgola
    text = re.sub(r'[ ]+', ' ', text)  # Sostituisce spazi multipli con singoli MA mantiene i ritorni a capo
    return text  # Non rimuoviamo '\n'!

@st.cache_data
def load_file(uploaded_file):
    """Carica il file CSV o TXT con separatori misti senza perdere la struttura"""
    if uploaded_file.name.endswith(('.csv', '.txt')):
        try:
            raw_text = uploaded_file.getvalue().decode("utf-8")  # Legge il contenuto del file
            normalized_text = normalize_separator(raw_text)  # Normalizza i separatori
            df = pd.read_csv(io.StringIO(normalized_text), sep=",", engine="python")  # Legge il file con pandas

            if df.empty:
                st.error("❌ Il dataset è vuoto. Controlla il file e il separatore.")
                return None

            return df

        except pd.errors.ParserError as e:
            st.error(f"❌ Errore di parsing: {e}")
            return None

    elif uploaded_file.name.endswith('.xlsx'):
        return pd.read_excel(uploaded_file)
    else:
        st.error("Formato file non supportato")
        return None

# 🔹 Funzione per inferire e analizzare le date nel DataFrame
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

# 🔹 Funzione per mantenere i tipi originali delle colonne
def preserve_column_types(df):
    """
    Mantiene il tipo di dati originale di ogni colonna:
    - Se la colonna ha solo interi -> mantiene int
    - Se ha numeri decimali -> mantiene float
    - Se contiene testo -> mantiene stringhe
    """
    for col in df.columns:
        # Controlla se la colonna contiene solo numeri interi
        if pd.api.types.is_numeric_dtype(df[col]) and all(df[col] % 1 == 0):  
            df[col] = df[col].astype(int)  # Converte in interi
        
        # Se la colonna contiene numeri decimali, lascia float
        elif pd.api.types.is_float_dtype(df[col]):  
            df[col] = df[col].astype(float)  

        # Se la colonna contiene testo, lascia stringhe
        elif pd.api.types.is_object_dtype(df[col]):  
            df[col] = df[col].astype(str)  

    return df

# 🔹 Funzione per elaborare i dati del DataFrame
def process_file(df):
    """Elabora i dati del DataFrame."""
    df = infer_and_parse_dates(df)  # Analizza e converte le date
    df = preserve_column_types(df)  # Mantiene i tipi originali delle colonne
    return df

# 🔹 Funzione per caricare e visualizzare il file
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

# 🔹 Interfaccia utente
uploaded_file = st.file_uploader("Upload your file (CSV, TXT, Excel)", type=["csv", "txt", "xlsx"])

if uploaded_file is not None:
    load_and_display_file(uploaded_file)
else:
    st.info("No file.")



