# CrossFit Performance App - Product Specification

## Executive Summary

A mobile-first web application that provides objective, physics-style measurement of mixed-modal CrossFit output through **Effective Work Units (EWU)** and grouped physical-performance domain scores displayed as an "Athlete Completeness" radar chart.

---

## 1. Core Value Proposition

### Problem Statement
Current CrossFit apps focus on workout logging and leaderboards but fail to:
- Compute unified, objective performance metrics across mixed modalities
- Provide cross-workout comparison ("apples-to-apples")
- Track performance completeness across physical domains
- Improve accuracy over time with more data

### Solution
A performance measurement system that:
1. **EWU Language**: Standardized work accounting across modalities
2. **Density Power**: Work output over time (EWU/min)
3. **Repeatability Metrics**: Drift and spread analysis
4. **Workout Taxonomy**: Auto-classification for normalized comparison
5. **Confidence Scoring**: Accuracy improves with more logged sessions
6. **Exportable Data**: Full portability of athlete dataset

---

## 2. User Flows

### 2.1 Onboarding Flow
```
Landing Page → Sign Up → Profile Setup → Dashboard (Empty State)
```

### 2.2 Workout Logging Flow
```
Dashboard → Log Workout → Select Template → Enter Movements → 
Enter Time/Splits → Review & Save → Results Screen
```

### 2.3 Review Performance Flow
```
Dashboard → View Radar Chart → Drill into Domain → View Trends
```

### 2.4 History & Export Flow
```
Dashboard → History → Filter/Search → Select Workout → View Details
Dashboard → Export → Select Format → Download
```

---

## 3. Pages & Screens

### 3.1 Authentication Pages
- **Landing/Login**: Sign in or create account
- **Register**: Email, password, name
- **Profile Setup**: Basic athlete info (height, weight - optional)

### 3.2 Dashboard (Home)
- **Athlete Completeness Radar**: 5-domain spider chart
  - Strength Output
  - Monostructural Output
  - Mixed-Modal Capacity
  - Sprint/Power Capacity
  - Repeatability
- **Confidence Indicators**: Per-domain sample size badges
- **Quick Stats**: Recent density power, total EWU this week
- **Trend Sparklines**: 7/30/90 day toggles
- **Quick Log CTA**: Prominent button to log workout

### 3.3 Log Workout Screen
- **Template Selection**:
  - Interval (EMOM/E3MOM)
  - Chipper
  - Sprint Test
  - Threshold
  - Endurance
  - Strength Session
  - Mono-structural Test
- **Movement Entry** (Dynamic form):
  - Movement type dropdown (Echo Bike, Power Snatch, etc.)
  - Load (lbs) - for barbell movements
  - Reps
  - Add/remove movement buttons
- **Time Entry**:
  - Total time (required)
  - Interval/Round count
  - Split times (optional, per round)
- **Notes**: Free text field
- **Submit Button**: Computes and saves

### 3.4 Workout Results Screen
- **Summary Card**:
  - Total EWU
  - Density Power (EWU/min)
  - Workout Type Tag
- **Detailed Metrics**:
  - Active Power (if splits provided)
  - Repeatability: Drift %, Spread %
  - Modality Share: Lift % vs Machine %
- **Domain Impact**: Which domains this workout updated
- **Historical Comparison**: Percentile rank for this workout type

### 3.5 History Page
- **Workout List**: Cards with date, name, EWU, type
- **Filters**:
  - Date range
  - Workout type
  - Movement tags
- **Search**: By workout name/notes
- **Sort**: By date, EWU, density power

### 3.6 Workout Detail Page
- Full breakdown of logged workout
- All computed metrics
- Edit/Delete options

### 3.7 Export Page
- Format selection: CSV or JSON
- Date range filter
- Download button

---

## 4. Data Fields

### 4.1 User Profile
| Field | Type | Required |
|-------|------|----------|
| id | UUID | Yes |
| email | String | Yes |
| password_hash | String | Yes |
| name | String | Yes |
| height_in | Integer | No |
| weight_lb | Integer | No |
| created_at | Timestamp | Yes |
| updated_at | Timestamp | Yes |

