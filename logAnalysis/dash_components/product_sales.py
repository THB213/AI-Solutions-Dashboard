import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc, callback, Input, Output, clientside_callback
from django.db.models import Count
from django.db.models.functions import ExtractYear
from ..models import ServerLog

def create_product_analytics_app():
    """Creates and returns the configured product analytics Dash application"""
    # Initialize the app
    app = DjangoDash('ProductAnalyticsChart', external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

    def get_product_data(selected_year=None):
        """Fetches and processes product view and purchase data, filtered by year if provided"""
        # Base query
        queryset = ServerLog.objects.all()

        # Filter by year if specified
        if selected_year and selected_year != 'all':
            queryset = queryset.filter(timestamp__year=int(selected_year))

        # Get product views (GET requests to /solutions/ URLs)
        product_views = (
            queryset
            .filter(url__startswith="/solutions/", request_method="GET")
            .values('url')
            .annotate(view_count=Count('url')))
        
        # Get purchases (POST requests)
        purchases = (
            queryset
            .filter(request_method="POST")
            .values('url')
            .annotate(purchase_count=Count('url')))
        
        # Convert to DataFrames
        views_df = pd.DataFrame(list(product_views))
        purchases_df = pd.DataFrame(list(purchases))
        
        if views_df.empty and purchases_df.empty:
            return pd.DataFrame()

        # Extract product names from URLs
        def extract_product_name(url):
            parts = str(url).split("/")
            return parts[2] if len(parts) > 2 else "Unknown"
        
        views_df['product'] = views_df['url'].apply(extract_product_name) if not views_df.empty else []
        purchases_df['product'] = purchases_df['url'].apply(extract_product_name) if not purchases_df.empty else []
        
        # Merge views and purchases
        merged_df = pd.merge(
            views_df.groupby('product')['view_count'].sum().reset_index() if not views_df.empty else pd.DataFrame({'product': [], 'view_count': []}),
            purchases_df.groupby('product')['purchase_count'].sum().reset_index() if not purchases_df.empty else pd.DataFrame({'product': [], 'purchase_count': []}),
            on='product',
            how='outer'
        ).fillna(0)
        
        return merged_df.sort_values('view_count', ascending=False).head(10)

    def create_stacked_chart(selected_year=None):
        """Creates the stacked column chart figure"""
        product_df = get_product_data(selected_year)
        
        if product_df.empty:
            return px.bar(title="No product data available")
        
        # Create stacked column chart
        fig = px.bar(
            product_df,
            x='product',
            y=['view_count', 'purchase_count'],
            title="Product Views vs Purchases",
            labels={'product': '', 'value': '', 'variable': 'Metric'},
            color_discrete_map={
                'view_count': '#1f77b4',  # Blue for views
                'purchase_count': '#2ca02c'  # Green for purchases
            }
        )
        
        # Customize layout for stacked columns
        fig.update_layout(
            barmode='stack',
            plot_bgcolor='white',
            hovermode='x',
            margin={"r": 30, "t": 60, "l": 30, "b": 60},
            font=dict(size=10),
            legend=dict(font=dict(size=9), title_font=dict(size=12)),
            title_font=dict(size=12)
        )
        
        # Style axes
        fig.update_xaxes(
            tickangle=45,
            title=None,
            tickfont=dict(size=9)
        )
        fig.update_yaxes(
            title=None,
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(size=8)
        )
        
        return fig

    # Set the app layout
    app.layout = html.Div([
        dcc.Store(id='year-store', data='all'),  # Store to hold selected year
        dcc.Input(id='hidden-year-input', type='hidden', value='all'),  # Hidden input for triggering
        dcc.Graph(
            id='product-analytics-chart',
            figure=create_stacked_chart(),
            config={'displayModeBar': False},
            style={'height': '250px', 'width': '100%'}
        )
    ], style={'padding': '0px'})

    # Callback to update chart based on stored year
    @callback(
        Output('product-analytics-chart', 'figure'),
        Input('year-store', 'data')
    )
    def update_chart(selected_year):
        print(f"Updating chart with year: {selected_year}")  # Debug
        return create_stacked_chart(selected_year)

    # Clientside callback to update store when year changes
    app.clientside_callback(
        """
        function(hiddenYear) {
            console.log('Client-side callback triggered with year:', hiddenYear);
            return hiddenYear || 'all';
        }
        """,
        Output('year-store', 'data'),
        Input('hidden-year-input', 'value')
    )

    return app