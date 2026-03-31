from django.shortcuts import render
from django.http import JsonResponse, Http404
from .api_client import get_all_matches, get_match_by_id
from .algorithm import calculate_win_probability


def match_list(request):
    """Serve the main match listing page."""
    return render(request, 'dashboard/match_list.html')


def match_detail(request, match_id):
    """Serve the match detail page."""
    return render(request, 'dashboard/match_detail.html', {'match_id': match_id})


def api_matches(request):
    """Return all matches as JSON for the listing page."""
    matches = get_all_matches(use_mock=False)
    return JsonResponse(matches)


def api_match_detail(request, match_id):
    match = get_match_by_id(match_id, use_mock=False)

    if not match:
        raise Http404("Match not found")

    if match.get('status') == 'live' and match.get('target', 0) > 0:
        probability = calculate_win_probability(
            target=match.get('target', 0),
            runs=match.get('score', 0),
            wickets=match.get('wickets', 0),
            balls_bowled=match.get('balls_bowled', 0),
        )
        match['batting_win_prob'] = probability['batting_team']
        match['bowling_win_prob'] = probability['bowling_team']
    else:
        match['batting_win_prob'] = None
        match['bowling_win_prob'] = None

    return JsonResponse(match)