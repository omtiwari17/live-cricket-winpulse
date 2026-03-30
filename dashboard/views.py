from django.shortcuts import render
from django.http import JsonResponse
from .api_client import get_live_match
from .algorithm import calculate_win_probability


def index(request):
    """Serve the main dashboard HTML page."""
    return render(request, 'dashboard/index.html')


def match_data(request):
    """
    Return current match data + win probability as JSON.
    Called by JavaScript every few seconds.
    """
    # During development use mock=True
    # When ready for real data change to use_mock=False
    match = get_live_match(use_mock=True)

    # Calculate win probability from algorithm
    probability = calculate_win_probability(
        target=match['target'],
        runs=match['score'],
        wickets=match['wickets'],
        balls_bowled=match['balls_bowled']
    )

    # Combine match data + probability into one response
    response = {
        **match,
        'batting_win_prob': probability['batting_team'],
        'bowling_win_prob': probability['bowling_team'],
    }

    return JsonResponse(response)