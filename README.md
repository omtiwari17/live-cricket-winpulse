# WinPulse - Live Cricket Win Probability Dashboard

A real-time cricket dashboard built with Django. Shows live IPL and India match scores with a WASP-inspired win probability algorithm that updates as the match progresses.

**Live:** [live-cricket-winpulse.onrender.com](https://live-cricket-winpulse.onrender.com)

---

## What It Does

- Shows live scores for IPL matches and India international matches
- Calculates win probability ball by ball using a custom algorithm
- Displays CRR, RRR, balls left, target, and over progress
- Filters matches by tournament (IPL / India / World Cup) and status (Live / Upcoming / Results)
- Color-coded by tournament IPL in amber, India bilateral in blue, ICC tournaments in purple, RCB in red
- Admin panel to toggle which matches appear on the dashboard

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django |
| Frontend | Django Templates + Tailwind CSS |
| Auto-refresh | JavaScript `setInterval` polling |
| Data | CricketData.org API (CricAPI) |
| Deployment | Render (free tier) |
| Static files | Whitenoise |

---

## Project Structure

```
live-cricket-winpulse/
│
├── dashboard/
│   ├── templates/dashboard/
│   │   ├── base.html           # shared header/layout
│   │   ├── match_list.html     # index page — all matches
│   │   └── match_detail.html   # detail page — single match
│   │
│   ├── static/dashboard/
│   │   ├── css/
│   │   │   ├── base.css        # shared variables and components
│   │   │   ├── match_list.css  # index page styles
│   │   │   └── match_detail.css# detail page styles
│   │   └── js/
│   │       ├── list.js         # auto-refresh for listing page
│   │       └── detail.js       # auto-refresh for detail page
│   │
│   ├── algorithm.py            # win probability calculation
│   ├── api_client.py           # CricketData API + key rotation
│   ├── views.py                # Django views
│   ├── urls.py                 # URL routing
│   ├── models.py               # Match model with is_active toggle
│   └── admin.py                # Admin panel configuration
│
├── winpulse/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── .env                        # secrets — never committed
├── build.sh                    # Render build script
├── requirements.txt
└── manage.py
```

---

## Win Probability Algorithm

The algorithm is WASP-inspired and lives entirely in `dashboard/algorithm.py`. It takes four inputs and returns a probability for both teams:

```python
calculate_win_probability(
    target=186,
    runs=142,
    wickets=3,
    balls_bowled=92
)
# → {'batting_team': 38.5, 'bowling_team': 61.5}
```

**Factors considered:**
- Required Run Rate vs Current Run Rate
- Wickets lost (weighted by balls remaining early wickets penalised more)
- Momentum (scoring rate relative to required rate)
- Pressure factor (when RRR exceeds 2 runs per ball)

Win probability is only calculated in the second innings when a target exists. First innings shows `1st INN`.

---

## API Strategy

Uses [CricketData.org](https://cricketdata.org) (formerly CricAPI) free tier.

**Limits:** 100 API calls per day per account

**Key rotation:** Multiple accounts configured when one key hits its daily limit, the system automatically rotates to the next key.

**Smart polling intervals:**
```
Active play     → 15s
Between balls   → 30s
No live match   → 60s
Listing page    → 60s
```

At 30s polling a full 3.5 hour IPL match uses approximately 150-200 API calls within two key's daily limit.

**Coverage:**
- All IPL matches
- India bilateral series (Tests, ODIs, T20Is)
- ICC T20 World Cup, ODI World Cup, Champions Trophy, WTC Final

**Note:** Player scorecard and ball-by-ball data require a paid CricAPI plan. The free tier provides live score summaries only.

---

## Local Setup

**Requirements:** Python 3.11+

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/live-cricket-winpulse.git
cd live-cricket-winpulse

# Virtual environment
python -m venv venv
venv\Scripts\activate  # Mac: source venv/bin/activate 

# Dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env and add your keys

# Database
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run
python manage.py runserver
```

Open `http://127.0.0.1:8000`

---

## Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-django-secret-key
DEBUG=True

CRICKET_API_KEY_1=your-first-cricketdata-key
CRICKET_API_KEY_2=your-second-cricketdata-key
CRICKET_API_KEY_3=your-third-cricketdata-key
```

**Important:** Never commit `.env` to GitHub. It is already in `.gitignore`.

---

## Deployment (Render)

The app is deployed on [Render](https://render.com) free tier.

**Build command:** `./build.sh`
**Start command:** `gunicorn winpulse.wsgi:application`

Add environment variables in the Render dashboard under **Environment**. Do not put secrets in `render.yaml`.

**Note:** Render free tier spins down after 15 minutes of inactivity. First visit after idle takes ~30 seconds to cold start. This is expected behaviour.

---

## Admin Panel

Go to `/admin/` to manage matches.

The `Match` model has an `is_active` toggle uncheck any match to hide it from the dashboard without deleting it. Useful for controlling which matches appear and avoiding unnecessary API calls during off-season.

---

## Development vs Production

The codebase uses `use_mock` flags to switch between real and mock data:

```python
# views.py
matches = get_all_matches(use_mock=False)   # True = mock data
```

Set `use_mock=True` while building to avoid burning real API calls. Switch to `False` only when a live match is scheduled and you're ready to test with real data.

---

## Running Tests

```bash
python manage.py test
```

Tests cover the win probability algorithm — easy chase, tough chase, balanced position, match won, match lost.

---

## License

MIT