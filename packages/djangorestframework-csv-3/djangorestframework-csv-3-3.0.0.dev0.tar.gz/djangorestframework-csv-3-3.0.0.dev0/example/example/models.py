from __future__ import annotations

from django.db import models


class Talk(models.Model):
    topic = models.TextField()
    speaker = models.TextField()
    scheduled_at = models.DateTimeField()
