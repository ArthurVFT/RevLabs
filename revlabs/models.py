from django.db import models

class Track(models.Model):
    slug_id = models.CharField(max_length=50, unique=True, help_text="e.g., 'monza'")
    name = models.CharField(max_length=100)
    length_km = models.FloatField()
    speed_multiplier = models.FloatField()
    image_path = models.CharField(max_length=255, help_text="e.g., 'img/monza.png'")

    def __str__(self):
        return self.name

class Car(models.Model):
    slug_id = models.CharField(max_length=50, unique=True, help_text="e.g., 'mercedes'")
    name = models.CharField(max_length=100)
    base_avg_speed_kmh = models.FloatField()
    power_hp = models.IntegerField()
    weight_kg = models.IntegerField()
    image_path = models.CharField(max_length=255, help_text="e.g., 'img/mercedes-amg.png'")

    def __str__(self):
        return self.name