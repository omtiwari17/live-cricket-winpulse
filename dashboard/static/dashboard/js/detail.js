// ── WinPulse — detail.js ────────────────────────────────────────────────────
'use strict';

const API_BASE      = '/api/match/';
const POLL_ACTIVE   = 5000;
const POLL_NORMAL   = 15000;
const POLL_BREAK    = 30000;

let pollTimer       = null;
let countdownTimer  = null;
let currentInterval = POLL_NORMAL;
let countdown       = 15;
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
  updateBallTimeline(data);
  updateCommentary(data);
  updateScorecard(data);

  const mockEl = document.getElementById('mock-indicator');
  if (mockEl) mockEl.style.display = data.is_mock ? 'inline-flex' : 'none';

  setText('last-updated', `Updated ${new Date().toLocaleTimeString()}`);
  flashEl('scoreboard-card');
  flashEl('stats-card');
}

// ── Accent ────────────────────────────────────────────────────────────────────
function applyAccent(accent) {
  ['scoreboard-card', 'commentary-card', 'scorecard-card'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.setAttribute('data-accent', accent);
  });
}

// ── Scoreboard ────────────────────────────────────────────────────────────────
function updateScoreboard(data) {
  const isLive   = data.status === 'live';
  const score    = data.score    ?? 0;
  const wickets  = data.wickets  ?? 0;
  const overs    = data.overs    || '0.0';
  const target   = data.target   || 0;
  const batProb  = data.batting_win_prob;
  const bowlProb = data.bowling_win_prob;

  setText('team-batting-name', data.team_batting || data.team_a || '—');
  setText('team-bowling-name', data.team_bowling || data.team_b || '—');

  if (isLive) {
    setText('batting-score',  `${score}/${wickets}`);
    setText('batting-detail', `${overs} OV`);
    setText('bowling-score',  target > 0 ? String(target) : '—');
    setText('bowling-detail', target > 0 ? 'TARGET' : 'BOWLING');
  } else {
    setText('batting-score',  data.team_a_score || '—');
    setText('batting-detail', '');
    setText('bowling-score',  data.team_b_score || '—');
    setText('bowling-detail', '');
  }

  setText('center-overs', `${overs} OV`);

  if (batProb !== null && batProb !== undefined) {
    setText('batting-win-pct',  `${batProb}%`);
    setText('bowling-win-pct',  `${bowlProb}%`);
    setText('prob-display',     `${batProb}% — ${bowlProb}%`);
    setText('prob-left-label',  data.team_bowling || data.team_b || '—');
    setText('prob-right-label', data.team_batting || data.team_a || '—');
    const bar = document.getElementById('prob-bar');
    if (bar) bar.style.width = `${batProb}%`;
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

  setText('stat-target', target > 0 ? target : '—');
  setText('stat-needed', target > 0 ? needed  : '—');
  setText('stat-balls',  ballsLeft);
  setText('stat-crr',    crr.toFixed(2));
  setText('stat-rrr',    rrr.toFixed(2));

  const rrrEl = document.getElementById('stat-rrr');
  if (rrrEl) {
    rrrEl.className = 'stat-val ' + (rrr > 12 ? 'danger' : rrr > 9 ? 'warn' : 'good');
  }

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

  setText('over-footer', `${oversCompleted} of ${totalOvers} overs complete · ${ballsThisOver} ball(s) this over`);
}

// ── Ball timeline ─────────────────────────────────────────────────────────────
function updateBallTimeline(data) {
  const row    = document.getElementById('ball-row');
  const footer = document.getElementById('ball-footer');
  if (!row) return;

  const history = data.ball_history || [];
  row.innerHTML = '';

  let overRuns    = 0;
  let overWickets = 0;

  history.forEach(ball => {
    const chip = document.createElement('div');
    const isW  = ball === 'W' || ball === 'w';
    const val  = parseInt(ball);

    let cls = 'ball-chip ';
    if (isW)            { cls += 'b-wicket'; overWickets++; }
    else if (val === 0) { cls += 'b-dot'; }
    else if (val === 4) { cls += 'b-four'; overRuns += 4; }
    else if (val === 6) { cls += 'b-six';  overRuns += 6; }
    else                { cls += 'b-run';  overRuns += val; }

    chip.className   = cls;
    chip.textContent = isW ? 'W' : (val === 0 ? '•' : val);
    row.appendChild(chip);
  });

  for (let i = history.length; i < 6; i++) {
    const chip = document.createElement('div');
    chip.className   = 'ball-chip b-empty';
    chip.textContent = '—';
    row.appendChild(chip);
  }

  if (footer) {
    footer.textContent = history.length
      ? `This over: ${overRuns} run${overRuns !== 1 ? 's' : ''} · ${overWickets} wicket${overWickets !== 1 ? 's' : ''}`
      : 'Over not started yet';
  }
}

// ── Commentary ────────────────────────────────────────────────────────────────
function updateCommentary(data) {
  setText('commentary-text', data.commentary || data.result || 'No commentary available.');
}

// ── Scorecard ─────────────────────────────────────────────────────────────────
function updateScorecard(data) {
  updateBattingTable(data.batting_players || []);
  updateBowlingTable(data.bowling_players || []);
}

function updateBattingTable(players) {
  const tbody = document.getElementById('batting-tbody');
  if (!tbody || !players.length) return;

  tbody.innerHTML = players.map(p => {
    const isBatting = p.status === 'batting';
    const srClass   = p.sr >= 150 ? 'sr-good' : p.sr >= 100 ? 'sr-ok' : 'sr-low';
    return `
      <tr>
        <td>
          <div class="player-name">
            ${isBatting ? '<span class="batting-indicator"></span>' : ''}${p.name}
          </div>
          <div class="player-status">${isBatting ? 'Batting' : p.status || '—'}</div>
        </td>
        <td class="num" style="font-weight:700;font-size:0.92rem;">${p.runs ?? '—'}</td>
        <td class="num">${p.balls ?? '—'}</td>
        <td class="num">${p.fours ?? '—'}</td>
        <td class="num">${p.sixes ?? '—'}</td>
        <td class="num ${srClass}">${p.sr != null ? p.sr.toFixed(1) : '—'}</td>
      </tr>`;
  }).join('');
}

function updateBowlingTable(players) {
  const tbody = document.getElementById('bowling-tbody');
  if (!tbody || !players.length) return;

  tbody.innerHTML = players.map(p => {
    const ecoClass = p.economy <= 7 ? 'sr-good' : p.economy <= 9 ? 'sr-ok' : 'sr-low';
    return `
      <tr>
        <td><div class="player-name">${p.name}</div></td>
        <td class="num">${p.overs   ?? '—'}</td>
        <td class="num">${p.runs    ?? '—'}</td>
        <td class="num" style="font-weight:700;">${p.wickets ?? '—'}</td>
        <td class="num ${ecoClass}">${p.economy != null ? p.economy.toFixed(2) : '—'}</td>
      </tr>`;
  }).join('');
}

// ── Tab switching ─────────────────────────────────────────────────────────────
function switchTab(tab) {
  document.querySelectorAll('.scorecard-tab').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tab);
  });
  document.getElementById('tab-batting').style.display = tab === 'batting' ? 'block' : 'none';
  document.getElementById('tab-bowling').style.display = tab === 'bowling' ? 'block' : 'none';
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function flashEl(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('flash');
  void el.offsetWidth;
  el.classList.add('flash');
}