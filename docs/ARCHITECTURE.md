# System Architecture

## Overview

The CrossFit Performance App follows a clean, layered architecture with clear separation between:
- **Data Layer**: Raw workout logs and user data
- **Computation Layer**: EWU engine, metrics, normalization
- **Presentation Layer**: API and Frontend

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React PWA)                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │Dashboard│ │Log Form │ │Results  │ │History  │ │ Export  │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
│       └───────────┴───────────┴───────────┴───────────┘        │
│                              │                                  │
│                    ┌─────────┴─────────┐                       │
│                    │   API Client      │                       │
│                    │   (React Query)   │                       │
│                    └─────────┬─────────┘                       │
└──────────────────────────────┼──────────────────────────────────┘
                               │ HTTPS/REST
┌──────────────────────────────┼──────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                    ┌─────────┴─────────┐                       │
│                    │   API Router      │                       │
│                    │   /api/v1/*       │                       │
│                    └─────────┬─────────┘                       │
│                              │                                  │
│  ┌───────────────────────────┼───────────────────────────────┐ │
│  │              SERVICE LAYER                                 │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │ Auth     │  │ Workout  │  │ Scoring  │  │ Export   │  │ │
│  │  │ Service  │  │ Service  │  │ Engine   │  │ Service  │  │ │
│  │  └──────────┘  └──────────┘  └────┬─────┘  └──────────┘  │ │
│  │                                    │                       │ │
│  │  ┌─────────────────────────────────┼─────────────────────┐│ │
│  │  │           SCORING ENGINE                              ││ │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ││ │
│  │  │  │ EWU      │ │ Metrics  │ │ Normalize│ │ Domain   │ ││ │
│  │  │  │ Computer │ │ Computer │ │ Engine   │ │ Scorer   │ ││ │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ ││ │
│  │  └───────────────────────────────────────────────────────┘│ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                    ┌─────────┴─────────┐                       │
│                    │   Data Access     │                       │
│                    │   Layer (SQLAlchemy)                      │
│                    └─────────┬─────────┘                       │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                      DATABASE (PostgreSQL)                      │
│  ┌────────┐ ┌─────────┐ ┌──────────┐ ┌────────────┐ ┌────────┐│
│  │ users  │ │workouts │ │movements │ │ splits     │ │metrics ││
│  └────────┘ └─────────┘ └──────────┘ └────────────┘ └────────┘│
│  ┌─────────────────┐ ┌───────────────────┐                     │
│  │ domain_scores   │ │ distributions     │                     │
│  └─────────────────┘ └───────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Breakdown

### 1. Frontend Modules

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/           # Buttons, inputs, cards
│   │   ├── charts/           # RadarChart, LineChart, Sparkline
│   │   ├── workout/          # WorkoutForm, MovementEntry, SplitInput
│   │   └── dashboard/        # DomainCard, ConfidenceBadge
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── LogWorkout.tsx
│   │   ├── WorkoutResults.tsx
│   │   ├── History.tsx
│   │   ├── WorkoutDetail.tsx
│   │   └── Export.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useWorkouts.ts
│   │   └── useDomainScores.ts
│   ├── api/
│   │   └── client.ts         # Axios/fetch wrapper
│   ├── store/
│   │   └── authStore.ts      # Zustand for auth state
│   └── utils/
│       ├── formatters.ts
│       └── validators.ts
```

### 2. Backend Modules

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── workouts.py
│   │       ├── metrics.py
│   │       ├── domains.py
│   │       └── exports.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── models/
│   │   ├── user.py
│   │   ├── workout.py
│   │   ├── movement.py
│   │   ├── split.py
│   │   ├── metrics.py
│   │   └── domain_score.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── workout.py
│   │   └── metrics.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── workout_service.py
│   │   └── export_service.py
│   ├── engine/
│   │   ├── ewu_calculator.py
│   │   ├── metrics_calculator.py
│   │   ├── workout_typer.py
│   │   ├── normalizer.py
│   │   └── domain_scorer.py
│   └── db/
│       ├── database.py
│       └── migrations/
```

---

## Data Flow

### Workout Logging Flow

```
1. User submits workout form
   │
   ▼
2. POST /api/v1/workouts
   │
   ▼
3. Validate input (Pydantic)
   │
   ▼
4. Store raw workout data
   ├── workouts table
   ├── movements table
   └── splits table (if provided)
   │
   ▼
5. Trigger Scoring Engine
   │
   ├── 5a. EWU Calculator
   │   └── Compute Bike_EWU + Lift_EWU
   │
   ├── 5b. Metrics Calculator
   │   ├── Total EWU
   │   ├── Density Power
   │   ├── Active Power (if splits)
   │   ├── Repeatability (drift, spread)
   │   └── Modality Share
   │
   ├── 5c. Workout Typer
   │   └── Auto-classify workout type
   │
   └── 5d. Store computed metrics
   │
   ▼
6. Update Domain Scores
   │
   ├── 6a. Update distributions
   │   └── Add to rolling window
   │
   ├── 6b. Normalizer
   │   └── Compute percentile scores
   │
   └── 6c. Domain Scorer
       ├── Update relevant domains
       └── Recalculate confidence
   │
   ▼
7. Return workout result with metrics
```

---

## Scoring Engine Architecture

### Component Responsibilities

#### EWU Calculator
```python
class EWUCalculator:
    """
    Computes Effective Work Units for each movement.
    
    Formulas:
    - Bike_EWU = echo_bike_calories
    - Lift_EWU = (load_lb * reps) / 50
    - Round_EWU = sum(movement_EWUs)
    
    Extensibility:
    - Row_EWU = row_calories * ROW_FACTOR (future)
    - Run_EWU = meters / RUN_DIVISOR (future)
    - Gymnastics_EWU = reps * MOVEMENT_FACTOR (future)
    """
```

#### Metrics Calculator
```python
class MetricsCalculator:
    """
    Computes derived metrics from EWU values.
    
    Metrics:
    - Total EWU: Sum of all Round_EWU
    - Density Power: Total_EWU / Total_Time
    - Active Power: Round_EWU / Bout_Time (per split)
    - Repeatability:
      - Drift: (avg_second_half - avg_first_half) / avg_first_half
      - Spread: (max_bout - min_bout) / avg_bout
    - Modality Share: lift_ewu / total_ewu
    """
```

#### Workout Typer
```python
class WorkoutTyper:
    """
    Auto-classifies workout based on structure.
    
    Heuristics:
    - Sprint: duration < 300s
    - Threshold: 300s <= duration < 900s
    - Endurance: duration >= 900s
    - Interval: has_splits AND round_count > 1
    - Chipper: movement_count > 4 AND round_count == 1
    - Strength: lift_share > 0.8 AND low_rep_per_set
    - Monostructural: machine_share == 1.0
    """
```

#### Normalizer
```python
class Normalizer:
    """
    Converts raw metrics to 0-100 scores via percentile.
    
    Process:
    1. Retrieve distribution for (user, workout_type, metric)
    2. Calculate percentile rank of new value
    3. Return normalized score (0-100)
    
    Special handling:
    - If sample_count < 5: return provisional score
    - Rolling window: last 180 days
    """
```

#### Domain Scorer
```python
class DomainScorer:
    """
    Updates Athlete Completeness domain scores.
    
    Domains:
    1. Strength Output: Updated by lift-heavy workouts
    2. Monostructural Output: Updated by mono workouts
    3. Mixed-Modal Capacity: Updated by density power
    4. Sprint/Power: Only from sub-5min tests
    5. Repeatability: Updated by drift/spread metrics
    
    Confidence:
    - Low: sample_count < 5
    - Medium: 5 <= sample_count < 15
    - High: sample_count >= 15
    """
```

---

## API Design Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/v1/auth/register | Create account |
| POST | /api/v1/auth/login | Get JWT token |
| GET | /api/v1/auth/me | Get current user |
| POST | /api/v1/workouts | Log new workout |
| GET | /api/v1/workouts | List workouts |
| GET | /api/v1/workouts/{id} | Get workout detail |
| PUT | /api/v1/workouts/{id} | Update workout |
| DELETE | /api/v1/workouts/{id} | Delete workout |
| GET | /api/v1/metrics/{workout_id} | Get computed metrics |
| GET | /api/v1/domains | Get all domain scores |
| GET | /api/v1/domains/{domain} | Get domain detail |
| GET | /api/v1/trends | Get trend data |
| GET | /api/v1/export/csv | Export as CSV |
| GET | /api/v1/export/json | Export as JSON |

---

## Database Design Principles

1. **Raw Data Immutability**: Never modify raw workout logs
2. **Computed Data Separation**: Metrics in separate tables
3. **Efficient Queries**: Indexes on user_id, performed_at, workout_type
4. **Audit Trail**: created_at, updated_at on all tables
5. **Soft Deletes**: Optional for workout recovery

---

## Security Architecture

### Authentication
- JWT tokens with 24h expiry
- Refresh token rotation
- Password hashing with bcrypt

### Authorization
- User can only access own data
- All endpoints require authentication (except login/register)

### Data Protection
- HTTPS only
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM

---

## Scalability Considerations

### Current Design (MVP)
- Single PostgreSQL database
- Synchronous request handling
- In-process computation

### Future Scaling
- Background jobs for heavy computation (Celery)
- Read replicas for dashboard queries
- Caching layer for radar chart data (Redis)
- Horizontal API scaling (stateless JWT)
