import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.transform import cumsum
from bokeh.palettes import Category20c
from math import pi
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
    st.write("🔍 Debug: Dati in ingresso per il Pie Chart (Bokeh)")
    st.write(df[[names_col, values_col]].head())  # Controllo dati

    df = df[[names_col, values_col]].copy()  
    df['angle'] = df[values_col] / df[values_col].sum() * 2 * pi  # Converti in angoli
    df['color'] = Category20c[min(len(df), 20)]  # Prendi massimo 20 colori

    source = ColumnDataSource(df)

    fig = figure(plot_height=500, title="Pie Chart con Bokeh", toolbar_location=None,
                 tools="hover", tooltips=f"@{names_col}: @{values_col}", x_range=(-1, 1))

    fig.wedge(x=0, y=0, radius=0.8,
              start_angle=cumsum('angle', include_zero=True), 
              end_angle=cumsum('angle'),
              line_color="white", fill_color='color', source=source)

    fig.axis.axis_label = None
    fig.axis.visible = False
    fig.grid.grid_line_color = None  # ✅ CORRETTO!

    st.bokeh_chart(fig, use_container_width=True)
    return fig


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

