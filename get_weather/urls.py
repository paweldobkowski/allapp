from django.urls import path
from . import views

app_name = 'get_weather'

urlpatterns = [
    path('weather/', views.get_weather, name="get_weather"),
    path('', views.before_display, name='before_display'),
]