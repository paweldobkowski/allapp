from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.main, name='main'),
    path('introduction/', views.introduction, name='introduction'),
    path('skip/', views.skip, name='skip'),
    path('fight/', views.fight, name='fight'),
    path('summary/', views.summary, name='summary'),
    path('c/', views.clear, name='clear'),
]