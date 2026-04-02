import requests
from django.conf import settings

# ── Key rotation state ───────────────────────────────────────────────────────
_current_key_index = 0


def _get_current_key():
    keys = settings.CRICKET_API_KEYS
    if not keys:
        return None
    return keys[_current_key_index]


def _rotate_key():
    global _current_key_index
    keys = settings.CRICKET_API_KEYS
    if _current_key_index < len(keys) - 1:
        _current_key_index += 1
        print(f"[API] Rotated to key {_current_key_index + 1}")
        return True
    print("[API] All keys exhausted for today.")
    return False


def _make_request(endpoint, params={}):
    global _current_key_index
    keys = settings.CRICKET_API_KEYS

    while _current_key_index < len(keys):
        key = keys[_current_key_index]
        url = f"https://api.cricapi.com/v1/{endpoint}"
        try:
            response = requests.get(
                url,
                params={"apikey": key, **params},
                timeout=5
            )
            data = response.json()
            if data.get("status") == "failure":
                reason = data.get("reason", "unknown error")
                print(f"[API] Key {_current_key_index + 1} failed: {reason}")
                if not _rotate_key():
                    return None
                continue
            return data
        except requests.exceptions.Timeout:
            print(f"[API] Key {_current_key_index + 1} timed out.")
            if not _rotate_key():
                return None
            continue
        except requests.exceptions.RequestException as e:
            print(f"[API] Request error: {e}")
            return None
    return None


# ── Tournament types ─────────────────────────────────────────────────────────
TOURNAMENT_IPL         = "IPL"
TOURNAMENT_T20_WC      = "T20 World Cup"
TOURNAMENT_ODI_WC      = "ODI World Cup"
TOURNAMENT_CT          = "Champions Trophy"
TOURNAMENT_WTC         = "WTC Final"
TOURNAMENT_INDIA_TEST  = "India Test"
TOURNAMENT_INDIA_ODI   = "India ODI"
TOURNAMENT_INDIA_T20   = "India T20I"

ICC_TOURNAMENTS = [
    TOURNAMENT_T20_WC,
    TOURNAMENT_ODI_WC,
    TOURNAMENT_CT,
    TOURNAMENT_WTC,
    TOURNAMENT_INDIA_TEST,
    TOURNAMENT_INDIA_ODI,
    TOURNAMENT_INDIA_T20,
]


