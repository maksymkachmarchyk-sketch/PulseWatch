const API = ['localhost', '127.0.0.1'].includes(location.hostname) && location.port !== '8000' ? 'http://localhost:8000' : ''
const LS = localStorage
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
const saveTokens = t => { t.access && LS.setItem('pw_access', t.access); t.refresh && LS.setItem('pw_refresh', t.refresh) }
const logout = () => { LS.removeItem('pw_access'); LS.removeItem('pw_refresh'); location.href = '/login.html' }
const flat = d => typeof d === 'string' ? d : Object.entries(d || {}).map(([k, v]) => (['detail', 'error', 'message', 'non_field_errors'].includes(k) ? '' : k + ': ') + [].concat(v).join(' ')).join('\n')

function raw(p, o = {}, auth = true) {
  const h = { 'Content-Type': 'application/json' }
  if (auth && LS.getItem('pw_access')) h.Authorization = 'Bearer ' + LS.getItem('pw_access')
  return fetch(API + p, { ...o, headers: h, body: o.body && JSON.stringify(o.body) })
}
async function api(p, o = {}, auth = true) {
  let r = await raw(p, o, auth)
  if (r.status === 401 && auth && LS.getItem('pw_refresh')) {
    const rr = await raw('/api/accounts/token/refresh/', { method: 'POST', body: { refresh: LS.getItem('pw_refresh') } }, false)
    if (rr.ok) { saveTokens(await rr.json()); r = await raw(p, o, auth) } else logout()
  }
  const d = r.status === 204 ? null : await r.json().catch(() => null)
  if (!r.ok) throw new Error(flat(d) || 'Request failed (' + r.status + ')')
  return d
}

/* ---- helpers ---- */
const P = { pulse: 'M22 12h-4l-3 9L9 3l-3 9H2', home: 'M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z', alert: 'M12 8v5M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z', ok: 'M22 11.1V12a10 10 0 1 1-5.9-9.1M22 4 12 14l-3-3', clock: 'M12 6v6l4 2M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0z', list: 'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 3h6v4H9zM9 12h6M9 16h6', back: 'M19 12H5M12 19l-7-7 7-7', user: 'M20 21a8 8 0 0 0-16 0M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z', out: 'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9', trash: 'M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6', bell: 'M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0', edit: 'M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z' }
const ic = (n, s = 20) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${P[n]}"/></svg>`
const fmtInt = s => s % 3600 === 0 ? s / 3600 + 'h' : s % 60 === 0 ? s / 60 + 'm' : s + 's'
const fmtDate = d => new Date(d).toLocaleString([], { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit' })
const p95 = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.ceil(.95 * s.length) - 1] }
const errBox = m => `<div class="alert-box">${esc(m)}</div>`
const badge = (ok, t) => `<span class="badge ${ok ? 'ok' : 'bad'}">${t}</span>`
const stat = (label, value, icon, tone, pct = 100) => `<div class="stat ${tone}"><div class="stat-top"><div><div class="lbl">${label}</div><div class="val">${value}</div></div><div class="tile">${ic(icon)}</div></div><div class="bar"><i style="width:${Math.min(100, Math.max(4, pct))}%"></i></div></div>`

/* ---- app shell (sidebar) — call on every protected page; returns <main> ---- */
function shell(active) {
  if (!LS.getItem('pw_refresh')) { location.href = '/login.html'; return }
  const link = (href, key, icon, text) => `<a href="${href}" class="side-link ${active === key ? 'on' : ''}"><span class="tile">${ic(icon)}</span>${text}</a>`
  document.getElementById('app').innerHTML = `<div class="shell"><aside>
    <div class="brand"><span class="logo">${ic('pulse')}</span><div><b>PULSEWATCH</b><small>monitor everything</small></div></div>
    <div class="sec-lbl">MAIN</div>${link('/index.html', 'home', 'home', 'Dashboard')}${link('/monitors.html', 'monitors', 'pulse', 'Monitors')}
    <div class="sec-lbl">ACTIVITY</div>${link('/incidents.html', 'incidents', 'alert', 'Incidents')}${link('/notifications.html', 'notifications', 'bell', 'Notifications')}
    <div class="grow"></div><div class="account"><a href="/profile.html" class="d-flex align-items-center gap-2 flex-grow-1 text-decoration-none" style="min-width:0;color:inherit"><span class="tile">${ic('user')}</span><div style="min-width:0"><b id="me-name">Account</b><small id="me-mail">Profile</small></div></a>
    <button class="btn btn-sm text-secondary" aria-label="Sign out" onclick="logout()">${ic('out', 18)}</button></div></aside><main id="main"></main></div>`
  api('/api/accounts/profile/').then(u => { me_name.textContent = u.username; me_mail.textContent = u.email }).catch(() => {})
  return document.getElementById('main')
}

