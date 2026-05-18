from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    country_of_origin = models.CharField(max_length=100, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    car_make = models.ForeignKey(
        CarMake,
        on_delete=models.CASCADE,
        related_name='carmodels'
    )
    dealer_id = models.IntegerField(help_text="Dealer ID from Cloudant database")

    name = models.CharField(max_length=100)

    TYPE_CHOICES = [
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Wagon', 'Wagon'),
        ('Hatchback', 'Hatchback'),
        ('Coupe', 'Coupe'),
        ('Convertible', 'Convertible'),
        ('Truck', 'Truck'),
        ('Van', 'Van'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    year = models.IntegerField(
        validators=[
            MinValueValidator(2015),
            MaxValueValidator(2023)
        ]
    )

    # Additional useful fields
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    engine = models.CharField(max_length=100, blank=True)
    fuel_type = models.CharField(
        max_length=50,
        choices=[
            ('Petrol', 'Petrol'),
            ('Diesel', 'Diesel'),
            ('Electric', 'Electric'),
            ('Hybrid', 'Hybrid'),
        ],
        blank=True
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"