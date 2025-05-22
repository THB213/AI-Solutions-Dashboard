import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from django.db.models import Count
from ..models import ServerLog  # Relative import

def create_referrer_pie_app():
    """Creates and returns the configured referrer pie chart Dash application"""
    
    # Initialize the app
    app = DjangoDash(
        'ReferrerPieChart',
        external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"],
        suppress_callback_exceptions=True
    )

    def get_referrer_data():
        """Fetches and processes referrer data"""
        referrer_distribution = (
            ServerLog.objects
            .values('referrer')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return pd.DataFrame(list(referrer_distribution))

    def categorize_referrer(url):
        """Categorizes referrers into specific social platforms"""
        if not url or str(url).strip() == "-":
            return None
        url = str(url).lower()
        if 'google.com' in url:
            return 'Google'
        elif 'linkedin.com' in url:
            return 'LinkedIn'
        elif 'twitter.com' in url:
            return 'Twitter'
        return None

    def create_pie_chart():
        """Creates the referrer pie chart figure"""
        referrer_df = get_referrer_data()
        
        if referrer_df.empty:
            return px.pie(title="No referrer data available")
            
        referrer_df['category'] = referrer_df['referrer'].apply(categorize_referrer)
        filtered_df = referrer_df.dropna(subset=['category'])
        grouped_df = filtered_df.groupby('category')['count'].sum().reset_index()

        # Create pie chart with only the three categories
        fig = px.pie(
            grouped_df,
            names='category',
            values='count',
            title=None,
            color='category',
            color_discrete_map={
                'Google': '#4285F4',
                'LinkedIn': '#0077B5',
                'Twitter': '#1DA1F2'
            },
            hole=0.3
        )

        # Customize appearance
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#ffffff', width=1)),
            textfont_size=12,
            insidetextorientation='radial',
            pull=[0.05, 0, 0]
        )

        fig.update_layout(
            margin={"r": 0, "t": 30, "l": 0, "b": 0},  # Added top margin for title
            showlegend=False,
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig

    # Set the app layout with the new title
    app.layout = html.Div([
        html.Div(
            "Sources of Traffic",
            style={
                'textAlign': 'center',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'color': '#333',
                'marginBottom': '10px'
            }
        ),
        dcc.Graph(
            id='referrer-pie-chart',
            figure=create_pie_chart(),
            config={'displayModeBar': False},
            style={
                'height': '190px',
                'width': '100%',
                'margin': '0 auto'
            }
        ),
        html.Div(
            "Traffic from Google, LinkedIn, and Twitter",
            style={
                'textAlign': 'center',
                'fontSize': '12px',
                'color': '#666',
                'marginTop': '20px'
            }
        )
    ], style={'backgroundColor': 'white', 'padding': '10px'})

    return app