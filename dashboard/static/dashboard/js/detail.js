// ── WinPulse — detail.js ────────────────────────────────────────────────────
'use strict';

const API_BASE      = '/api/match/';
const POLL_ACTIVE   = 15000;
const POLL_NORMAL   = 30000;
const POLL_BREAK    = 60000;

let pollTimer       = null;
let countdownTimer  = null;
let currentInterval = POLL_NORMAL;
let countdown       = 30;
let lastBalls       = -1;

// ── Boot ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (typeof MATCH_ID === 'undefined' || !MATCH_ID) {
    console.error('[WinPulse] No MATCH_ID found.');
    return;
  }
  fetchAndUpdate();
});

// ── Fetch ─────────────────────────────────────────────────────────────────────
async function fetchAndUpdate() {
  try {
    const res  = await fetch(`${API_BASE}${MATCH_ID}/`);
    const data = await res.json();
    updateAll(data);
    scheduleNext(data);
  } catch (err) {
    console.error('[WinPulse] Fetch failed:', err);
    scheduleNext(null);
  }
}

// ── Smart polling ─────────────────────────────────────────────────────────────
function scheduleNext(data) {
  clearTimeout(pollTimer);
  clearInterval(countdownTimer);

  if (!data || data.status !== 'live') {
    currentInterval = POLL_BREAK;
  } else if (data.balls_bowled !== lastBalls) {
    currentInterval = POLL_ACTIVE;
    lastBalls = data.balls_bowled;
  } else {
    currentInterval = POLL_NORMAL;
  }

  countdown = Math.floor(currentInterval / 1000);
  updateCountdown();

  countdownTimer = setInterval(() => {
    countdown--;
    updateCountdown();
    if (countdown <= 0) clearInterval(countdownTimer);
  }, 1000);

  pollTimer = setTimeout(fetchAndUpdate, currentInterval);
}

function updateCountdown() {
  setText('next-poll', `Next refresh in ${countdown}s`);
}

// ── Main update ───────────────────────────────────────────────────────────────
function updateAll(data) {
  applyAccent(data.accent || 'blue');
  updateScoreboard(data);
  updateStats(data);
  updateOverDots(data);
  updateCommentary(data);
  updateVenue(data);

  const mockEl = document.getElementById('mock-indicator');
  if (mockEl) mockEl.style.display = data.is_mock ? 'inline-flex' : 'none';

  setText('last-updated', `Updated ${new Date().toLocaleTimeString()}`);
  flashEl('scoreboard-card');
  flashEl('stats-card');
}

// ── Accent ────────────────────────────────────────────────────────────────────
function applyAccent(accent) {
  ['scoreboard-card', 'commentary-card'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.setAttribute('data-accent', accent);
  });
}

// ── Scoreboard ────────────────────────────────────────────────────────────────
function updateScoreboard(data) {
  const isLive      = data.status === 'live';
  const score       = data.score    ?? 0;
  const wickets     = data.wickets  ?? 0;
  const overs       = data.overs    || '0.0';
  const target      = data.target   || 0;
  const batProb     = data.batting_win_prob;
  const bowlProb    = data.bowling_win_prob;
  const firstInnings = data.first_innings || false;

  // Team names
  setText('team-batting-name', data.team_batting || data.team_a || '—');
  setText('team-bowling-name', data.team_bowling || data.team_b || '—');

  // Team logos
  setLogo('team-batting-logo', data.team_a_logo || data.team_batting_logo || '');
  setLogo('team-bowling-logo', data.team_b_logo || data.team_bowling_logo || '');

  // Scores
  if (isLive) {
    setText('batting-score',  `${score}/${wickets}`);
    setText('batting-detail', `${overs} OV`);
    if (target > 0) {
      setText('bowling-score',  String(target));
      setText('bowling-detail', 'TARGET');
    } else {
      setText('bowling-score',  '1st INN');
      setText('bowling-detail', 'BOWLING');
    }
  } else {
    setText('batting-score',  data.team_a_score || '—');
    setText('batting-detail', '');
    setText('bowling-score',  data.team_b_score || '—');
    setText('bowling-detail', '');
  }

  setText('center-overs', `${overs} OV`);

  // Win probability
  if (batProb !== null && batProb !== undefined) {
    setText('batting-win-pct',  `${batProb}%`);
    setText('bowling-win-pct',  `${bowlProb}%`);
    setText('prob-display',     `${batProb}% — ${bowlProb}%`);
    setText('prob-left-label',  data.team_bowling || data.team_b || '—');
    setText('prob-right-label', data.team_batting || data.team_a || '—');
    const bar = document.getElementById('prob-bar');
    if (bar) bar.style.width = `${batProb}%`;

  } else if (firstInnings) {
    setText('batting-win-pct',  '1st INN');
    setText('bowling-win-pct',  'BOWLING');
    setText('prob-display',     'Available after 1st innings');
    setText('prob-left-label',  data.team_bowling || data.team_b || '—');
    setText('prob-right-label', data.team_batting || data.team_a || '—');
    const bar = document.getElementById('prob-bar');
    if (bar) bar.style.width = '50%';

  } else {
    setText('batting-win-pct', '—');
    setText('bowling-win-pct', '—');
    setText('prob-display',    data.result || 'Match ended');
    const bar = document.getElementById('prob-bar');
    if (bar) bar.style.width = '50%';
  }
}

