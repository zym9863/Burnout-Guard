[🇬🇧 English](./README-EN.md) | [🇨🇳 中文](./README.md)

# 🛡️ Burnout Guard (耗尽卫士)

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A FastAPI-based cognitive load monitoring and intervention scheduling system to help developers prevent burnout.

## ✨ Features

### 🧠 Cognitive Load Aggregation

- **Multi-source data** — supports GitHub activity, calendar events, screen time, and other sources
- **Real-time energy slot calculation** — computes current energy level (0-100) using a weighted algorithm
- **Fatigue tracking** — accounts for cumulative fatigue based on continuous work duration

### ⏰ Forced Blocking & Recovery Scheduling

- **Automatic intervention triggers** — triggers interventions when energy is too low or fatigue is too high
- **Webhook notifications** — supports registering multiple webhooks to receive intervention notifications
- **Smart recovery schedules** — dynamically generates personalized recovery plans based on fatigue level

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Install

```bash
# Clone the repository
git clone https://github.com/zym9863/burnout-guard.git
cd burnout-guard

# Install dependencies
uv sync
```

### Run

```bash
# Start the development server
uv run uvicorn main:app --reload --port 8000
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to view the interactive API documentation.

## 📚 API Endpoints

### Data Input

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/data/github` | POST | Submit GitHub activity data |
| `/api/data/calendar` | POST | Submit calendar event data |
| `/api/data/screen` | POST | Submit screen time data |

### Energy Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/energy` | GET | Get the current energy slot |
| `/api/fatigue` | GET | Get the fatigue index |
| `/api/status` | GET | Get a full status summary |

### Intervention Scheduling

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/webhook/register` | POST | Register a webhook endpoint |
| `/api/webhook/{id}` | DELETE | Unregister a webhook |
| `/api/webhook` | GET | List registered webhooks |
| `/api/recovery-schedule` | GET | Get the recovery schedule |
| `/api/intervention/trigger` | POST | Manually trigger an intervention |
| `/api/intervention/history` | GET | Get intervention history |

## 🔧 Configuration

Configurable via environment variables or a `.env` file (prefix `BURNOUT_`):

| Variable | Default | Description |
|---|---:|---|
| `BURNOUT_GITHUB_WEIGHT` | 0.35 | GitHub activity weight |
| `BURNOUT_CALENDAR_WEIGHT` | 0.35 | Calendar events weight |
| `BURNOUT_SCREEN_WEIGHT` | 0.30 | Screen time weight |
| `BURNOUT_ENERGY_CRITICAL_THRESHOLD` | 20.0 | Energy critical threshold |
| `BURNOUT_FATIGUE_CRITICAL_THRESHOLD` | 80.0 | Fatigue critical threshold |

## 📐 Algorithm

### Energy Slot Calculation

```
energy = 100 - (github_weight × github_load 
              + calendar_weight × calendar_load 
              + screen_weight × screen_load)
```

### Fatigue Index Calculation

```
fatigue = base_fatigue × (1 + duration_factor × hours_worked)

where: base_fatigue = 100 - energy
```

## 📁 Project Structure

```
Burnout-Guard/
├── main.py                    # FastAPI app entrypoint
├── pyproject.toml             # Project configuration
├── app/
│   ├── core/                  # Core configuration
│   │   └── config.py          # App configuration
│   ├── models/                # Pydantic data models
│   │   ├── data_input.py      # Data input models
│   │   ├── energy.py          # Energy models
│   │   └── intervention.py    # Intervention scheduling models
│   ├── services/              # Business logic services
│   │   ├── aggregator.py      # Cognitive load aggregation
│   │   └── scheduler.py       # Intervention scheduler
│   └── routers/               # API routers
│       ├── data.py            # Data input routes
│       ├── energy.py          # Energy routes
│       └── intervention.py    # Intervention routes
```

## 🤝 Contributing

Issues and pull requests are welcome!

## 📄 License

This project is licensed under the MIT License.
