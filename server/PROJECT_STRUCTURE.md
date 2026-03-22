# Weather-Aware Food Recommendation System — Project Structure

> Entity Design v1.0 | 2026

---

## I. Tổng quan hệ thống

Hệ thống nhận 3 nhóm đầu vào **(Thời tiết · Vị trí · Cá nhân)**, chuyển đổi thành các vector chuẩn hóa, tính `PhysiologicalDemand`, áp ràng buộc, rồi chấm điểm và xếp hạng `Dish`.

```
Raw Input  →  3 Vectors  →  PhysiologicalDemand  →  Filter  →  Scoring  →  RankedDishList
```

---

## II. Cây thư mục dự án

```
app/
├── config.py                        # Cấu hình app, DB, Redis, Weather API keys, TTL
├── __init__.py
│
├── models/                          # SQLAlchemy ORM — ánh xạ database entities
│   ├── __init__.py
│   ├── ingredient.py                # Ingredient
│   ├── dish.py                      # Dish, DishIngredient (junction)
│   ├── user.py                      # PersonalInput (stored profile)
│   ├── recommendation.py            # RecommendationResult, RankedDish
│   ├── feedback.py                  # UserFeedback, UserPreferenceModel
│   ├── weather_cache.py             # WeatherCache (geo-cell, Redis-backed)
│   └── explanation.py               # ExplanationFragment
│
├── schemas/                         # Pydantic schemas — validation & serialization
│   ├── __init__.py
│   ├── inputs.py                    # WeatherInput, LocationInput, PersonalInput
│   ├── vectors.py                   # WeatherVector, LocationVector, PersonalVector
│   ├── demand.py                    # PhysiologicalDemand
│   ├── constraints.py               # ConstraintProfile, ConstraintRule
│   ├── dish.py                      # DishVector schema (computed)
│   └── recommendation.py            # RecommendationResult, RankedDish response
│
├── services/                        # Business logic — pipeline steps
│   ├── __init__.py
│   │
│   │   ── PIPELINE LAYER ──
│   ├── weather_service.py           # Bước 1+1.5: fetch Weather API + Geo-Cell Cache lookup
│   ├── location_service.py          # Bước 3: build LocationVector (climate_type, seasonality…)
│   ├── personal_service.py          # Bước 4: build PersonalVector (BMI, BMR, TDEE, flags)
│   ├── demand_service.py            # Bước 5: tổng hợp PhysiologicalDemand (12 chiều)
│   ├── constraint_service.py        # Bước 6: tạo ConstraintProfile từ disease_flags + diet
│   ├── filter_service.py            # Bước 7-8: lọc Ingredient Pool + Dish Pool (hard constraints)
│   ├── scoring_service.py           # Bước 9-11: tính DishVector + dot-product Score(dish)
│   ├── ranking_service.py           # Bước 12-14: FinalScore = 0.75×score + 0.15×taste + 0.10×season; top-K + fallback
│   ├── recommendation_service.py    # Bước 15: orchestrate toàn bộ pipeline, tạo RecommendationResult
│   │
│   │   ── LEARNING LAYER (Lớp 3) ──
│   ├── feedback_service.py          # Ghi UserFeedback, cập nhật SessionState (Redis)
│   ├── learning_service.py          # EMA update UserPreferenceModel; drift detection & local reset
│   │
│   │   ── EXPLANATION LAYER ──
│   ├── explanation_service.py       # Ghép ExplanationFragment (Context + Dish + Constraint)
│   │
│   └── users_service.py             # CRUD user profile (đã có)
│
├── cache/                           # Cache layer
│   ├── __init__.py
│   └── weather_cache.py             # Geo-Cell logic: tọa độ → grid key, TTL adaptive (15/30/60 min)
│
├── api/                             # FastAPI routers
│   ├── __init__.py
│   ├── recommend.py                 # POST /recommend  → chạy full pipeline
│   ├── feedback.py                  # POST /feedback   → ghi UserFeedback + SessionState
│   └── users.py                     # GET/POST/PUT /users
│
└── utils/
    ├── helpers.py                   # (đã có)
    ├── normalization.py             # Min-Max norm cho WeatherVector [0,1]
    └── formula.py                   # BMR (Mifflin-St Jeor), TDEE, PhysiologicalDemand formulas

document/                            # Tài liệu thiết kế gốc
migration/                           # Alembic migrations
test/                                # Unit & integration tests
project_overview.txt                 # Đặc tả hệ thống đầy đủ
PROJECT_STRUCTURE.md                 # File này
```

---

## III. Các nhóm entity & module tương ứng

### 3.1 Input Entities → Vectors

| Entity | Module | Ghi chú |
|---|---|---|
| `WeatherInput` | `schemas/inputs.py` | Raw từ API thời tiết |
| `WeatherVector` | `schemas/vectors.py` | Sau Min-Max norm; 6 chiều [0,1] |
| `WeatherCache` | `models/weather_cache.py` + `cache/weather_cache.py` | Geo-cell Redis cache |
| `LocationInput` | `schemas/inputs.py` | lat, lon, city, country_code |
| `LocationVector` | `schemas/vectors.py` | climate_type, seasonality_factor, local_spice_index… |
| `PersonalInput` | `schemas/inputs.py` + `models/user.py` | Profile người dùng |
| `PersonalVector` | `schemas/vectors.py` | BMI, BMR, TDEE, disease_flags, taste_weight |

### 3.2 Core Entities

| Entity | Module | Ghi chú |
|---|---|---|
| `PhysiologicalDemand` | `schemas/demand.py` | Fusion WeatherVector ⊕ PersonalVector; 8 chiều |
| `Ingredient` | `models/ingredient.py` | warming_score, cooling_score, satiety_score, GI, sodium… |
| `Dish` | `models/dish.py` | dish_warming/cooling/satiety_score, taste_profile |
| `DishIngredient` | `models/dish.py` | Junction table; weight_in_dish = qty_i / Σqty |

### 3.3 Constraint & Result Entities

| Entity | Module | Ghi chú |
|---|---|---|
| `ConstraintProfile` | `schemas/constraints.py` | hard_constraints → loại; soft_constraints → trừ điểm |
| `RecommendationResult` | `models/recommendation.py` | Snapshot + ranked_dishes + explanation |
| `RankedDish` | `models/recommendation.py` | rank, final_score, score_breakdown, substitutions |

### 3.4 Feedback & Learning Entities (Lớp 3)

| Entity | Storage | Ghi chú |
|---|---|---|
| `UserFeedback` | PostgreSQL | action_type, rating, context_snapshot, time_to_action |
| `UserPreferenceModel` | PostgreSQL | learned_taste_weight (EMA), ingredient_affinity, confidence_score |
| `SessionState` | Redis (TTL) | delta_taste_weight tạm thời; hủy nếu rating < 4 |

### 3.5 Explanation Entity

| Entity | Module | Ghi chú |
|---|---|---|
| `ExplanationFragment` | `models/explanation.py` | fragment_type (context/dish/constraint), text_template, variant_index, language |

---

## IV. Processing Pipeline (15 bước + bước 1.5)

```
Bước 1   Thu thập Raw Input          → WeatherInput + LocationInput + PersonalInput
Bước 1.5 Weather Cache Lookup        → Geo-cell key → Redis hit/miss → WeatherVector (cached or fresh)
Bước 2   Chuẩn hóa WeatherVector     → Min-Max Norm → [0,1]
Bước 3   Xây dựng LocationVector     → climate_type, seasonality_factor, local_spice_index
Bước 4   Tính PersonalVector         → BMI, BMR, TDEE, disease_flags, taste_weight
Bước 5   Tổng hợp PhysiologicalDemand→ WeatherVector ⊕ PersonalVector (8 chiều)
Bước 6   Tạo ConstraintProfile       → hard + soft rules từ disease_flags, allergies, diet_type
Bước 7   Lọc Ingredient Pool         → hard constraints (allergen, vegan, sodium…)
Bước 8   Lọc Dish Pool               → chỉ dish có đủ ingredient hợp lệ
Bước 9   Tính DishVector             → DishVector[dim] = Σ(weight_i × Ingredient_i[dim])
Bước 10  Áp Soft Constraints         → ConstraintMultiplier ∈ {0, 0.5, 1} per dim
Bước 11  Chấm điểm Score(Dish)       → dot-product: Demand × DishVector × ConstraintMultiplier

         [Lớp 3 can thiệp điểm 1]   → Nếu confidence_score ≥ ngưỡng: dùng learned_taste_weight
                                        Ưu tiên: SessionDelta > LearnedWeight > OriginalWeight

Bước 12  Cộng Taste & Seasonality    → FinalScore = 0.75×Score + 0.15×taste_bonus + 0.10×seasonality_factor
Bước 13  Xếp hạng top-K             → argsort → top 10

         [Lớp 3 can thiệp điểm 2]   → Áp ingredient_affinity penalty/bonus lên FinalScore

Bước 14  Kiểm tra Fallback           → Nếu top-10 rỗng → nới lỏng soft constraints
Bước 15  Tạo RecommendationResult    → snapshots + explanation (ghép ExplanationFragment)
```

