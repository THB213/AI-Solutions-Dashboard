import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from dash.dependencies import Input, Output
from ..models import ServerLog  # Relative import
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from dash import html, dcc, Input, Output
from datetime import datetime
from ..models import ServerLog
from django.db.models.functions import ExtractYear, ExtractHour
from django.db.models import Count, Avg

def filter_by_year(queryset, year):
    if year and year != 'all':
        return queryset.filter(timestamp__year=int(year))
    return queryset

def create_bounce_rate_gauge_chart(year):
    logs = filter_by_year(ServerLog.objects.filter(request_method="POST"), year)

    ip_data = []
    for log in logs:
        if log.ip_address:
            ip_data.append(log.ip_address)

    df = pd.DataFrame(ip_data, columns=["ip_address"]) if ip_data else pd.DataFrame(columns=["ip_address"])

    if df.empty:
        bounce_rate = 0
    else:
        ip_counts = df['ip_address'].value_counts()
        bounces = (ip_counts == 1).sum()
        total_ips = ip_counts.shape[0]
        bounce_rate = (bounces / total_ips) * 100 if total_ips > 0 else 0

    target = 40  # Target bounce rate (%)

    # Lower bounce rate is better
    color = '#D32F2F' if bounce_rate < target else '#FF9800' if bounce_rate <= target * 1.25 else '#2E7D32'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bounce_rate - 60,
        number={'suffix': "%", 'valueformat': ",.1f"},
        #title={"text": f"Bounce Rate ({year})"},
        gauge={
            'axis': {
                'range': [0, max(100, target * 1.5)],
                'tickwidth': 1,
                'tickcolor': "black"
            },
            'bar': {'color': color},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': 'gray',
            'steps': [
                {'range': [0, 0.6 * target], 'color': "#d7e7d7"},
                {'range': [0.6 * target, target], 'color': "#e7e7e7"},
                {'range': [target, max(100, target * 1.5)], 'color': "#f7f7f7"}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'value': target
            }
        }
    ))

    fig.update_layout(
        margin={'l': 10, 'r': 10, 't': 30, 'b': 10},
        height=100,
        font={'size': 12}
    )

    return fig
