import re
import io
import pandas as pd
import streamlit as st

# 🔹 Rimuove il separatore delle migliaia senza toccare i separatori di colonna
def remove_thousands_separator(text):
    """Rimuove la virgola come separatore delle migliaia, senza toccare i separatori di colonna."""
    return re.sub(r'(?<=\d),(?=\d{1,3}(\D|$))', '', text)

def detect_separator(text):
    """Rileva il separatore di colonna in base alla riga con più separatori."""
    possible_separators = [';', ',', '\t', ' ']  # Separatori comuni
    lines = text.split("\n")
    
    # Cerca la riga con più separatori
    best_line = max(lines, key=lambda line: sum(line.count(sep) for sep in possible_separators))

    # Conta le occorrenze di ciascun separatore nella riga selezionata
    separator_counts = {sep: best_line.count(sep) for sep in possible_separators}

    # Se lo spazio ha meno occorrenze di altri separatori, lo escludiamo per evitare errori
    if separator_counts[' '] < max(separator_counts.values()):
        separator_counts.pop(' ')  

    return max(separator_counts, key=separator_counts.get) if max(separator_counts.values()) > 0 else ','

def normalize_separator(text, detected_separator):
    """Normalizza i separatori mantenendo le righe separate"""
    text = remove_thousands_separator(text)  # Rimuove separatori delle migliaia

    # Normalizza separatori, ma mantiene il principale rilevato
    text = re.sub(r'\s*,\s*', ',', text)  # Rimuove spazi attorno alle virgole
    text = re.sub(r'\s*;\s*', ';', text)  # Rimuove spazi attorno ai punti e virgola
    text = re.sub(r'\s*[,;]\s*', detected_separator, text)  # Unifica i separatori alla modalità corretta
    text = re.sub(r'[ ,;]+', detected_separator, text)  # Sostituisce separatori misti con quello corretto

    return text  # Manteniamo i ritorni a capo

def load_file(uploaded_file):
    """Carica il file CSV o TXT con separatori misti senza perdere la struttura"""
    if uploaded_file.name.endswith(('.csv', '.txt')):
        try:
            raw_text = uploaded_file.getvalue().decode("utf-8")  # Legge il contenuto del file
            detected_separator = detect_separator(raw_text)  # Rileva il separatore
            normalized_text = normalize_separator(raw_text, detected_separator)  # Normalizza il testo
            df = pd.read_csv(io.StringIO(normalized_text), sep=detected_separator, engine="python")  # Legge il file con pandas

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