# ── Rich mock data ───────────────────────────────────────────────────────────
MOCK_MATCHES = [

    # ── LIVE ────────────────────────────────────────────────────────────────
    {
        "match_id":       "ipl_001",
        "tournament":     TOURNAMENT_IPL,
        "status":         "live",
        "team_a":         "Mumbai Indians",
        "team_a_short":   "MI",
        "team_b":         "Chennai Super Kings",
        "team_b_short":   "CSK",
        "team_batting":   "Chennai Super Kings",
        "team_bowling":   "Mumbai Indians",
        "score":          142,
        "wickets":        3,
        "overs":          "15.2",
        "balls_bowled":   92,
        "target":         186,
        "crr":            9.26,
        "rrr":            12.0,
        "venue":          "Wankhede Stadium, Mumbai",
        "batting_players": [
            {"name": "Ruturaj Gaikwad", "runs": 67, "balls": 42, "fours": 6, "sixes": 3, "sr": 159.5, "status": "batting"},
            {"name": "Shivam Dube",     "runs": 34, "balls": 21, "fours": 2, "sixes": 2, "sr": 161.9, "status": "batting"},
            {"name": "MS Dhoni",        "runs": 18, "balls": 14, "fours": 1, "sixes": 1, "sr": 128.5, "status": "yet to bat"},
        ],
        "bowling_players": [
            {"name": "Jasprit Bumrah",  "overs": "4.0", "runs": 28, "wickets": 1, "economy": 7.0},
            {"name": "Hardik Pandya",   "overs": "3.2", "runs": 42, "wickets": 1, "economy": 12.6},
            {"name": "Piyush Chawla",   "overs": "3.0", "runs": 31, "wickets": 1, "economy": 10.3},
        ],
        "ball_history":   [1, 4, 0, 6, "W", 2],
        "commentary":     "CSK need 44 runs off 28 balls. Gaikwad is in fine touch.",
        "is_mock":        True,
    },
    {
        "match_id":       "ct_001",
        "tournament":     TOURNAMENT_CT,
        "status":         "live",
        "team_a":         "India",
        "team_a_short":   "IND",
        "team_b":         "Pakistan",
        "team_b_short":   "PAK",
        "team_batting":   "India",
        "team_bowling":   "Pakistan",
        "score":          198,
        "wickets":        4,
        "overs":          "43.1",
        "balls_bowled":   259,
        "target":         242,
        "crr":            7.28,
        "rrr":            8.14,
        "venue":          "Dubai International Stadium",
        "batting_players": [
            {"name": "Virat Kohli",     "runs": 82, "balls": 91, "fours": 7, "sixes": 2, "sr": 90.1, "status": "batting"},
            {"name": "KL Rahul",        "runs": 54, "balls": 61, "fours": 4, "sixes": 1, "sr": 88.5, "status": "batting"},
            {"name": "Hardik Pandya",   "runs": 0,  "balls": 0,  "fours": 0, "sixes": 0, "sr": 0.0,  "status": "yet to bat"},
        ],
        "bowling_players": [
            {"name": "Shaheen Afridi",  "overs": "9.1", "runs": 52, "wickets": 2, "economy": 5.67},
            {"name": "Haris Rauf",      "overs": "8.0", "runs": 61, "wickets": 1, "economy": 7.62},
            {"name": "Shadab Khan",     "overs": "9.0", "runs": 41, "wickets": 1, "economy": 4.55},
        ],
        "ball_history":   [1, 1, 4, 0, 1, 2],
        "commentary":     "India need 44 runs off 41 balls with 6 wickets in hand. Kohli looking solid.",
        "is_mock":        True,
    },

    # ── UPCOMING ─────────────────────────────────────────────────────────────
    {
        "match_id":       "ipl_002",
        "tournament":     TOURNAMENT_IPL,
        "status":         "upcoming",
        "team_a":         "Royal Challengers Bangalore",
        "team_a_short":   "RCB",
        "team_b":         "Kolkata Knight Riders",
        "team_b_short":   "KKR",
        "match_time":     "Today, 7:30 PM IST",
        "venue":          "M. Chinnaswamy Stadium, Bengaluru",
        "is_mock":        True,
    },
    {
        "match_id":       "t20wc_001",
        "tournament":     TOURNAMENT_T20_WC,
        "status":         "upcoming",
        "team_a":         "Australia",
        "team_a_short":   "AUS",
        "team_b":         "England",
        "team_b_short":   "ENG",
        "match_time":     "Tomorrow, 2:00 PM IST",
        "venue":          "Melbourne Cricket Ground",
        "is_mock":        True,
    },
    {
        "match_id":       "wtc_001",
        "tournament":     TOURNAMENT_WTC,
        "status":         "upcoming",
        "team_a":         "South Africa",
        "team_a_short":   "SA",
        "team_b":         "New Zealand",
        "team_b_short":   "NZ",
        "match_time":     "Apr 5, 3:30 PM IST",
        "venue":          "Lord's Cricket Ground, London",
        "is_mock":        True,
    },

    # ── COMPLETED ────────────────────────────────────────────────────────────
    {
        "match_id":       "ipl_003",
        "tournament":     TOURNAMENT_IPL,
        "status":         "completed",
        "team_a":         "Rajasthan Royals",
        "team_a_short":   "RR",
        "team_b":         "Delhi Capitals",
        "team_b_short":   "DC",
        "result":         "Rajasthan Royals won by 6 wickets",
        "team_a_score":   "174/4 (19.2 ov)",
        "team_b_score":   "171/7 (20 ov)",
        "venue":          "Sawai Mansingh Stadium, Jaipur",
        "is_mock":        True,
    },
    {
        "match_id":       "odiwc_001",
        "tournament":     TOURNAMENT_ODI_WC,
        "status":         "completed",
        "team_a":         "India",
        "team_a_short":   "IND",
        "team_b":         "New Zealand",
        "team_b_short":   "NZ",
        "result":         "India won by 4 wickets",
        "team_a_score":   "274/6 (48.3 ov)",
        "team_b_score":   "273/8 (50 ov)",
        "venue":          "BRSABV Ekana Cricket Stadium, Lucknow",
        "is_mock":        True,
    },
    # ── INDIA INTERNATIONAL ──────────────────────────────────────────────────
    {
        "match_id":       "ind_t20_001",
        "tournament":     TOURNAMENT_INDIA_T20,
        "status":         "live",
        "team_a":         "India",
        "team_a_short":   "IND",
        "team_b":         "Sri Lanka",
        "team_b_short":   "SL",
        "team_batting":   "India",
        "team_bowling":   "Sri Lanka",
        "score":          88,
        "wickets":        1,
        "overs":          "10.3",
        "balls_bowled":   63,
        "target":         154,
        "crr":            8.38,
        "rrr":            11.66,
        "venue":          "M. A. Chidambaram Stadium, Chennai",
        "batting_players": [
            {"name": "Rohit Sharma",  "runs": 51, "balls": 32, "fours": 5, "sixes": 3, "sr": 159.3, "status": "batting"},
            {"name": "Shubman Gill",  "runs": 29, "balls": 24, "fours": 3, "sixes": 1, "sr": 120.8, "status": "batting"},
            {"name": "Virat Kohli",   "runs": 0,  "balls": 0,  "fours": 0, "sixes": 0, "sr": 0.0,   "status": "yet to bat"},
        ],
        "bowling_players": [
            {"name": "Wanindu Hasaranga", "overs": "3.0", "runs": 22, "wickets": 1, "economy": 7.33},
            {"name": "Matheesha Pathirana","overs": "2.3","runs": 28, "wickets": 0, "economy": 11.2},
            {"name": "Dushmantha Chameera","overs": "2.0","runs": 18, "wickets": 0, "economy": 9.0},
        ],
        "ball_history":   [4, 1, 1, 0, 4, 1],
        "commentary":     "India need 66 runs off 57 balls. Rohit is playing aggressively.",
        "is_mock":        True,
    },
    {
        "match_id":       "ind_test_001",
        "tournament":     TOURNAMENT_INDIA_TEST,
        "status":         "live",
        "team_a":         "India",
        "team_a_short":   "IND",
        "team_b":         "England",
        "team_b_short":   "ENG",
        "team_batting":   "England",
        "team_bowling":   "India",
        "score":          312,
        "wickets":        6,
        "overs":          "87.4",
        "balls_bowled":   526,
        "target":         0,
        "crr":            3.57,
        "rrr":            0,
        "venue":          "Lord's Cricket Ground, London",
        "batting_players": [
            {"name": "Ben Stokes",    "runs": 74, "balls": 98,  "fours": 8, "sixes": 2, "sr": 75.5, "status": "batting"},
            {"name": "Jonny Bairstow","runs": 41, "balls": 67,  "fours": 4, "sixes": 0, "sr": 61.1, "status": "batting"},
            {"name": "Stuart Broad",  "runs": 0,  "balls": 0,   "fours": 0, "sixes": 0, "sr": 0.0,  "status": "yet to bat"},
        ],
        "bowling_players": [
            {"name": "Jasprit Bumrah",  "overs": "22.0", "runs": 68,  "wickets": 3, "economy": 3.09},
            {"name": "Ravichandran Ashwin","overs":"24.4","runs": 91,  "wickets": 2, "economy": 3.69},
            {"name": "Mohammed Siraj",  "overs": "18.0", "runs": 72,  "wickets": 1, "economy": 4.0},
        ],
        "ball_history":   [0, 1, 0, 0, 1, 4],
        "commentary":     "England trail by 128 runs with 4 wickets remaining. Stokes fighting hard.",
        "is_mock":        True,
    },
    {
        "match_id":       "ind_odi_001",
        "tournament":     TOURNAMENT_INDIA_ODI,
        "status":         "upcoming",
        "team_a":         "India",
        "team_a_short":   "IND",
        "team_b":         "West Indies",
        "team_b_short":   "WI",
        "match_time":     "Tomorrow, 1:30 PM IST",
        "venue":          "Narendra Modi Stadium, Ahmedabad",
        "is_mock":        True,
    },
    {
        "match_id":       "ind_test_002",
        "tournament":     TOURNAMENT_INDIA_TEST,
        "status":         "completed",
        "team_a":         "India",
        "team_a_short":   "IND",
        "team_b":         "Australia",
        "team_b_short":   "AUS",
        "result":         "India won by an innings and 47 runs",
        "team_a_score":   "571/8 dec",
        "team_b_score":   "263 & 261",
        "venue":          "Chinnaswamy Stadium, Bengaluru",
        "is_mock":        True,
    },
]


