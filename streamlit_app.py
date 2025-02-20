import streamlit as st
# Importa tutte le funzioni dalla cartella "Function"
st.set_page_config(layout="wide", page_title="Land instability", page_icon="🌍", initial_sidebar_state="auto")
import hydralit_components as hc
from PIL import Image
from utils.display_dashboard import display_dashboard
# Definizione della UI per il "Map Generator" e "Statistics"
class WebUI:
    def __init__(self):
        # Impostazione della pagina
        st.set_page_config(page_title="maps4FS", page_icon="🚜", layout="wide")

        # Creazione dei tabs
        generator_tab, statistics_tab = st.tabs([
            "🗺️ Map Generator",
            "📊 Statistics",
        ])

        with generator_tab:
            self.generate_map()

        with statistics_tab:
            self.show_statistics()

    def generate_map(self):
        st.subheader("Map Generator")
        # Aggiungi la tua logica per visualizzare la mappa con i punti caricati
        # Supponiamo che i tuoi dati siano in un DataFrame chiamato `df_points`
        df_points = st.session_state.get("data_points", pd.DataFrame())  # Ad esempio, dati caricati precedentemente
        if not df_points.empty:
            # Visualizzare i punti sulla mappa (esempio con Plotly)
            fig = px.scatter_geo(df_points, lat="latitude", lon="longitude", color="category")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No points data available to generate the map.")
        
    def show_statistics(self):
        st.subheader("Statistics")
        # Carica i dati filtrati come definito nel tuo codice
        uploaded_file = st.file_uploader("Carica il tuo file (CSV, TXT, Excel)", type=["csv", "txt", "xlsx"])
        if uploaded_file is not None:
            df = load_and_display_file(uploaded_file)
            if df is not None:
                st.write("Dati caricati:", df.head())

                # Aggiungi operazioni statistiche
                st.markdown("### Operazioni sui Dati")
                operation_type = st.selectbox("Scegli il tipo di operazione", ["Somma", "Media", "Conteggio"])
                column = st.selectbox("Scegli la colonna", df.columns.tolist())
                
                if operation_type == "Somma":
                    result = df[column].sum()
                elif operation_type == "Media":
                    result = df[column].mean()
                elif operation_type == "Conteggio":
                    result = df[column].count()
                
                st.write(f"Risultato dell'operazione {operation_type}: {result}")

                # Visualizza i grafici
                plot_type = st.selectbox("Scegli il tipo di grafico", ["Bar Chart", "Line Chart", "Scatter Chart"])
                x_axis = st.selectbox("Scegli l'asse X", df.columns.tolist())
                y_axis = st.selectbox("Scegli l'asse Y", df.columns.tolist())

                if plot_type == "Bar Chart":
                    fig = create_basic_bar_chart(df, x_axis, y_axis)
                elif plot_type == "Line Chart":
                    fig = create_basic_line_chart(df, x_axis, y_axis)
                elif plot_type == "Scatter Chart":
                    fig = create_basic_scatter_chart(df, x_axis, y_axis)

                st.plotly_chart(fig, use_container_width=True)
def main():
    # Definisci il menu con le voci principali e i sottomenu
    menu_data = [
        {'label': "Dashboard", 'ttip': "I'm the Dashboard tooltip!"},
        {'label': "Info", 'ttip': "For some problem, Contact us!"}
    ]
        # Tema personalizzato per il menu
    over_theme = {
        'txc_inactive': '#FFFFFF',  # Colore del testo inattivo
        'menu_background': '#2E8B57',  # Verde scuro per lo sfondo della barra
        'txc_active': '#FFFFFF',  # Testo bianco quando attivo
        'option_active': '#2E8B57',  # Verde scuro menta per l'opzione attiva
    }
    # Carica l'immagine "itineris.jpg" per il logo in alto a sinistra
    logo_itineris = Image.open('itineris.jpg')

    # Crea la barra di navigazione al centro
    menu_id = hc.nav_bar(
        menu_definition=menu_data,
        override_theme=over_theme,
        hide_streamlit_markers=True, # Mostra il segnaposto di Streamlit
        sticky_nav=True, # Appiccicoso in alto
        sticky_mode='sticky', # Appiccicoso
    )
    # Cambia l'URL in base al menu selezionato
    if menu_id == 'Dashboard':
        st.query_params["page"] = "Dashboard"
    elif menu_id == 'Info':
        st.query_params["page"] = "Info"
    # Retrieve and display the current query parameters
    query_params = st.query_params
#################################################################################################################################################################################################################
##################### Dashboard #################################################################################################################################################################################
#################################################################################################################################################################################################################
    # Verifica cosa è stato selezionato nel menu
    if menu_id == "Dashboard":
        # Carica e mostra l'immagine di copertura centrata        
        st.title("Welcome to Downstream - Land Domain")
        display_dashboard()
        st.stop()
#################################################################################################################################################################################################################
##################### CONTACT #################################################################################################################################################################################
#################################################################################################################################################################################################################
    # Sezione Contatti
    if menu_id == "Info":
        st.header("Information")
        st.subheader("Contact Us")
        st.write("""Information about how to contact the team or get support. 
                 Rachele Franceschini : rfranceschini@ogs.it""")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("For more details about ITINERIS project, click on link -> **[ITINERIS](https://itineris.d4science.org/)**")
    else:
        # Gestione della UI "Map Generator" e "Statistics"
        WebUI()
if __name__ == "__main__":
    main()
