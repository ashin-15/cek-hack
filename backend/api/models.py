from django.db import models


class Snapshot(models.Model):
    name = models.CharField(max_length=40, unique=True)
    payload = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