def get_match_accent(match):
    team_a     = match.get("team_a", "")
    team_b     = match.get("team_b", "")
    tournament = match.get("tournament", "")

    # RCB — red
    if "Royal Challengers" in team_a or "Royal Challengers" in team_b:
        return "red"

    # IPL — amber
    if tournament == TOURNAMENT_IPL:
        return "amber"

    # India bilateral — blue
    if tournament in [TOURNAMENT_INDIA_TEST, TOURNAMENT_INDIA_ODI, TOURNAMENT_INDIA_T20]:
        return "blue"

    # ICC tournaments (World Cups, CT, WTC) — purple
    return "purple"


def _clean_team_name(raw):
    """Remove bracket shortcode — 'Gujarat Titans [GT]' → 'Gujarat Titans'"""
    if '[' in raw:
        return raw[:raw.index('[')].strip()
    return raw.strip()

def _clean_team_short(raw):
    """Extract shortcode — 'Gujarat Titans [GT]' → 'GT'"""
    if '[' in raw and ']' in raw:
        return raw[raw.index('[')+1:raw.index(']')]
    return raw[:3].upper()

def _detect_tournament(series):
    """Detect tournament type from series name."""
    s = series.lower()
    if 'indian premier league' in s or 'ipl' in s:
        return TOURNAMENT_IPL
    if 't20 world cup' in s:
        return TOURNAMENT_T20_WC
    if 'odi world cup' in s or 'cricket world cup' in s:
        return TOURNAMENT_ODI_WC
    if 'champions trophy' in s:
        return TOURNAMENT_CT
    if 'world test championship' in s or 'wtc' in s:
        return TOURNAMENT_WTC
    if 'india' in s:
        # Check if it's a bilateral India series
        match_type = s
        if 'test' in match_type:
            return TOURNAMENT_INDIA_TEST
        if 'odi' in match_type:
            return TOURNAMENT_INDIA_ODI
        return TOURNAMENT_INDIA_T20
    return None   # not a tournament we track

