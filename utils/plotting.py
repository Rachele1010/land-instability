import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.transform import cumsum
from bokeh.palettes import Category20c
from math import pi
from itertools import cycle
@st.cache_data

def create_basic_bar_chart(df, x, y):
    fig = px.bar(df, x=x, y=y, title="Basic Bar Chart")
    return fig

def create_basic_line_chart(df, x, y):
    fig = px.line(df, x=x, y=y, title="Basic Line Chart")
    return fig

def create_stacked_line_chart(df, x, y1, y2):
    fig = px.line(df, x=x, y=[y1, y2], title="Stacked Line Chart")
    return fig

def create_multiple_y_axes_chart(df, x, y1, y2):
    fig = go.Figure()

    # Grafico a barre
    fig.add_trace(go.Bar(x=df[x], y=df[y1], name='Bar Data', yaxis='y1'))

    # Grafico a linee
    fig.add_trace(go.Line(x=df[x], y=df[y2], name='Line Data', yaxis='y2'))

    # Impostazioni degli assi
    fig.update_layout(
        yaxis=dict(title=y1),
        yaxis2=dict(title=y2, overlaying='y', side='right'),
        title="Multiple Y Axes Chart"
    )
    return fig

def create_mixed_line_and_bar_chart(df, x, y_line, y_bar):
    fig = go.Figure()

    # Aggiungi il grafico a barre
    fig.add_trace(go.Bar(x=df[x], y=df[y_bar], name='Bar Data'))

    # Aggiungi il grafico a linee
    fig.add_trace(go.Line(x=df[x], y=df[y_line], name='Line Data'))

    fig.update_layout(title="Mixed Line and Bar Chart")
    return fig

def create_basic_scatter_chart(df, x, y):
    fig = px.scatter(df, x=x, y=y, title="Basic Scatter Chart")
    return fig

def create_effect_scatter_chart(df, x, y):
    fig = px.scatter(df, x=x, y=y, title="Effect Scatter", size=df[y], color=df[x])
    return fig

def create_calendar_heatmap(df, date_col, value_col):
    fig = px.density_heatmap(df, x=date_col, y=value_col, title="Calendar Heatmap")
    return fig

def create_datazoom_chart(df, x, y):
    fig = px.bar(df, x=x, y=y, title="Data Zoom Chart")
    fig.update_layout(xaxis_rangeslider_visible=True)
    return fig
    
def render_pie_chart_bokeh(df, values_col, names_col):
    try:
        if df.empty:
            st.error("❌ Errore: Il DataFrame è vuoto. Impossibile generare il grafico.")
            return None  # Evita crash

        if values_col not in df.columns or names_col not in df.columns:
            st.error(f"❌ Errore: Le colonne '{values_col}' e '{names_col}' non esistono nel DataFrame.")
            return None  

        df = df[[names_col, values_col]].copy()
        df.dropna(inplace=True)  # Rimuove valori NaN
        df = df[df[values_col] > 0]  # Evita problemi con valori negativi o nulli

        if df.empty:
            st.error("❌ Errore: Tutti i valori validi sono stati filtrati. Controlla i dati.")
            return None  

        df['angle'] = df[values_col] / df[values_col].sum() * 2 * pi

        # 🔹 Assicura che ci siano abbastanza colori
        colors = list(cycle(Category20c[20]))  # Se il dataset è più grande di 20, ripete i colori
        df['color'] = colors[:len(df)]  

        source = ColumnDataSource(df)

        fig = figure(plot_height=500, title="Pie Chart con Bokeh", toolbar_location=None,
                     tools="hover", tooltips=f"@{names_col}: @{values_col}", x_range=(-1, 1))

        fig.wedge(x=0, y=0, radius=0.8,
                  start_angle=cumsum('angle', include_zero=True), 
                  end_angle=cumsum('angle'),
                  line_color="white", fill_color='color', source=source)

        fig.axis.axis_label = None
        fig.axis.visible = False
        fig.grid.grid_line_color = None

        st.bokeh_chart(fig, use_container_width=True)
        return fig  # Restituisce il grafico in caso di successo

    except Exception as e:
        st.error("❌ Errore: Non è stato possibile generare il grafico.")
        st.write("🔍 Dettagli dell'errore (per debugging):", str(e))  # Opzionale
        return None  # Evita crash
# Funzione per creare e visualizzare i grafici
def create_and_render_plot(df, x_axis, y_axis, plot_type):
    if plot_type == "Basic Bar":
        chart = create_basic_bar_chart(df, x_axis, y_axis)
    elif plot_type == "Basic Line":
        chart = create_basic_line_chart(df, x_axis, y_axis)
    elif plot_type == "Basic Scatter":
        chart = create_basic_scatter_chart(df, x_axis, y_axis)
    elif plot_type == "Effect Scatter":
        chart = create_effect_scatter_chart(df, x_axis, y_axis)
    elif plot_type == "Calendar Heatmap":
        chart = create_calendar_heatmap(df, x_axis, y_axis)
    elif plot_type == "DataZoom":
        chart = create_datazoom_chart(df, x_axis, y_axis)
    elif plot_type == "Mixed Line and Bar":
        y_axis_line = st.selectbox("Select Line Y axis", df.columns.tolist(), key=f"y_axis_line_{x_axis}")
        y_axis_bar = st.selectbox("Select Bar Y axis", df.columns.tolist(), key=f"y_axis_bar_{x_axis}")
        chart = create_mixed_line_and_bar_chart(df, x_axis, y_axis_line, y_axis_bar)
    elif plot_type == "Pie Chart (Bokeh)":
        render_pie_chart_bokeh(df, y_axis, x_axis)
    #return chart
    #st.plotly_chart(chart, use_container_width=True)
    #st.stop

