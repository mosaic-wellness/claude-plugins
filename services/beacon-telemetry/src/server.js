import Fastify from 'fastify';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();
const fastify = Fastify({ logger: true });

// --- API Routes ---

// Tracking endpoint — GET /t?c=doctor&u=email&p=project&s=agent
fastify.get('/t', async (request, reply) => {
  const { c, u, p, s } = request.query;

  if (c && u) {
    await prisma.event.create({
      data: {
        command: String(c).slice(0, 50),
        userEmail: String(u).slice(0, 255),
        projectName: String(p || 'unknown').slice(0, 255),
        source: String(s || 'prompt').slice(0, 10),
        ts: new Date(),
      },
    });
  }

  reply.code(204).send();
});

// Legacy POST endpoint
fastify.post('/beacon/telemetry', async (request, reply) => {
  const { command, user_email, project_name, ts } = request.body || {};

  if (!command || !user_email) {
    return reply.code(400).send({ ok: false, error: 'command and user_email required' });
  }

  await prisma.event.create({
    data: {
      command: command.slice(0, 50),
      userEmail: user_email.slice(0, 255),
      projectName: (project_name || 'unknown').slice(0, 255),
      ts: ts ? new Date(ts) : new Date(),
    },
  });

  return { ok: true };
});

fastify.get('/beacon/telemetry/stats', async (request) => {
  const days = parseInt(request.query.days || '30', 10);
  const since = new Date(Date.now() - days * 86400000);

  const byCommand = await prisma.$queryRaw`
    SELECT command, COUNT(*)::int as count
    FROM beacon_events WHERE ts >= ${since}
    GROUP BY command ORDER BY count DESC
  `;

  const byUser = await prisma.$queryRaw`
    SELECT user_email, COUNT(*)::int as count
    FROM beacon_events WHERE ts >= ${since}
    GROUP BY user_email ORDER BY count DESC
  `;

  const byProject = await prisma.$queryRaw`
    SELECT project_name, COUNT(*)::int as count
    FROM beacon_events WHERE ts >= ${since}
    GROUP BY project_name ORDER BY count DESC
  `;

  const daily = await prisma.$queryRaw`
    SELECT ts::date as date, COUNT(*)::int as count
    FROM beacon_events WHERE ts >= ${since}
    GROUP BY ts::date ORDER BY date
  `;

  const recent = await prisma.$queryRaw`
    SELECT command, user_email, project_name, ts
    FROM beacon_events ORDER BY ts DESC LIMIT 50
  `;

  const total = await prisma.event.count({ where: { ts: { gte: since } } });

  return { total, days, byCommand, byUser, byProject, daily, recent };
});

fastify.get('/health', async () => ({ status: 'ok' }));

// --- Dashboard ---

fastify.get('/', async (request, reply) => {
  reply.type('text/html');
  return reply.send(dashboardHtml);
});

