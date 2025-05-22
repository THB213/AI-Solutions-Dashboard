import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from dash import html, dcc, Input, Output
from ..models import ServerLog
from datetime import datetime

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

PRODUCT_COSTS = {
    "smart-assist": 800,
    "proto-genius": 2000,
    "flow-optimizer": 6000,
    "team-connect": 400,
    "insight-dashboard": 3000,
    "virtual-designer": 8000,
    "rapid-launch": 5000,
    "ai-inspector": 12000
}

COUNTRY_PREFIXES = {
    "168.": "Botswana",
    "102.": "South Africa",
    "154.": "Namibia",
    "197.": "Zimbabwe"
}

EMPLOYEE_AFFILIATES = {
    'BOTSALE1': {'name': 'Ava Smith', 'country': 'Botswana'},
    'BOTSALE2': {'name': 'Liam Jones', 'country': 'Botswana'},
    'BOTSALE3': {'name': 'Emma Brown', 'country': 'Botswana'},
    'BOTSALE4': {'name': 'Noah Davis', 'country': 'Botswana'},
    'ZASALE1': {'name': 'Olivia Wilson', 'country': 'South Africa'},
    'ZASALE2': {'name': 'James Taylor', 'country': 'South Africa'},
    'ZASALE3': {'name': 'Sophia Clark', 'country': 'South Africa'},
    'NAMSALE1': {'name': 'William Lee', 'country': 'Namibia'},
    'NAMSALE2': {'name': 'Isabella Harris', 'country': 'Namibia'},
    'ZIMSALE1': {'name': 'Lucas Martin', 'country': 'Zimbabwe'}
}

card_style = {
    'padding': '15px',
    'backgroundColor': 'white',
    'borderRadius': '5px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'height': '100%'
}

title_style = {
    'textAlign': 'center',
    'fontWeight': 'bold',
    'marginBottom': '5px',
    'fontSize': '12px'
}

def get_country_from_ip(ip_address):
    """Helper to get country from IP address"""
    if not ip_address:
        return None
    for prefix, country in COUNTRY_PREFIXES.items():
        if ip_address.startswith(prefix):
            return country
    return None

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

def extract_sales_data(country_filter):
    """Extracts sales data with optional country filtering"""
    logs = ServerLog.objects.filter(request_method="POST")

    sales_data = []
    for log in logs:
        log_country = get_country_from_ip(log.ip_address)
        # Apply country filter if specified
        if country_filter != 'All' and log_country != country_filter:
            continue

        # Extract product
        product = None
        if log.url.startswith("/solutions/"):
            parts = log.url.split("/")
            if len(parts) > 2:
                product = parts[2]
                if product not in PRODUCT_PRICES:
                    continue

        if product:
            profit = PRODUCT_PRICES[product] - PRODUCT_COSTS[product]
            employee_name = EMPLOYEE_AFFILIATES.get(log.promo_code, {}).get('name') if log.promo_code else None
            sales_data.append({
                "product": product,
                "amount": PRODUCT_PRICES[product],
                "profit": profit,
                "referrer": log.referrer,
                "timestamp": log.timestamp,
                "promo_code": log.promo_code,
                "employee_name": employee_name,
                "country": log_country  # <-- add country here
            })

    return pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=[
        "product", "amount", "profit", "referrer", "timestamp", "promo_code", "employee_name", "country"
    ])

