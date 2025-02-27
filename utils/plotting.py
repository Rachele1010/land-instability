import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Funzioni di creazione dei grafici
def create_basic_bar_chart(df, x, y):
    return px.bar(df, x=x, y=y, title="Basic Bar Chart")

def create_basic_line_chart(df, x, y):
    return px.line(df, x=x, y=y, title="Basic Line Chart")

def create_basic_scatter_chart(df, x, y):
    return px.scatter(df, x=x, y=y, title="Basic Scatter Chart")

def create_effect_scatter_chart(df, x, y):
    return px.scatter(df, x=x, y=y, title="Effect Scatter", size=df[y], color=df[x])

def create_calendar_heatmap(df, date_col, value_col):
    return px.density_heatmap(df, x=date_col, y=value_col, title="Calendar Heatmap")

def create_datazoom_chart(df, x, y):
    fig = px.bar(df, x=x, y=y, title="Data Zoom Chart")
    fig.update_layout(xaxis_rangeslider_visible=True)
    return fig

def create_mixed_line_and_bar_chart(df, x, y_line, y_bar):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[x], y=df[y_bar], name='Bar Data'))
    fig.add_trace(go.Scatter(x=df[x], y=df[y_line], name='Line Data', mode='lines'))
    fig.update_layout(title="Mixed Line and Bar Chart")
    return fig

# Funzione per creare e visualizzare i grafici con gestione errori
def create_and_render_plot(df, x_axis, y_axis, plot_type):
    chart = None  # Inizializza per evitare errori

    if df.empty:
        st.error("❌ Errore: Il dataset è vuoto. Impossibile generare il grafico.")
        return

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
    else:
        st.error("❌ Errore: Tipo di grafico non supportato.")
        return

    if chart:
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.error("❌ Errore: Impossibile generare il grafico.")

    return chart