def _parse_real_match(raw):
    """Parse a single match from real CricAPI response."""
    team_a_raw = raw.get('t1', '')
    team_b_raw = raw.get('t2', '')
    series     = raw.get('series', '')
    ms         = raw.get('ms', '')       # 'live', 'fixture', 'result'
    t1s        = raw.get('t1s', '')      # team 1 score e.g. '28/0 (2.3)'
    t2s        = raw.get('t2s', '')

    team_a       = _clean_team_name(team_a_raw)
    team_b       = _clean_team_name(team_b_raw)
    team_a_short = _clean_team_short(team_a_raw)
    team_b_short = _clean_team_short(team_b_raw)

    # Map ms to our status
    if ms == 'live':
        status = 'live'
    elif ms == 'result':
        status = 'completed'
    else:
        status = 'upcoming'

    match = {
        'match_id':     raw.get('id', ''),
        'tournament':   _detect_tournament(series) or series,
        'series':       series,
        'status':       status,
        'team_a':       team_a,
        'team_a_short': team_a_short,
        'team_b':       team_b,
        'team_b_short': team_b_short,
        'venue':        '',
        'is_mock':      False,
    }

    if status == 'live':
        # Determine who is batting based on which score exists
        if t1s and t2s:
            # Both have scores — second innings, t2 is batting
            match['team_batting']  = team_b
            match['team_bowling']  = team_a
            score_str = t2s
            target_str = t1s
            t_runs, t_wkts, t_overs, t_balls = _parse_score_string(target_str)
            match['target'] = t_runs + 1
        elif t1s:
            # Only t1 has score — t1 is batting, first innings
            match['team_batting']  = team_a
            match['team_bowling']  = team_b
            score_str = t1s
            match['target'] = 0
        elif t2s:
            # Only t2 has score — t2 is batting
            match['team_batting']  = team_b
            match['team_bowling']  = team_a
            score_str = t2s
            match['target'] = 0
        else:
            match['team_batting']  = team_a
            match['team_bowling']  = team_b
            score_str = ''
            match['target'] = 0

        runs, wickets, overs, balls = _parse_score_string(score_str)
        match['score']        = runs
        match['wickets']      = wickets
        match['overs']        = overs
        match['balls_bowled'] = balls
        match['crr']          = round((runs / balls * 6), 2) if balls > 0 else 0
        match['rrr']          = round(((match['target'] - runs) / max(120 - balls, 1) * 6), 2) if match['target'] > 0 else 0
        match['commentary']   = raw.get('status', '')
        match['ball_history'] = []
        match['batting_players']  = []
        match['bowling_players']  = []
    
    # Parse team logos from teamInfo
    team_info = raw.get('teamInfo', [])
    logos = {}
    for ti in team_info:
        logos[ti.get('name', '')] = ti.get('img', '')

    match['team_a_logo'] = logos.get(team_a, '')
    match['team_b_logo'] = logos.get(team_b, '')

    # Also grab from top level t1img/t2img if available (cricScore response)
    if not match['team_a_logo']:
        match['team_a_logo'] = raw.get('t1img', '')
    if not match['team_b_logo']:
        match['team_b_logo'] = raw.get('t2img', '')
    return match


