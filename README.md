# CrossFit Performance App

A physics-based performance measurement system for CrossFit athletes. The core differentiator is objective, physics-style measurement of mixed-modal CrossFit output through **Effective Work Units (EWU)** and a 5-domain "Athlete Completeness" radar chart.

## Why This App Wins

Most CrossFit apps are workout logging + leaderboards. They don't compute a unified, objective performance model across mixed modalities. Our moat:

1. **EWU Output Language** - Cross-modality work accounting
2. **Density Power & Repeatability** - Performance metrics that matter
3. **Workout Taxonomy** - Apples-to-apples comparison
4. **Confidence Scoring** - Values get more accurate with more data
5. **Exportable Data** - Your data, your control

## Core Concepts

### EWU (Effective Work Unit)
- `Bike_EWU = echo_bike_calories`
- `Lift_EWU = (load_lb × reps) / 50`
- `Round_EWU = Bike_EWU + Lift_EWU`

### Output Metrics
- **Total EWU**: Sum of all work
- **Density Power**: EWU/min (work rate over total time)
- **Active Power**: EWU/min during active bouts (requires split times)
- **Repeatability**: Drift (fatigue) and Spread (consistency)
- **Modality Share**: Lift % vs Machine %

### Athlete Completeness (5 Domains)
1. **Strength Output** - From lift-heavy workouts
2. **Monostructural Output** - From pure machine work
3. **Mixed-Modal Capacity** - Density power in mixed workouts
4. **Sprint/Power Capacity** - Only from sub-5min tests
5. **Repeatability** - From split time analysis

## Quick Start

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment
```bash
docker-compose up --build
```

## Sample Workout Calculation

```
Workout: 6 sets E3MOM
- 10 cal Echo + 8 power snatch @95 + 10 cal Echo
- Split times: 90, 88, 89, 89, 96, 94 sec
- Total time: 18:14

Results:
┌─────────────────────────────────────────────────────────┐
│ TOTAL EWU:             211.20                           │
│ DENSITY POWER:          11.58 EWU/min                   │
│ ACTIVE POWER:           23.23 EWU/min                   │
│ REPEATABILITY:                                          │
│   - Drift:                4.5%                          │
│   - Spread:               8.8%                          │
│   - Consistency:         96.5%                          │
│ MODALITY SHARE:                                         │
│   - Lift:                43.2%                          │
│   - Machine:             56.8%                          │
│ WORKOUT TYPE:        INTERVAL                           │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS + Recharts
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Auth**: JWT tokens
- **Deployment**: Docker + nginx

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/           # REST endpoints
│   │   ├── core/             # Config, security
│   │   ├── db/               # Database setup
│   │   ├── engine/           # Scoring engine
│   │   │   ├── ewu_calculator.py
│   │   │   ├── metrics_calculator.py
│   │   │   ├── workout_typer.py
│   │   │   ├── normalizer.py
│   │   │   └── domain_scorer.py
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic
│   └── seed_data.py          # Example calculation
├── frontend/
│   └── src/
│       ├── components/       # Reusable UI
│       ├── pages/            # Route pages
│       ├── api/              # API client
│       └── store/            # Auth state
├── docs/
│   ├── PRODUCT_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   └── API_DESIGN.md
└── docker-compose.yml
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/v1/auth/register | Create account |
| POST | /api/v1/auth/login | Get JWT token |
| GET | /api/v1/auth/me | Get current user |
| POST | /api/v1/workouts | Log workout |
| GET | /api/v1/workouts | List workouts |
| GET | /api/v1/workouts/{id} | Get workout detail |
| GET | /api/v1/domains | Get radar chart data |
| GET | /api/v1/domains/trends | Get trend data |
| GET | /api/v1/export/csv | Export as CSV |
| GET | /api/v1/export/json | Export as JSON |

## MVP Features

- [x] User authentication (JWT)
- [x] Workout logging with templates
- [x] EWU computation engine
- [x] Density power & active power
- [x] Repeatability metrics
- [x] Workout auto-typing
- [x] 5-domain radar chart
- [x] Confidence scoring
- [x] Trend charts (7/30/90d)
- [x] Workout history with filters
- [x] CSV/JSON export

## Future Enhancements

- Heart rate integration
- Row/Run/Ski erg support
- Gymnastics EWU calibration
- Social/leaderboard features
- Native mobile apps
- Coaching dashboard
