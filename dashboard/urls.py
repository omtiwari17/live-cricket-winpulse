from django.urls import path
from . import views

urlpatterns = [
    path('', views.match_list, name='match_list'),
    path('match/<str:match_id>/', views.match_detail, name='match_detail'),
    path('api/matches/', views.api_matches, name='api_matches'),
    path('api/match/<str:match_id>/', views.api_match_detail, name='api_match_detail'),
]