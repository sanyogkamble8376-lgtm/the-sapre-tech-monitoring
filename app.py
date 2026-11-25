from datetime import datetime
from html import escape
from textwrap import dedent
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="The Sapre Tech | v2.7 • 40 Max",
    page_icon="🏭",
    layout="wide",
)

# ---------------- SESSION DEFAULTS ----------------

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://192.168.2.174:5000"
if "live_on" not in st.session_state:
    st.session_state.live_on = True
if "status_tab" not in st.session_state:
    st.session_state.status_tab = "All"
if "compact_mode" not in st.session_state:
    st.session_state.compact_mode = False
if "show_notice" not in st.session_state:
    st.session_state.show_notice = False
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False
if "custom_machines" not in st.session_state:
    st.session_state.custom_machines = {}
if "selected_machine" not in st.session_state:
    st.session_state.selected_machine = None

# ---------------- STYLES ----------------

st.markdown(
    dedent("""
<style>
.stApp {
    background-color: #070b14;
    color: #e2e8f0;
}
.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    max-width: 1700px;
}
.brand-title {
    font-size: 28px;
    font-weight: 800;
    color: #f8fafc;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
.badge-ver {
    background: #1e293b;
    color: #facc15;
    border: 1px solid #334155;
    font-size: 12px;
    padding: 3px 9px;
    border-radius: 6px;
    font-weight: 700;
}
.badge-loc {
    background: #0f172a;
    color: #94a3b8;
    border: 1px solid #1e293b;
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 6px;
}
.shift-sub {
    color: #94a3b8;
    font-size: 12px;
    margin-top: 4px;
}
.m-card {
    background: #0d1526;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 8px;
}
.m-card.compact {
    padding: 11px;
    margin-bottom: 6px;
}
.m-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}
.m-id {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
}
.m-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 3px;
}
.pill {
    font-size: 12px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
    border: 1px solid transparent;
}
.pill-Running {
    background: rgba(16, 185, 129, 0.14);
    color: #34d399;
    border-color: rgba(16, 185, 129, 0.35);
}
.pill-Idle {
    background: rgba(245, 158, 11, 0.14);
    color: #fbbf24;
    border-color: rgba(245, 158, 11, 0.35);
}
.pill-Alarm {
    background: rgba(239, 68, 68, 0.14);
    color: #f87171;
    border-color: rgba(239, 68, 68, 0.35);
}
.banner-warn {
    background: rgba(245, 158, 11, 0.13);
    border: 1px solid rgba(245, 158, 11, 0.35);
    color: #fcd34d;
    border-radius: 8px;
    padding: 7px 11px;
    font-size: 12px;
    font-weight: 700;
    margin: 10px 0;
}
.banner-good {
    background: rgba(16, 185, 129, 0.13);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #6ee7b7;
    border-radius: 8px;
    padding: 7px 11px;
    font-size: 12px;
    font-weight: 700;
    margin: 10px 0;
}
.op-box {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #111c32;
    border: 1px solid #1e293b;
    border-radius: 9px;
    padding: 8px 10px;
    margin: 10px 0;
}
.op-name {
    font-size: 15px;
    font-weight: 700;
    color: #f8fafc;
}
.mini-tag {
    font-size: 11px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 5px;
    background: #1e293b;
    color: #cbd5e1;
    margin-left: 4px;
}
.prog-label {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 5px;
}
.prog-track {
    width: 100%;
    height: 7px;
    background: #1e293b;
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 12px;
}
.prog-fill {
    height: 100%;
    background: linear-gradient(90deg, #10b981, #22c55e);
    border-radius: 999px;
}
.kpi-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 10px;
}
.kpi-box {
    background: #111c32;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 8px 6px;
    text-align: center;
}
.kpi-lbl {
    font-size: 11px;
    color: #94a3b8;
}
.kpi-val {
    font-size: 16px;
    font-weight: 800;
    color: #ffffff;
    margin-top: 2px;
}
.m-foot {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #64748b;
    padding-top: 4px;
}
</style>
"""),
    unsafe_allow_html=True,
)

