from django.db import models

class Incident(models.Model):
    user_id = models.IntegerField()
    street = models.CharField(max_length=200)
    description = models.TextField(null=False, default="No description provided")
    # Если вам нужно поле, которое может быть пустым, но без значения NULL:
    # description = models.TextField(default="No description provided", blank=True)
    photo = models.ImageField(upload_to='incidents/', null=True, blank=True)
