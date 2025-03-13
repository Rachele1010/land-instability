import streamlit as st
# Importa tutte le funzioni dalla cartella "Function"
st.set_page_config(layout="wide", page_title="Land instability", page_icon="🌍", initial_sidebar_state="auto")
import hydralit_components as hc
from PIL import Image
from script_app.display_dashboard import display_dashboard

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
    #else:
        # Gestisci la visualizzazione dei tab
        #generator_tab, statistics_tab = st.tabs([
        #    "📊 Statistics", "🗺️ Map Generator",])
        
#################################################################################################################################################################################################################
##################### CONTACT #################################################################################################################################################################################
#################################################################################################################################################################################################################
    # Sezione Contatti
    if menu_id == "Info":
        st.header("Information")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Readme - Format file")
            st.caption("Data type")
            st.write("""The following file types can be uploaded: xlsx, csv, txt. 
                        The application reads the comma as a point according to the most widely used scientific system.""") 
            st.caption("Split data")
            st.write("""The column separators must be unique, or all commas, or all spaces, or all semicolons. If the column separators are not the same, 
                    the application may read the data incorrectly and not display it correctly in charts, tables and maps.""")
            st.caption("Datatime")
            st.write("""If the date format is present, the following formats are read: Unixtime, YYYY-MM-DD and is translated to DD-MM-YYYY.""")
            st.caption("Coordinates")
            st.write("""The existing coordinates are preferred in the case studies: latitude, longitude, lat, long, x and y. 
                    However, the system also reads if there is a different formulation with the words "lat" or "lon" within the data frame. 
                    The coordinates should be given in degrees, with a comma as a separator. """)        
        with col2:
            st.subheader("Contact Us")
            st.write("""Information about how to contact the team or get support. Rachele Franceschini : rfranceschini@ogs.it""")
            st.markdown("For more details about ITINERIS project, click on link -> **[ITINERIS](https://itineris.d4science.org/)**")
if __name__ == "__main__":
    main()
