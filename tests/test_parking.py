from datetime import datetime, timedelta
import pytest
from parking_logic import create_parking_slots, find_available_slot, park_vehicle, remove_vehicle, calculate_fee, get_parking_statistics

def test_create_parking_slots():
    slots = create_parking_slots(3)
    assert len(slots) == 3
    assert all(slot["status"] == "Available" for slot in slots)

def test_negative_slot_count_rejected():
    with pytest.raises(ValueError):
        create_parking_slots(-1)

def test_find_available_slot_returns_first_available():
    assert find_available_slot(create_parking_slots(2))["slot_id"] == 1

def test_park_vehicle_assigns_first_slot():
    slots = create_parking_slots(2)
    success, _ = park_vehicle(slots, "tn 38 ab 1234")
    assert success and slots[0]["vehicle_number"] == "TN 38 AB 1234"

def test_duplicate_vehicle_is_rejected():
    slots = create_parking_slots(2)
    assert park_vehicle(slots, "TN01AB1234")[0]
    assert not park_vehicle(slots, "tn01ab1234")[0]

def test_empty_vehicle_number_is_rejected():
    assert not park_vehicle(create_parking_slots(2), " ")[0]

def test_full_parking_lot_rejects_entry():
    slots = create_parking_slots(1)
    park_vehicle(slots, "CAR1")
    assert not park_vehicle(slots, "CAR2")[0]

def test_fee_is_minimum_one_hour():
    entry = datetime(2025, 1, 1, 10, 0)
    assert calculate_fee(entry, entry + timedelta(minutes=10), 30) == 30

def test_fee_rounds_partial_hours_up():
    entry = datetime(2025, 1, 1, 10, 0)
    assert calculate_fee(entry, entry + timedelta(hours=1, minutes=1), 30) == 60

def test_fee_rejects_exit_before_entry():
    entry = datetime(2025, 1, 1, 10, 0)
    with pytest.raises(ValueError):
        calculate_fee(entry, entry - timedelta(minutes=1), 30)

def test_fee_rejects_negative_rate():
    entry = datetime(2025, 1, 1, 10, 0)
    with pytest.raises(ValueError):
        calculate_fee(entry, entry, -1)

def test_remove_vehicle_releases_slot():
    slots = create_parking_slots(1)
    park_vehicle(slots, "CAR1")
    success, fee, _ = remove_vehicle(slots, "CAR1", datetime.now() + timedelta(minutes=5))
    assert success and fee >= 0 and slots[0]["status"] == "Available"

def test_remove_unknown_vehicle():
    success, fee, _ = remove_vehicle(create_parking_slots(2), "MISSING")
    assert not success and fee == 0.0

def test_statistics_for_empty_lot():
    assert get_parking_statistics([]) == {"total": 0, "occupied": 0, "available": 0, "occupancy_percent": 0.0}

def test_statistics_after_parking():
    slots = create_parking_slots(4)
    park_vehicle(slots, "CAR1")
    stats = get_parking_statistics(slots)
    assert stats["occupied"] == 1 and stats["available"] == 3 and stats["occupancy_percent"] == 25.0
