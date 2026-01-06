# API Design

## Base URL
```
https://api.crossfit-performance.app/api/v1
```

## Authentication
All endpoints except `/auth/register` and `/auth/login` require:
```
Authorization: Bearer <jwt_token>
```

---

## Endpoints

### Authentication

#### POST /auth/register
Create a new user account.

**Request:**
```json
{
  "email": "athlete@example.com",
  "password": "securePassword123",
  "name": "John Athlete",
  "height_in": 70,
  "weight_lb": 175
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "athlete@example.com",
  "name": "John Athlete",
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

#### POST /auth/login
Authenticate and receive JWT token.

**Request:**
```json
{
  "email": "athlete@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "athlete@example.com",
    "name": "John Athlete"
  }
}
```

#### GET /auth/me
Get current user profile.

**Response (200):**
```json
{
  "id": "uuid",
  "email": "athlete@example.com",
  "name": "John Athlete",
  "height_in": 70,
  "weight_lb": 175,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Workouts

#### POST /workouts
Log a new workout.

**Request:**
```json
{
  "name": "E3MOM Power Snatch Complex",
  "template_type": "interval",
  "total_time_seconds": 1094,
  "round_count": 6,
  "performed_at": "2024-01-15T10:00:00Z",
  "notes": "Felt strong, grip was good",
  "movements": [
    {
      "movement_type": "echo_bike",
      "calories": 10,
      "reps": 1,
      "order_index": 0
    },
    {
      "movement_type": "power_snatch",
      "load_lb": 95,
      "reps": 8,
      "order_index": 1
    },
    {
      "movement_type": "echo_bike",
      "calories": 10,
      "reps": 1,
      "order_index": 2
    }
  ],
  "splits": [
    {"round_number": 1, "time_seconds": 90},
    {"round_number": 2, "time_seconds": 88},
    {"round_number": 3, "time_seconds": 89},
    {"round_number": 4, "time_seconds": 89},
    {"round_number": 5, "time_seconds": 96},
    {"round_number": 6, "time_seconds": 94}
  ]
}
```

**Response (201):**
```json
{
  "workout": {
    "id": "uuid",
    "name": "E3MOM Power Snatch Complex",
    "workout_type": "interval",
    "template_type": "interval",
    "total_time_seconds": 1094,
    "round_count": 6,
    "performed_at": "2024-01-15T10:00:00Z",
    "movements": [...],
    "splits": [...]
  },
  "metrics": {
    "total_ewu": 211.2,
    "density_power_min": 11.58,
    "density_power_sec": 0.193,
    "active_power": 23.83,
    "repeatability_drift": 0.056,
    "repeatability_spread": 0.088,
    "lift_share": 0.432,
    "machine_share": 0.568
  },
  "domains_updated": ["mixed_modal_capacity", "repeatability"]
}
```

#### GET /workouts
List user's workouts with pagination and filters.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `workout_type` (string): Filter by type
- `start_date` (date): Filter from date
- `end_date` (date): Filter to date
- `movement_type` (string): Filter by movement

**Response (200):**
```json
{
  "workouts": [
    {
      "id": "uuid",
      "name": "E3MOM Power Snatch Complex",
      "workout_type": "interval",
      "total_time_seconds": 1094,
      "performed_at": "2024-01-15T10:00:00Z",
      "metrics_summary": {
        "total_ewu": 211.2,
        "density_power_min": 11.58
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

#### GET /workouts/{id}
Get workout details with all metrics.

**Response (200):**
```json
{
  "id": "uuid",
  "name": "E3MOM Power Snatch Complex",
  "workout_type": "interval",
  "template_type": "interval",
  "total_time_seconds": 1094,
  "round_count": 6,
  "performed_at": "2024-01-15T10:00:00Z",
  "notes": "Felt strong, grip was good",
  "movements": [
    {
      "id": "uuid",
      "movement_type": "echo_bike",
      "modality": "machine",
      "calories": 10,
      "reps": 1,
      "order_index": 0
    },
    {
      "id": "uuid",
      "movement_type": "power_snatch",
      "modality": "lift",
      "load_lb": 95,
      "reps": 8,
      "order_index": 1
    }
  ],
  "splits": [
    {"round_number": 1, "time_seconds": 90},
    {"round_number": 2, "time_seconds": 88}
  ],
  "metrics": {
    "total_ewu": 211.2,
    "density_power_min": 11.58,
    "density_power_sec": 0.193,
    "active_power": 23.83,
    "repeatability_drift": 0.056,
    "repeatability_spread": 0.088,
    "lift_share": 0.432,
    "machine_share": 0.568,
    "computed_at": "2024-01-15T10:30:00Z"
  },
  "percentile_rank": {
    "workout_type": "interval",
    "density_power_percentile": 72.5,
    "sample_size": 18
  }
}
```

#### PUT /workouts/{id}
Update a workout.

**Request:** Same structure as POST, partial updates allowed.

**Response (200):** Same as GET /workouts/{id}

#### DELETE /workouts/{id}
Delete a workout.

**Response (204):** No content

---

### Domains & Radar

#### GET /domains
Get all domain scores for radar chart.

**Response (200):**
```json
{
  "domains": [
    {
      "domain": "strength_output",
      "raw_value": 45.2,
      "normalized_score": 68.5,
      "sample_count": 12,
      "confidence": "medium"
    },
    {
      "domain": "monostructural_output",
      "raw_value": 52.1,
      "normalized_score": 75.2,
      "sample_count": 8,
      "confidence": "medium"
    },
    {
      "domain": "mixed_modal_capacity",
      "raw_value": 11.58,
      "normalized_score": 82.3,
      "sample_count": 22,
      "confidence": "high"
    },
    {
      "domain": "sprint_power_capacity",
      "raw_value": null,
      "normalized_score": null,
      "sample_count": 0,
      "confidence": "no_data"
    },
    {
      "domain": "repeatability",
      "raw_value": 0.042,
      "normalized_score": 71.8,
      "sample_count": 18,
      "confidence": "high"
    }
  ],
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### GET /domains/{domain}
Get detailed domain breakdown.

**Response (200):**
```json
{
  "domain": "mixed_modal_capacity",
  "raw_value": 11.58,
  "normalized_score": 82.3,
  "sample_count": 22,
  "confidence": "high",
  "contributing_workouts": [
    {
      "id": "uuid",
      "name": "E3MOM Power Snatch",
      "performed_at": "2024-01-15",
      "density_power": 11.58
    }
  ],
  "historical_scores": [
    {"date": "2024-01-01", "score": 75.2},
    {"date": "2024-01-08", "score": 78.4},
    {"date": "2024-01-15", "score": 82.3}
  ]
}
```

---

### Trends

#### GET /trends
Get trend data for charts.

**Query Parameters:**
- `period` (string): "7d" | "30d" | "90d" (default: "30d")
- `metrics` (string): Comma-separated metrics to include

**Response (200):**
```json
{
  "period": "30d",
  "density_power": {
    "data": [
      {"date": "2024-01-01", "value": 10.2},
      {"date": "2024-01-05", "value": 11.1},
      {"date": "2024-01-10", "value": 10.8}
    ],
    "average": 10.7,
    "trend": "up",
    "change_percent": 5.8
  },
  "repeatability": {
    "data": [
      {"date": "2024-01-01", "value": 0.068},
      {"date": "2024-01-05", "value": 0.055},
      {"date": "2024-01-10", "value": 0.042}
    ],
    "average": 0.055,
    "trend": "down",
    "change_percent": -38.2
  },
  "total_ewu": {
    "data": [...],
    "sum": 1245.6,
    "average_per_workout": 124.56
  }
}
```

---

### Export

#### GET /export/csv
Export all workout data as CSV.

**Query Parameters:**
- `start_date` (date): Optional start date filter
- `end_date` (date): Optional end date filter

**Response (200):**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="crossfit_export_2024-01-15.csv"

workout_id,name,type,date,total_time_sec,total_ewu,density_power_min,...
uuid1,E3MOM Power Snatch,interval,2024-01-15,1094,211.2,11.58,...
```

#### GET /export/json
Export all workout data as JSON.

**Query Parameters:**
- `start_date` (date): Optional start date filter  
- `end_date` (date): Optional end date filter
- `include_distributions` (bool): Include raw distribution data

**Response (200):**
```json
{
  "export_date": "2024-01-15T12:00:00Z",
  "user": {
    "id": "uuid",
    "name": "John Athlete"
  },
  "workouts": [...],
  "domain_scores": [...],
  "distributions": [...] 
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error",
  "errors": [
    {"field": "total_time_seconds", "message": "Must be positive integer"}
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "detail": "Workout not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "request_id": "uuid"
}
```

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| POST /auth/* | 10/minute |
| POST /workouts | 30/minute |
| GET /* | 100/minute |
| GET /export/* | 5/minute |
