# Intelligent Smart Parking Management System

A beginner-friendly Python and Streamlit portfolio project that simulates parking-space allocation, vehicle entry and exit, parking fees, occupancy analytics, and CSV reports.

## Features
- Dashboard KPIs for total, occupied, available, and occupancy percentage
- Color-coded parking map with 40 simulated spaces
- Vehicle entry with duplicate-registration checks
- Vehicle exit and configurable hourly fee calculation
- Occupancy charts and current vehicle list
- Completed session history and CSV export
- Unit tests for core parking operations

## Technology
Python, Streamlit, Pandas, Plotly, Pytest

## Run locally
Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies and launch:
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Run tests:
```bash
python -m pytest -q
```

## Important limitation
This version uses Streamlit session state, so simulated parking data is not permanently stored. It is intended as a portfolio demo, not a production parking system.

## Future improvements
- SQLite persistence
- ESP32 and ultrasonic/IR sensor integration
- QR check-in and reservations
- Authentication and role-based access
- Deployment on Streamlit Community Cloud