---

## V. Công thức cốt lõi

### PhysiologicalDemand
```
hydration_need        = 0.5×dehydration_risk + 0.3×heat_stress_index + 0.2×activity_mult
electrolyte_need      = 0.6×hydration_need + 0.4×activity_mult
thermoregulation_need = max(heat_stress_index, cold_stress_index)
energy_need           = TDEE × (1 - 0.1×heat_stress_index + 0.1×cold_stress_index)
warming_food_need     = 0.6×cold_stress_index + 0.4×(1 - heat_stress_index)
cooling_food_need     = 0.6×heat_stress_index + 0.4×(1 - cold_stress_index)
glycemic_control_need = diabetes_flag × 1.0
sodium_control_need   = hypertension_flag × 1.0
```

### DishVector
```
DishVector[dim]    = Σ_i (weight_i × Ingredient_i[dim]),  weight_i = qty_i / Σqty
dish_energy_total  = Σ_i (qty_i/100 × energy_density_i)
dish_glycemic_load = Σ_i (GI_i × carb_g_i / 100)
dish_sodium_total  = Σ_i (qty_i/100 × sodium_density_i)
```

### Scoring
```
Score(dish)  = Σ_dim (Demand[dim] × DishVector[dim] × ConstraintMultiplier[dim])
taste_bonus  = Σ_t (taste_weight_t × taste_profile_dish[t])
FinalScore   = 0.75×Score + 0.15×taste_bonus + 0.10×seasonality_factor
```

### Geo-Cell Cache Key
```
grid_lat = round(lat / cell_size) × cell_size   # cell_size = 0.1° (~11km)
grid_lon = round(lon / cell_size) × cell_size
cache_key = f"weather:{grid_lat}:{grid_lon}"
TTL: 30min (6h–22h) | 60min (22h–6h) | 15min (AQI cao / thời tiết cực đoan)
```

### EMA — UserPreferenceModel
```
new_weight = 0.8 × old_weight + 0.2 × signal_from_feedback
# Kích hoạt learned_weight khi confidence_score ≥ 20 rated interactions
```

---

## VI. ERD tóm tắt

```
PersonalInput   1:1  PersonalVector      (transformation)
WeatherInput    1:1  WeatherVector       (normalization)
LocationInput   1:1  LocationVector      (lookup + enrichment)

WeatherVector
+ LocationVector
+ PersonalVector  N:1  PhysiologicalDemand  (fusion, 1 per session)

PhysiologicalDemand  1:N  RecommendationResult
RecommendationResult 1:N  RankedDish
Dish                 M:N  Ingredient           (qua DishIngredient)
PersonalVector       1:1  ConstraintProfile
ConstraintProfile    1:N  ConstraintRule
UserFeedback         N:1  UserPreferenceModel
```

---

## VII. Dependency khởi tạo

```
config.py
  └─ models/*          (DB schema)
  └─ cache/weather_cache.py  (Redis)
       └─ services/weather_service.py
            └─ services/location_service.py
            └─ services/personal_service.py
                 └─ services/demand_service.py
                 └─ services/constraint_service.py
                      └─ services/filter_service.py
                           └─ services/scoring_service.py
                                └─ services/ranking_service.py  ← Lớp 3 injection
                                     └─ services/explanation_service.py
                                          └─ services/recommendation_service.py
                                               └─ api/recommend.py

[Background jobs]
services/feedback_service.py  →  services/learning_service.py  (EMA batch)
```

---

## VIII. Tech stack đề xuất

| Thành phần | Công nghệ |
|---|---|
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.x + Alembic |
| Database | PostgreSQL |
| Cache | Redis (WeatherCache + SessionState) |
| Validation | Pydantic v2 |
| Background jobs | Celery hoặc APScheduler |
| Weather API | OpenWeatherMap / WeatherAPI.com |