# ---------------- DATA HELPERS ----------------

OPERATORS = [
    "राहुल पाटील",
    "अमित जाधव",
    "सुरेश शिंदे",
    "विक्रम माने",
    "संदीप पवार",
    "योगेश देशमुख",
    "नितीन चव्हाण",
    "विशाल गायकवाड",
]


def build_default_40():
    rows = []
    for i in range(1, 26):
        mid = f"CNC-{i:02d}"
        status = (
            "Running"
            if i % 6 != 0
            else ("Idle" if i % 12 == 6 else "Alarm")
        )
        parts = 70 + (i * 5) % 120
        target = 200
        rows.append({
            "id": mid,
            "mtype": "CNC Turning",
            "program": f"O{1000 + i*10}_PART_{i:02d}.NC",
            "status": status,
            "operator": OPERATORS[i % len(OPERATORS)],
            "parts": parts,
            "target": target,
            "rpm": (2100 + i * 45) if status == "Running" else 0,
            "oee": f"{68 + (i * 3) % 27}%",
            "message": (
                "GOOD WORKING"
                if i % 4 == 0
                else ("PLEASE IMPROVEMENT" if i % 3 == 0 else "")
            ),
            "note": (
                "Coolant / Servo Alert"
                if status == "Alarm"
                else ("Tool Change" if status == "Idle" else "-")
            ),
            "updated": "14:40:21",
        })

    for j in range(1, 16):
        mid = f"VMC-{j:02d}"
        axis = "VMC 3-Axis" if j % 2 == 1 else "VMC 4-Axis"
        status = (
            "Running"
            if j % 4 != 0
            else ("Alarm" if j % 8 == 4 else "Idle")
        )
        parts = 55 + (j * 7) % 90
        target = 120
        rows.append({
            "id": mid,
            "mtype": axis,
            "program": f"O{1150 + j*10}_PART_{j:02d}.NC",
            "status": status,
            "operator": OPERATORS[(j + 3) % len(OPERATORS)],
            "parts": parts,
            "target": target,
            "rpm": (2400 + j * 60) if status == "Running" else 0,
            "oee": f"{70 + (j * 4) % 25}%",
            "message": (
                "GOOD WORKING"
                if j == 6
                else (
                    "PLEASE IMPROVEMENT"
                    if status == "Alarm" and j < 5
                    else ""
                )
            ),
            "note": (
                "Coolant / Servo Alert"
                if status == "Alarm"
                else ("Job Loading" if status == "Idle" else "-")
            ),
            "updated": "14:40:21",
        })
    return rows


def fetch_machines(base_url: str):
    base_rows = build_default_40()
    by_id = {r["id"]: r for r in base_rows}
    connected = False

    try:
        res = requests.get(
            f"{base_url.rstrip('/')}/api/machines", timeout=2.5
        )
        res.raise_for_status()
        payload = res.json()
        if isinstance(payload, list):
            connected = True
            for item in payload:
                mid = item.get("id")
                if mid in by_id:
                    raw_status = str(item.get("status", "OFFLINE")).upper()
                    mapped_status = (
                        "Running"
                        if raw_status == "RUNNING"
                        else (
                            "Idle"
                            if raw_status == "IDLE"
                            else "Alarm" if raw_status == "ALARM" else "Idle"
                        )
                    )
                    updated_row = {
                        "status": mapped_status,
                        "parts": int(
                            pd.to_numeric(
                                item.get("part_count", item.get("parts")),
                                errors="coerce",
                            )
                            or 0
                        ),
                        "updated": str(
                            item.get("updated_at")
                            or datetime.now().strftime("%H:%M:%S")
                        )[-8:],
                    }
                    for optional_key in [
                        "operator",
                        "program",
                        "rpm",
                        "oee",
                        "message",
                        "note",
                        "target",
                    ]:
                        if item.get(optional_key) is not None:
                            updated_row[optional_key] = item.get(optional_key)
                    by_id[mid].update(updated_row)
    except Exception:
        connected = False

    for mid, extra in st.session_state.custom_machines.items():
        if mid in by_id:
            by_id[mid].update(extra)
        else:
            by_id[mid] = extra

    return pd.DataFrame(list(by_id.values())), connected


