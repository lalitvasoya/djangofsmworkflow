from django.db import models


class Workflow(models.Model):
    name = models.CharField(max_length=254)
    states = models.CharField(max_length=254)
