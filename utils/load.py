import streamlit as st
import pandas as pd
import io

# Funzione per rilevare il separatore di colonna nei file CSV o TXT
def detect_separator(uploaded_file):
    """Rileva il separatore di colonna in un CSV o TXT."""
    first_line = io.StringIO(uploaded_file.getvalue().decode("utf-8")).readline()
    possible_separators = [';', ',', '\t', ' ']  
    separator_counts = {sep: first_line.count(sep) for sep in possible_separators}
    return max(separator_counts, key=separator_counts.get) if max(separator_counts.values()) > 0 else ','

# Funzione per caricare un file con gestione degli errori
@st.cache_data
@st.cache_data
def load_file(uploaded_file):
    """Carica un file CSV, TXT o Excel e lo converte sempre in DataFrame."""
    try:
        if uploaded_file.name.endswith(('.csv', '.txt')):
            sep = detect_separator(uploaded_file)
            df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")), sep=sep)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, sheet_name=0)

            # Se il risultato è una Series, convertirlo in DataFrame
            if isinstance(df, pd.Series):
                df = df.to_frame()

            # Se la prima riga è numerica o None, impostala come intestazione
            if df.shape[0] > 1 and not isinstance(df.columns[0], str):
                df.columns = df.iloc[0]  # Imposta la prima riga come intestazione
                df = df[1:].reset_index(drop=True)

        else:
            st.error("❌ Formato file non supportato.")
            return None

        return df
    except Exception as e:
        st.error(f"❌ Errore nel caricamento del file {uploaded_file.name}: {e}")
        return None

# Funzione per convertire colonne di testo in formato data
def infer_and_parse_dates(df):
    """Converti automaticamente colonne contenenti date."""
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")  # Converti in datetime, ignora errori
    return df

# Funzione per convertire i numeri con il separatore decimale corretto
def convert_decimal_format(df, decimal_sep):
    """Converte i numeri con il separatore decimale scelto (punto o virgola)."""
    for col in df.columns:
        if df[col].dtype == 'object':  # Considera solo colonne di testo
            try:
                df[col] = df[col].str.replace(' ', '').str.replace(',', '.') if decimal_sep == '.' else df[col].str.replace('.', '').str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors="coerce")  # Converte in numero
            except Exception:
                continue
    return df

# Funzione principale per elaborare i dati
def process_file(df, decimal_sep):
    """Elabora il DataFrame, gestendo date e numeri."""
    df = infer_and_parse_dates(df)  # Converti le date
    df = convert_decimal_format(df, decimal_sep)  # Converti i numeri

    # Se l'utente ha scelto la virgola, formatta i numeri per la visualizzazione
    if decimal_sep == ",":
        df = df.applymap(lambda x: f"{x:.2f}".replace(".", ",") if isinstance(x, float) else x)
    
    return df

# Funzione per caricare e visualizzare il file
def load_and_display_file(uploaded_file, decimal_sep):
    """Carica e mostra il file con il separatore decimale scelto dall'utente."""
    try:
        file_name = uploaded_file.name  

        if file_name not in st.session_state:  # Evita ricaricamenti inutili
            df = load_file(uploaded_file)  
            if df is not None:
                df = process_file(df, decimal_sep)  
                st.session_state[file_name] = df  

        df = st.session_state.get(file_name)
        if df is not None:
            st.subheader(f"📂 File: {file_name}")  
            st.dataframe(df)  
            return df

    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")

    return None

# UI di Streamlit
st.title("📊 Caricamento e Elaborazione Dati")
uploaded_file = st.file_uploader("📂 Carica un file CSV, TXT o Excel", type=["csv", "txt", "xlsx"])

# Selettore per il separatore decimale
#decimal_sep = st.radio("Scegli il separatore decimale:", (".", ","))

if uploaded_file is not None:
    load_and_display_file(uploaded_file, decimal_sep)
else:
    st.info("📁 Nessun file caricato.")