# ---------------- TOP BAR ----------------

h_left, h_right = st.columns([5, 6])

with h_left:
    st.markdown(
        dedent("""
    <div class="brand-title">
        <span>The Sapre Tech</span>
        <span class="badge-ver">v2.7 • 40 Max</span>
        <span class="badge-loc">Shiroli MIDC Shopfloor</span>
    </div>
    <div class="shift-sub">Shift 1 (Morning: 8 AM - 4 PM) • Live: 3s • Away Alert: 9s</div>
    """),
        unsafe_allow_html=True,
    )

with h_right:
    b1, b2, b3, b4, b5, b6, b7 = st.columns([
        1.2,
        1.7,
        1.1,
        0.9,
        1.2,
        0.8,
        1.0,
    ])
    with b1:
        live_label = "● LIVE ON" if st.session_state.live_on else "○ PAUSED"
        if st.button(live_label, use_container_width=True):
            st.session_state.live_on = not st.session_state.live_on
    with b2:
        if st.button("⚡ Load 40 Machines", use_container_width=True):
            st.session_state.custom_machines = {}
            st.session_state.selected_machine = None
            st.rerun()
    with b3:
        if st.button("📣 Notice", use_container_width=True):
            st.session_state.show_notice = not st.session_state.show_notice
    with b4:
        if st.button("+ Add", use_container_width=True):
            st.session_state.show_add_form = not st.session_state.show_add_form
    with b5:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.show_settings = not st.session_state.show_settings
    with b6:
        df_temp, _ = fetch_machines(st.session_state.api_url)
        st.download_button(
            "CSV",
            data=df_temp.to_csv(index=False).encode("utf-8"),
            file_name="sapre_tech_machines.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with b7:
        if st.button("Reset", use_container_width=True):
            st.session_state.status_tab = "All"
            st.session_state.compact_mode = False
            st.session_state.custom_machines = {}
            st.session_state.selected_machine = None
            st.rerun()

# ---------------- OPTIONAL PANELS ----------------

if st.session_state.show_settings:
    with st.expander("⚙️ API & Dashboard Settings", expanded=True):
        new_url = st.text_input(
            "Backend API Base URL", value=st.session_state.api_url
        )
        if st.button("Save API URL"):
            st.session_state.api_url = new_url.strip()
            st.rerun()

if st.session_state.show_notice:
    st.info(
        "📢 Shopfloor Notice: Shift 1 production & alarm check active at Shiroli"
        " MIDC."
    )

if st.session_state.show_add_form:
    with st.form("add_machine_form", clear_on_submit=True):
        st.markdown("**Add / Override Machine Entry**")
        c_a, c_b, c_c, c_d = st.columns(4)
        m_id = c_a.text_input("Machine ID", placeholder="CNC-26")
        m_op = c_b.text_input("Operator", placeholder="महेश पाटील")
        m_st = c_c.selectbox("Status", ["Running", "Idle", "Alarm"])
        m_pt = c_d.number_input("Parts", min_value=0, max_value=9999, value=50)
        if st.form_submit_button("Save Machine") and m_id.strip():
            mid_clean = m_id.strip().upper()
            st.session_state.custom_machines[mid_clean] = {
                "id": mid_clean,
                "mtype": "Custom Machine",
                "program": "O9000_CUSTOM.NC",
                "status": m_st,
                "operator": m_op.strip() or "ऑपरेटर",
                "parts": int(m_pt),
                "target": 150,
                "rpm": 2500 if m_st == "Running" else 0,
                "oee": "80%",
                "message": (
                    "GOOD WORKING"
                    if m_st == "Running"
                    else "PLEASE IMPROVEMENT"
                ),
                "note": "Manual Entry",
                "updated": datetime.now().strftime("%H:%M:%S"),
            }
            st.rerun()

# ---------------- LIVE FRAGMENT ----------------


@st.fragment(run_every="3s" if st.session_state.live_on else None)
def render_shopfloor():
    df, connected = fetch_machines(st.session_state.api_url)

    total_cnt = len(df)
    run_cnt = int((df["status"] == "Running").sum())
    idle_cnt = int((df["status"] == "Idle").sum())
    alarm_cnt = int((df["status"] == "Alarm").sum())
    total_parts = int(
        pd.to_numeric(df["parts"], errors="coerce").fillna(0).sum()
    )

    # Summary Row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("एकूण मशीन्स", total_cnt)
    k2.metric("चालू (Running)", run_cnt)
    k3.metric("थांबलेली (Idle)", idle_cnt)
    k4.metric("अलार्म (Alarm)", alarm_cnt)
    k5.metric("एकूण तयार पार्ट्स", total_parts)

    # Filter Bar
    f_cols = st.columns([0.7, 1.0, 0.7, 0.9, 2.7, 1.3, 1.2])
    for idx, tab_name in enumerate(["All", "Running", "Idle", "Alarm"]):
        with f_cols[idx]:
            if st.button(
                tab_name, key=f"tab_{tab_name}", use_container_width=True
            ):
                st.session_state.status_tab = tab_name

    with f_cols[4]:
        query = st.text_input(
            "Search",
            placeholder="मशीन किंवा ऑपरेटर शोधा...",
            label_visibility="collapsed",
        )

    with f_cols[5]:
        type_filter = st.selectbox(
            "Type",
            ["सर्व दाखवा", "CNC Turning", "VMC 3-Axis", "VMC 4-Axis"],
            label_visibility="collapsed",
        )

    with f_cols[6]:
        comp_lbl = f"Compact: {'ON' if st.session_state.compact_mode else 'OFF'}"
        if st.button(comp_lbl, use_container_width=True):
            st.session_state.compact_mode = not st.session_state.compact_mode

    filtered = df.copy()
    if st.session_state.status_tab != "All":
        filtered = filtered[filtered["status"] == st.session_state.status_tab]
    if type_filter != "सर्व दाखवा":
        filtered = filtered[filtered["mtype"] == type_filter]
    if query.strip():
        q = query.strip().lower()
        filtered = filtered[
            filtered["id"].str.lower().str.contains(q, na=False)
            | filtered["operator"].str.lower().str.contains(q, na=False)
        ]

    st.caption(
        f"Showing {len(filtered)} of {len(df)} filtered ({len(df)}/{len(df)}"
        f" total) • {'API Live' if connected else 'Preview Data'} • Last Sync:"
        f" {datetime.now().strftime('%H:%M:%S')}"
    )

    # Quick Machine Edit Panel when ऑप / प्रो / 💬 is clicked
    if st.session_state.selected_machine:
        sel_id = st.session_state.selected_machine
        match = df[df["id"] == sel_id]
        if not match.empty:
            cur = match.iloc[0].to_dict()
            with st.expander(f"✏️ Quick Update — {sel_id}", expanded=True):
                with st.form(f"quick_edit_{sel_id}"):
                    e1, e2, e3 = st.columns(3)
                    new_op = e1.text_input(
                        "ऑपरेटर (Operator)", value=str(cur.get("operator", ""))
                    )
                    new_prog = e2.text_input(
                        "प्रोग्राम (Program)", value=str(cur.get("program", ""))
                    )
                    new_msg = e3.selectbox(
                        "मेसेज / स्टेटस बॅनर",
                        ["", "GOOD WORKING", "PLEASE IMPROVEMENT"],
                        index=(
                            ["", "GOOD WORKING", "PLEASE IMPROVEMENT"].index(
                                cur.get("message", "")
                            )
                            if cur.get("message", "")
                            in ["", "GOOD WORKING", "PLEASE IMPROVEMENT"]
                            else 0
                        ),
                    )
                    s_col1, s_col2 = st.columns([1, 5])
                    if s_col1.form_submit_button("Update"):
                        updated_item = dict(cur)
                        updated_item.update({
                            "operator": new_op.strip() or "ऑपरेटर",
                            "program": new_prog.strip() or "O0000.NC",
                            "message": new_msg,
                            "updated": datetime.now().strftime("%H:%M:%S"),
                        })
                        st.session_state.custom_machines[sel_id] = updated_item
                        st.session_state.selected_machine = None
                        st.rerun()
                    if s_col2.form_submit_button("Close"):
                        st.session_state.selected_machine = None
                        st.rerun()

    # Cards Grid
    cols_per_row = 5 if st.session_state.compact_mode else 4
    card_cls = "m-card compact" if st.session_state.compact_mode else "m-card"

    for start in range(0, len(filtered), cols_per_row):
        row_cols = st.columns(cols_per_row)
        chunk = filtered.iloc[start : start + cols_per_row]

        for col, (_, m) in zip(row_cols, chunk.iterrows()):
            raw_mid = str(m["id"])
            mid = escape(raw_mid)
            mtype = escape(str(m["mtype"]))
            prog = escape(str(m["program"]))
            status = str(m["status"])
            op = escape(str(m["operator"]))
            parts = int(m["parts"])
            target = max(int(m["target"]), 1)
            pct = min(int(round((parts / target) * 100)), 100)
            rpm = escape(str(m["rpm"]))
            oee = escape(str(m["oee"]))
            msg = str(m["message"]).strip()
            note = escape(str(m["note"]))
            upd = escape(str(m["updated"]))

            if msg == "GOOD WORKING":
                banner_html = '<div class="banner-good">✔ GOOD WORKING</div>'
            elif msg == "PLEASE IMPROVEMENT":
                banner_html = (
                    '<div class="banner-warn">💬 PLEASE IMPROVEMENT</div>'
                )
            else:
                banner_html = ""

            single_line_card = (
                f'<div class="{card_cls}">'
                '<div class="m-top">'
                (
                    f'<div><div class="m-id">{mid}</div><div'
                    f' class="m-sub">{mtype} • {prog}</div></div>'
                ),
                f'<span class="pill pill-{escape(status)}">{escape(status)}</span>',
                "</div>",
                f"{banner_html}",
                '<div class="op-box">',
                (
                    '<div><div class="m-sub"'
                    f' style="margin-top:0;">ऑपरेटर</div><div'
                    f' class="op-name">{op}</div></div>'
                ),
                (
                    '<div><span class="mini-tag">ऑप</span><span'
                    ' class="mini-tag">प्रो</span><span'
                    ' class="mini-tag">💬</span></div>'
                ),
                "</div>",
                (
                    '<div class="prog-label"><span>Progress</span><span>'
                    f"{parts}/{target} ({pct}%)</span></div>"
                ),
                (
                    '<div class="prog-track"><div class="prog-fill"'
                    f' style="width: {pct}%;"></div></div>'
                ),
                '<div class="kpi-row">',
                (
                    '<div class="kpi-box"><div'
                    f' class="kpi-lbl">Parts</div><div'
                    f' class="kpi-val">{parts}</div></div>'
                ),
                (
                    '<div class="kpi-box"><div'
                    f' class="kpi-lbl">RPM</div><div'
                    f' class="kpi-val">{rpm}</div></div>'
                ),
                (
                    '<div class="kpi-box"><div'
                    f' class="kpi-lbl">OEE</div><div'
                    f' class="kpi-val">{oee}</div></div>'
                ),
                "</div>",
                (
                    f'<div class="m-foot"><span>{note}</span><span>{upd}'
                    "</span></div>"
                ),
                "</div>",
            )

            with col:
                st.markdown(single_line_card, unsafe_allow_html=True)
                if st.button(
                    f"Edit {raw_mid}",
                    key=f"edit_btn_{raw_mid}",
                    use_container_width=True,
                ):
                    st.session_state.selected_machine = raw_mid
                    st.rerun()


render_shopfloor()