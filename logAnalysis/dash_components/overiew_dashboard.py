import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from dash import html, dcc, Input, Output
from datetime import datetime
from ..models import ServerLog
from django.db.models.functions import ExtractYear, ExtractHour
from django.db.models import Count, Avg
from .sales_by_country import create_sales_by_country_chart
from .profit_gauge import create_profit_gauge_chart
from .peak_hours2 import create_peak_hours_chart
from .refferer_chart import create_referrer_chart
from .daily_visitors import create_unique_visitors_gauge_chart, create_virtual_assistant_gauge_chart
from .bounce_rate import create_bounce_rate_gauge_chart
from collections import Counter

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

def create_overview_dashboard():
    """Creates a dashboard with all analytics charts and a shared year dropdown"""
    app = DjangoDash('OverviewDashboard', external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])
    
    # Create year dropdown options
    def get_year_options():
        """Get available years from the data"""
        years = ServerLog.objects.annotate(
            year=ExtractYear('timestamp')
        ).values_list('year', flat=True).distinct()
        
        options = [{'label': 'All Years', 'value': 'all'}] + [
            {'label': str(year), 'value': str(year)}
            for year in sorted(years)
        ]
        return options
    
    # App layout with dropdown and all charts
    app.layout = html.Div([
        # Header section with title and filter
        html.Div([
            html.Div([
                html.Span("Showing Data For:", style={
                    'marginRight': '10px',
                    'fontWeight': 'bold',
                    'fontSize': '12px'
                }),
                dcc.Dropdown(
                    id='year-filter',
                    options=get_year_options(),
                    value='all',
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
        
        # Main content area
        html.Div([
            # First row - with gauge chart and 3 existing charts
            html.Div([
                # Container for the two stacked boxes
                html.Div([
                    # Top box (replaced with gauge chart)
                    html.Div([
                        html.H3("Average Yearly Profit", style=title_style),
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
                    
                    # Bottom box (unchanged)
                    html.Div([
                        html.H3("Avg Daily Unique Visitors", style=title_style),
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
                
                # Existing charts
                html.Div([
                    html.H3("Sales by Country", style=title_style),
                    dcc.Graph(id='sales-by-country-chart', config={'displayModeBar': False}, style={'height': '220px'})
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),

                html.Div([
                    html.H3("Product Performance", style=title_style),
                    dcc.Graph(id='product-analytics-chart', config={'displayModeBar': False}, style={'height': '220px'})
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),

                html.Div([
                    html.H3("Weekly Sales Forecast", style=title_style),
                    dcc.Graph(id='referrer-pie-chart', config={'displayModeBar': False}, style={'height': '220px'})
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'})
            ], className="row", style={'marginBottom': '5px'}),

            # Second row - unchanged
            html.Div([
                # Container for the two new stacked boxes
                html.Div([
                    # Top box
                    # Top box (bounce rate gauge chart)
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
                    
                    # Bottom box
                    html.Div([
                        html.H4("Virtual Assistant Usage", style=title_style),
                        dcc.Graph(id='virtual-assistant-gauge-chart', config={'displayModeBar': False}, style={'height': '70px'}),
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
                
                # First chart in second row
                html.Div([
                    html.H3("Peak Traffic Hours", style=title_style),
                    dcc.Graph(id='peak-hours-chart', config={'displayModeBar': False}, style={'height': '220px'})
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),

                # Second chart in second row
                html.Div([
                    html.H3("Weekly Visitor Patterns", style=title_style),
                    dcc.Graph(id='daily-avg-chart', config={'displayModeBar': False}, style={'height': '220px'})
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),
                html.Div([
                    html.H3("Top 5 Visited Pages", style=title_style),
                    dcc.Graph(id='top-pages-chart', config={'displayModeBar': False}, style={'height': '220px'})
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'})

            ], className="row")
        ], style={
            'padding': '5px',
            'backgroundColor': '#f5f7fa'
        })
    ], style={
        'fontFamily': 'Arial, sans-serif',
        'maxWidth': '1500px',
        'margin': '0 auto'
    })

    # Callback to update all charts including the new gauge chart
    @app.callback(
    [
        Output('profit-gauge-chart', 'figure'),
        Output('unique-visitors-gauge-chart', 'figure'),
        Output('bounce-rate-gauge-chart', 'figure'),
        Output('virtual-assistant-gauge-chart', 'figure'),  # ⬅️ Added here
        Output('peak-hours-chart', 'figure'),
        Output('daily-avg-chart', 'figure'),
        Output('product-analytics-chart', 'figure'),
        Output('referrer-pie-chart', 'figure'),
        Output('sales-by-country-chart', 'figure'),
        Output('top-pages-chart', 'figure')
    ],
    [Input('year-filter', 'value')]
)

    def update_charts(selected_year):
        # Helper function to filter data by year
        def filter_by_year(queryset, year):
            if year and year != 'all':
                return queryset.filter(timestamp__year=int(year))
            return queryset
        
        # 0. Create gauge chart for average yearly profit

        def create_top_pages_chart():
            """Returns a vertical bar chart of the top 5 most visited URLs."""
            logs = ServerLog.objects.all().values_list('url', flat=True)

            url_counts = Counter(logs)
            top_5 = url_counts.most_common(5)
            urls, counts = zip(*top_5) if top_5 else ([], [])

            fig = go.Figure(data=[go.Bar(
                x=urls,
                y=counts,
                marker_color='#4e79a7'
            )])

            fig.update_layout(
                height=220,
                margin=dict(l=10, r=10, t=10, b=0),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12),
                xaxis=dict(
                    #title='Page URL',
                    tickangle=-30,
                    tickfont=dict(size=10),
                    showgrid=False
                ),
                yaxis=dict(
                    #title='Visits',
                    showgrid=True,
                    gridcolor='lightgray'
                )
            )

            return fig

        # 1. Update peak hours chart
        # 2. Update daily averages chart
        def create_daily_avg_chart(year):
            logs = filter_by_year(ServerLog.objects, year).values_list('timestamp', flat=True)
            sales = filter_by_year(ServerLog.objects.filter(request_method="POST"), year).values_list('timestamp', flat=True)
            
            if not logs:
                return px.bar(title="No visitor data available")
                
            visitor_days = [datetime.fromisoformat(str(log)).strftime('%A') for log in logs]
            visitor_counts = pd.Series(visitor_days).value_counts().to_dict()
            
            sale_days = [datetime.fromisoformat(str(sale)).strftime('%A') for sale in sales]
            sale_counts = pd.Series(sale_days).value_counts().to_dict()
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            data = []
            
            for day in days:
                visitors = visitor_counts.get(day, 0)
                sales_count = sale_counts.get(day, 0)
                conversion = (sales_count / visitors * 100) if visitors > 0 else 0
                data.append({
                    'day_name': day,
                    'visitors': visitors,
                    'sales': sales_count,
                    'conversion_rate': conversion
                })
                
            daily_df = pd.DataFrame(data)
            
            fig = px.bar(
                daily_df,
                x='day_name',
                y='visitors',
                labels={'visitors': 'Avg Visitors', 'day_name': 'Day of Week'},
                color_discrete_sequence=['#4e79a7'],
                category_orders={"day_name": days}
            )
            
            fig.add_scatter(
                x=daily_df['day_name'],
                y=daily_df['conversion_rate'],
                name='Conversion Rate',
                line=dict(color='#f28e2b', width=3),
                yaxis='y2',
                mode='lines+markers',
                marker=dict(size=8, color='#e15759')
            )
            
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin={"r": 10, "t": 10, "l": 10, "b": 30},
                xaxis={
                    'title': None,
                    'showline': True,
                    'linecolor': 'lightgray',
                    'tickfont': dict(size=10)
                },
                yaxis={
                    'title': 'Avg Visitors',
                    'showline': True,
                    'linecolor': 'lightgray',
                    'gridcolor': 'rgba(0,0,0,0.05)',
                    'tickfont': dict(size=10),
                    'title_font': dict(size=10)
                },
                yaxis2={
                    'title': 'Conversion Rate (%)',
                    'overlaying': 'y',
                    'side': 'right',
                    'showgrid': False,
                    'range': [0, daily_df['conversion_rate'].max() * 1.2],
                    'tickfont': dict(size=10),
                    'title_font': dict(size=10)
                },
                legend={
                    'orientation': 'h',
                    'yanchor': 'bottom',
                    'y': 1.02,
                    'xanchor': 'right',
                    'x': 1,
                    'font': dict(size=10)
                },
                hovermode='x unified'
            )
            
            fig.update_traces(
                marker_line_width=0,
                opacity=0.8,
                hovertemplate='Day: %{x}<br>Visitors: %{y:.0f}<extra></extra>'
            )
            
            fig.update_traces(
                selector={'name': 'Conversion Rate'},
                hovertemplate='Day: %{x}<br>Conversion: %{y:.1f}%<extra></extra>'
            )
            
            return fig
        
        # 3. Update product analytics chart
        def create_product_chart(year):
            queryset = filter_by_year(ServerLog.objects, year)
            
            product_views = (
                queryset
                .filter(url__startswith="/solutions/", request_method="GET")
                .values('url')
                .annotate(view_count=Count('url')))
            
            purchases = (
                queryset
                .filter(request_method="POST")
                .values('url')
                .annotate(purchase_count=Count('url')))
            
            views_df = pd.DataFrame(list(product_views))
            purchases_df = pd.DataFrame(list(purchases))
            
            if views_df.empty and purchases_df.empty:
                return px.bar(title="No product data available")

            def extract_product_name(url):
                parts = str(url).split("/")
                return parts[2] if len(parts) > 2 else "Unknown"
            
            views_df['product'] = views_df['url'].apply(extract_product_name) if not views_df.empty else []
            purchases_df['product'] = purchases_df['url'].apply(extract_product_name) if not purchases_df.empty else []
            
            merged_df = pd.merge(
                views_df.groupby('product')['view_count'].sum().reset_index() if not views_df.empty else pd.DataFrame({'product': [], 'view_count': []}),
                purchases_df.groupby('product')['purchase_count'].sum().reset_index() if not purchases_df.empty else pd.DataFrame({'product': [], 'purchase_count': []}),
                on='product',
                how='outer'
            ).fillna(0)
            
            product_df = merged_df.sort_values('view_count', ascending=False).head(10)
            
            fig = px.bar(
                product_df,
                x='product',
                y=['view_count', 'purchase_count'],
                labels={'product': '', 'value': '', 'variable': 'Metric'},
                color_discrete_map={
                    'view_count': '#4e79a7',  # Blue for views
                    'purchase_count': '#59a14f'  # Green for purchases
                }
            )
            
            fig.update_layout(
                barmode='stack',
                plot_bgcolor='white',
                paper_bgcolor='white',
                hovermode='x',
                margin={"r": 10, "t": 10, "l": 10, "b": 30},
                font=dict(size=10),
                legend=dict(
                    font=dict(size=10),
                    title_font=dict(size=10),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                xaxis={
                    'tickangle': 45,
                    'title': None,
                    'tickfont': dict(size=10)
                },
                yaxis={
                    'title': None,
                    'gridcolor': 'rgba(0,0,0,0.05)',
                    'tickfont': dict(size=10)
                }
            )
            
            return fig
        
        # 4. Update referrer pie chart

        
        
        
        # Return all figures
        return (
            create_profit_gauge_chart(selected_year),
            create_unique_visitors_gauge_chart(selected_year),
            create_bounce_rate_gauge_chart(selected_year),
            create_virtual_assistant_gauge_chart(selected_year),  # ⬅️ Added here
            create_peak_hours_chart(selected_year),
            create_daily_avg_chart(selected_year),
            create_product_chart(selected_year),
            create_referrer_chart(selected_year),
            create_sales_by_country_chart(selected_year),
            create_top_pages_chart()
        )
