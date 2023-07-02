from django.contrib.auth.models import User
from django.db import models

class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100)

    def __str__(self):
        return self.name
