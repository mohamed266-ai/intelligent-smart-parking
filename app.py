"""Streamlit interface for the Intelligent Smart Parking Management System."""
from datetime import datetime
import pandas as pd
import streamlit as st

from parking_logic import (
    create_parking_slots,
    park_vehicle,
    remove_vehicle,
    calculate_fee,
    get_parking_statistics,
    get_active_vehicles,
)
from analytics import (
    slots_to_dataframe,
    occupancy_chart,
    occupancy_by_slot_chart,
    activity_to_dataframe,
    make_activity_record,
)

st.set_page_config(
    page_title="Smart Parking System",
    page_icon="🅿️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {font-size: 2rem; font-weight: 750; margin-bottom: 0.15rem;}
    .subtitle {color: #64748b; margin-bottom: 1.2rem;}
    .slot-label {font-size: 0.76rem; color: #64748b; margin-bottom: 0.15rem;}
    .slot-number {font-size: 1.1rem; font-weight: 750; margin-bottom: 0.25rem;}
    .slot-status {font-size: 0.78rem; font-weight: 650;}
    .slot-vehicle {font-size: 0.72rem; color: #475569; overflow-wrap: anywhere;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">🅿️ Intelligent Smart Parking Management System</div>'
    '<div class="subtitle">Parking allocation, vehicle entry/exit, fee calculation, and occupancy analytics.</div>',
    unsafe_allow_html=True,
)

# Keep simulated state during Streamlit reruns in this browser session.
if "parking_slots" not in st.session_state:
    st.session_state.parking_slots = create_parking_slots(40)
if "parking_activity" not in st.session_state:
    st.session_state.parking_activity = []

slots = st.session_state.parking_slots
activity = st.session_state.parking_activity

with st.sidebar:
    st.header("Control panel")
    st.caption("This version uses simulated parking data.")
    hourly_rate = st.number_input(
        "Hourly parking rate (₹)", min_value=0.0, value=30.0, step=5.0
    )
    st.divider()
    if st.button("Reset parking lot", width="stretch"):
        st.session_state.parking_slots = create_parking_slots(40)
        st.session_state.parking_activity = []
        st.rerun()
    st.caption("Reset clears the current simulated session.")

stats = get_parking_statistics(slots)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total spaces", stats["total"])
k2.metric("Occupied", stats["occupied"], delta=None)
k3.metric("Available", stats["available"])
k4.metric("Occupancy", f'{stats["occupancy_percent"]:.1f}%')

tab_dashboard, tab_entry, tab_exit, tab_reports = st.tabs(
    ["Dashboard", "Vehicle Entry", "Vehicle Exit", "Reports"]
)

with tab_dashboard:
    st.subheader("Parking overview")
    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(occupancy_chart(slots), width="stretch")
    with right:
        st.plotly_chart(occupancy_by_slot_chart(slots), width="stretch")

    st.subheader("Live parking map")
    st.caption("🟢 Available · 🔴 Occupied. The map is simulated and updates after each entry or exit.")
    columns_per_row = 8

    for start in range(0, len(slots), columns_per_row):
        row_slots = slots[start:start + columns_per_row]
        row = st.columns(columns_per_row, gap="small")
        for index, slot in enumerate(row_slots):
            occupied = slot["status"] == "Occupied"
            color = "#FEE2E2" if occupied else "#DCFCE7"
            border = "#EF4444" if occupied else "#22C55E"
            icon = "🚗" if occupied else "🅿️"
            status_text = "OCCUPIED" if occupied else "AVAILABLE"
            vehicle = slot.get("vehicle_number") or "No vehicle"
            with row[index]:
                st.markdown(
                    f"""
                    <div style="
                        min-height: 104px;
                        box-sizing: border-box;
                        padding: 10px 7px;
                        margin-bottom: 8px;
                        border: 1px solid {border};
                        border-left: 5px solid {border};
                        border-radius: 10px;
                        background: {color};
                        text-align: center;
                    ">
                      <div style="font-size: 1.35rem;">{icon}</div>
                      <div style="font-size: 0.9rem; font-weight: 750;">Slot {slot['slot_id']:02d}</div>
                      <div style="font-size: 0.68rem; font-weight: 700; color: {border};">{status_text}</div>
                      <div style="font-size: 0.68rem; color: #475569; overflow-wrap: anywhere;">{vehicle}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.subheader("Vehicles currently parked")
    active = get_active_vehicles(slots)
    if active:
        active_df = pd.DataFrame(active)
        active_df["entry_time"] = active_df["entry_time"].astype(str)
        st.dataframe(active_df, width="stretch", hide_index=True)
    else:
        st.info("No vehicles are currently parked. Use Vehicle Entry to simulate a new arrival.")

with tab_entry:
    st.subheader("Register vehicle entry")
    st.write("The system assigns the first available parking space.")
    with st.form("entry_form", clear_on_submit=True):
        vehicle_number = st.text_input(
            "Vehicle registration number",
            placeholder="Example: TN 38 AB 1234",
            help="Letters and numbers are accepted; spaces are normalized.",
        )
        submitted = st.form_submit_button("Park vehicle", width="stretch")
    if submitted:
        success, message = park_vehicle(slots, vehicle_number)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

with tab_exit:
    st.subheader("Register vehicle exit")
    active_vehicles = get_active_vehicles(slots)
    vehicle_options = [item["vehicle_number"] for item in active_vehicles]
    if not vehicle_options:
        st.info("There are no vehicles to check out. Register a vehicle in Vehicle Entry first.")
    else:
        selected_vehicle = st.selectbox("Select vehicle", vehicle_options)
        if st.button("Check out vehicle", width="stretch"):
            matching_slot = next(
                item for item in slots
                if item["vehicle_number"] == selected_vehicle
            )
            entry_time = matching_slot["entry_time"]
            slot_id = matching_slot["slot_id"]
            exit_time = datetime.now()
            fee = calculate_fee(entry_time, exit_time, hourly_rate)
            success, _, message = remove_vehicle(
                slots, selected_vehicle, exit_time=exit_time
            )
            if success:
                activity.append(
                    make_activity_record(
                        selected_vehicle, slot_id, entry_time, exit_time, fee
                    )
                )
                st.success(message)
                st.metric("Parking fee", f"₹{fee:.2f}")
                st.rerun()
            else:
                st.error(message)

with tab_reports:
    st.subheader("Parking slot report")
    st.dataframe(slots_to_dataframe(slots), width="stretch", hide_index=True)

    st.subheader("Completed parking sessions")
    activity_df = activity_to_dataframe(activity)
    if activity_df.empty:
        st.info("No completed sessions yet. Check out a vehicle to create a record.")
    else:
        st.dataframe(activity_df, width="stretch", hide_index=True)
        revenue = float(activity_df["Fee (INR)"].sum())
        st.metric("Recorded revenue", f"₹{revenue:.2f}")
        st.download_button(
            "Download activity CSV",
            data=activity_df.to_csv(index=False).encode("utf-8"),
            file_name="parking_activity.csv",
            mime="text/csv",
            width="stretch",
        )

st.divider()
st.caption("Portfolio demo · Simulated data only · Parking data is session-based, not permanently stored.")