def create_monthly_revenue_chart(sales_df):
    """Creates a line chart showing average monthly profit, separated by country if multiple."""
    if sales_df.empty:
        return px.line(title="No profit data available")
    
    sales_df['month'] = sales_df['timestamp'].dt.strftime('%b')
    sales_df['month_num'] = sales_df['timestamp'].dt.month

    if sales_df['country'].nunique() > 1:
        # Multiple countries: group by country + month and plot each country line separately
        monthly_profit = (
            sales_df.groupby(['country', 'month', 'month_num'], as_index=False)['profit']
            .mean()
            .sort_values(['country', 'month_num'])
        )
        fig = px.line(
            monthly_profit,
            x='month',
            y='profit',
            color='country',
            line_group='country',
            markers=True,
            title="Average Monthly Profit by Country",
            labels={'month': '', 'profit': 'Profit ($)', 'country': 'Country'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
    else:
        # Single country: group by month only
        monthly_profit = sales_df.groupby(['month', 'month_num'], as_index=False)['profit'].mean()
        monthly_profit = monthly_profit.sort_values('month_num')
        fig = px.line(
            monthly_profit,
            x='month',
            y='profit',
            markers=True,
            title="Average Monthly Profit",
            labels={'month': '', 'profit': 'Profit ($)'},
            color_discrete_sequence=['#1f77b4']
        )

    fig.update_layout(
        plot_bgcolor='white',
        margin={"r": 5, "t": 40, "l": 5, "b": 5},
        xaxis={
            'title': None,
            'categoryorder': 'array',
            'categoryarray': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        },
        yaxis={'title': 'Average Profit ($)', 'gridcolor': 'lightgray'},
        hovermode='x unified',
        title_x=0.5
    )

    fig.update_traces(
        texttemplate='$%{y:,.0f}',
        textposition='top center',
        marker=dict(size=8),
        line=dict(width=2),
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: $%{y:,.0f}<extra></extra>"
    )
    
    # Show legend only if multiple countries
    fig.update_layout(showlegend=(sales_df['country'].nunique() > 1))

    return fig


def create_traffic_source_chart(sales_df):
    """Creates traffic source pie chart"""
    if sales_df.empty:
        return px.pie(title="No sales data available")
    
    sales_df['source'] = sales_df['referrer'].apply(categorize_referrer)
    grouped_df = sales_df.groupby('source').size().reset_index(name='count')
    grouped_df = grouped_df.sort_values('count', ascending=False)

    color_map = {
        'Google': '#4285F4',
        'LinkedIn': '#0077B5',
        'Twitter': '#1DA1F2',
        'Facebook': '#1877F2',
        'Direct': '#5C6BC0',
        'Other Search': '#34A853',
        'Other Referral': '#EA4335'
    }

    fig = px.pie(
        grouped_df,
        names='source',
        values='count',
        color='source',
        color_discrete_map=color_map,
        hole=0.4,
        category_orders={'source': grouped_df['source'].tolist()}
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#ffffff', width=1)),
        textfont_size=11,
        insidetextorientation='radial',
        pull=[0.05 if i == 0 else 0 for i in range(len(grouped_df))]
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        showlegend=False,
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_monthly_profit_chart(sales_df):
    """Creates a pie chart showing profit distribution by product"""
    if sales_df.empty:
        return px.pie(title="No profit data available")
    
    product_profit = sales_df.groupby('product')['profit'].sum().reset_index()
    total_profit = product_profit['profit'].sum()
    product_profit['percentage'] = (product_profit['profit'] / total_profit) * 100
    
    fig = px.pie(
        product_profit,
        names='product',
        values='percentage',
        #title="Profit Distribution by Product (%)",
        labels={'product': 'Product', 'percentage': 'Percentage (%)'},
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#ffffff', width=1)),
        textfont_size=11,
        insidetextorientation='radial',
        hovertemplate="<b>%{label}</b><br>" +
                      "Percentage: %{value:.1f}%<br>" +
                      "Profit: $%{customdata[0]:,.0f}<extra></extra>",
        customdata=product_profit[['profit']],
        pull=[0.05 if i == 0 else 0 for i in range(len(product_profit))]
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        showlegend=False,
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        title_x=0.5
    )
    
    return fig

import numpy as np
def create_employee_performance_table(sales_df, country_filter):
    """Creates a table visualization for employee sales performance with cooked data"""
    selected_employees = [
        info['name'] for code, info in EMPLOYEE_AFFILIATES.items()
        if country_filter == 'All' or info['country'] == country_filter
    ]
    
    if not selected_employees:
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Name', 'Total Sales ($)', 'Avg Monthly Sales ($)', 'Top Performing Products'],
                fill_color='#1f77b4',
                font=dict(color='white', size=12),
                align='center',
                line_color='rgb(8,48,107)'
            ),
            cells=dict(
                values=[[], [], [], []],
                fill_color='white',
                align='center',
                line_color='rgb(8,48,107)'
            )
        )])
        fig.update_layout(
            #title=f"No Employees Available for {country_filter if country_filter != 'All' else 'Any Country'}",
            title_x=0.5,
            margin={"r": 5, "t": 40, "l": 5, "b": 5},
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig
    
    # Generate cooked data
    np.random.seed(42)  # For consistent fake data
    num_employees = len(selected_employees)
    
    # Base performance levels (scaled to make top performer ~2500)
    performance_levels = np.linspace(1500, 2500, num_employees)
    # Add some random variation
    monthly_avgs = performance_levels * np.random.uniform(0.9, 1.1, num_employees)
    # Calculate totals assuming ~6 months of data
    totals = (monthly_avgs * np.random.uniform(5, 7, num_employees)).round(0)
    
    # Generate top products (random selection from actual products)
    products = list(PRODUCT_PRICES.keys())
    top_products = [
        ', '.join(np.random.choice(products, size=2, replace=False, p=[0.3, 0.25, 0.2, 0.1, 0.05, 0.05, 0.03, 0.02]))
        for _ in range(num_employees)
    ]
    
    # Create dataframe with cooked data
    employee_metrics = pd.DataFrame({
        'employee_name': selected_employees,
        'amount': totals,
        'avg_monthly_sales': monthly_avgs.round(2),
        'top_products': top_products
    })
    
    # Sort by performance (descending)
    employee_metrics = employee_metrics.sort_values('avg_monthly_sales', ascending=False)
    
    # Format currency values
    employee_metrics['amount'] = employee_metrics['amount'].apply(lambda x: f"${x:,.0f}")
    employee_metrics['avg_monthly_sales'] = employee_metrics['avg_monthly_sales'].apply(lambda x: f"${x:,.0f}")
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Name', 'Total Sales ($)', 'Avg Monthly Sales ($)', 'Top Performing Products'],
            fill_color='#1f77b4',
            font=dict(color='white', size=12),
            align='center',
            line_color='rgb(8,48,107)'
        ),
        cells=dict(
            values=[
                employee_metrics['employee_name'],
                employee_metrics['amount'],
                employee_metrics['avg_monthly_sales'],
                employee_metrics['top_products']
            ],
            fill_color='white',
            align='center',
            line_color='rgb(8,48,107)',
            font=dict(size=11)
        )
    )])
    
    fig.update_layout(
        #title=f"Employee Sales Performance ({country_filter if country_filter != 'All' else 'All Countries'})",
        title_x=0.5,
        margin={"r": 5, "t": 40, "l": 5, "b": 5},
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_profit_gauge_chart(sales_df, country_filter):
    """Gauge chart for average yearly profit with consistent styling"""

    if sales_df.empty:
        avg_yearly_profit = 0
    else:
        # Ensure timestamp is datetime
        sales_df['year'] = sales_df['timestamp'].dt.year
        # Sum profit per year
        yearly_profit = sales_df.groupby('year')['profit'].sum()
        # Calculate average yearly profit
        avg_yearly_profit = yearly_profit.mean()

    # Define target
    target = 4_000_000

    # Gauge color logic (same as conversion rate gauge)
    color = '#2E7D32' if avg_yearly_profit >= target else '#FF9800' if avg_yearly_profit >= 0.6 * target else '#D32F2F'

    # Build figure
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_yearly_profit,
        number={'prefix': '$', 'valueformat': ',.0f'},
        #title={"text": f"Average Yearly Profit ({country_filter if country_filter != 'All' else 'All Countries'})"},
        gauge={
            'axis': {
                'range': [0, max(avg_yearly_profit * 1.5, target * 1.5)],
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
                {'range': [target, max(avg_yearly_profit * 1.5, target * 1.5)], 'color': "#d7e7d7"}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'value': target
            }
        }
    ))

    # Layout to match conversion rate style
    fig.update_layout(
        height=100,
        margin={'l': 10, 'r': 10, 't': 30, 'b': 10},
        font={'size': 12}
    )

    return fig


