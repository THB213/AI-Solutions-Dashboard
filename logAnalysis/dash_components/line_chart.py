import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from django.db.models import Count
from ..models import ServerLog  # Relative import
from datetime import datetime

def create_daily_avg_app():
    """Creates and returns the configured day-of-week averages chart"""
    
    # Initialize the app
    app = DjangoDash(
        'DailyAveragesChart',
        external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"],
        suppress_callback_exceptions=True
    )

    def get_daily_avg_data():
        """Fetches and processes day-of-week averages"""
        # Get all logs and process day of week in Python
        logs = ServerLog.objects.all().values_list('timestamp', flat=True)
        sales = ServerLog.objects.filter(request_method="POST").values_list('timestamp', flat=True)
        
        if not logs:
            return pd.DataFrame()
            
        # Process visitor counts by day of week
        visitor_days = [datetime.fromisoformat(str(log)).strftime('%A') for log in logs]
        visitor_counts = pd.Series(visitor_days).value_counts().to_dict()
        
        # Process sales counts by day of week
        sale_days = [datetime.fromisoformat(str(sale)).strftime('%A') for sale in sales]
        sale_counts = pd.Series(sale_days).value_counts().to_dict()
        
        # Create DataFrame with all days
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
            
        return pd.DataFrame(data)

    def create_daily_avg_chart():
        """Creates the day-of-week averages chart"""
        daily_df = get_daily_avg_data()
        
        if daily_df.empty:
            return px.bar(title="No visitor data available")
            
        # Create figure with secondary y-axis
        fig = px.bar(
            daily_df,
            x='day_name',
            y='visitors',
            title=None,
            labels={'visitors': 'Avg Visitors', 'day_name': 'Day of Week'},
            color_discrete_sequence=['#4285F4'],
            category_orders={"day_name": ["Monday", "Tuesday", "Wednesday", 
                                       "Thursday", "Friday", "Saturday", "Sunday"]}
        )
        
        # Add conversion rate line
        fig.add_scatter(
            x=daily_df['day_name'],
            y=daily_df['conversion_rate'],
            name='Conversion Rate',
            line=dict(color='#FBBC05', width=3),
            yaxis='y2',
            mode='lines+markers',
            marker=dict(size=8, color='#EA4335')
        )
        
        # Customize appearance
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin={"r": 5, "t": 40, "l": 5, "b": 5},
            xaxis={
                'title': 'Day of Week',
                'showline': True,
                'linecolor': 'lightgray',
                'tickfont': dict(size=10)
            },
            yaxis={
                'title': 'Avg Visitors',
                'showline': True,
                'linecolor': 'lightgray',
                'gridcolor': 'lightgray',
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
        
        # Style the bars
        fig.update_traces(
            marker_line_width=0,
            opacity=0.8,
            hovertemplate='Day: %{x}<br>Visitors: %{y:.0f}<extra></extra>'
        )
        
        # Style the line
        fig.update_traces(
            selector={'name': 'Conversion Rate'},
            hovertemplate='Day: %{x}<br>Conversion: %{y:.1f}%<extra></extra>'
        )
        
        return fig

    # Set the app layout
    app.layout = html.Div([
        html.Div(
            "Weekly Visitor & Conversion Patterns",
            style={
                'textAlign': 'center',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'color': '#333',
                'marginBottom': '10px'
            }
        ),
        dcc.Graph(
            id='daily-avg-chart',
            figure=create_daily_avg_chart(),
            config={'displayModeBar': False},
            style={
                'height': '270px',
                'width': '100%',
                'margin': '0 auto'
            }
        ),
        html.Div(
            "Average values by day of week",
            style={
                'textAlign': 'center',
                'fontSize': '12px',
                'color': '#666',
                'marginTop': '-20px'
            }
        )
    ], style={'backgroundColor': 'white', 'padding': '10px'})

    return app