def calculate_win_probability(target, runs, wickets, balls_bowled):
    """
    Calculate win probability for the batting team.

    Args:
        target      (int): Runs needed to win
        runs        (int): Runs scored so far
        wickets     (int): Wickets lost so far
        balls_bowled(int): Balls faced so far

    Returns:
        dict: {
            'batting_team': float (0-100),
            'bowling_team': float (0-100)
        }
    """

    # ── Edge cases ──────────────────────────────────────────────────
    if runs >= target:
        return {'batting_team': 100.0, 'bowling_team': 0.0}

    balls_left = 120 - balls_bowled
    runs_needed = target - runs

    if balls_left <= 0 or wickets >= 10:
        return {'batting_team': 0.0, 'bowling_team': 100.0}

    # ── Core calculations ────────────────────────────────────────────
    rrr = (runs_needed / balls_left) * 6      # Required Run Rate
    crr = (runs / balls_bowled) * 6 if balls_bowled > 0 else 0  # Current Run Rate

    # ── Base probability from RRR ────────────────────────────────────
    # At RRR = 6 (par), base = 50%
    # Each run above par RPO drops probability
    # Each run below par RPO raises probability
    par_rpo = 8.0   # average T20 scoring rate
    base = 50 - ((rrr - par_rpo) * 6)

    # ── Wicket penalty ───────────────────────────────────────────────
    # Each wicket reduces probability
    # Early wickets hurt more (multiplied by balls_left factor)
    wicket_weight = 1 + (balls_left / 120)     # ranges from 1.0 to 2.0
    wicket_penalty = wickets * 5.5 * wicket_weight
    base -= wicket_penalty

    # ── Momentum factor ──────────────────────────────────────────────
    # If scoring faster than needed, batting team has momentum
    momentum = (crr - rrr) * 2.5
    base += momentum

    # ── Pressure factor ──────────────────────────────────────────────
    # As balls run out and runs still needed, pressure increases sharply
    pressure_ratio = runs_needed / max(balls_left, 1)
    if pressure_ratio > 2:      # need more than 2 runs per ball
        base -= (pressure_ratio - 2) * 10

    # ── Clamp between 3 and 97 ───────────────────────────────────────
    # Never show 0% or 100% unless match is actually over
    batting_probability = round(min(97, max(3, base)), 1)
    bowling_probability = round(100 - batting_probability, 1)

    return {
        'batting_team': batting_probability,
        'bowling_team': bowling_probability
    }