/* ---- overview chart: duration line + P95/Avg + OK/FAIL step (SVG string) ---- */
function overview(checks, avg) {
  if (!checks.length) return '<div class="empty">No checks in this period yet.</div>'
  const W = 1000, H = 340, L = 56, R = 60, T = 14, B = 34, iw = W - L - R, ih = H - T - B
  const ts = c => +new Date(c.checked_at), t0 = ts(checks[0]), span = Math.max(ts(checks[checks.length - 1]) - t0, 1)
  const times = checks.map(c => c.response_time).filter(v => v != null)
  const max = Math.max(150, Math.ceil(Math.max(0, ...times) * 1.2 / 150) * 150)
  const x = c => L + (ts(c) - t0) / span * iw, y = v => T + ih - v / max * ih, sy = c => c.is_success ? y(max / 4) : y(0)
  const pts = checks.filter(c => c.response_time != null).map(c => [x(c), y(c.response_time), c]), p = p95(times)
  const line = pts.map((q, i) => { if (!i) return `M${q[0]},${q[1]}`; const a = pts[i - 1], m = (q[0] + a[0]) / 2; return `C${m},${a[1]} ${m},${q[1]} ${q[0]},${q[1]}` }).join('')
  const area = checks.map((c, i) => i ? `H${x(c)} V${sy(c)}` : `M${x(c)},${sy(c)}`).join('') + `V${y(0)} H${x(checks[0])}Z`
  const yt = [0, 1, 2, 3, 4].map(i => max / 4 * i), xt = [0, 1, 2, 3, 4, 5].map(i => t0 + span * i / 5), xp = t => L + (t - t0) / span * iw
  return `<svg viewBox="0 0 ${W} ${H}" class="chart"><defs><linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5fd9a3" stop-opacity=".22"/><stop offset="1" stop-color="#f27d7d" stop-opacity=".08"/></linearGradient></defs>
  ${yt.map(v => `<line x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}" class="grid"/><text x="${L - 12}" y="${y(v) + 4}" text-anchor="end" class="tick">${Math.round(v)}</text>`).join('')}
  ${xt.map(t => `<line x1="${xp(t)}" x2="${xp(t)}" y1="${T}" y2="${T + ih}" class="grid"/><text x="${xp(t)}" y="${H - 8}" text-anchor="middle" class="tick">${new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</text>`).join('')}
  <text x="${W - R + 12}" y="${y(max / 4) + 4}" class="tick">OK</text><text x="${W - R + 12}" y="${y(0) + 4}" class="tick">FAIL</text><path d="${area}" fill="url(#ga)"/>
  ${checks.slice(1).map((c, i) => { const a = checks[i]; return `<path d="M${x(a)},${sy(a)} H${x(c)} V${sy(c)}" class="step ${a.is_success ? 'ok' : 'bad'}"/>` }).join('')}
  ${p != null ? `<line x1="${L}" x2="${W - R}" y1="${y(p)}" y2="${y(p)}" class="ref p95"/><text x="${L + 8}" y="${y(p) - 6}" class="reflbl bad">P95 ${Math.round(p)}ms</text>` : ''}
  ${avg != null ? `<line x1="${L}" x2="${W - R}" y1="${y(avg)}" y2="${y(avg)}" class="ref avg"/><text x="${L + 8}" y="${y(avg) + 16}" class="reflbl blue">Avg ${Math.round(avg)}ms</text>` : ''}
  <path d="${line}" class="dur"/>${pts.map(q => `<circle cx="${q[0]}" cy="${q[1]}" r="3.5" class="dot ${q[2].is_success ? 'ok' : 'bad'}"><title>${fmtDate(q[2].checked_at)} · ${q[2].response_time} ms · HTTP ${q[2].status_code ?? '-'}</title></circle>`).join('')}</svg>`
}

const fmtDur = ms => { const m = Math.round(ms / 60000); return m < 1 ? '<1 min' : m < 60 ? m + ' min' : m < 1440 ? Math.floor(m / 60) + ' h ' + (m % 60) + ' min' : Math.floor(m / 1440) + ' d ' + Math.floor(m % 1440 / 60) + ' h' }
