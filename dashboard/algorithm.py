def get_format_overs(tournament="", series=""):
    """
    Determine the total overs for a match based on its tournament name or series description.
    Returns 20 (T20), 50 (ODI), or 90 (Test).
    """
    text = f"{tournament} {series}".lower()
    if "test" in text or "wtc" in text:
        return 90
    if "odi" in text or "champions trophy" in text or "50" in text or ("world cup" in text and "t20" not in text):
        return 50
    return 20


def calculate_win_probability(target, runs, wickets, balls_bowled, total_overs=20, first_innings=False, **kwargs):
    """
    Calculate win probability for the batting team.

    Args:
        target       (int): Runs needed to win
        runs         (int): Runs scored so far
        wickets      (int): Wickets lost so far
        balls_bowled (int): Balls faced so far
        total_overs  (int): Total overs in match format (20 for T20, 50 for ODI, 90 for Test)
        first_innings(bool): True if match is currently in first innings
        **kwargs          : Tolerates extra parameters without raising TypeError

    Returns:
        dict: {
            'batting_team': float (0-100) or None,
            'bowling_team': float (0-100) or None
        }
    """

    # ── First innings or missing target ─────────────────────────────
    if first_innings or not target or target <= 0:
        return {'batting_team': None, 'bowling_team': None}

    # ── Edge cases ──────────────────────────────────────────────────
    if runs >= target:
        return {'batting_team': 100.0, 'bowling_team': 0.0}

    total_balls = max(total_overs * 6, 1)
    balls_left = max(0, total_balls - balls_bowled)
    runs_needed = target - runs

    if balls_left <= 0 or wickets >= 10:
        return {'batting_team': 0.0, 'bowling_team': 100.0}

    # ── Core calculations ────────────────────────────────────────────
    rrr = (runs_needed / balls_left) * 6 if balls_left > 0 else 999.0      # Required Run Rate
    crr = (runs / balls_bowled) * 6 if balls_bowled > 0 else 0.0           # Current Run Rate

    # ── Base probability from RRR ────────────────────────────────────
    # Scale par scoring rate, sensitivity, and wicket penalty based on format
    if total_overs >= 90:
        par_rpo = 3.5
        par_multiplier = 6.0
        w_factor = 2.0
    elif total_overs >= 50:
        par_rpo = 5.5
        par_multiplier = 7.0
        w_factor = 3.0
    else:
        par_rpo = 8.0   # average T20 scoring rate
        par_multiplier = 6.0
        w_factor = 5.5

    base = 50.0 - ((rrr - par_rpo) * par_multiplier)

    # ── Wicket penalty ───────────────────────────────────────────────
    # Each wicket reduces probability
    # Early wickets hurt more (multiplied by balls_left factor)
    wicket_weight = 1.0 + (balls_left / total_balls)     # ranges from 1.0 to 2.0
    wicket_penalty = wickets * w_factor * wicket_weight
    base -= wicket_penalty

    # ── Momentum factor ──────────────────────────────────────────────
    # If scoring faster than needed, batting team has momentum
    momentum = (crr - rrr) * 2.5
    base += momentum

    # ── Pressure factor ──────────────────────────────────────────────
    # As balls run out and runs still needed, pressure increases sharply
    pressure_ratio = runs_needed / max(balls_left, 1)
    if total_overs >= 90:
        pressure_threshold = 0.83
    elif total_overs >= 50:
        pressure_threshold = 1.33
    else:
        pressure_threshold = 2.0

    if pressure_ratio > pressure_threshold:
        base -= (pressure_ratio - pressure_threshold) * 10.0

    # Dynamic floor based on match situation
    if total_overs >= 90:
        floor = 1.0 if rrr > 8.0 else (2.0 if rrr > 6.0 else 3.0)
    elif total_overs >= 50:
        floor = 1.0 if rrr > 12.0 else (2.0 if rrr > 10.0 else 3.0)
    else:
        if rrr > 18.0:
            floor = 1.0      # nearly impossible
        elif rrr > 15.0:
            floor = 2.0      # very difficult
        else:
            floor = 3.0      # standard floor

    batting_probability = round(min(97.0, max(floor, base)), 1)
    bowling_probability = round(100.0 - batting_probability, 1)

    return {
        'batting_team': batting_probability,
        'bowling_team': bowling_probability
    }
