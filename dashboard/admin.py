from django.contrib import admin
from .models import Match

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display  = ['match_id', 'team_a', 'team_b', 'tournament', 'status', 'is_active']
    list_editable = ['is_active']   # toggle active/inactive directly from list
    list_filter   = ['status', 'tournament', 'is_active']
    search_fields = ['team_a', 'team_b', 'match_id']
