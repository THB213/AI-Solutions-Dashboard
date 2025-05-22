import pandas as pd
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash
from django.db.models import Count
from django.db import models

from logAnalysis.models import ServerLog  # Adjust this if your model path is different

# ---------- Line Chart Dash App ----------
app = DjangoDash('LineChartDash', external_scripts=['https://cdn.plot.ly/plotly-basic-2.18.2.min.js'])

app.layout = html.Div([
    dcc.Graph(id='line-chart', style={'height': '200px', 'width': '300px', "color": "black"})
])

def get_log_data():
    logs = (
        ServerLog.objects
        .annotate(day=models.functions.TruncDay('timestamp'))
        .values('day')
        .annotate(total_logs=Count('id'))
        .order_by('day')
    )

    df = pd.DataFrame.from_records(logs)
    if not df.empty:
        df['day'] = pd.to_datetime(df['day']).dt.date
    return df

@app.callback(
    Output('line-chart', 'figure'),
    [Input('line-chart', 'id')]
)
def update_chart(_):
    df = get_log_data()

    if df.empty:
        fig = px.line(title=None)
    else:
        fig = px.line(df, x="day", y="total_logs", markers=False)

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            title=None,
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(
            showgrid=False,
            title=None,
            showline=True,
            linecolor='black'
        ),
        hovermode=False
    )

    fig.update_traces(
        hoverinfo='none',
        showlegend=False
    )

    return fig
