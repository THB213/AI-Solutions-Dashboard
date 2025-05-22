import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from django.db.models import Count
from django.db.models.functions import ExtractHour
from ..models import ServerLog  # Relative import

def create_peak_hours_app():
    """Creates and returns the configured peak hours histogram Dash application"""
    
    # Initialize the app
    app = DjangoDash(
        'TrafficHistogram',
        external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"],
        suppress_callback_exceptions=True
    )

    def get_hourly_traffic_data():
        """Fetches and processes hourly traffic data"""
        hourly_traffic = (
            ServerLog.objects
            .annotate(hour=ExtractHour('timestamp'))
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('hour')
        )
        df = pd.DataFrame(list(hourly_traffic))
        if not df.empty:
            df['time_of_day'] = df['hour'].apply(lambda x: f"{x}:00")
        return df

    def create_histogram():
        """Creates the hourly traffic histogram figure"""
        hourly_df = get_hourly_traffic_data()
        
        if hourly_df.empty:
            return px.bar(title="No traffic data available")
            
        fig = px.bar(
            hourly_df,
            x='time_of_day',
            y='count',
            title='Peak Traffic Hours',
            labels={'time_of_day': 'Hour of Day', 'count': 'Visits'},
            color='count',
            color_continuous_scale=['#e6f2ff', '#99ccff', '#4da6ff', '#0066cc', '#004080'],
            text='count',
            range_color=[0, hourly_df['count'].max()]  # Ensure consistent color scaling
        )

        # Customize the appearance
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis={'categoryorder': 'array', 'categoryarray': [f"{h}:00" for h in range(24)]},
            margin={"r": 5, "t": 40, "l": 5, "b": 5},
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="Hour of Day",
            yaxis_title="Number of Visits"
        )

        # Style the bars
        fig.update_traces(
            marker_line_width=0.5,
            marker_line_color='rgba(0,0,0,0.3)',
            texttemplate='%{y:,}',
            textposition='outside',
            textfont_size=8,
            opacity=0.9,
            textfont_color='#333333'
        )

        # Customize axes
        fig.update_xaxes(
            tickangle=0,
            tickfont=dict(size=8, color='#333333'),
            title_font=dict(size=10, color='#333333'),
            linecolor='#e6e6e6',
            mirror=True
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor='#e6e6e6',
            tickfont=dict(size=8, color='#333333'),
            title_font=dict(size=10, color='#333333'),
            linecolor='#e6e6e6',
            mirror=True
        )
        
        return fig

    # Set the app layout
    app.layout = html.Div([
        dcc.Graph(
            id='traffic-histogram',
            figure=create_histogram(),
            config={'displayModeBar': False},
            style={
                'height': '250px',
                'width': '100%',
                'margin': '0 auto'
            }
        )
    ], style={'backgroundColor': 'transparent'})

    return app