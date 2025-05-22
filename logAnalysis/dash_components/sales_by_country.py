import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from dash.dependencies import Input, Output
from ..models import ServerLog  # Relative import


def filter_by_year(queryset, year):
    if year and year != 'all':
        return queryset.filter(timestamp__year=int(year))
    return queryset
# 5. Update sales by country chart
def create_sales_by_country_chart(year):
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
        "102.": "Zambia",
        "154.": "Namibia",
        "197.": "Zimbabwe"
    }

    COUNTRY_TARGETS = {
        "Botswana": 10_000_000,
        "Namibia": 5_000_000,
        "Zambia": 2_000_000,
        "Zimbabwe": 2_000_000
    }
    
    logs = filter_by_year(ServerLog.objects.filter(request_method="POST"), year)
    
    sales_data = []
    for log in logs:
        product = None
        if log.url.startswith("/solutions/"):
            parts = log.url.split("/")
            if len(parts) > 2:
                product = parts[2]
                if product not in PRODUCT_PRICES:
                    continue
        
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
                "country": country,
                "referrer": log.referrer,
                "amount": PRODUCT_PRICES[product]
            })
    
    df = pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=["country", "amount"])
    
    if df.empty:
        return px.bar(title="No sales data available")
        
    country_sales = df.groupby("country", as_index=False)["amount"].sum()
    country_sales["target"] = country_sales["country"].map(COUNTRY_TARGETS)
    country_sales["variance"] = country_sales["amount"] - country_sales["target"]
    country_sales["achieved"] = country_sales[["amount", "target"]].min(axis=1)
    country_sales["over_achieved"] = country_sales["variance"].apply(lambda x: x if x > 0 else 0)
    country_sales["under_achieved"] = country_sales["variance"].apply(lambda x: -x if x < 0 else 0)
    
    melted_df = pd.melt(
        country_sales,
        id_vars=["country"],
        value_vars=["achieved", "over_achieved", "under_achieved"],
        var_name="category",
        value_name="amount"
    )
    
    color_map = {
        "achieved": "#4e79a7",
        "over_achieved": "#59a14f",
        "under_achieved": "#e15759"
    }
    
    fig = px.bar(
        melted_df,
        x="country",
        y="amount",
        color="category",
        color_discrete_map=color_map,
        labels={"amount": "Revenue ($)", "country": "Country"},
        text="amount"
    )
    
    for i, row in country_sales.iterrows():
        fig.add_shape(
            type="line",
            x0=i-0.4, x1=i+0.4,
            y0=row["target"], y1=row["target"],
            line=dict(color="#333", width=2, dash="dot"),
            xref="x",
            yref="y"
        )
    
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin={"r": 10, "t": 10, "l": 10, "b": 30},
        xaxis={
            "showline": True,
            "linecolor": "lightgray",
            "tickfont": dict(size=10),
            "title_font": dict(size=12),
            "title": None
        },
        yaxis={
            "showline": True,
            "linecolor": "lightgray",
            "gridcolor": "rgba(0,0,0,0.05)",
            "title": "Revenue ($)",
            "tickfont": dict(size=10),
            "title_font": dict(size=10)
        },
        legend={
            "font": dict(size=10),
            "title_font": dict(size=10),
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1
        },
        barmode="stack"
    )
    
    fig.update_traces(
        texttemplate="$%{y:,.0f}",
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.1)",
        marker_line_width=0.5,
        textfont_size=10
    )
    
    return fig