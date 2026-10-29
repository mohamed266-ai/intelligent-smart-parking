"""Analytics helpers for the Smart Parking System."""
from datetime import datetime
import pandas as pd
import plotly.express as px


def slots_to_dataframe(slots: list[dict]) -> pd.DataFrame:
    """Convert slot state into a table suitable for display."""
    rows = []
    for slot in slots:
        entry_time = slot.get("entry_time")
        rows.append({
            "Slot": slot["slot_id"],
            "Status": slot["status"],
            "Vehicle": slot.get("vehicle_number") or "—",
            "Entry time": entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(entry_time, datetime) else "—",
        })
    return pd.DataFrame(rows, columns=["Slot", "Status", "Vehicle", "Entry time"])


def occupancy_chart(slots: list[dict]):
    """Create a donut chart showing available versus occupied spaces."""
    occupied = sum(slot["status"] == "Occupied" for slot in slots)
    available = len(slots) - occupied
    frame = pd.DataFrame({
        "Status": ["Occupied", "Available"],
        "Spaces": [occupied, available],
    })
    figure = px.pie(
        frame,
        names="Status",
        values="Spaces",
        hole=0.58,
        title="Parking occupancy",
        color="Status",
        color_discrete_map={"Occupied": "#E45756", "Available": "#54A24B"},
    )
    figure.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="%{label}: %{value} spaces<extra></extra>",
    )
    figure.update_layout(
        margin=dict(l=10, r=10, t=55, b=10),
        legend_title_text="Space status",
        height=320,
    )
    return figure


def occupancy_by_slot_chart(slots: list[dict]):
    """Create a compact bar chart showing each slot's occupancy state."""
    frame = slots_to_dataframe(slots)
    frame["Occupied"] = frame["Status"].map({"Occupied": 1, "Available": 0})
    figure = px.bar(
        frame,
        x="Slot",
        y="Occupied",
        color="Status",
        title="Status by parking slot",
        color_discrete_map={"Occupied": "#E45756", "Available": "#54A24B"},
        category_orders={"Status": ["Available", "Occupied"]},
    )
    figure.update_layout(
        margin=dict(l=10, r=10, t=55, b=10),
        height=320,
        xaxis_title="Parking slot",
        yaxis_title="Occupied (1 = yes)",
        yaxis=dict(range=[0, 1.15], tickmode="array", tickvals=[0, 1]),
        legend_title_text="Space status",
    )
    figure.update_traces(hovertemplate="Slot %{x}<br>Occupied: %{y}<extra></extra>")
    return figure


def make_activity_record(vehicle_number: str, slot_id: int,
                         entry_time: datetime, exit_time: datetime,
                         fee: float) -> dict:
    """Build a completed parking activity record."""
    return {
        "Vehicle": vehicle_number,
        "Slot": slot_id,
        "Entry time": entry_time.isoformat(timespec="seconds"),
        "Exit time": exit_time.isoformat(timespec="seconds"),
        "Duration minutes": max(0, int((exit_time - entry_time).total_seconds() / 60)),
        "Fee (INR)": round(float(fee), 2),
    }


def activity_to_dataframe(activity: list[dict]) -> pd.DataFrame:
    """Convert activity history into a DataFrame."""
    columns = [
        "Vehicle", "Slot", "Entry time", "Exit time",
        "Duration minutes", "Fee (INR)",
    ]
    return pd.DataFrame(activity, columns=columns)