def _parse_score_string(score_str):
    """
    Parse '28/0 (2.3)' into (runs, wickets, overs, balls_bowled)
    Returns (0, 0, '0.0', 0) if parsing fails.
    """
    try:
        if not score_str:
            return 0, 0, '0.0', 0

        # Split score and overs
        parts = score_str.strip().split(' ')
        score_part = parts[0]   # '28/0'
        overs_part = parts[1].strip('()') if len(parts) > 1 else '0.0'  # '2.3'

        runs, wickets = score_part.split('/')
        runs    = int(runs)
        wickets = int(wickets)

        # Convert overs to balls
        over_parts   = overs_part.split('.')
        full_overs   = int(over_parts[0])
        extra_balls  = int(over_parts[1]) if len(over_parts) > 1 else 0
        balls_bowled = full_overs * 6 + extra_balls

        return runs, wickets, overs_part, balls_bowled

    except Exception:
        return 0, 0, '0.0', 0


def _format_match_time(dt_str):
    """Format ISO datetime string to readable time."""
    try:
        from datetime import datetime, timezone, timedelta
        dt  = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        ist = dt + timedelta(hours=5, minutes=30)
        return ist.strftime('%b %d, %I:%M %p IST')
    except Exception:
        return dt_str


def get_all_matches(use_mock=False):
    """Return all matches grouped by status."""
    if use_mock:
        live      = [m for m in MOCK_MATCHES if m["status"] == "live"]
        upcoming  = [m for m in MOCK_MATCHES if m["status"] == "upcoming"]
        completed = [m for m in MOCK_MATCHES if m["status"] == "completed"]
        for m in live + upcoming + completed:
            m["accent"] = get_match_accent(m)
        return {"live": live, "upcoming": upcoming, "completed": completed}

    data = _make_request("cricScore")
    if not data:
        return get_all_matches(use_mock=True)

    raw_matches = data.get('data', [])

    live, upcoming, completed = [], [], []

    for raw in raw_matches:
        tournament = _detect_tournament(raw.get('series', ''))

        # Only include IPL and India/ICC matches we care about
        if tournament is None:
            continue

        match = _parse_real_match(raw)

        if match['status'] == 'live':
            live.append(match)
        elif match['status'] == 'upcoming':
            upcoming.append(match)
        else:
            completed.append(match)

    # If nothing found fall back to mock
    if not live and not upcoming and not completed:
        return get_all_matches(use_mock=True)

    return {"live": live, "upcoming": upcoming, "completed": completed}


