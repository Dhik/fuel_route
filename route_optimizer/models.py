from django.db import models

class FuelStation(models.Model):
    truckstop_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    rack_id = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"
