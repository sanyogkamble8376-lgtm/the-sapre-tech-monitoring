
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="THE SAPRE TECH",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 THE SAPRE TECH")
st.subheader("Smart 40 CNC / VMC Machine Monitoring")

st.markdown("---")

# Create 40 machines
machines = []

for i in range(1, 26):
    machines.append({
        "Machine ID": f"CNC-{i:02d}",
        "Type": "CNC",
        "Status": "OFFLINE",
        "Part Count": 0
    })

for i in range(1, 16):
    machines.append({
        "Machine ID": f"VMC-{i:02d}",
        "Type": "VMC",
        "Status": "OFFLINE",
        "Part Count": 0
    })

df = pd.DataFrame(machines)

# Summary
total = len(df)
running = len(df[df["Status"] == "RUNNING"])
idle = len(df[df["Status"] == "IDLE"])
alarm = len(df[df["Status"] == "ALARM"])
offline = len(df[df["Status"] == "OFFLINE"])

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Machines", total)
c2.metric("Running", running)
c3.metric("Idle", idle)
c4.metric("Alarm", alarm)
c5.metric("Offline", offline)

st.markdown("---")

# Machine filters
st.subheader("Machine Details")

machine_type = st.selectbox(
    "Select Machine Type",
    ["ALL", "CNC", "VMC"]
)

if machine_type != "ALL":
    df = df[df["Type"] == machine_type]

search = st.text_input("Search Machine ID")

if search:
    df = df[df["Machine ID"].str.contains(search, case=False)]

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Last Dashboard Refresh: " +
    datetime.now().strftime("%d-%m-%Y %H:%M:%S")
)

st.info(
    "Initial Dashboard: Machine values are currently OFFLINE. "
    "Live controller data integration will be added in the next steps."
)
