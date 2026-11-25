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


def safe_text(val, default="-"):
    if val is None or pd.isna(val):
        return default
    text = str(val).strip()
    return text if text else default


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
            "id": "CNC-17",
            "mtype": "CNC Turning",
            "program": "O1170_PART_17.NC",
            "status": "Running",
            "operator": "ऑपरेटर 17",
            "parts": 160,
            "target": 200,
            "rpm": 2150,
            "oee": "75%",
            "message": "",
            "note": "-",
            "updated": "14:40:21",
        },
        {
            "id": "CNC-18",
            "mtype": "CNC Turning",
            "program": "O1180_PART_18.NC",
            "status": "Idle",
            "operator": "सुरेश शिंदे",
            "parts": 160,
            "target": 200,
            "rpm": 0,
            "oee": "68%",
            "message": "PLEASE IMPROVEMENT",
            "note": "-",
            "updated": "14:40:21",
        },
        {
            "id": "CNC-19",
            "mtype": "CNC Turning",
            "program": "O1190_PART_19.NC",
            "status": "Running",
            "operator": "ऑपरेटर 19",
            "parts": 165,
            "target": 200,
            "rpm": 2400,
            "oee": "76%",
            "message": "",
            "note": "-",
            "updated": "14:40:21",
        },
        {
            "id": "CNC-20",
            "mtype": "CNC Turning",
            "program": "O1200_PART_20.NC",
            "status": "Running",
            "operator": "संदीप पवार",
            "parts": 170,
            "target": 200,
            "rpm": 3000,
            "oee": "74%",
            "message": "GOOD WORKING",
            "note": "-",
            "updated": "14:40:21",
        },
    ]
)

# =====================================================
# HEADER & CONTROLS
# =====================================================
st.title("The Sapre Tech")

top_left, top_right = st.columns([3, 1])
with top_left:
    st.caption("Shift 1 (Morning: 8 AM - 4 PM) • Live Machine Monitoring")
with top_right:
    if st.button(
        f"Compact: {'ON' if st.session_state.compact_mode else 'OFF'}",
        use_container_width=True,
    ):
        st.session_state.compact_mode = not st.session_state.compact_mode
        st.rerun()

st.divider()

# =====================================================
# MACHINE CARDS GRID (NATIVE STREAMLIT COMPONENTS)
# =====================================================
cols_per_row = 5 if st.session_state.compact_mode else 4

status_badge = {
    "Running": "🟢 Running",
    "Idle": "🟡 Idle",
    "Alarm": "🔴 Alarm",
}

for start in range(0, len(filtered), cols_per_row):
    row_cols = st.columns(cols_per_row)
    chunk = filtered.iloc[start : start + cols_per_row]

    for col, (_, m) in zip(row_cols, chunk.iterrows()):
        raw_mid = safe_text(m["id"], "MACHINE")
        mtype = safe_text(m["mtype"], "CNC")
        prog = safe_text(m["program"], "-")

        status = safe_text(m["status"], "Idle")
        if status not in status_badge:
            status = "Idle"

        op = safe_text(m["operator"], "-")
        parts = max(safe_int(m["parts"], 0), 0)
        target = max(safe_int(m["target"], 1), 1)
        pct = min(int(round((parts / target) * 100)), 100)

        rpm = safe_text(m["rpm"], "0")
        oee = safe_text(m["oee"], "0%")
        msg = safe_text(m["message"], "")
        note = safe_text(m["note"], "-")
        upd = safe_text(m["updated"], "-")

        with col:
            with st.container(border=True):
                head_l, head_r = st.columns([2, 1])
                with head_l:
                    st.markdown(f"### {raw_mid}")
                    st.caption(f"{mtype} • {prog}")
                with head_r:
                    st.markdown(f"**{status_badge[status]}**")

                if msg == "GOOD WORKING":
                    st.success("✔ GOOD WORKING")
                elif msg == "PLEASE IMPROVEMENT":
                    st.warning("💬 PLEASE IMPROVEMENT")
                elif msg:
                    st.info(msg)

                st.caption("ऑपरेटर")
                st.markdown(f"**{op}**  •  `ऑप` `प्रो` `💬`")

                st.caption(f"Progress: {parts}/{target} ({pct}%)")
                st.progress(pct / 100.0)

                k1, k2, k3 = st.columns(3)
                k1.metric("Parts", parts)
                k2.metric("RPM", rpm)
                k3.metric("OEE", oee)

                st.caption(f"Note: {note}  |  Updated: {upd}")

                if st.button(
                    f"Edit {raw_mid}",
                    key=f"edit_btn_{raw_mid}",
                    use_container_width=True,
                ):
                    st.session_state.selected_machine = raw_mid
                    st.toast(f"{raw_mid} निवडले आहे")