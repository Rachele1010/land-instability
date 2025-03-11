import streamlit as st
import pandas as pd
import io
import re
def remove_thousands_separator(text):
    """Rimuove la virgola come separatore delle migliaia, senza toccare i separatori di colonna."""
    # Sostituisce le virgole nei numeri (ma non tra parole)
    return re.sub(r'(?<=\d),(?=\d{3}\b)', '', text)

# Funzione per rilevare il separatore in un file CSV o TXT
# Funzione migliorata per normalizzare il separatore senza eliminare i ritorni a capo
def normalize_separator(text):
    """Normalizza i separatori mantenendo le righe separate"""
    text = remove_thousands_separator(text)  # Rimuove il separatore delle migliaia
    text = re.sub(r'\s*,\s*', ',', text)  # Rimuove spazi attorno alle virgole (separatore di colonna)
    text = re.sub(r'\s*;\s*', ';', text)  # Rimuove spazi attorno ai punti e virgola
    text = re.sub(r'[ ]+', ' ', text)  # Sostituisce spazi multipli con singoli MA mantiene i ritorni a capo
    return text  # Non rimuoviamo '\n'!

@st.cache_data
def load_file(uploaded_file):
    """Carica il file CSV o TXT con separatori misti senza perdere la struttura"""
    if uploaded_file.name.endswith(('.csv', '.txt')):
        try:
            # Legge il contenuto del file
            raw_text = uploaded_file.getvalue().decode("utf-8")

            # DEBUG 1: Mostra il file originale
            #st.write("📄 **Anteprima del file originale:**")
            #st.text("\n".join(raw_text.split("\n")[:10]))  # Prime 10 righe

            # Normalizza il testo SENZA eliminare i ritorni a capo
            normalized_text = normalize_separator(raw_text)

            # DEBUG 2: Mostra il file dopo la normalizzazione
            #st.write("📄 **Anteprima dopo la normalizzazione:**")
            #st.text("\n".join(normalized_text.split("\n")[:10]))

            # Legge il file con pandas usando la virgola come separatore
            df = pd.read_csv(io.StringIO(normalized_text), sep=",", engine="python")

            # DEBUG 3: Mostra la forma del DataFrame
            #st.write(f"📊 **Shape del DataFrame:** {df.shape}")

            # Se il dataframe è vuoto, avvisa l'utente
            if df.empty:
                st.error("❌ Il dataset è ancora vuoto dopo il caricamento. Controlla il file e il separatore.")
                return None

            # DEBUG 4: Mostra le prime righe del DataFrame
            #st.write("📊 **Anteprima del DataFrame:**")
            #st.write(df.head())

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


