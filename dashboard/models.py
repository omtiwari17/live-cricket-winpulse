from django.db import models

class Match(models.Model):
    match_id    = models.CharField(max_length=100, unique=True)
    tournament  = models.CharField(max_length=100)
    status      = models.CharField(max_length=20)  # live / upcoming / completed
    team_a      = models.CharField(max_length=100)
    team_a_short= models.CharField(max_length=10)
    team_b      = models.CharField(max_length=100)
    team_b_short= models.CharField(max_length=10)
    venue       = models.CharField(max_length=200, blank=True)
    is_active   = models.BooleanField(default=True)  # uncheck to hide from dashboard
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} — {self.tournament}"

    class Meta:
        ordering = ['-created_at']
        verbose_name        = 'Match'
        verbose_name_plural = 'Matches'
