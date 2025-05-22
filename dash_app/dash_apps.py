import dash
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from django.db.models import Count
from django.utils.timezone import localtime
from logAnalysis.models import ServerLog  # Replace 'myapp' with your actual app name
from django.db import models

# Create Dash app
app = DjangoDash('SimpleDash', external_scripts=['https://cdn.plot.ly/plotly-basic-2.18.2.min.js'])

app.layout = html.Div([
    dcc.Graph(id='line-chart', style={'height': '600px', 'width': '100%'})  # Increase graph size
])

def get_log_data():
    """Fetch logs grouped by day and return a DataFrame."""
    logs = (
        ServerLog.objects
        .annotate(day=models.functions.TruncDay('timestamp'))  # Extract date from timestamp
        .values('day')
        .annotate(total_logs=Count('id'))  # Count logs per day
        .order_by('day')  # Order by date
    )

    # Convert QuerySet to Pandas DataFrame
    df = pd.DataFrame.from_records(logs)

    if not df.empty:
        df['day'] = pd.to_datetime(df['day']).dt.date  # Convert to date format

    return df

@app.callback(
    Output('line-chart', 'figure'),
    [Input('line-chart', 'id')]  # Dummy Input just to trigger callback
)
def update_chart(_):
    df = get_log_data()  # Get logs from database
    
    if df.empty:
        fig = px.line(title="No Data Available")
    else:
        fig = px.line(df, x="day", y="total_logs", markers=True, title="Server Logs Per Day")

    # Explicitly set figure size
    fig.update_layout(
        height=600,
        width=1000,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig



