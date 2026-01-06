# Database Schema

## Entity Relationship Diagram

```
┌──────────────────┐       ┌──────────────────────┐
│      users       │       │      workouts        │
├──────────────────┤       ├──────────────────────┤
│ id (PK)          │───┐   │ id (PK)              │
│ email            │   │   │ user_id (FK)         │◄──┐
│ password_hash    │   └──►│ name                 │   │
│ name             │       │ workout_type         │   │
│ height_in        │       │ template_type        │   │
│ weight_lb        │       │ total_time_seconds   │   │
│ created_at       │       │ round_count          │   │
│ updated_at       │       │ notes                │   │
└──────────────────┘       │ performed_at         │   │
                           │ created_at           │   │
                           │ updated_at           │   │
                           └──────────┬───────────┘   │
                                      │               │
           ┌──────────────────────────┼───────────────┤
           │                          │               │
           ▼                          ▼               │
┌──────────────────────┐   ┌──────────────────┐      │
│      movements       │   │      splits      │      │
├──────────────────────┤   ├──────────────────┤      │
│ id (PK)              │   │ id (PK)          │      │
│ workout_id (FK)      │   │ workout_id (FK)  │      │
│ movement_type        │   │ round_number     │      │
│ modality             │   │ time_seconds     │      │
│ load_lb              │   │ created_at       │      │
│ reps                 │   └──────────────────┘      │
│ calories             │                              │
│ order_index          │                              │
│ created_at           │                              │
└──────────────────────┘                              │
                                                      │
┌──────────────────────┐   ┌──────────────────────┐  │
│   computed_metrics   │   │    domain_scores     │  │
├──────────────────────┤   ├──────────────────────┤  │
│ id (PK)              │   │ id (PK)              │  │
│ workout_id (FK)      │   │ user_id (FK)         │──┘
│ total_ewu            │   │ domain               │
│ density_power_min    │   │ raw_value            │
│ density_power_sec    │   │ normalized_score     │
│ active_power         │   │ sample_count         │
│ repeatability_drift  │   │ confidence           │
│ repeatability_spread │   │ updated_at           │
│ lift_share           │   └──────────────────────┘
│ machine_share        │
│ computed_at          │   ┌──────────────────────┐
└──────────────────────┘   │    distributions     │
                           ├──────────────────────┤
                           │ id (PK)              │
                           │ user_id (FK)         │
                           │ workout_type         │
                           │ metric_name          │
                           │ values_json          │
                           │ window_days          │
                           │ updated_at           │
                           └──────────────────────┘
```

---

## Table Definitions

### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    height_in INTEGER,
    weight_lb INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

### workouts
```sql
CREATE TYPE workout_type AS ENUM (
    'sprint',
    'threshold', 
    'endurance',
    'interval',
    'chipper',
    'strength',
    'monostructural'
);

CREATE TYPE template_type AS ENUM (
    'interval',
    'chipper',
    'sprint_test',
    'threshold',
    'endurance',
    'strength_session',
    'monostructural_test',
    'custom'
);

CREATE TABLE workouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    workout_type workout_type,
    template_type template_type NOT NULL,
    total_time_seconds INTEGER NOT NULL,
    round_count INTEGER DEFAULT 1,
    notes TEXT,
    performed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_workouts_user_id ON workouts(user_id);
CREATE INDEX idx_workouts_performed_at ON workouts(performed_at);
CREATE INDEX idx_workouts_type ON workouts(workout_type);
CREATE INDEX idx_workouts_user_performed ON workouts(user_id, performed_at DESC);
```

### movements
```sql
CREATE TYPE movement_type AS ENUM (
    -- Machine/Monostructural
    'echo_bike',
    'rower',
    'ski_erg',
    'run',
    'assault_bike',
    
    -- Barbell
    'power_snatch',
    'squat_snatch',
    'power_clean',
    'squat_clean',
    'clean_and_jerk',
    'deadlift',
    'back_squat',
    'front_squat',
    'overhead_squat',
    'strict_press',
    'push_press',
    'push_jerk',
    'split_jerk',
    'thruster',
    'hang_power_snatch',
    'hang_power_clean',
    'hang_squat_snatch',
    'hang_squat_clean',
    'sumo_deadlift',
    'romanian_deadlift',
    
    -- Gymnastics (placeholder)
    'pull_up',
    'chest_to_bar',
    'muscle_up',
    'bar_muscle_up',
    'toes_to_bar',
    'handstand_push_up',
    'box_jump',
    'box_jump_over',
    'burpee',
    'burpee_box_jump_over',
    'double_under',
    'wall_ball',
    'kettlebell_swing',
    'dumbbell_snatch',
    'dumbbell_clean'
);

CREATE TYPE modality AS ENUM (
    'machine',
    'lift',
    'gymnastics'
);

CREATE TABLE movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workout_id UUID NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    movement_type movement_type NOT NULL,
    modality modality NOT NULL,
    load_lb DECIMAL(6,2),
    reps INTEGER NOT NULL,
    calories INTEGER,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_movements_workout_id ON movements(workout_id);
CREATE INDEX idx_movements_type ON movements(movement_type);
```

