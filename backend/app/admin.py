from django.contrib import admin
from .models import CustomUser, FoodBank, FoodSource

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(FoodBank)
admin.site.register(FoodSource)