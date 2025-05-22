from django.db import models
import pandas as pd
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash
from django.db.models import Count

from .models import ServerLog  # Import your model
import sys
from pathlib import Path

# Add these TWO paths (both project root and app directory)
sys.path.append(str(Path(__file__).parent.parent))  # Project root
sys.path.append(str(Path(__file__).parent))         # App directory

# Now use absolute imports
from logAnalysis.dash_components.line_chart import create_daily_avg_app

# Rest of your code...
line_chart_app = create_daily_avg_app()

# ---------- Peal Hours Histogram ----------
# Add this import at the top
from .dash_components.peak_hours import create_peak_hours_app

# Initialize the app (replace your existing peak hours code with this)
hist_app = create_peak_hours_app()
# ---------- Geo Distribution Dash App ----------

# Add this import at the top
from .dash_components.geo_distribution import create_geo_distribution_app

# Initialize the app (replace your existing geo distribution code with this)
geo_distribution_app = create_geo_distribution_app()
# ==============================================
# 2. Top Pages Bar Chart App
# ==============================================
# Add this import at the top
from .dash_components.top_pages import create_top_pages_app

# Initialize the app (replace your existing top pages code with this)
pages_app = create_top_pages_app()

# Add this import at the top
from .dash_components.referrer_pie import create_referrer_pie_app

# Initialize the app (replace your existing referrer pie code with this)
referrer_app = create_referrer_pie_app()

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#-----------------------------------------------SALES Dashboard-------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
# Add this import at the top
#from .dash_components.sales_by_country import create_sales_by_country_app

# Initialize the app (replace your existing sales by country code with this)
#sales_app = create_sales_by_country_app()
# ==============================================
# 2. Sales Line Chart
# ==============================================
# Add this import at the top
from .dash_components.sales_trend import create_sales_trend_app

# Initialize the app (replace your existing sales trend code with this)
sales_trend_app = create_sales_trend_app()
# ==============================================
# 2. Sales By Product
# ==============================================
# Add this import at the top
from .dash_components.product_sales import create_product_analytics_app

# Initialize the app (replace your existing product sales code with this)
product_sales_app = create_product_analytics_app()


from logAnalysis.dash_components.dropdown_app import create_dropdown_app

# Rest of your code...
drop_down_app = create_dropdown_app()

# Add this import at the top
from .dash_components.sales_dashboard import create_sales_dashboard

# Initialize the dashboard app
sales_dashboard_app = create_sales_dashboard()

from .dash_components.overiew_dashboard import create_overview_dashboard

# Initialize the dashboard app
overview_dashboard = create_overview_dashboard()