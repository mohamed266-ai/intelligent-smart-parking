"""Core parking operations for the Smart Parking System."""
from datetime import datetime
import math

HOURLY_RATE = 30.0


def create_parking_slots(total_slots: int = 40) -> list[dict]:
    """Create a list of initially available parking spaces."""
    if total_slots < 0:
        raise ValueError("Total slots cannot be negative.")
    return [
        {"slot_id": number, "status": "Available",
         "vehicle_number": None, "entry_time": None}
        for number in range(1, total_slots + 1)
    ]


def find_available_slot(slots: list[dict]) -> dict | None:
    """Return the first available space, or None when full."""
    return next((slot for slot in slots if slot["status"] == "Available"), None)


def park_vehicle(slots: list[dict], vehicle_number: str):
    """Assign the first available space to a vehicle."""
    if not isinstance(vehicle_number, str) or not vehicle_number.strip():
        return False, "Enter a valid vehicle number."
    vehicle_number = vehicle_number.strip().upper()
    if any(slot["vehicle_number"] == vehicle_number for slot in slots):
        return False, "This vehicle is already parked."
    slot = find_available_slot(slots)
    if slot is None:
        return False, "Parking lot is full."
    slot["status"] = "Occupied"
    slot["vehicle_number"] = vehicle_number
    slot["entry_time"] = datetime.now()
    return True, f"Vehicle parked in slot {slot['slot_id']}."


def calculate_fee(entry_time: datetime, exit_time: datetime | None = None,
                  hourly_rate: float = HOURLY_RATE) -> float:
    """Charge at least one hour and round partial hours up."""
    if exit_time is None:
        exit_time = datetime.now()
    if exit_time < entry_time:
        raise ValueError("Exit time cannot precede entry time.")
    if hourly_rate < 0:
        raise ValueError("Hourly rate cannot be negative.")
    seconds = (exit_time - entry_time).total_seconds()
    hours = max(1, math.ceil(seconds / 3600))
    return round(hours * hourly_rate, 2)


def remove_vehicle(slots: list[dict], vehicle_number: str,
                   exit_time: datetime | None = None):
    """Release a vehicle's space and return (success, fee, message)."""
    if not isinstance(vehicle_number, str) or not vehicle_number.strip():
        return False, 0.0, "Enter a valid vehicle number."
    vehicle_number = vehicle_number.strip().upper()
    for slot in slots:
        if slot["vehicle_number"] == vehicle_number:
            fee = calculate_fee(slot["entry_time"], exit_time)
            slot_id = slot["slot_id"]
            slot.update({"status": "Available", "vehicle_number": None,
                         "entry_time": None})
            return True, fee, f"Vehicle exited from slot {slot_id}."
    return False, 0.0, "Vehicle not found in the parking lot."


def get_parking_statistics(slots: list[dict]) -> dict:
    """Return total, occupied, available, and occupancy percentage."""
    total = len(slots)
    occupied = sum(slot["status"] == "Occupied" for slot in slots)
    available = total - occupied
    percent = occupied / total * 100 if total else 0.0
    return {"total": total, "occupied": occupied, "available": available,
            "occupancy_percent": round(percent, 2)}


def get_active_vehicles(slots: list[dict]) -> list[dict]:
    """Return details for currently occupied spaces."""
    return [
        {"slot_id": slot["slot_id"], "vehicle_number": slot["vehicle_number"],
         "entry_time": slot["entry_time"]}
        for slot in slots if slot["status"] == "Occupied"
    ]
