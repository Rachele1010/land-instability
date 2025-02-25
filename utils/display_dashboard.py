import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_echarts import st_echarts
from utils.plotting import create_and_render_plot
from utils.load import load_file, process_file
from utils.map_combined_datasets import map_combined_datasets
from utils.Statistics import Statistics

def display_dashboard():
    st.header("Data Analysis and Plotting")
    st.write("Here you can upload and view your data on a map and plot." 
             " Use the side window to upload your files, and the dashboard will display the various products: **🌍 Map Generator** and **📊 Statistics**."
             " Choose the chart format, correlate, and implement simple analyses. There is no data loading limit.")

    # Upload dei file
    st.sidebar.header("📂 Upload Files")
    uploaded_files = st.sidebar.file_uploader("Drag & Drop your CSV files here", type=['csv', 'xlsx', 'txt'], accept_multiple_files=True)

    if not uploaded_files:
        st.sidebar.info("No files uploaded yet.")
        return
    
    df_list = []
    filenames = []

    for uploaded_file in uploaded_files:
        df = load_file(uploaded_file)
        if df is not None:
            df = process_file(df)
            df_list.append(df)
            filenames.append(uploaded_file.name)
    
    tab1, tab2 = st.tabs(["🌍 Map Generator", "📊 Statistics"])
    
    with tab1:
        map_combined_datasets(df_list, filenames)
    
    with tab2:
        Statistics(df_list, filenames)
