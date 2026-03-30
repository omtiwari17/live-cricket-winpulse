import requests
from django.conf import settings

# ── Track which key we're currently using ───────────────────────────────────
# Starts at 0 (first key), increments when a key hits its limit
_current_key_index = 0


def _get_current_key():
    """Return the currently active API key."""
    keys = settings.CRICKET_API_KEYS
    if not keys:
        return None
    return keys[_current_key_index]


def _rotate_key():
    """
    Move to the next available key.
    Returns True if a new key is available, False if all keys exhausted.
    """
    global _current_key_index
    keys = settings.CRICKET_API_KEYS

    if _current_key_index < len(keys) - 1:
        _current_key_index += 1
        print(f"[API] Rotated to key {_current_key_index + 1}")
        return True

    print("[API] All keys exhausted for today.")
    return False


def _make_request(endpoint, params={}):
    """
    Make a single API request with the current key.
    Rotates key automatically if limit is hit.

    Args:
        endpoint (str): API endpoint path e.g. 'cricScore'
        params   (dict): Extra query parameters

    Returns:
        dict: API response data or None if all keys failed
    """
    global _current_key_index
    keys = settings.CRICKET_API_KEYS

    while _current_key_index < len(keys):
        key = keys[_current_key_index]
        url = f"https://api.cricapi.com/v1/{endpoint}"

        try:
            response = requests.get(
                url,
                params={"apikey": key, **params},
                timeout=5      # don't wait more than 5 seconds
            )
            data = response.json()

            # CricketData returns status "failure" when limit is hit
            if data.get("status") == "failure":
                reason = data.get("reason", "unknown error")
                print(f"[API] Key {_current_key_index + 1} failed: {reason}")

                if not _rotate_key():
                    return None     # all keys exhausted
                continue            # retry with new key

            return data             # success

        except requests.exceptions.Timeout:
            print(f"[API] Key {_current_key_index + 1} timed out.")
            if not _rotate_key():
                return None
            continue

        except requests.exceptions.RequestException as e:
            print(f"[API] Request error: {e}")
            return None

    return None


# ── Mock data for development ────────────────────────────────────────────────
# Use this while building so you don't waste real API calls
MOCK_MATCH_DATA = {
    "match_id": "mock_001",
    "team_batting": "India",
    "team_bowling": "Australia",
    "score": 142,
    "wickets": 3,
    "overs": "15.2",
    "balls_bowled": 92,
    "target": 186,
    "crr": 9.26,
    "rrr": 12.0,
    "status": "live",
    "is_mock": True
}


def get_live_match(use_mock=False):
    """
    Main function called by Django views to get current match data.

    Args:
        use_mock (bool): If True, return mock data (use during development)

    Returns:
        dict: Cleaned match data ready for the algorithm and frontend
    """
    if use_mock:
        return MOCK_MATCH_DATA

    # Step 1 — Get list of live matches
    data = _make_request("cricScore")
    if not data:
        print("[API] Falling back to mock data.")
        return MOCK_MATCH_DATA

    matches = data.get("data", [])
    if not matches:
        return MOCK_MATCH_DATA

    # Step 2 — Find first India match or first live match
    target_match = None
    for match in matches:
        teams = match.get("name", "").lower()
        if "india" in teams:
            target_match = match
            break

    # If no India match, just take the first live match
    if not target_match and matches:
        target_match = matches[0]

    if not target_match:
        return MOCK_MATCH_DATA

    # Step 3 — Return cleaned data
    return _parse_match(target_match)


def _parse_match(raw):
    """
    Clean raw API response into a consistent format
    that the rest of the app always expects.
    """
    return {
        "match_id": raw.get("id", ""),
        "team_batting": raw.get("t2", "Team A"),
        "team_bowling": raw.get("t1", "Team B"),
        "score": raw.get("t2s", 0),
        "wickets": 0,       # will refine when we get ball-by-ball endpoint
        "overs": raw.get("t2s", "0.0"),
        "balls_bowled": 0,
        "target": 0,
        "crr": 0.0,
        "rrr": 0.0,
        "status": raw.get("matchStarted", False),
        "is_mock": False
    }