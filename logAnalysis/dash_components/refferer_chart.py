import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from dash.dependencies import Input, Output
from ..models import ServerLog  # Relative import
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from dash import html, dcc, Input, Output
from datetime import datetime
from ..models import ServerLog
from django.db.models.functions import ExtractYear, ExtractHour
from django.db.models import Count, Avg

from django.db.models.functions import TruncWeek
import plotly.express as px
import pandas as pd
from django.db.models import Avg

def filter_by_year(queryset, year):
    if year and year != 'all':
        return queryset.filter(timestamp__year=int(year))
    return queryset

import pandas as pd
import plotly.express as px
from django.db.models import Q

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

def create_referrer_chart(year):
    logs = filter_by_year(ServerLog.objects.filter(request_method="POST"), year)

    sales_data = []
    for log in logs:
        product = None
        if log.url.startswith("/solutions/"):
            parts = log.url.split("/")
            if len(parts) > 2:
                product = parts[2]
                if product in PRODUCT_PRICES:
                    sales_data.append({
                        "product": product,
                        "timestamp": log.timestamp,
                        "amount": PRODUCT_PRICES[product]
                    })

    df = pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=["amount", "timestamp"])

    if df.empty:
        return px.line(title="No sales data available")

    # Convert to datetime just in case
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Create a 'week' column
    df["week"] = df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time)

    # Group by week and calculate average profit
    weekly_avg = df.groupby("week")["amount"].mean().reset_index(name="average_profit")

    # Create the line chart
    fig = px.line(
        weekly_avg,
        x="week",
        y="average_profit",
        #title="Average Weekly Profit",
        labels={"week": "Week", "average_profit": "Avg. Profit ($)"},
        markers=True
    )

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin={"r": 10, "t": 40, "l": 10, "b": 10}
    )

    fig.update_traces(line=dict(color="#28a745"))

    return fig
