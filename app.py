import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="THE SAPRE TECH | Smart 40 CNC & VMC Shopfloor System",
    layout="wide",
)

# =====================================================
# ALL 40 MACHINES DATA (CNC-01 TO CNC-40)
# (तुमचा खरा `machines.db` डेटा असेल तर इथे तो जोडा)
# =====================================================
operators = [
    "SANYOG KAMBLE",
    "NITIN KUMBHAR",
    "VIKAS KADAM",
    "AMIT PATIL",
    "ROHAN DESAI",
    "SWAPNIL MORE",
    "PRAVIN JADHAV",
    "KIRAN SAWANT",
]

parts_list = [
    "GEAR BLANK - B05",
    "VALVE BODY - V90",
    "PUMP HOUSING - P22",
    "FLANGE HUB - F14",
    "PISTON PIN - K08",
    "BEARING CAP - C19",
    "SPINDLE NUT - S04",
    "SHAFT COUPLING - A12",
]

machines_data = []
for i in range(1, 41):
    mid = f"CNC-{i:02d}"

    if i <= 33:
        status = "RUNNING"
    elif i <= 37:
        status = "IDLE"
    else:
        status = "ALARM"

    is_warn = (i % 7 == 0)
    is_where = (status == "ALARM") or (i % 9 == 0)
    is_tool_due = (i % 8 == 0)

    machines_data.append(
        {
            "id": mid,
            "status": status,
            "banner": "IMPROVEMENT NEEDED" if is_warn else "GOOD WORKING",
            "banner_type": "warn" if is_warn else "good",
            "where_r_u": is_where,
            "tool_life": min(35 + (i * 2) % 60, 95),
            "part": parts_list[(i - 1) % len(parts_list)],
            "operator": operators[(i - 1) % len(operators)],
            "shift": "09:00 AM - 06:00 PM" if i % 2 == 1 else "08:00 AM - 05:00 PM",
            "ok": 70 + (i * 2) % 75,
            "target": 150,
            "rej": 1 if i % 4 == 0 else 0,
            "tool_due": is_tool_due,
        }
    )

machines_json = json.dumps(machines_data, ensure_ascii=False)

dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: "Segoe UI", system-ui, sans-serif; }}
  body {{ background: #070d19; color: #f8fafc; padding: 14px; }}
  .panel {{
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 14px;
    text-align: center;
  }}
  .title {{ font-size: 32px; font-weight: 800; color: #22d3ee; letter-spacing: 1px; }}
  .subtitle {{ font-size: 12px; color: #94a3b8; margin-top: 4px; letter-spacing: 0.6px; }}
  .toolbar {{
    display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 14px;
  }}
  .btn {{
    border: 1px solid #334155; background: #1e293b; color: #f8fafc;
    padding: 8px 14px; border-radius: 8px; font-weight: 600; font-size: 13px; cursor: pointer;
  }}
  .btn-clock {{ background: #091120; border-color: #1e3a5f; color: #34d399; font-family: monospace; font-size: 14px; }}
  .btn-tv {{ background: #312e81; border-color: #4f46e5; }}
  .btn-email {{ background: #d97706; border-color: #f59e0b; color: #fff; }}
  .btn-excel {{ background: #059669; border-color: #10b981; color: #fff; }}

  .kpi-grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 12px; }}
  .kpi-grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 14px; }}
  .kpi-card {{
    background: #111c33; border: 1px solid #1e293b; border-radius: 12px;
    padding: 14px; text-align: center;
  }}
  .kpi-lbl {{ font-size: 11px; color: #94a3b8; font-weight: 700; letter-spacing: 0.5px; }}
  .kpi-val {{ font-size: 26px; font-weight: 800; margin-top: 4px; }}
  .c-white {{ color: #f8fafc; }}
  .c-green {{ color: #22c55e; }}
  .c-yellow {{ color: #eab308; }}
  .c-red {{ color: #ef4444; }}
  .b-green {{ border-color: #15803d; }}
  .b-red {{ border-color: #991b1b; }}

  .filter-bar {{
    background: #0f172a; border: 1px solid #1e293b; border-radius: 12px;
    padding: 10px 12px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 16px;
  }}
  .search-input {{
    flex: 1; min-width: 240px; background: #1e293b; border: 1px solid #334155;
    color: #f8fafc; padding: 8px 12px; border-radius: 8px; font-size: 12px;
  }}
  .chip {{
    background: #1e293b; border: 1px solid #334155; color: #cbd5e1;
    padding: 7px 12px; border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer;
  }}
  .chip.active {{ background: #0284c7; border-color: #38bdf8; color: #fff; }}

  .cards-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
  .m-card {{
    background: #0f172a; border: 1px solid #1e293b; border-radius: 14px;
    padding: 14px; display: flex; flex-direction: column; gap: 10px;
  }}
  .m-top {{ display: flex; justify-content: space-between; align-items: center; }}
  .m-id {{ font-size: 16px; font-weight: 800; color: #f8fafc; }}
  .badge-run {{
    background: rgba(34, 197, 94, 0.18); color: #4ade80; border: 1px solid #16a34a;
    padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;
  }}
  .badge-idle {{
    background: rgba(234, 179, 8, 0.18); color: #facc15; border: 1px solid #ca8a04;
    padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;
  }}
  .badge-alarm {{
    background: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid #dc2626;
    padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;
  }}
  .banner-good {{
    background: rgba(22, 163, 74, 0.25); border: 1px solid #22c55e; color: #86efac;
    text-align: center; padding: 6px; border-radius: 8px; font-size: 11px; font-weight: 800;
  }}
  .banner-warn {{
    background: rgba(180, 83, 9, 0.3); border: 1px solid #f59e0b; color: #fcd34d;
    text-align: center; padding: 6px; border-radius: 8px; font-size: 11px; font-weight: 800;
  }}
  .banner-tool {{
    background: rgba(154, 52, 18, 0.35); border: 1px solid #ea580c; color: #fdba74;
    text-align: center; padding: 5px; border-radius: 8px; font-size: 11px; font-weight: 800;
  }}
  .meta-line {{ display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; }}
  .info-box {{
    background: #111c33; border: 1px solid #1e293b; border-radius: 10px;
    padding: 10px; display: flex; flex-direction: column; gap: 5px; font-size: 12px;
  }}
  .part-txt {{ color: #38bdf8; font-weight: 700; }}
  .op-txt {{ color: #c084fc; font-weight: 700; font-size: 11px; }}
  .shift-txt {{ color: #94a3b8; font-size: 11px; }}
  .prog-row {{ display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; }}
  .ok-txt {{ color: #22c55e; }}
  .rej-txt {{ color: #ef4444; }}
  .bar-bg {{ width: 100%; height: 6px; background: #1e293b; border-radius: 999px; overflow: hidden; }}
  .bar-fill {{ height: 100%; background: #0ea5e9; }}
  .edit-btn {{
    width: 100%; background: #1e293b; border: 1px solid #334155; color: #e2e8f0;
    padding: 7px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer;
  }}
  .edit-btn:hover {{ background: #334155; }}
  @media (max-width: 1100px) {{
    .cards-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .kpi-grid-4 {{ grid-template-columns: repeat(2, 1fr); }}
  }}
</style>
</head>
<body>
  <div class="panel">
    <div class="title">🏭 THE SAPRE TECH</div>
    <div class="subtitle">SMART 40 CNC &amp; VMC SHOPFLOOR SYSTEM (PC, MOBILE &amp; TV)</div>
    <div class="toolbar">
      <button class="btn btn-clock" id="clockBtn">05:12:16 PM</button>
      <button class="btn" id="soundBtn" onclick="toggleSound()">🔇 Sound: OFF</button>
      <button class="btn btn-tv" id="tvBtn" onclick="toggleTv()">📺 TV Scroll: OFF</button>
      <button class="btn btn-email" onclick="alert('Email Report triggered!')">📧 Email Report</button>
      <button class="btn btn-excel" onclick="alert('Excel Report triggered!')">📊 Excel Report</button>
    </div>
  </div>

  <div class="kpi-grid-4">
    <div class="kpi-card"><div class="kpi-lbl">TOTAL M/C</div><div class="kpi-val c-white" id="kpiTotal">40</div></div>
    <div class="kpi-card"><div class="kpi-lbl">RUNNING</div><div class="kpi-val c-green" id="kpiRunning">0</div></div>
    <div class="kpi-card"><div class="kpi-lbl">IDLE</div><div class="kpi-val c-yellow" id="kpiIdle">0</div></div>
    <div class="kpi-card"><div class="kpi-lbl">ALARM</div><div class="kpi-val c-red" id="kpiAlarm">0</div></div>
  </div>

  <div class="kpi-grid-3">
    <div class="kpi-card b-green"><div class="kpi-lbl c-green">☀️ GOOD WORK</div><div class="kpi-val c-green" id="kpiGood">0</div></div>
    <div class="kpi-card b-red"><div class="kpi-lbl c-red">🚨 WHERE R U?</div><div class="kpi-val c-red" id="kpiWhere">0</div></div>
    <div class="kpi-card b-red"><div class="kpi-lbl c-red">🔧 TOOL ALERT</div><div class="kpi-val c-red" id="kpiTool">0</div></div>
  </div>

  <div class="filter-bar">
    <input class="search-input" id="searchBox" type="text" placeholder="🔍 SEARCH MACHINE (CNC-01), OPERATOR OR PART NAME.." oninput="renderCards()" />
    <button class="chip active" data-filter="ALL" id="chipAll" onclick="setFilter('ALL', this)">ALL (40)</button>
    <button class="chip" data-filter="RUNNING" onclick="setFilter('RUNNING', this)">RUNNING</button>
    <button class="chip" data-filter="WHERE" onclick="setFilter('WHERE', this)">🚨 WHERE R U?</button>
    <button class="chip" data-filter="WARN" onclick="setFilter('WARN', this)">⚠️ IMPROVEMENT</button>
    <button class="chip" data-filter="GOOD" onclick="setFilter('GOOD', this)">☀️ GOOD</button>
    <button class="chip" data-filter="TOOL" onclick="setFilter('TOOL', this)">🔧 TOOL DUE</button>
  </div>

  <div class="cards-grid" id="cardsGrid"></div>

<script>
  const machines = {machines_json};
  let activeFilter = "ALL";
  let soundOn = false;
  let tvOn = false;

  function updateKpis() {{
    document.getElementById("kpiTotal").textContent = machines.length;
    document.getElementById("kpiRunning").textContent = machines.filter(m => m.status === "RUNNING").length;
    document.getElementById("kpiIdle").textContent = machines.filter(m => m.status === "IDLE").length;
    document.getElementById("kpiAlarm").textContent = machines.filter(m => m.status === "ALARM").length;
    document.getElementById("kpiGood").textContent = machines.filter(m => m.banner_type === "good").length;
    document.getElementById("kpiWhere").textContent = machines.filter(m => m.where_r_u).length;
    document.getElementById("kpiTool").textContent = machines.filter(m => m.tool_due).length;
    document.getElementById("chipAll").textContent = `ALL (${{machines.length}})`;
  }}

  function updateClock() {{
    const now = new Date();
    document.getElementById("clockBtn").textContent = now.toLocaleTimeString("en-US", {{ hour12: true }});
  }}
  setInterval(updateClock, 1000);
  updateClock();

  function toggleSound() {{
    soundOn = !soundOn;
    document.getElementById("soundBtn").textContent = soundOn ? "🔊 Sound: ON" : "🔇 Sound: OFF";
  }}

  function toggleTv() {{
    tvOn = !tvOn;
    document.getElementById("tvBtn").textContent = tvOn ? "📺 TV Scroll: ON" : "📺 TV Scroll: OFF";
  }}

  function setFilter(f, el) {{
    activeFilter = f;
    document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
    el.classList.add("active");
    renderCards();
  }}

  function getStatusBadge(status) {{
    if (status === "IDLE") return `<span class="badge-idle">IDLE</span>`;
    if (status === "ALARM") return `<span class="badge-alarm">ALARM</span>`;
    return `<span class="badge-run">RUNNING</span>`;
  }}

  function renderCards() {{
    const q = document.getElementById("searchBox").value.trim().toLowerCase();
    const grid = document.getElementById("cardsGrid");
    const filtered = machines.filter(m => {{
      const matchSearch = !q ||
        m.id.toLowerCase().includes(q) ||
        m.operator.toLowerCase().includes(q) ||
        m.part.toLowerCase().includes(q);
      if (!matchSearch) return false;
      if (activeFilter === "RUNNING") return m.status === "RUNNING";
      if (activeFilter === "WHERE") return m.where_r_u;
      if (activeFilter === "GOOD") return m.banner_type === "good";
      if (activeFilter === "WARN") return m.banner_type === "warn";
      if (activeFilter === "TOOL") return m.tool_due;
      return true;
    }});

    grid.innerHTML = filtered.map(m => {{
      const pct = Math.min(Math.round((m.ok / Math.max(m.target, 1)) * 100), 100);
      const bannerHtml = m.banner_type === "good"
        ? `<div class="banner-good">☀️ ${{m.banner}}</div>`
        : `<div class="banner-warn">⚠️ ${{m.banner}}</div>`;
      const toolHtml = m.tool_due
        ? `<div class="banner-tool">🔧 TOOL CHANGE DUE (${{m.tool_life}}%)</div>`
        : "";
      return `
        <div class="m-card">
          <div class="m-top">
            <div class="m-id">${{m.id}}</div>
            ${{getStatusBadge(m.status)}}
          </div>
          ${{bannerHtml}}
          ${{toolHtml}}
          <div class="meta-line">
            <span>🔧 Tool Life Used:</span>
            <strong>${{m.tool_life}}%</strong>
          </div>
          <div class="info-box">
            <div class="part-txt">⚙️ ${{m.part}}</div>
            <div class="op-txt">👤 ${{m.operator}}</div>
            <div class="shift-txt">🕒 ${{m.shift}}</div>
          </div>
          <div class="prog-row">
            <span><span class="ok-txt">OK: ${{m.ok}}</span> / Target: <strong>${{m.target}}</strong></span>
            <span class="rej-txt">Rej: ${{m.rej}}</span>
          </div>
          <div class="bar-bg"><div class="bar-fill" style="width:${{pct}}%;"></div></div>
          <button class="edit-btn" onclick="alert('Edit ${{m.id}}')">✏️ Edit / Quality / Tool</button>
        </div>
      `;
    }}).join("");
  }}

  updateKpis();
  renderCards();
</script>
</body>
</html>
"""

components.html(dashboard_html, height=2800, scrolling=True)