def get_match_by_id(match_id, use_mock=False):
    # Check mock IDs first
    for match in MOCK_MATCHES:
        if match["match_id"] == match_id:
            match["accent"] = get_match_accent(match)
            return match

    if use_mock:
        return None

    # Get detailed match info
    info_data = _make_request("match_info", params={"id": match_id})
    if not info_data or not info_data.get('data'):
        return None

    raw = info_data['data']

    # Build a unified raw dict that _parse_real_match understands
    # cricScore fields aren't in match_info so we reconstruct them
    series = raw.get('name', '')
    teams  = raw.get('teams', [])

    team_info = raw.get('teamInfo', [])
    logos = {ti['name']: ti.get('img', '') for ti in team_info}

    # Determine status
    if raw.get('matchEnded'):
        ms = 'result'
    elif raw.get('matchStarted'):
        ms = 'live'
    else:
        ms = 'fixture'

    # Get scores from score array if available
    scores     = raw.get('score', [])
    t1s        = ''
    t2s        = ''
    if scores:
        t1s = f"{scores[0].get('r',0)}/{scores[0].get('w',0)} ({scores[0].get('o',0)})" if len(scores) > 0 else ''
        t2s = f"{scores[1].get('r',0)}/{scores[1].get('w',0)} ({scores[1].get('o',0)})" if len(scores) > 1 else ''

    reconstructed = {
        'id':          match_id,
        't1':          f"{teams[0]} [{team_info[0]['shortname']}]" if team_info else (teams[0] if teams else ''),
        't2':          f"{teams[1]} [{team_info[1]['shortname']}]" if len(team_info) > 1 else (teams[1] if len(teams) > 1 else ''),
        't1s':         t1s,
        't2s':         t2s,
        'ms':          ms,
        'series':      series,
        'status':      raw.get('status', ''),
        'venue':       raw.get('venue', ''),
        'dateTimeGMT': raw.get('dateTimeGMT', ''),
        'teamInfo':    team_info,
        't1img':       logos.get(teams[0], '') if teams else '',
        't2img':       logos.get(teams[1], '') if len(teams) > 1 else '',
    }

    match = _parse_real_match(reconstructed)
    match['venue'] = raw.get('venue', '')
    return match
    

# Legacy — kept for compatibility
MOCK_MATCH_DATA = MOCK_MATCHES[0]


def get_live_match(use_mock=True):
    return MOCK_MATCH_DATA if use_mock else None


def get_match_accent(match):
    """
    Returns the accent color key for a match.
    Used by frontend to apply correct theme.
    """
    team_a = match.get("team_a", "")
    team_b = match.get("team_b", "")
    tournament = match.get("tournament", "")

    # RCB check — red accent
    if "Royal Challengers" in team_a or "Royal Challengers" in team_b:
        return "red"

    # IPL — amber
    if tournament == TOURNAMENT_IPL:
        return "amber"
    
    # India bilateral matches — blue
    if tournament in [TOURNAMENT_INDIA_TEST, TOURNAMENT_INDIA_ODI, TOURNAMENT_INDIA_T20]:
        return "blue"

    # Everything else — purple
    return "purple"

