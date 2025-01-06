from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('createfoodbanks/', views.create_foodbanks, name='foodbanks'),
    path('foodbanks/', views.AllFoodBanksView.as_view(), name='allfoodbanks'),
    path('foodsource/create/', views.FoodSourceCreateAPIView.as_view(), name='foodsource-create'),
    path('boom/', views.FoodSourceCreateView.as_view()),
    path('foodsources/all', views.AllFoodSources().as_view())
]