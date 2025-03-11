import streamlit as st
import pandas as pd
import io

# Funzione per rilevare il separatore in un file CSV o TXT
def detect_separator(uploaded_file):
    """Rileva il separatore predominante in un file con separatori misti."""
    content = io.StringIO(uploaded_file.getvalue().decode("utf-8"))

    # Legge le prime 5 righe del file
    lines = [content.readline().strip() for _ in range(5)]

    # Normalizza gli spazi multipli in un solo spazio
    lines = [re.sub(r'\s+', ' ', line) for line in lines]

    possible_separators = [',', ';', '\t', ' ']

    # Conta la frequenza dei separatori per ogni riga
    separator_counts = {sep: sum(line.count(sep) for line in lines) for sep in possible_separators}

    # Trova il separatore più coerente
    best_separator = max(separator_counts, key=separator_counts.get)

    # Se lo spazio è il separatore principale, assicurati che non sia dovuto a spazi multipli
    if best_separator == ' ':
        for line in lines:
            if ',' in line or ';' in line or '\t' in line:
                best_separator = ','  # Riprova con la virgola come fallback
                break

    return best_separator

# Funzione per caricare il file in base al tipo di estensione
@st.cache_data
def load_file(uploaded_file):
    """Carica un file CSV, TXT o Excel con separatori misti e normalizza i dati."""
    if uploaded_file.name.endswith(('.csv', '.txt')):
        sep = detect_separator(uploaded_file)

        try:
            # Normalizza il contenuto per eliminare spazi multipli prima del parsing
            raw_text = uploaded_file.getvalue().decode("utf-8")
            raw_text = re.sub(r'\s+', ' ', raw_text)  # Converte spazi multipli in singoli
            
            # Crea un DataFrame
            df = pd.read_csv(io.StringIO(raw_text), sep=sep, engine='python')

            # Controllo sulla correttezza del parsing
            if df.shape[1] == 1:
                st.warning("⚠️ Il file non sembra tabulato correttamente. Il separatore potrebbe essere errato.")

            # Prova a convertire colonne numeriche e date
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='ignore')  # Converte numeri
                df[col] = pd.to_datetime(df[col], errors='ignore')  # Converte date

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


