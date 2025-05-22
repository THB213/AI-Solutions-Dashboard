import time
import random
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from django.core.files.storage import FileSystemStorage
import os
import re
from .models import ServerLog
from datetime import datetime
from django.contrib import messages
from django.db.models import Count
from django.utils.dateformat import DateFormat

import json

def generate_logs():
    """Yields real-time log entries"""
    while True:
        log_entry = (
            f"192.168.1.{random.randint(1, 255)} - - "
            f"[{time.strftime('%d/%b/%Y:%H:%M:%S')}] "
            f'"GET / HTTP/1.1" {random.choice([200, 404, 500])} {random.randint(500, 5000)}\n'
        )
        yield log_entry
        time.sleep(random.uniform(0.5, 2))  # Simulate delays

def stream_logs(request):
    return StreamingHttpResponse(generate_logs(), content_type="text/plain")

def dashboard(request):
    total_requests = ServerLog.objects.count()
    successful_requests = ServerLog.objects.filter(status_code=200).count()
    not_found_requests = ServerLog.objects.filter(status_code=404).count()
    internal_server_errors = ServerLog.objects.filter(status_code=500).count()
    unique_visitors = ServerLog.objects.values("ip_address").distinct().count()

    # Aggregate unique visitors per day
    unique_visitors_per_day = (
        ServerLog.objects.values("timestamp__date")
        .annotate(unique_visitors=Count("ip_address", distinct=True))
        .order_by("timestamp__date")
    )

    # Prepare data for the chart (convert to lists)
    labels = [DateFormat(entry["timestamp__date"]).format("Y-m-d") for entry in unique_visitors_per_day]
    data = [entry["unique_visitors"] for entry in unique_visitors_per_day]

    # Aggregate user agents
    user_agents = (
        ServerLog.objects.values("user_agent")
        .annotate(request_count=Count("user_agent"))
        .order_by("-request_count")[:10]  # Top 10 most frequent user agents
    )

    user_agent_labels = [entry["user_agent"] for entry in user_agents]
    user_agent_counts = [entry["request_count"] for entry in user_agents]

    context = {
        "chart_labels": json.dumps(labels),  # Convert to JSON for JS consumption
        "chart_data": json.dumps(data),
    }

    return render(request, "logAnalysis/chatGPTdashboard.html", context)


# Updated regex pattern to include promo codes
LOG_PATTERN = re.compile(
    r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>.*?)\] "(?P<method>\w+) (?P<url>.*?)(?:\?(?P<query>.*?))? (?P<http_version>HTTP\/\d\.\d)" (?P<status>\d+) (?P<size>\d+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
)

def extract_promo_code(query_string):
    """Extract promo code from query string if present"""
    if not query_string:
        return None
    params = query_string.split('&')
    for param in params:
        if param.startswith('promo_code='):
            return param.split('=')[1]
    return None

def upload_logs(request):
    if request.method == "POST" and request.FILES.get("log_file"):
        log_file = request.FILES["log_file"]

        if not log_file.name.endswith(".txt"):
            messages.error(request, "Invalid file type. Please upload a .txt file.")
            return redirect("dashboard")

        fs = FileSystemStorage(location="logs/")
        filename = fs.save(log_file.name, log_file)
        file_path = fs.path(filename)

        log_count = 0
        error_count = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    match = LOG_PATTERN.match(line)
                    if match:
                        data = match.groupdict()

                        try:
                            # Convert timestamp to Python datetime object
                            timestamp = datetime.strptime(data["timestamp"], "%d/%b/%Y:%H:%M:%S %z")
                            
                            # Extract promo code from URL query parameters
                            promo_code = extract_promo_code(data.get("query"))

                            # Save the log entry in the database
                            ServerLog.objects.create(
                                ip_address=data["ip"],
                                timestamp=timestamp,
                                request_method=data["method"],
                                url=data["url"],
                                http_version=data["http_version"],
                                status_code=int(data["status"]),
                                response_size=int(data["size"]),
                                referrer=data["referrer"] if data["referrer"] != "-" else None,
                                user_agent=data["user_agent"],
                                promo_code=promo_code
                            )
                            log_count += 1
                        except Exception as e:
                            error_count += 1

            if log_count > 0:
                messages.success(request, f"Successfully uploaded {log_count} log entries.")
            if error_count > 0:
                messages.warning(request, f"{error_count} log entries could not be processed.")

        except Exception as e:
            messages.error(request, f"An error occurred while processing the file: {str(e)}")

        return redirect("dashboard")

    messages.error(request, "No file was uploaded.")
    return redirect("dashboard")


def dashboard_view1(request):
    return render(request, 'LogAnalysis/dashboard_tester.html')

def Salesdashboard(request):

    context = {
    }

    return render(request, "logAnalysis/Salesdashboard.html", context)

from django.shortcuts import render
from logAnalysis.models import ServerLog
from django.db.models.functions import ExtractYear

def NewDashboard(request):
    # Fetch unique years from ServerLog timestamps
    years = ServerLog.objects.annotate(
        year=ExtractYear('timestamp')
    ).values('year').distinct().order_by('-year')

    # Convert to a list for the template
    year_list = [str(item['year']) for item in years]

    context = {
        'years': year_list,
    }
    return render(request, 'logAnalysis/new_dashboard.html', context)

def RegionalSalesAnalysis(request):
    context = {

    }

    return render(request, 'logAnalysis/regional_sales_analysis.html', context)