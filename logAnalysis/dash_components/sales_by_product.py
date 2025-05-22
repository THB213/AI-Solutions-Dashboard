import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc, Input, Output
from ..models import ServerLog

# Configuration constants
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

COUNTRY_PREFIXES = {
    "168.": "Botswana",
    "102.": "South Africa",
    "154.": "Namibia",
    "197.": "Zimbabwe"
}

def create_country_dropdown():
    """Creates a standalone country dropdown component"""
    country_options = [{'label': 'All Countries', 'value': 'All'}] + [
        {'label': country, 'value': country}
        for country in sorted(COUNTRY_PREFIXES.values())
    ]
    
    return dcc.Dropdown(
        id='country-filter',
        options=country_options,
        value='All',
        clearable=False,
        style={'width': '200px', 'marginBottom': '10px'}
    )

def create_sales_by_product_app():
    """Creates a sales by product bar chart without dropdown filter"""
    app = DjangoDash('SalesByProduct', external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

    def extract_sales_data():
        """Extracts all sales data (no country filtering)"""
        logs = ServerLog.objects.filter(request_method="POST")
        
        sales_data = []
        for log in logs:
            # Extract product
            product = None
            if log.url.startswith("/solutions/"):
                parts = log.url.split("/")
                if len(parts) > 2:
                    product = parts[2]
                    if product not in PRODUCT_PRICES:
                        continue
            
            if product:
                sales_data.append({
                    "product": product,
                    "amount": PRODUCT_PRICES[product]
                })
        
        return pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=["product", "amount"])

    def create_bar_chart():
        """Creates the sales by product bar chart"""
        sales_df = extract_sales_data()
        
        if sales_df.empty:
            return px.bar(title="No sales data available")
            
        # Aggregate by product
        product_sales = sales_df.groupby('product', as_index=False)['amount'].sum()
        product_sales = product_sales.sort_values('amount', ascending=False)
        
        fig = px.bar(
            product_sales,
            x='product',
            y='amount',
            text='amount',
            title="Product Sales Revenue",  # Added title here
            labels={'product': '', 'amount': 'Revenue ($)'},
            color_discrete_sequence=['#1f77b4']  # Single blue color for all bars
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            margin={"r": 5, "t": 40, "l": 5, "b": 5},  # Increased top margin for title
            xaxis={'title': None},
            yaxis={'title': None, 'gridcolor': 'lightgray'},
            showlegend=False,
            hovermode='x',
            title_x=0.5  # Center the title
        )
        
        fig.update_traces(
            texttemplate='$%{y:,.0f}',
            textposition='outside',
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5,
            textfont_size=10
        )
        
        return fig

    # Simplified app layout without dropdown
    app.layout = html.Div([
        dcc.Graph(
            id='sales-by-product-chart',
            figure=create_bar_chart(),  # Generate initial figure
            style={'height': '270px', 'width': '100%'}
        )
    ])
    
    return app