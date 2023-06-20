

from django.db import models

class User(models.Model):
    id   = models.IntegerField(primary_key=True)
    name = models.CharField   (max_length=100)


