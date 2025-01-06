import random

from django.contrib.auth.models import AbstractUser, Permission, Group
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)    


class Medication(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    side_effects = models.TextField(blank=True, null=True)
    dosage = models.CharField(max_length=255, blank=True, null=True)
    precautions = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_to_take = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    
    # Generate 6-digit random ID
    id = models.IntegerField(default=random.randint(100000, 999999), unique=True, primary_key=True, editable=False)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    date_of_birth = models.DateField(_("date of birth"), null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(
        _("gender"), max_length=1, choices=GENDER_CHOICES, blank=True, null=True
    )
    phone_number = models.CharField(_("phone number"), max_length=15, blank=True, null=True)
    location = models.CharField(_("location"), max_length=255, blank=True, null=True)
    family_members = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users',
        related_query_name='custom_user',
        blank=True,
        verbose_name=_('user permissions'),
        help_text=_('Specific permissions for this user.'),
    )    

class FoodSource(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    latitude = models.CharField(max_length=500, null=True, blank=True)
    longitude = models.CharField(max_length=500, null=True, blank=True)
    source_type = models.CharField(
        max_length=50, 
        choices=[('GROCERY', 'Grocery Store'), ('RESTAURANT', 'Restaurant'), ('FARM', 'Farm')]
    )

    def __str__(self):
        return self.name

class FoodBank(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    street_address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    county = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    resource_type = models.CharField(max_length=50, null=True, blank=True)
    web_link = models.URLField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class SurplusFood(models.Model):
    source = models.ForeignKey(FoodSource, on_delete=models.CASCADE, related_name='surplus_foods')
    food_type = models.CharField(max_length=100)
    quantity_kg = models.FloatField()
    expiry_date = models.DateField()
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_type} - {self.quantity_kg}kg from {self.source.name}"

class Delivery(models.Model):
    surplus_food = models.ForeignKey(SurplusFood, on_delete=models.CASCADE, related_name='deliveries')
    destination = models.CharField(max_length=255)
    delivery_date = models.DateField()
    delivery_status = models.CharField(
        max_length=50, 
        choices=[('PENDING', 'Pending'), ('IN_TRANSIT', 'In Transit'), ('DELIVERED', 'Delivered')]
    )

    def __str__(self):
        return f"Delivery to {self.destination} on {self.delivery_date}"

class AIModelData(models.Model):
    date = models.DateField()
    food_demand_predictions = models.JSONField()  # Stores demand predictions per location/type
    delivery_routes = models.JSONField()  # Optimized delivery routes

    def __str__(self):
        return f"AI Data for {self.date}"
