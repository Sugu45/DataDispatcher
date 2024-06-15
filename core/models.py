from django.db import models
import uuid
from django.core.exceptions import ValidationError


class Account(models.Model):
    email = models.EmailField(unique=True)
    account_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    account_name = models.CharField(max_length=255)
    app_secret_token = models.CharField(max_length=255, default=uuid.uuid4().hex)
    website = models.URLField(blank=True, null=True)

def validate_http_method(value):
    allowed_methods = ['GET', 'POST', 'PUT']
    if value not in allowed_methods:
        raise ValidationError(f"{value} is not a valid HTTP method. Allowed methods are: {', '.join(allowed_methods)}")
class Destination(models.Model):
    account = models.ForeignKey(Account, related_name='destinations', on_delete=models.CASCADE)
    url = models.URLField()
    http_method = models.CharField(max_length=10)
    headers = models.JSONField()


