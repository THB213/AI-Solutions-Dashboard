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

def create_profit_gauge_chart(year):
    PRODUCT_PRICES = {
        "smart-assist": 2000,
        "proto-genius": 5000,
        "flow-optimizer": 15000,
        "team-connect": 1200,
        "insight-dashboard": 8000,
        "virtual-designer": 20000,
        "rapid-launch": 12000,
        "ai-inspector": 30000
    }

    logs = filter_by_year(ServerLog.objects.filter(request_method="POST"), year)

    sales_data = []
    for log in logs:
        if log.url.startswith("/solutions/"):
            parts = log.url.split("/")
            if len(parts) > 2:
                product = parts[2]
                if product in PRODUCT_PRICES:
                    sales_data.append({
                        "product": product,
                        "timestamp": log.timestamp,
                        "amount": PRODUCT_PRICES[product]
                    })

    df = pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=["amount", "timestamp"])

    if df.empty:
        avg_profit = 0
    else:
        if year == 'all':
            df['year'] = df['timestamp'].dt.year
            avg_profit = df.groupby('year')['amount'].sum().mean()
        else:
            avg_profit = df['amount'].sum()

    # Target and styling
    target = 15_000_000
    color = '#2E7D32' if avg_profit >= target else '#FF9800' if avg_profit >= 0.6 * target else '#D32F2F'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_profit,
        number={'prefix': "$", 'valueformat': ",.0f"},
        #title={"text": f"{'Average Yearly' if year == 'all' else 'Total'} Profit ({year.title() if year != 'all' else 'All Years'})"},
        gauge={
            'axis': {'range': [0, target * 1.5], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 0.6 * target], 'color': "#f7f7f7"},
                {'range': [0.6 * target, target], 'color': "#e7e7e7"},
                {'range': [target, target * 1.5], 'color': "#d7e7d7"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'value': target
            }
        }
    ))

    fig.update_layout(
        height=100,
        margin=dict(l=10, r=10, t=30, b=10),
        font={'size': 12}
    )

    return fig

