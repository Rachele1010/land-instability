import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_echarts import st_echarts
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
    
def create_pie_chart(df, values_col, names_col):
    fig = px.pie(df, values=values_col, names=names_col, title="Pie Chart")
    return fig
# Funzione per rendere il grafico a torta con eCharts

def render_pie_chart(df, values_col, names_col):
    data = df[[values_col, names_col]].to_dict(orient='records')
    options = {
        "title": {"text": "Dati Personalizzati", "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "vertical", "left": "left"},
        "series": [{
            "name": "Dati",
            "type": "pie",
            "radius": "50%",
            "data": data,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }]
    }
    st_echarts(options=options, height="500px")

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
    elif plot_type == "Pie":
        chart = create_pie_chart(df, x_axis, y_axis)
    elif plot_type == "Pie Chart (eCharts)":
        chart =  render_pie_chart(df, y_axis, x_axis)
        return chart
    st.plotly_chart(chart, use_container_width=True)
    st.stop
