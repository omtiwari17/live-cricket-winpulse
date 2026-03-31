// ── WinPulse — list.js ──────────────────────────────────────────────────────
'use strict';

const API_URL       = '/api/matches/';
const POLL_INTERVAL = 15000;

let pollTimer      = null;
let countdownTimer = null;
let countdown      = 15;
let allMatches     = { live: [], upcoming: [], completed: [] };

// Active filters
let activeStatus     = 'all';       // 'all' | 'live' | 'upcoming' | 'completed'
let activeTournament = 'all';       // 'all' | 'ipl' | 'india' | 'icc'

// ── Boot ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  bindFilters();
  fetchAndRender();
});

// ── Bind filter buttons ───────────────────────────────────────────────────────
function bindFilters() {
  // Status filters
  document.querySelectorAll('[data-status-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      activeStatus = btn.dataset.statusFilter;
      document.querySelectorAll('[data-status-filter]').forEach(b => b.classList.remove('filter-active'));
      btn.classList.add('filter-active');
      applyFiltersAndRender();
    });
  });

  // Tournament filters
  document.querySelectorAll('[data-tournament-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      activeTournament = btn.dataset.tournamentFilter;
      document.querySelectorAll('[data-tournament-filter]').forEach(b => b.classList.remove('filter-active'));
      btn.classList.add('filter-active');
      applyFiltersAndRender();
    });
  });
}

// ── Fetch ─────────────────────────────────────────────────────────────────────
async function fetchAndRender() {
  try {
    const res  = await fetch(API_URL);
    const data = await res.json();
    allMatches = data;
    applyFiltersAndRender();
  } catch (err) {
    console.error('[WinPulse] Fetch failed:', err);
    showError();
  } finally {
    scheduleNext();
  }
}

function scheduleNext() {
  clearTimeout(pollTimer);
  clearInterval(countdownTimer);

  countdown = POLL_INTERVAL / 1000;
  updateCountdown();

  countdownTimer = setInterval(() => {
    countdown--;
    updateCountdown();
    if (countdown <= 0) clearInterval(countdownTimer);
  }, 1000);

  pollTimer = setTimeout(fetchAndRender, POLL_INTERVAL);
}

function updateCountdown() {
  setText('next-poll', `Refreshes in ${countdown}s`);
}

// ── Filter logic ──────────────────────────────────────────────────────────────
function matchesTournamentFilter(match) {
  if (activeTournament === 'all') return true;
  const t = (match.tournament || '').toLowerCase();

  if (activeTournament === 'ipl')   return t === 'ipl';
  if (activeTournament === 'india') return t.includes('india');
  if (activeTournament === 'icc')   return (
    t.includes('world cup') || t.includes('champions trophy') || t.includes('wtc')
  );
  return true;
}

function applyFiltersAndRender() {
  const live      = allMatches.live      || [];
  const upcoming  = allMatches.upcoming  || [];
  const completed = allMatches.completed || [];

  // Filter by tournament
  const fLive      = live.filter(matchesTournamentFilter);
  const fUpcoming  = upcoming.filter(matchesTournamentFilter);
  const fCompleted = completed.filter(matchesTournamentFilter);

  // Show/hide sections based on status filter
  const showLive      = activeStatus === 'all' || activeStatus === 'live';
  const showUpcoming  = activeStatus === 'all' || activeStatus === 'upcoming';
  const showCompleted = activeStatus === 'all' || activeStatus === 'completed';

  const sectionLive      = document.getElementById('section-live');
  const sectionUpcoming  = document.getElementById('section-upcoming');
  const sectionCompleted = document.getElementById('section-completed');

  if (sectionLive)      sectionLive.style.display      = showLive      ? 'block' : 'none';
  if (sectionUpcoming)  sectionUpcoming.style.display  = showUpcoming  ? 'block' : 'none';
  if (sectionCompleted) sectionCompleted.style.display = showCompleted ? 'block' : 'none';

  if (showLive)      renderSection('live-grid',      fLive,      renderLiveCard);
  if (showUpcoming)  renderSection('upcoming-grid',  fUpcoming,  renderUpcomingCard);
  if (showCompleted) renderSection('completed-grid', fCompleted, renderCompletedCard);

  // Update counts
  setText('live-count',      `${fLive.length} match${fLive.length !== 1 ? 'es' : ''}`);
  setText('upcoming-count',  `${fUpcoming.length} match${fUpcoming.length !== 1 ? 'es' : ''}`);
  setText('completed-count', `${fCompleted.length} match${fCompleted.length !== 1 ? 'es' : ''}`);

  // Mock indicator
  const all    = [...live, ...upcoming, ...completed];
  const mockEl = document.getElementById('mock-indicator');
  if (mockEl) mockEl.style.display = all.some(m => m.is_mock) ? 'inline-flex' : 'none';

  setText('last-updated', `Updated ${new Date().toLocaleTimeString()}`);
}

// ── Render sections ───────────────────────────────────────────────────────────
function renderSection(gridId, matches, renderFn) {
  const grid = document.getElementById(gridId);
  if (!grid) return;

  if (!matches.length) {
    grid.innerHTML = '<div class="empty-state">No matches found</div>';
    return;
  }

  grid.innerHTML = matches.map(renderFn).join('');
}

