from django.db import models

class ServerLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField()
    request_method = models.CharField(max_length=10)
    url = models.CharField(max_length=500)
    http_version = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_size = models.IntegerField()
    referrer = models.URLField(blank=True, null=True)
    user_agent = models.TextField()
    promo_code = models.CharField(max_length=20, blank=True, null=True)  # New field

    def __str__(self):
        return f"{self.ip_address} - {self.request_method} {self.url} ({self.status_code})"

