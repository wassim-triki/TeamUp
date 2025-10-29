from django.db import models


# Add shared models for the public site here.
class Example(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