// ── Tournament badge ──────────────────────────────────────────────────────────
function tournamentBadgeClass(tournament) {
  if (!tournament) return 'badge-ipl';
  const t = tournament.toLowerCase();
  if (t === 'ipl')           return 'badge-ipl';
  if (t.includes('india'))   return 'badge-india';
  return 'badge-icc';
}

// ── Live card ─────────────────────────────────────────────────────────────────
function renderLiveCard(match) {
  const accent     = match.accent || 'blue';
  const badgeClass = tournamentBadgeClass(match.tournament);
  const batProb    = match.batting_win_prob  || 50;
  const bowlProb   = match.bowling_win_prob  || 50;
  const score      = match.score !== undefined
    ? `${match.score}/${match.wickets} (${match.overs} ov)` : '—';

  return `
    <a class="match-card fade-up" href="/match/${match.match_id}/" data-accent="${accent}">
      <div class="card-top">
        <span class="badge ${badgeClass}">${match.tournament || 'Cricket'}</span>
        <div class="badge badge-live"><div class="live-dot"></div> LIVE</div>
      </div>
      <div class="card-teams">
        <div class="team-info">
          <div class="team-short">${match.team_bowling || match.team_b_short || '—'}</div>
          <div class="team-full">${match.team_bowling || match.team_b || '—'}</div>
          <div class="team-score">${bowlProb}%</div>
        </div>
        <div class="vs-divider">VS</div>
        <div class="team-info right">
          <div class="team-short">${match.team_batting || match.team_a_short || '—'}</div>
          <div class="team-full">${match.team_batting || match.team_a || '—'}</div>
          <div class="team-score">${batProb}%</div>
        </div>
      </div>
      <div class="mini-prob-wrap">
        <div class="mini-prob-label">
          <span>${match.team_bowling || match.team_b || '—'}</span>
          <span>${score}</span>
        </div>
        <div class="mini-prob-track">
          <div class="mini-prob-fill" style="width:${batProb}%"></div>
        </div>
      </div>
      <div class="card-footer">
        <span class="card-venue">${match.venue || '—'}</span>
        <span class="card-arrow">→</span>
      </div>
    </a>`;
}

// ── Upcoming card ─────────────────────────────────────────────────────────────
function renderUpcomingCard(match) {
  const accent     = match.accent || 'blue';
  const badgeClass = tournamentBadgeClass(match.tournament);

  return `
    <a class="match-card fade-up" href="/match/${match.match_id}/" data-accent="${accent}">
      <div class="card-top">
        <span class="badge ${badgeClass}">${match.tournament || 'Cricket'}</span>
        <div class="badge badge-upcoming">UPCOMING</div>
      </div>
      <div class="card-teams">
        <div class="team-info">
          <div class="team-short">${match.team_a_short || '—'}</div>
          <div class="team-full">${match.team_a || '—'}</div>
        </div>
        <div class="vs-divider">VS</div>
        <div class="team-info right">
          <div class="team-short">${match.team_b_short || '—'}</div>
          <div class="team-full">${match.team_b || '—'}</div>
        </div>
      </div>
      <div style="margin-bottom:14px;">
        <span class="match-time">${match.match_time || 'TBD'}</span>
      </div>
      <div class="card-footer">
        <span class="card-venue">${match.venue || '—'}</span>
        <span class="card-arrow">→</span>
      </div>
    </a>`;
}

// ── Completed card ────────────────────────────────────────────────────────────
function renderCompletedCard(match) {
  const accent     = match.accent || 'blue';
  const badgeClass = tournamentBadgeClass(match.tournament);

  return `
    <a class="match-card fade-up" href="/match/${match.match_id}/" data-accent="${accent}">
      <div class="card-top">
        <span class="badge ${badgeClass}">${match.tournament || 'Cricket'}</span>
        <div class="badge badge-completed">COMPLETED</div>
      </div>
      <div class="card-teams">
        <div class="team-info">
          <div class="team-short">${match.team_a_short || '—'}</div>
          <div class="team-full">${match.team_a || '—'}</div>
          <div style="font-family:var(--font-mono);font-size:0.72rem;color:var(--text-muted);margin-top:4px;">
            ${match.team_a_score || '—'}
          </div>
        </div>
        <div class="vs-divider">VS</div>
        <div class="team-info right">
          <div class="team-short">${match.team_b_short || '—'}</div>
          <div class="team-full">${match.team_b || '—'}</div>
          <div style="font-family:var(--font-mono);font-size:0.72rem;color:var(--text-muted);margin-top:4px;">
            ${match.team_b_score || '—'}
          </div>
        </div>
      </div>
      <div class="result-text">${match.result || '—'}</div>
      <div class="card-footer">
        <span class="card-venue">${match.venue || '—'}</span>
        <span class="card-arrow">→</span>
      </div>
    </a>`;
}

// ── Error ─────────────────────────────────────────────────────────────────────
function showError() {
  ['live-grid', 'upcoming-grid', 'completed-grid'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<div class="empty-state">Failed to load. Retrying...</div>';
  });
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}