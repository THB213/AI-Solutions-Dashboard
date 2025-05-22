
            document.addEventListener("DOMContentLoaded", function () {
                // Unique Visitors Line Chart
                var ctx1 = document.getElementById("uniqueVisitorsChart").getContext("2d");
                new Chart(ctx1, {
                    type: "line",
                    data: {
                        labels: {{ chart_labels|safe }},
                        datasets: [{
                            label: "Unique Visitors",
                            data: {{ chart_data|safe }},
                            borderColor: "rgba(75, 192, 192, 1)",
                            backgroundColor: "rgba(75, 192, 192, 0.2)",
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: { title: { display: true, text: "Date" }},
                            y: { beginAtZero: true, title: { display: true, text: "Unique Visitors" }}
                        }
                    }
                });
        
                // User Agent Bar Chart
                var ctx2 = document.getElementById("userAgentChart").getContext("2d");
                new Chart(ctx2, {
                    type: "bar",
                    data: {
                        labels: {{ user_agent_labels|safe }},
                        datasets: [{
                            label: "Number of Requests",
                            data: {{ user_agent_counts|safe }},
                            backgroundColor: "rgba(54, 162, 235, 0.5)",
                            borderColor: "rgba(54, 162, 235, 1)",
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: { title: { display: true, text: "User Agent" }},
                            y: { beginAtZero: true, title: { display: true, text: "Number of Requests" }}
                        }
                    }
                });
            });

