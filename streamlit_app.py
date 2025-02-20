import streamlit as st
# Importa tutte le funzioni dalla cartella "Function"
#st.set_page_config(layout="wide", page_title="Land instability", page_icon="🌍", initial_sidebar_state="auto")
def __init__(self):
        st.set_page_config(layout="wide", page_title="Land instability", page_icon="🌍", initial_sidebar_state="auto")
        #st.set_page_config(page_title="maps4FS", page_icon="🚜", layout="wide")
        (
            generator_tab,
            statistics_tab,
            step_by_step_tab,
            video_tutorials_tab,
            coverage_tab,
            toolbox_tab,
            knowledge_tab,
            faq_tab,
        ) = st.tabs(
            [
                "🗺️ Map Generator",
                "📊 Statistics",
                "🔢 Step by step",
                "📹 Video Tutorials",
                "🌐 Coverage",
                "🧰 Modder Toolbox",
                "📖 Knowledge base",
                "📝 FAQ",
            ]
        )

        with generator_tab:
            self.generator = GeneratorUI()

        with statistics_tab:
            components.iframe(
                "https://stats.maps4fs.xyz/public/dashboard/"
                "f8defe6a-09db-4db1-911f-b6b02075d4b2#refresh=60",
                height=2500,
                scrolling=False,
            )
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
        #cover_image = Image.open('copertina_4ai.png')
        #st.image(cover_image, use_column_width=True)
        # Carica e mostra l'immagine di copertura centrata        
        st.title("Welcome to Downstream - Land Domain")
        # Testo giustificato usando st.markdown e HTML
        #st.markdown(
        #"""
        #<div style="text-align: justify; font-size: 20px;">
        #ITINERIS - Italian Integrated Environmental Research Infrastructures System is a project funded by EU - 
        #Next Generation EU PNRR- Mission 4 “Education and Research” - Component 2: “From research to business” - 
        #Investment 3.1: “Fund for the realisation of an integrated system of research and innovation infrastructures”.
        #ITINERIS coordinates a network of national nodes from 22 Research Infrastructures, as ATLaS (Advanced Technologies for Landslides).
        #ATLaS is a research infrastructure established aiming to develop leading-edge methodologies (Mission)
        #for the prevention and management of ground instabilities. 
        #Downstream VRE - Land Domain proposes the main aim to provide scientific and openly accessible digital data on environmental observations.
        #The Itineris project has allowed the application of monitoring systems in different sites distributed in the Italian national territory.
        #The case studies are presented below. Through the Dashboard system it is possible to query and view the data currently available for instability monitoring.
        #</div>
        #""", unsafe_allow_html=True)
        #st.subheader("Visualization and Plotting data")
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
         #with col2:
            #st.image(logo_itineris, caption='Copyright © ITINERIS 2023-2024', use_container_width=False)

if __name__ == "__main__":
    main()
