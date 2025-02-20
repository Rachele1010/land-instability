import streamlit as st
# Importa tutte le funzioni dalla cartella "Function"
st.set_page_config(layout="wide", page_title="Land instability", page_icon="🌍", initial_sidebar_state="auto")
import hydralit_components as hc
from PIL import Image
from utils.display_dashboard import display_dashboard

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
        #display_dashboard()
        st.stop()
#################################################################################################################################################################################################################
##################### CONTACT #################################################################################################################################################################################
#################################################################################################################################################################################################################
    # Sezione Contatti
    elif menu_id == "Info":
        st.header("Information")
        st.subheader("Contact Us")
        st.write("""Information about how to contact the team or get support. 
                 Rachele Franceschini : rfranceschini@ogs.it""")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("For more details about ITINERIS project, click on link -> **[ITINERIS](https://itineris.d4science.org/)**")
    else:
        # Gestisci la visualizzazione dei tab
        generator_tab, statistics_tab = st.tabs([
            "🗺️ Map Generator",
            "📊 Statistics",
        ])

if __name__ == "__main__":
    main()
