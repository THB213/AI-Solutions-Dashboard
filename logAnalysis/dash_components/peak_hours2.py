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

def create_peak_hours_chart(year):
    hourly_traffic = (
        filter_by_year(ServerLog.objects, year)
        .annotate(hour=ExtractHour('timestamp'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )
    df = pd.DataFrame(list(hourly_traffic))
    
    if df.empty:
        return px.bar(title="No traffic data available")
        
    df['time_of_day'] = df['hour'].apply(lambda x: f"{x}:00")
    
    fig = px.bar(
        df,
        x='time_of_day',
        y='count',
        labels={'time_of_day': 'Hour of Day', 'count': 'Visits'},
        color='count',
        color_continuous_scale=['#e6f2ff', '#99ccff', '#4da6ff', '#0066cc', '#004080'],
        text='count'
    )

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis={
            'categoryorder': 'array',
            'categoryarray': [f"{h}:00" for h in range(24)],
            'tickfont': dict(size=10),
            'title_font': dict(size=12)
        },
        yaxis={
            'gridcolor': 'rgba(0,0,0,0.05)',
            'tickfont': dict(size=10),
            'title_font': dict(size=12)
        },
        margin={"r": 10, "t": 10, "l": 10, "b": 30},
        showlegend=False,
        coloraxis_showscale=False
    )

    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color='rgba(0,0,0,0.1)',
        texttemplate='%{y:,}',
        textposition='outside',
        textfont_size=10,
        opacity=0.9
    )
    
    return fig

