from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/match-data/', views.match_data, name='match_data'),
]