const dashboardHtml = /* html */ `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Beacon Telemetry</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0f; color: #e0e0e8; min-height: 100vh; }
  .header { padding: 32px 40px 24px; border-bottom: 1px solid #1a1a2e; }
  .header h1 { font-size: 20px; font-weight: 600; color: #fff; }
  .header p { font-size: 13px; color: #666; margin-top: 4px; }
  .controls { padding: 16px 40px; display: flex; gap: 8px; }
  .controls button { padding: 6px 14px; border-radius: 6px; border: 1px solid #1a1a2e; background: transparent; color: #888; font-size: 13px; cursor: pointer; transition: all 0.15s; }
  .controls button:hover { border-color: #333; color: #ccc; }
  .controls button.active { background: #1a1a2e; color: #fff; border-color: #2a2a4e; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; padding: 8px 40px 24px; }
  .stat-card { background: #111118; border: 1px solid #1a1a2e; border-radius: 10px; padding: 20px; }
  .stat-card .label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #555; }
  .stat-card .value { font-size: 28px; font-weight: 700; color: #fff; margin-top: 4px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 0 40px 24px; }
  .card { background: #111118; border: 1px solid #1a1a2e; border-radius: 10px; padding: 24px; }
  .card h2 { font-size: 13px; font-weight: 600; color: #888; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.5px; }
  .bar-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
  .bar-label { font-size: 13px; color: #ccc; width: 140px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 0; }
  .bar-track { flex: 1; height: 24px; background: #0a0a0f; border-radius: 4px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; transition: width 0.4s ease; }
  .bar-count { font-size: 13px; color: #666; width: 40px; text-align: right; flex-shrink: 0; }
  .chart-area { width: 100%; height: 180px; position: relative; }
  .chart-area svg { width: 100%; height: 100%; }
  .full-width { grid-column: 1 / -1; }
  table { width: 100%; border-collapse: collapse; }
  th { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #555; text-align: left; padding: 8px 12px; border-bottom: 1px solid #1a1a2e; }
  td { font-size: 13px; padding: 8px 12px; border-bottom: 1px solid #0f0f18; color: #bbb; }
  tr:hover td { background: #0f0f18; }
  .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
  .empty-msg { color: #444; font-size: 13px; padding: 20px 0; text-align: center; }
  @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } .header, .controls, .stats, .grid { padding-left: 20px; padding-right: 20px; } }
</style>
</head>
<body>
  <div class="header">
    <h1>Beacon Telemetry</h1>
    <p>Plugin usage across the team</p>
  </div>
  <div class="controls" id="controls"></div>
  <div class="stats" id="stats"></div>
  <div class="grid" id="grid"></div>

<script>
const COLORS = ['#6366f1','#8b5cf6','#a78bfa','#c4b5fd','#818cf8','#7c3aed','#5b21b6','#4f46e5'];
const CMD_COLORS = { doctor:'#ef4444', review:'#f59e0b', brainstorm:'#22c55e', grillme:'#ec4899',
  ux:'#06b6d4', debug:'#f97316', document:'#8b5cf6', '10x':'#6366f1', 'review-stack':'#14b8a6', recommendations:'#64748b' };
let currentDays = 30;

function esc(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.textContent;
}

function el(tag, attrs, children) {
  const e = document.createElement(tag);
  if (attrs) Object.entries(attrs).forEach(([k, v]) => {
    if (k === 'style' && typeof v === 'object') Object.assign(e.style, v);
    else if (k === 'className') e.className = v;
    else e.setAttribute(k, v);
  });
  if (typeof children === 'string') e.textContent = children;
  else if (Array.isArray(children)) children.forEach(c => { if (c) e.appendChild(c); });
  else if (children instanceof Node) e.appendChild(children);
  return e;
}

function buildControls() {
  const container = document.getElementById('controls');
  container.replaceChildren();
  [7, 14, 30, 90].forEach(d => {
    const btn = el('button', { 'data-days': d, className: d === currentDays ? 'active' : '' }, d + ' days');
    btn.addEventListener('click', () => load(d));
    container.appendChild(btn);
  });
}

function statCard(label, value) {
  return el('div', { className: 'stat-card' }, [
    el('div', { className: 'label' }, label),
    el('div', { className: 'value' }, String(value)),
  ]);
}

function barRow(label, count, max, color) {
  const pct = (count / max * 100).toFixed(1);
  const fill = el('div', { className: 'bar-fill', style: { width: pct + '%', background: color } });
  return el('div', { className: 'bar-row' }, [
    el('span', { className: 'bar-label', title: label }, label),
    el('div', { className: 'bar-track' }, fill),
    el('span', { className: 'bar-count' }, String(count)),
  ]);
}

function card(title, contentEl, extra) {
  const c = el('div', { className: 'card' + (extra ? ' ' + extra : '') }, [
    el('h2', null, title),
    contentEl,
  ]);
  return c;
}

function emptyMsg() {
  return el('div', { className: 'empty-msg' }, 'No data yet');
}

function sparkChart(daily) {
  const maxVal = Math.max(...daily.map(d => d.count), 1);
  const w = 100, h = 100, pad = 5;
  const step = daily.length > 1 ? (w - 2 * pad) / (daily.length - 1) : 0;
  const pts = daily.map((d, i) => [pad + i * step, h - pad - (d.count / maxVal) * (h - 2 * pad)]);

  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
  svg.setAttribute('preserveAspectRatio', 'none');

  const areaPoints = pad + ',' + (h - pad) + ' ' + pts.map(p => p.join(',')).join(' ') + ' ' + (pad + (daily.length - 1) * step) + ',' + (h - pad);
  const poly = document.createElementNS(ns, 'polygon');
  poly.setAttribute('points', areaPoints);
  poly.setAttribute('fill', 'rgba(99,102,241,0.15)');
  svg.appendChild(poly);

  const line = document.createElementNS(ns, 'polyline');
  line.setAttribute('points', pts.map(p => p.join(',')).join(' '));
  line.setAttribute('fill', 'none');
  line.setAttribute('stroke', '#6366f1');
  line.setAttribute('stroke-width', '1.5');
  svg.appendChild(line);

  pts.forEach(p => {
    const c = document.createElementNS(ns, 'circle');
    c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); c.setAttribute('r', '1.5'); c.setAttribute('fill', '#6366f1');
    svg.appendChild(c);
  });

  const container = el('div', { className: 'chart-area' });
  container.appendChild(svg);
  return container;
}

function recentTable(rows) {
  const thead = el('thead', null, [
    el('tr', null, ['Command', 'User', 'Project', 'Time'].map(t => el('th', null, t)))
  ]);
  const tbody = el('tbody');
  rows.forEach(r => {
    const color = CMD_COLORS[r.command] || '#6366f1';
    const tag = el('span', { className: 'tag', style: { background: color + '22', color: color } }, esc(r.command));
    const tr = el('tr', null, [
      el('td', null, tag),
      el('td', null, esc(r.user_email.split('@')[0])),
      el('td', null, esc(r.project_name)),
      el('td', null, timeAgo(new Date(r.ts))),
    ]);
    tbody.appendChild(tr);
  });
  return el('table', null, [thead, tbody]);
}

function timeAgo(date) {
  const s = Math.floor((Date.now() - date) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return Math.floor(s / 60) + 'm ago';
  if (s < 86400) return Math.floor(s / 3600) + 'h ago';
  return Math.floor(s / 86400) + 'd ago';
}

async function load(days) {
  currentDays = days;
  buildControls();

  const res = await fetch('/beacon/telemetry/stats?days=' + days);
  const d = await res.json();

  const statsEl = document.getElementById('stats');
  const gridEl = document.getElementById('grid');
  statsEl.replaceChildren();
  gridEl.replaceChildren();

  const topCmd = d.byCommand[0] ? d.byCommand[0].command : '-';
  [['Total Events', d.total], ['Active Users', d.byUser.length], ['Projects', d.byProject.length], ['Top Command', topCmd]]
    .forEach(([l, v]) => statsEl.appendChild(statCard(l, v)));

  const maxCmd = Math.max(...d.byCommand.map(r => r.count), 1);
  const cmdContent = d.byCommand.length ? el('div', null, d.byCommand.map(r => barRow(r.command, r.count, maxCmd, CMD_COLORS[r.command] || '#6366f1'))) : emptyMsg();
  gridEl.appendChild(card('Commands', cmdContent));

  const maxUser = Math.max(...d.byUser.map(r => r.count), 1);
  const userContent = d.byUser.length ? el('div', null, d.byUser.map((r, i) => barRow(r.user_email.split('@')[0], r.count, maxUser, COLORS[i % COLORS.length]))) : emptyMsg();
  gridEl.appendChild(card('Team Members', userContent));

  const maxProj = Math.max(...d.byProject.map(r => r.count), 1);
  const projContent = d.byProject.length ? el('div', null, d.byProject.map((r, i) => barRow(r.project_name, r.count, maxProj, COLORS[(i + 3) % COLORS.length]))) : emptyMsg();
  gridEl.appendChild(card('Projects', projContent));

  const chartContent = d.daily.length ? sparkChart(d.daily) : emptyMsg();
  gridEl.appendChild(card('Daily Activity', chartContent));

  const tableContent = d.recent.length ? recentTable(d.recent) : emptyMsg();
  gridEl.appendChild(card('Recent Activity', tableContent, 'full-width'));
}

buildControls();
load(30);
</script>
</body>
</html>`;

const start = async () => {
  const port = parseInt(process.env.PORT || '3000', 10);
  await fastify.listen({ port, host: '0.0.0.0' });
};

start().catch((err) => {
  fastify.log.error(err);
  process.exit(1);
});
