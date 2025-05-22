import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from dash.dependencies import Input, Output
from ..models import ServerLog  # Relative import

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
    "168.": "BW",
    "102.": "ZA",
    "154.": "Na",
    "197.": "ZW"
}

def create_sales_trend_app():
    """Creates and returns the configured sales trend Dash application"""
    
    # Initialize the app
    app = DjangoDash(
        'SalesTrend',
        suppress_callback_exceptions=True,
        external_scripts=["https://cdn.plot.ly/plotly-latest.min.js"]
    )

    def extract_sales_data():
        """Extracts and transforms sales data from server logs"""
        logs = ServerLog.objects.filter(request_method="POST")
        
        sales_data = []
        for log in logs:
            # Extract product name from URL
            product = None
            if log.url.startswith("/solutions/"):
                parts = log.url.split("/")
                if len(parts) > 2:
                    product = parts[2]
                    if product not in PRODUCT_PRICES:
                        continue
            
            # Extract country from IP
            country = None
            ip_str = str(log.ip_address).strip() if log.ip_address else ""
            for prefix, country_name in COUNTRY_PREFIXES.items():
                if ip_str.startswith(prefix):
                    country = country_name
                    break
            
            if product and country:
                sales_data.append({
                    "product": product,
                    "timestamp": log.timestamp,
                    "date": log.timestamp.date(),
                    "week": log.timestamp.date().isocalendar()[1],
                    "year": log.timestamp.date().year,
                    "country": country,
                    "referrer": log.referrer,
                    "amount": PRODUCT_PRICES[product]
                })
        
        return pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=["date", "week", "amount"])

    def create_trend_chart(df):
        """Creates the sales trend line chart"""
        if df.empty:
            return px.line(title="No sales data available")
            
        # Group by year and week
        df['year_week'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
        weekly_df = df.groupby(['year', 'week', 'year_week'], as_index=False)['amount'].sum()
        
        # Sort by year and week
        weekly_df = weekly_df.sort_values(['year', 'week'])
        
        fig = px.line(
            weekly_df,
            x='year_week',
            y='amount',
            markers=True
        ).update_layout(
            plot_bgcolor='white',
            xaxis=dict(showline=True, linecolor='black', title='Week'),
            yaxis=dict(showline=True, linecolor='black', gridcolor='lightgrey', title='Sales'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        # Add light blue fill under the line
        fig.update_traces(
            fill='tozeroy',
            line_color='blue',
            fillcolor='rgba(173, 216, 230, 0.4)'
        )
        
        fig.update_yaxes(tickprefix='$', tickformat=',.0f')
        
        return fig

    # Set the app layout
    app.layout = html.Div([
        dcc.Interval(
            id='startup-trigger',
            interval=100,
            n_intervals=0,
            max_intervals=1
        ),
        dcc.Graph(
            id='sales-trend-chart',
            style={'height': '200px', 'width': '600px', "color": "black"}
        ),
        dcc.Store(id='sales-data-store')
    ])

    # Callback to extract and store sales data
    @app.callback(
        Output('sales-data-store', 'data'),
        Input('startup-trigger', 'n_intervals')
    )
    def process_data(_):
        try:
            df = extract_sales_data()
            return df.to_dict('records')
        except Exception as e:
            print(f"Error processing data: {e}")
            return []

    # Callback to update chart with weekly data
    @app.callback(
        Output('sales-trend-chart', 'figure'),
        Input('sales-data-store', 'data')
    )
    def update_chart(stored_data):
        if not stored_data:
            return px.line(title="No data available")
        
        df = pd.DataFrame(stored_data)
        return create_trend_chart(df)
    
    return app