// ── Stats ─────────────────────────────────────────────────────────────────────
function updateStats(data) {
  const balls     = data.balls_bowled || 0;
  const score     = data.score        || 0;
  const target    = data.target       || 0;
  const crr       = data.crr          || 0;
  const rrr       = data.rrr          || 0;
  const ballsLeft = Math.max(0, 120 - balls);
  const needed    = Math.max(0, target - score);

  setText('stat-target', target > 0 ? target : '1st INN');
  setText('stat-needed', target > 0 ? needed  : '—');
  setText('stat-balls',  ballsLeft > 0 ? ballsLeft : '—');
  setText('stat-crr',    crr > 0 ? crr.toFixed(2) : '—');
  setText('stat-rrr',    rrr > 0 ? rrr.toFixed(2) : '—');

  // RRR color
  const rrrEl = document.getElementById('stat-rrr');
  if (rrrEl && rrr > 0) {
    rrrEl.className = 'stat-val ' + (rrr > 12 ? 'danger' : rrr > 9 ? 'warn' : 'good');
  }

  // CRR minibar
  const crrBar = document.getElementById('crr-bar');
  if (crrBar) crrBar.style.width = `${Math.min(100, (crr / 12) * 100)}%`;
}

// ── Over dots ─────────────────────────────────────────────────────────────────
function updateOverDots(data) {
  const balls          = data.balls_bowled || 0;
  const oversCompleted = Math.floor(balls / 6);
  const ballsThisOver  = balls % 6;
  const container      = document.getElementById('over-dots');
  if (!container) return;

  const isTest     = data.tournament && data.tournament.toLowerCase().includes('test');
  const totalOvers = isTest ? 90 : 20;

  container.innerHTML = '';
  for (let i = 0; i < totalOvers; i++) {
    const dot = document.createElement('div');
    dot.className = 'over-dot';
    if (i < oversCompleted)                              dot.classList.add('done');
    else if (i === oversCompleted && ballsThisOver > 0)  dot.classList.add('current');
    else                                                 dot.classList.add('upcoming');
    container.appendChild(dot);
  }

  setText('over-footer',
    `${oversCompleted} of ${totalOvers} overs complete · ${ballsThisOver} ball(s) this over`
  );
}

// ── Commentary ────────────────────────────────────────────────────────────────
function updateCommentary(data) {
  const text = data.commentary || data.result || data.status || 'No commentary available.';
  setText('commentary-text', text);
}

// ── Venue ─────────────────────────────────────────────────────────────────────
function updateVenue(data) {
  const venue = data.venue || '';
  const el    = document.getElementById('venue-card');
  if (!venue && el) {
    el.style.display = 'none';
    return;
  }
  if (el) el.style.display = 'flex';
  setText('venue-text', venue);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function setLogo(id, url) {
  const el = document.getElementById(id);
  if (!el) return;
  if (url) {
    el.src          = url;
    el.style.display = 'block';
  } else {
    el.style.display = 'none';
  }
}

function flashEl(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('flash');
  void el.offsetWidth;
  el.classList.add('flash');
}