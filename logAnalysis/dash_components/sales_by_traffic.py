import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from django.db.models import Count
from ..models import ServerLog  # Relative import

def create_sales_by_traffic_app():
    """Creates a pie chart showing sales distribution by traffic source"""
    app = DjangoDash(
        'SalesByTrafficChart',
        external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"],
        suppress_callback_exceptions=True
    )

    def get_sales_by_referrer():
        """Fetches sales data grouped by categorized referrers"""
        sales_data = (
            ServerLog.objects
            .filter(request_method="POST")  # Only purchase events
            .values('referrer')
            .annotate(count=Count('id'), total=Count('id'))
            .order_by('-count')
        )
        return pd.DataFrame(list(sales_data))

    def categorize_referrer(url):
        """Enhanced referrer categorization including direct/other"""
        if not url or str(url).strip() == "-":
            return "Direct"
        url = str(url).lower()
        if 'google.com' in url:
            return 'Google'
        elif 'linkedin.com' in url:
            return 'LinkedIn'
        elif 'twitter.com' in url:
            return 'Twitter'
        elif 'facebook.com' in url:
            return 'Facebook'
        elif any(domain in url for domain in ['bing.com', 'yahoo.com']):
            return 'Other Search'
        return 'Other Referral'

    def create_sales_pie_chart():
        """Creates the sales distribution pie chart"""
        sales_df = get_sales_by_referrer()
        
        if sales_df.empty:
            return px.pie(title="No sales data available")
            
        # Categorize and aggregate
        sales_df['source'] = sales_df['referrer'].apply(categorize_referrer)
        grouped_df = sales_df.groupby('source')['total'].sum().reset_index()
        grouped_df = grouped_df.sort_values('total', ascending=False)

        # Color mapping for all possible categories
        color_map = {
            'Google': '#4285F4',
            'LinkedIn': '#0077B5',
            'Twitter': '#1DA1F2',
            'Facebook': '#1877F2',
            'Direct': '#5C6BC0',
            'Other Search': '#34A853',
            'Other Referral': '#EA4335'
        }

        # Create pie chart
        fig = px.pie(
            grouped_df,
            names='source',
            values='total',
            color='source',
            color_discrete_map=color_map,
            hole=0.4,
            category_orders={'source': grouped_df['source'].tolist()}
        )

        # Customize appearance
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#ffffff', width=1)),
            textfont_size=11,
            insidetextorientation='radial',
            pull=[0.05 if i == 0 else 0 for i in range(len(grouped_df))]  # Slight pull on largest segment
        )

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            showlegend=False,
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig

    # App layout with descriptive titles
    app.layout = html.Div([
        html.Div(
            "Sales by Traffic Source",
            style={
                'textAlign': 'center',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'color': '#333',
                'marginBottom': '10px'
            }
        ),
        dcc.Graph(
            id='sales-pie-chart',
            figure=create_sales_pie_chart(),
            config={'displayModeBar': False},
            style={
                'height': '220px',
                'width': '100%',
                'margin': '0 auto'
            }
        ),
        html.Div(
            "Breakdown of purchases by originating source",
            style={
                'textAlign': 'center',
                'fontSize': '12px',
                'color': '#666',
                'marginTop': '10px'
            }
        )
    ], style={
        'backgroundColor': 'white',
        'padding': '15px',
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    })

    return app