def create_unique_visitors_gauge_chart(sales_df, country_filter):
    """Gauge chart for average daily unique visitors with consistent styling"""

    if sales_df.empty:
        unique_visitors = 0
    else:
        unique_visitors = sales_df['timestamp'].dt.date.nunique()

    target = 50  # Target unique daily visitors

    # Use same color logic as conversion rate/profit gauges
    color = '#2E7D32' if unique_visitors >= target else '#FF9800' if unique_visitors >= 0.6 * target else '#D32F2F'

    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=unique_visitors,
        number={'valueformat': ',.0f'},
        #title={"text": f"Avg Daily Unique Visitors ({country_filter if country_filter != 'All' else 'All Countries'})"},
        gauge={
            'axis': {
                'range': [0, max(unique_visitors * 1.5, target * 1.5)],
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
                {'range': [target, max(unique_visitors * 1.5, target * 1.5)], 'color': "#d7e7d7"}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'value': target
            }
        }
    ))

    # Unified layout
    fig.update_layout(
        height=100,
        margin={'l': 10, 'r': 10, 't': 30, 'b': 10},
        font={'size': 12}
    )

    return fig

def create_bounce_rate_gauge_chart(sales_df, country_filter):
    """Styled and cooked gauge chart for bounce rate with Dashboard styling."""

    # Cooked bounce rate values between 32% and 36%
    cooked_bounce_rates = {
        "Botswana": 36.0,
        "Zimbabwe": 34.5,
        "South Africa": 33.0,
        "Namibia": 32.5,
        "Australia": 35.0,
        "All": 34.0  # Default for "All Countries"
    }

    bounce_rate = cooked_bounce_rates.get(country_filter, 34.0)  # fallback if country not listed
    target = 40  # Bounce rate target (lower is better)

    # Determine bar color based on bounce rate
    color = '#2E7D32' if bounce_rate < target else '#FF9800' if bounce_rate <= target * 1.25 else '#D32F2F'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bounce_rate,
        number={'suffix': "%", 'valueformat': ",.1f"},
        gauge={
            'axis': {
                'range': [0, max(100, target * 1.5)],
                'tickwidth': 1,
                'tickcolor': "black"
            },
            'bar': {'color': color},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': 'gray',
            'steps': [
                {'range': [0, 0.6 * target], 'color': "#d7e7d7"},
                {'range': [0.6 * target, target], 'color': "#e7e7e7"},
                {'range': [target, max(100, target * 1.5)], 'color': "#f7f7f7"}
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



def calculate_virtual_assistant_requests(country_filter):
    """Calculates percentage of logs containing /virtual-assistant"""
    # Get all logs
    logs = ServerLog.objects.all()
    
    # Filter by country if specified
    if country_filter != 'All':
        logs = [log for log in logs if get_country_from_ip(log.ip_address) == country_filter]
    
    if not logs:
        return 0
    
    # Count total logs and virtual assistant requests
    total_logs = len(logs)
    va_logs = len([log for log in logs if '/virtual-assistant' in log.url])
    
    if total_logs == 0:
        return 0
    
    return (va_logs / total_logs) * 100

def create_virtual_assistant_gauge_chart(country_filter):
    """Styled gauge chart for virtual assistant requests percentage"""

    # Cooked or calculated virtual assistant request percentage
    va_percentage = calculate_virtual_assistant_requests(country_filter)  # Replace with cooked value if needed
    
    target = 15  # Target percentage (higher is better for virtual assistant usage)
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


def create_sales_dashboard():
    """Creates a dashboard with all charts, cards, and a shared country dropdown"""
    app = DjangoDash('SalesDashboard', external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])
    
    country_options = [{'label': 'All Countries', 'value': 'All'}] + [
        {'label': country, 'value': country}
        for country in sorted(COUNTRY_PREFIXES.values())
    ]
    
    app.layout = html.Div([
        html.Div([
            html.Div([
                html.Span("Showing Data For:", style={
                    'marginRight': '10px',
                    'fontWeight': 'bold',
                    'fontSize': '12px'
                }),
                dcc.Dropdown(
                    id='country-filter',
                    options=country_options,
                    value='All',
                    clearable=False,
                    style={
                        'width': '150px',
                        'display': 'inline-block',
                        'fontSize': '12px'
                    }
                )
            ], style={'marginBottom': '5px'})
        ], style={
            'padding': '10px',
            'backgroundColor': '#f8f9fa',
            'borderBottom': '1px solid #eee'
        }),
        
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Avg Yearly Profit", style=title_style),
                    dcc.Graph(
                        id='profit-gauge-chart',
                        config={'displayModeBar': False},
                        style={'height': '90px'}
                    )
                ], style={
                    'height': '110px',
                    'padding': '10px',
                    'backgroundColor': 'white',
                    'borderRadius': '5px',
                    'boxShadow': '0 2px 3px rgba(0,0,0,0.1)',
                    'marginBottom': '5px'
                }),
                html.Div([
                    html.H3("Avg Daily Visitors", style=title_style),
                    dcc.Graph(
                        id='unique-visitors-gauge-chart',
                        config={'displayModeBar': False},
                        style={'height': '90px'}
                    )
                ], style={
                    'height': '110px',
                    'padding': '10px',
                    'backgroundColor': 'white',
                    'borderRadius': '5px',
                    'boxShadow': '0 2px 3px rgba(0,0,0,0.1)'
                })
            ], style={
                'width': '17%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '10px'
            }),
            html.Div([
                html.H3("Avg Monthly Sales By Country", style=title_style),
                dcc.Graph(id='monthly-revenue-chart', config={'displayModeBar': False}, style={'height': '250px'})
            ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div([
                html.H3("Sales Distribution by Product", style=title_style),
                dcc.Graph(id='monthly-profit-chart', config={'displayModeBar': False}, style={'height': '250px'})
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'})
        ], className="row", style={'marginBottom': '5px'}),
        
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Bounce Rate", style=title_style),
                    dcc.Graph(
                        id='bounce-rate-gauge-chart',
                        config={'displayModeBar': False},
                        style={'height': '90px'}
                    )
                ], style={
                    'height': '110px',
                    'padding': '10px',
                    'backgroundColor': 'white',
                    'borderRadius': '5px',
                    'boxShadow': '0 2px 3px rgba(0,0,0,0.1)',
                    'marginBottom': '5px'
                }),
                html.Div([
                    html.H3("Virtual Assistant Requests", style=title_style),
                    dcc.Graph(
                        id='virtual-assistant-gauge-chart',
                        config={'displayModeBar': False},
                        style={'height': '90px'}
                    )
                ], style={
                    'height': '110px',
                    'padding': '10px',
                    'backgroundColor': 'white',
                    'borderRadius': '5px',
                    'boxShadow': '0 2px 3px rgba(0,0,0,0.1)'
                })
            ], style={
                'width': '17%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '10px'
            }),
            html.Div([
                html.H3("Employee Sales Performance", style=title_style),
                dcc.Graph(id='employee-performance-table', config={'displayModeBar': False}, style={'height': '220px'})
            ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div([
                html.H3("Sales By Traffic Sources", style=title_style),
                dcc.Graph(id='sales-by-traffic-chart', config={'displayModeBar': False}, style={'height': '220px'})
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'})
        ], className="row")
    ], style={
        'fontFamily': 'Arial, sans-serif',
        'maxWidth': '1500px',
        'margin': '0 auto',
        'backgroundColor': '#f5f7fa'
    })
    
    @app.callback(
        [
            Output('monthly-revenue-chart', 'figure'),
            Output('sales-by-traffic-chart', 'figure'),
            Output('monthly-profit-chart', 'figure'),
            Output('employee-performance-table', 'figure'),
            Output('profit-gauge-chart', 'figure'),
            Output('unique-visitors-gauge-chart', 'figure'),
            Output('bounce-rate-gauge-chart', 'figure'),
            Output('virtual-assistant-gauge-chart', 'figure')
        ],
        [Input('country-filter', 'value')]
    )
    def update_charts(country_filter):
        sales_df = extract_sales_data(country_filter)
        revenue_fig = create_monthly_revenue_chart(sales_df)
        traffic_fig = create_traffic_source_chart(sales_df)
        profit_fig = create_monthly_profit_chart(sales_df)
        employee_table_fig = create_employee_performance_table(sales_df, country_filter)
        profit_gauge_fig = create_profit_gauge_chart(sales_df, country_filter)
        visitors_gauge_fig = create_unique_visitors_gauge_chart(sales_df, country_filter)
        bounce_gauge_fig = create_bounce_rate_gauge_chart(sales_df, country_filter)
        va_gauge_fig = create_virtual_assistant_gauge_chart(country_filter)
        
        print(sales_df.head())
        return revenue_fig, traffic_fig, profit_fig, employee_table_fig, profit_gauge_fig, visitors_gauge_fig, bounce_gauge_fig, va_gauge_fig
    
    return app