import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from django.db.models import Count
from ..models import ServerLog  # Relative import

def create_top_pages_app():
    """Creates and returns the configured top pages Dash application"""
    
    # Initialize the app
    app = DjangoDash('TopPagesChart', external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

    def get_top_pages_data():
        """Fetches and processes top pages data"""
        # Get top 5 visited pages (sorted in descending order)
        top_pages = (
            ServerLog.objects
            .values('url')
            .annotate(visit_count=Count('url'))
            .order_by('-visit_count')[:5]
        )
        return pd.DataFrame(list(top_pages))

    def clean_url(url):
        """Shortens long URLs for better visualization"""
        url = str(url).split('?')[0]  # Remove query parameters
        if len(url) > 40:
            return f"{url[:20]}...{url[-15:]}"
        return url

    def create_bar_chart():
        """Creates the horizontal bar chart figure"""
        top_pages_df = get_top_pages_data()
        
        # Skip processing if no data
        if top_pages_df.empty:
            return px.bar(title="No page visit data available")
            
        top_pages_df['display_url'] = top_pages_df['url'].apply(clean_url)

        # Create horizontal bar chart
        fig = px.bar(
            top_pages_df,
            y='display_url',
            x='visit_count',
            orientation='h',
            title=None,  # Remove title for cleaner look
            labels={'display_url': '', 'visit_count': 'Number of Visits'},
            color_discrete_sequence=['#1f77b4']
        )

        # Customize the layout
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Number of Visits",
            showlegend=False,
            plot_bgcolor='white',
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            hovermode='y'
        )

        # Style axes
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False, tickfont=dict(size=12))

        # Style bars
        fig.update_traces(
            texttemplate='%{x:,}',
            textposition='outside',
            textfont_size=8,
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5
        )
        
        return fig

    # Set the app layout
    app.layout = html.Div([
        dcc.Graph(
            id='top-pages-chart',
            figure=create_bar_chart(),
            style={'height': '200px', 'width': '600px'}
        )
    ], style={'backgroundColor': '#f8f9fa'})

    return app