### 4.2 Workout
| Field | Type | Required |
|-------|------|----------|
| id | UUID | Yes |
| user_id | UUID | Yes |
| name | String | No |
| workout_type | Enum | Auto |
| template_type | Enum | Yes |
| total_time_seconds | Integer | Yes |
| round_count | Integer | No |
| notes | Text | No |
| performed_at | Timestamp | Yes |
| created_at | Timestamp | Yes |

### 4.3 Movement Entry
| Field | Type | Required |
|-------|------|----------|
| id | UUID | Yes |
| workout_id | UUID | Yes |
| movement_type | Enum | Yes |
| modality | Enum | Auto |
| load_lb | Float | Conditional |
| reps | Integer | Yes |
| calories | Integer | Conditional |
| order_index | Integer | Yes |

### 4.4 Split/Segment
| Field | Type | Required |
|-------|------|----------|
| id | UUID | Yes |
| workout_id | UUID | Yes |
| round_number | Integer | Yes |
| time_seconds | Float | Yes |

### 4.5 Computed Metrics
| Field | Type |
|-------|------|
| id | UUID |
| workout_id | UUID |
| total_ewu | Float |
| density_power_per_min | Float |
| density_power_per_sec | Float |
| active_power | Float (nullable) |
| repeatability_drift | Float (nullable) |
| repeatability_spread | Float (nullable) |
| lift_share | Float |
| machine_share | Float |
| computed_at | Timestamp |

### 4.6 Domain Score
| Field | Type |
|-------|------|
| id | UUID |
| user_id | UUID |
| domain | Enum |
| raw_value | Float |
| normalized_score | Float |
| sample_count | Integer |
| confidence | Enum |
| updated_at | Timestamp |

### 4.7 Distribution Data
| Field | Type |
|-------|------|
| id | UUID |
| user_id | UUID |
| workout_type | Enum |
| metric_name | String |
| values_json | JSON |
| window_days | Integer |
| updated_at | Timestamp |

---

## 5. MVP Scope

### In Scope (v1)
- User authentication (JWT)
- Workout logging with templates
- Movement types: Echo Bike, Barbell lifts
- EWU computation for bike + lifts
- Density power calculation
- Active power (with splits)
- Repeatability metrics
- Workout auto-typing
- 5-domain radar chart
- Confidence scoring per domain
- 7/30/90 day trends
- Workout history with filters
- CSV/JSON export

### Out of Scope (v1)
- Heart rate integration
- Row/Run/Ski erg (placeholder in engine)
- Gymnastics movements
- Social features / leaderboards
- Coaching features
- Native mobile apps (PWA only)

---

## 6. Movement Types (MVP)

### Machine/Monostructural
- Echo Bike (calories)
- Rower (calories) - placeholder
- Ski Erg (calories) - placeholder
- Run (meters) - placeholder

### Barbell/Lift
- Power Snatch
- Squat Snatch
- Power Clean
- Squat Clean
- Clean & Jerk
- Deadlift
- Back Squat
- Front Squat
- Overhead Squat
- Strict Press
- Push Press
- Push Jerk
- Thruster

### Gymnastics (Placeholder)
- Pull-up
- Chest-to-Bar
- Muscle-up
- Toes-to-Bar
- Handstand Push-up
- Box Jump

---

## 7. Workout Type Heuristics

| Type | Heuristic |
|------|-----------|
| Sprint | total_time < 5 min |
| Threshold | 5 min <= total_time < 15 min |
| Endurance | total_time >= 15 min |
| Interval | round_count > 1 AND has splits |
| Chipper | many movements (>4) AND single pass |
| Strength | >80% lift share AND low reps per set |
| Mono-structural | 100% machine share |

---

## 8. Success Metrics

- **Logging Speed**: < 60 seconds to log a workout
- **Accuracy**: EWU calculations match manual verification
- **Engagement**: Users log 3+ workouts/week
- **Confidence Growth**: Domain confidence reaches "high" within 30 days

---

## 9. Technical Requirements

- Mobile-first responsive design
- Works offline (PWA)
- Sub-second computation time
- Secure authentication
- Data export compliance
- Accessible (WCAG 2.1 AA)
