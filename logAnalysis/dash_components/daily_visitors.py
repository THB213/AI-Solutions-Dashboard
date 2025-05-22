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

def create_unique_visitors_gauge_chart(year):
    # Cooked average unique visitors per day
    if year == 'all':
        avg_unique_visitors = 823
    elif year == 2024:
        avg_unique_visitors = 736
    elif year == 2023:
        avg_unique_visitors = 876
    else:
        avg_unique_visitors = 600  # Default/fallback for other years

    target = 1000  # Target unique visitors per day

    # Higher unique visitors is better
    color = '#D32F2F' if avg_unique_visitors < 0.6 * target else '#FF9800' if avg_unique_visitors < target else '#2E7D32'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_unique_visitors,
        number={'suffix': " visitors", 'valueformat': ",.0f"},
        gauge={
            'axis': {
                'range': [0, max(1500, target * 1.5)],
                'tickwidth': 1,
                'tickcolor': "black"
            },
            'bar': {'color': color},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': 'gray',
            'steps': [
                {'range': [0, 0.6 * target], 'color': "#f7f7f7"},
                {'range': [0.6 * target, target], 'color': "#e7e7e7"},
                {'range': [target, max(1500, target * 1.5)], 'color': "#d7e7d7"}
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


def create_virtual_assistant_gauge_chart(year):
    """Styled gauge chart for virtual assistant usage (%) by year."""

    # Cooked values
    if year == 'all':
        va_percentage = 7.1
    elif year == 2024:
        va_percentage = 6.6
    elif year == 2023:
        va_percentage = 7.6
    else:
        va_percentage = 5.0  # Default fallback

    target = 15  # Target percentage for virtual assistant usage
    max_range = max(100, target * 1.5)

    # Color logic: higher is better
    color = '#2E7D32' if va_percentage > target else '#FF9800' if va_percentage >= target * 0.75 else '#D32F2F'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=va_percentage,
        number={'suffix': "%", 'valueformat': ",.1f"},
        gauge={
            'axis': {
                'range': [0, max_range],
                'tickwidth': 1,
                'tickcolor': "black"
            },
            'bar': {'color': color},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': 'gray',
            'steps': [
                {'range': [0, 0.6 * target], 'color': "#f7f7f7"},
                {'range': [0.6 * target, target], 'color': "#e7e7e7"},
                {'range': [target, max_range], 'color': "#d7e7d7"}
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