### splits
```sql
CREATE TABLE splits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workout_id UUID NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL,
    time_seconds DECIMAL(8,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(workout_id, round_number)
);

CREATE INDEX idx_splits_workout_id ON splits(workout_id);
```

### computed_metrics
```sql
CREATE TABLE computed_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workout_id UUID UNIQUE NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    total_ewu DECIMAL(10,2) NOT NULL,
    density_power_min DECIMAL(10,4) NOT NULL,
    density_power_sec DECIMAL(10,6) NOT NULL,
    active_power DECIMAL(10,4),
    repeatability_drift DECIMAL(6,4),
    repeatability_spread DECIMAL(6,4),
    lift_share DECIMAL(5,4) NOT NULL,
    machine_share DECIMAL(5,4) NOT NULL,
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_metrics_workout_id ON computed_metrics(workout_id);
```

### domain_scores
```sql
CREATE TYPE domain_type AS ENUM (
    'strength_output',
    'monostructural_output',
    'mixed_modal_capacity',
    'sprint_power_capacity',
    'repeatability'
);

CREATE TYPE confidence_level AS ENUM (
    'no_data',
    'low',
    'medium',
    'high'
);

CREATE TABLE domain_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    domain domain_type NOT NULL,
    raw_value DECIMAL(10,4),
    normalized_score DECIMAL(5,2),
    sample_count INTEGER DEFAULT 0,
    confidence confidence_level DEFAULT 'no_data',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, domain)
);

CREATE INDEX idx_domain_scores_user_id ON domain_scores(user_id);
```

### distributions
```sql
CREATE TABLE distributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workout_type workout_type NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    values_json JSONB NOT NULL DEFAULT '[]',
    window_days INTEGER DEFAULT 180,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, workout_type, metric_name)
);

CREATE INDEX idx_distributions_user_id ON distributions(user_id);
CREATE INDEX idx_distributions_lookup ON distributions(user_id, workout_type, metric_name);
```

---

## JSON Schema for distributions.values_json

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "value": { "type": "number" },
      "workout_id": { "type": "string", "format": "uuid" },
      "performed_at": { "type": "string", "format": "date-time" }
    },
    "required": ["value", "workout_id", "performed_at"]
  }
}
```

Example:
```json
[
  {"value": 45.2, "workout_id": "uuid1", "performed_at": "2024-01-15T10:00:00Z"},
  {"value": 48.7, "workout_id": "uuid2", "performed_at": "2024-01-18T09:30:00Z"},
  {"value": 42.1, "workout_id": "uuid3", "performed_at": "2024-01-22T11:00:00Z"}
]
```

---

## Indexes Summary

| Table | Index | Purpose |
|-------|-------|---------|
| users | idx_users_email | Login lookup |
| workouts | idx_workouts_user_id | User's workouts |
| workouts | idx_workouts_performed_at | Date range queries |
| workouts | idx_workouts_type | Type filtering |
| workouts | idx_workouts_user_performed | History pagination |
| movements | idx_movements_workout_id | Workout details |
| movements | idx_movements_type | Movement analysis |
| splits | idx_splits_workout_id | Workout splits |
| computed_metrics | idx_metrics_workout_id | Quick metric lookup |
| domain_scores | idx_domain_scores_user_id | Radar chart |
| distributions | idx_distributions_lookup | Percentile calc |

---

## Migration Strategy

### Initial Migration (001_initial)
1. Create all ENUM types
2. Create users table
3. Create workouts table
4. Create movements table
5. Create splits table
6. Create computed_metrics table
7. Create domain_scores table
8. Create distributions table
9. Create all indexes

### Future Migrations
- 002_add_gymnastics_ewu: Add gymnastics_ewu column to computed_metrics
- 003_add_hr_data: Add heart_rate tables (v2)
- 004_add_equipment: Add equipment/scaling tables
