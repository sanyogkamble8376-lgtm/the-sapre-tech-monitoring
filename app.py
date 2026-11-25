from html import escape
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="The Sapre Tech | Machine Monitoring",
    layout="wide",
)

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================
if "compact_mode" not in st.session_state:
    st.session_state.compact_mode = False

if "selected_machine" not in st.session_state:
    st.session_state.selected_machine = None


def safe_int(val, default=0):
    try:
        if val is None or pd.isna(val):
            return default
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return default


# =====================================================
# CUSTOM CSS (तुमचा मूळ CSS इथे ठेवू शकता)
# =====================================================
st.markdown(
    """
    <style>
    .m-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
        color: #f8fafc;
    }
    .m-card.compact {
        padding: 10px;
    }
    .m-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 8px;
    }
    .m-id {
        font-size: 16px;
        font-weight: 700;
    }
    .m-sub {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 2px;
    }
    .pill {
        font-size: 11px;
        padding: 3px 9px;
        border-radius: 999px;
        font-weight: 600;
    }
    .pill-Running {
        background: rgba(34, 197, 94, 0.18);
        color: #4ade80;
    }
    .pill-Idle {
        background: rgba(234, 179, 8, 0.18);
        color: #facc15;
    }
    .pill-Alarm {
        background: rgba(239, 68, 68, 0.18);
        color: #f87171;
    }
    .banner-good {
        margin-top: 10px;
        padding: 6px 10px;
        border-radius: 8px;
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        font-size: 12px;
        font-weight: 600;
    }
    .banner-warn {
        margin-top: 10px;
        padding: 6px 10px;
        border-radius: 8px;
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        font-size: 12px;
        font-weight: 600;
    }
    .op-box {
        margin-top: 10px;
        padding: 10px;
        border-radius: 10px;
        background: #1e293b;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .op-name {
        font-size: 14px;
        font-weight: 600;
        margin-top: 2px;
    }
    .mini-tag {
        display: inline-block;
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 2px 6px;
        font-size: 11px;
        margin-left: 4px;
    }
    .prog-label {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #cbd5e1;
        margin-top: 10px;
    }
    .prog-track {
        width: 100%;
        height: 7px;
        background: #1e293b;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 5px;
    }
    .prog-fill {
        height: 100%;
        background: #22c55e;
    }
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
        margin-top: 10px;
    }
    .kpi-box {
        background: #1e293b;
        border-radius: 8px;
        padding: 6px;
        text-align: center;
    }
    .kpi-lbl {
        font-size: 11px;
        color: #94a3b8;
    }
    .kpi-val {
        font-size: 13px;
        font-weight: 700;
        margin-top: 2px;
    }
    .m-foot {
        display: flex;
        justify-content: space-between;
        font-size: 11px;
        color: #94a3b8;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# SAMPLE DATA (तुमचा खरा DataFrame `filtered` इथे वापरा)
# =====================================================
filtered = pd.DataFrame(
    [
        {
            "id": "CNC-01",
            "mtype": "CNC Turning",
            "program": "O1010_PART_01.NC",
            "status": "Running",
            "operator": "ऑपरेटर 1",
            "parts": 75,
            "target": 200,
            "rpm": 2200,
            "oee": "78%",
            "message": "",
            "note": "-",
            "updated": "14:40:21",
        },
        {
            "id": "CNC-02",
            "mtype": "CNC Turning",
            "program": "O1020_PART_02.NC",
            "status": "Running",
            "operator": "ऑपरेटर 2",
            "parts": 80,
            "target": 200,
            "rpm": 2250,
            "oee": "79%",
            "message": "",
            "note": "-",
            "updated": "14:40:21",
        },
        {
            "id": "CNC-03",
            "mtype": "CNC Turning",
            "program": "O1030_PART_03.NC",
            "status": "Running",
            "operator": "विक्रम माने",
            "parts": 85,
            "target": 200,
            "rpm": 2235,
            "oee": "77%",
            "message": "PLEASE IMPROVEMENT",
            "note": "-",
            "updated": "14:40:21",
        },
        {
            "id": "CNC-04",
            "mtype": "CNC Turning",
            "program": "O1040_PART_04.NC",
            "status": "Running",
            "operator": "संदीप पवार",
            "parts": 90,
            "target": 200,
            "rpm": 2280,
            "oee": "80%",
            "message": "GOOD WORKING",
            "note": "-",
            "updated": "14:40:21",
        },
    ]
)

st.title("The Sapre Tech")

if st.button("Toggle Compact Mode"):
    st.session_state.compact_mode = not st.session_state.compact_mode
    st.rerun()


# =====================================================
# MACHINE CARDS GRID - SINGLE LINE CLEAN HTML
# =====================================================
cols_per_row = 5 if st.session_state.compact_mode else 4

card_cls = (
    "m-card compact"
    if st.session_state.compact_mode
    else "m-card"
)

for start in range(0, len(filtered), cols_per_row):
    row_cols = st.columns(cols_per_row)
    chunk = filtered.iloc[start : start + cols_per_row]

    for col, (_, m) in zip(row_cols, chunk.iterrows()):
        raw_mid = str(m["id"]).strip()
        mid = escape(raw_mid)
        mtype = escape(str(m["mtype"]).strip())
        prog = escape(str(m["program"]).strip())

        status = str(m["status"]).strip()
        if status not in ["Running", "Idle", "Alarm"]:
            status = "Idle"

        op = escape(str(m["operator"]).strip())
        parts = max(safe_int(m["parts"]), 0)
        target = max(safe_int(m["target"], 1), 1)

        pct = min(int(round((parts / target) * 100)), 100)

        rpm = escape(str(m["rpm"]).strip())
        oee = escape(str(m["oee"]).strip())
        msg = str(m["message"]).strip()
        note = escape(str(m["note"]).strip())
        upd = escape(str(m["updated"]).strip())

        banner_html = ""
        if msg == "GOOD WORKING":
            banner_html = '<div class="banner-good">✔ GOOD WORKING</div>'
        elif msg == "PLEASE IMPROVEMENT":
            banner_html = '<div class="banner-warn">💬 PLEASE IMPROVEMENT</div>'

        raw_card_html = f"""
<div class="{card_cls}">
<div class="m-top">
<div>
<div class="m-id">{mid}</div>
<div class="m-sub">{mtype} • {prog}</div>
</div>
<span class="pill pill-{status}">{escape(status)}</span>
</div>
{banner_html}
<div class="op-box">
<div>
<div class="m-sub" style="margin-top:0;">ऑपरेटर</div>
<div class="op-name">{op}</div>
</div>
<div>
<span class="mini-tag">ऑप</span>
<span class="mini-tag">प्रो</span>
<span class="mini-tag">💬</span>
</div>
</div>
<div class="prog-label">
<span>Progress</span>
<span>{parts}/{target} ({pct}%)</span>
</div>
<div class="prog-track">
<div class="prog-fill" style="width:{pct}%;"></div>
</div>
<div class="kpi-row">
<div class="kpi-box">
<div class="kpi-lbl">Parts</div>
<div class="kpi-val">{parts}</div>
</div>
<div class="kpi-box">
<div class="kpi-lbl">RPM</div>
<div class="kpi-val">{rpm}</div>
</div>
<div class="kpi-box">
<div class="kpi-lbl">OEE</div>
<div class="kpi-val">{oee}</div>
</div>
</div>
<div class="m-foot">
<span>{note}</span>
<span>{upd}</span>
</div>
</div>
"""
        card_html = "".join(
            line.strip() for line in raw_card_html.splitlines() if line.strip()
        )

        with col:
            st.markdown(
                card_html,
                unsafe_allow_html=True,
            )

            if st.button(
                f"Edit {raw_mid}",
                key=f"edit_btn_{raw_mid}",
                use_container_width=True,
            ):
                st.session_state.selected_machine = raw_mid
                st.rerun(scope="fragment")