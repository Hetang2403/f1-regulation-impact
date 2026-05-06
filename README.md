# F1 Regulation Impact Analyzer

A three-layer data science project that uses Formula 1 regulation cycles as natural experiments to measure causal impact, forecast competitive outcomes, and deliver insights through a modern cloud analytics stack.

Built to demonstrate causal inference methodology, walk-forward forecasting, and production-grade data infrastructure (Snowflake + dbt + Power BI).

---

## Project Summary

The 2022 F1 regulation overhaul was one of the most significant rule changes in the sport's history, designed to reduce the dominance of top-tier teams and rebalance competition. This project treats that rule change as a natural experiment and asks: did it actually work?

Layer 1 answers the causal question using Difference-in-Differences inference. Layer 2 builds a walk-forward forecasting model to predict how teams adapt under the incoming 2026 regulation reset. Layer 3 delivers everything through a Snowflake + dbt pipeline connected to a Power BI dashboard.

---

## Repository Structure

```
f1-regulation-impact/
├── data/
│   ├── raw/
│   │   └── fastf1_cache/           # FastF1 local cache (gitignored)
│   └── processed/
│       ├── team_race_panel.parquet        # Layer 1 — 1024 rows, 2019-2024, 8 teams
│       └── team_race_panel_forecast.parquet  # Layer 2 — 1376 rows, 2019-2026, 9 teams
├── src/
│   ├── utils.py                # Constants, team name maps, circuit name map
│   ├── data_pipeline.py        # FastF1 + Jolpica API, builds Layer 1 parquet
│   ├── parallel_trends.py      # Parallel trends visual + placebo tests
│   ├── did_model.py            # DiD with team fixed effects, HC3 robust SEs
│   ├── forecast_model.py       # Walk-forward Ridge, naive baseline, 2026 forecast
│   └── circuit_forecast.py     # Generic circuit-level GP forecast
├── f1_dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_team_race_panel.sql
│   │   │   ├── stg_team_race_panel_forecast.sql
│   │   │   └── sources.yml
│   │   └── marts/
│   │       ├── mart_competitive_balance.sql
│   │       ├── mart_did_effects.sql
│   │       └── mart_forecast_tracker.sql
│   └── dbt_project.yml
├── outputs/
│   └── figures/
├── F1_Regulation_Impact.pbix   # Power BI dashboard
├── requirements.txt
└── README.md
```

---

## Data Sources

- **FastF1** for race results, timing data, and lap-level telemetry
- **Jolpica/Ergast API** for historical constructor standings and race metadata
- Coverage spans 2019 to 2026 (2026 is a partial season with forecasts generated for remaining races)

---

## Layer 1 - Causal Inference (Difference-in-Differences)

### Research Question
Did the 2022 regulation overhaul causally reduce the competitive advantage of historically dominant teams?

### Design

**Treatment group:** Mercedes, Red Bull, Ferrari. These teams had entrenched aerodynamic advantages under pre-2022 regulations.

**Control group:** Alpine, Williams, Haas, AlphaTauri, Aston Martin. Midfield teams with less to lose from a regulation reset.

Note on McLaren: McLaren was excluded from the Layer 1 control group due to a major corporate restructuring during the pre-period (2019 to 2021) that confounds their performance trajectory. They are included in Layer 2.

**Pre-period:** 2019 to 2021
**Post-period:** 2022 to 2024
**Treatment year:** 2022

**Outcome variable:** `relative_perf` is team points per race normalized by the race maximum, producing a 0 to 1 scale. This controls for the varying number of points available across race weekends and is more stable than raw points.

Note on 2025: Excluded from Layer 1 analysis. Teams were deliberately managing resources and redirecting development toward 2026 regulations, making 2025 performance unrepresentative of the 2022 regulatory equilibrium.

### Parallel Trends Assumption

A parallel trends check was conducted visually and via placebo tests before running the DiD model. The 2019 placebo passed. The 2020 placebo failed, identified as a COVID season anomaly due to the compressed calendar and unusual race conditions. This is acknowledged as a limitation. The 2020 season is retained in the panel but flagged.

### Results

| Parameter | Estimate | p-value |
|---|---|---|
| post:treated (DiD coefficient) | +0.0682 | 0.050 |

The DiD coefficient is borderline significant at p = 0.050. The 2022 regulations produced a statistically marginal but directionally consistent convergence effect. Top-tier teams saw a modest relative performance reduction compared to the control group after the regulation change. The effect is real but not large, which is consistent with Red Bull quickly re-establishing dominance by 2023.

### Model Specification

- OLS with team fixed effects to absorb time-invariant team quality differences
- HC3 heteroskedasticity-consistent robust standard errors
- Outcome variable: `relative_perf`
- Key regressor: `post x treated` interaction term

---

## Layer 2 - Walk-Forward Forecasting

### Objective
Forecast team performance under the 2026 regulation reset and validate predictions against live race results as the season progresses.

### Feature Engineering

Three features derived from `relative_perf` to capture form, trajectory, and stability:

| Feature | Definition | Rationale |
|---|---|---|
| rolling_mean | Rolling mean of relative_perf (closed='left') | Recent form and current momentum |
| yoy_change | Year-over-year change in seasonal mean | Development trajectory |
| season_std | Within-season standard deviation | Consistency under pressure |

Data leakage prevention: All rolling features use closed='left', meaning the current row is excluded from its own rolling window. This ensures no future information leaks into the training data.

Additional features include `treated`, `post`, `new_reg` (1 if year >= 2026 to signal the 2026 regulation era), and team label encoding.

### Model

Ridge regression was chosen over tree models. With a small panel dataset (1024 rows, 8 teams, 6 years), regularization helps and interpretability is valuable. XGBoost is used in another project in this portfolio (F1 Pit Stop Predictor). Using Ridge here shows that I pick the right tool for the problem rather than defaulting to the same model every time.

### Walk-Forward Validation Results

| Validation Year | Ridge MSE | Naive Baseline MSE | Improvement |
|---|---|---|---|
| 2022 | 0.0507 | 0.0507 | Tie (regulation reset) |
| 2023 | 0.0506 | 0.0550 | Ridge wins |
| 2024 | 0.0484 | 0.0830 | Ridge wins (~40%) |
| 2025 | 0.0607 | 0.0640 | Ridge wins |

The tie at 2022 is expected and honest. No model can predict a regulation reset before it happens. The progressive improvement in later years shows the model learning regulation-response patterns as post-2022 data accumulates. The roughly 40% improvement over naive in 2024 is the headline result.

### 2026 Forecasts

**Canada GP 2026 predicted finishing order:**

| Position | Team |
|---|---|
| 1st | Mercedes |
| 2nd | Ferrari |
| 3rd | Red Bull |
| 4th | McLaren |

Forecasts for other circuits can be generated using `circuit_forecast.py` with any race name as input.

---

## Layer 3 - Data Infrastructure and Dashboard

### Snowflake + dbt Architecture

```
Raw Parquets (local)
       |
Snowflake RAW schema (loaded via Python connector)
       |
dbt STAGING models (views - clean, lowercase, typed)
       |
dbt MARTS models (tables - Power BI connects here)
```

**Snowflake setup:**
- Warehouse: F1_WH (X-SMALL, auto-suspend 60 seconds)
- Database: F1_DB
- Schemas: RAW, RAW_STAGING, RAW_MARTS

**dbt staging models** clean and standardize one raw table each:
- `stg_team_race_panel`
- `stg_team_race_panel_forecast`

**dbt mart models** contain the business logic that Power BI reads:
- `mart_competitive_balance` for team relative_perf trends 2019 to 2024
- `mart_did_effects` for treatment vs control group performance with readable group labels
- `mart_forecast_tracker` for the full 2019 to 2026 arc including forecasts

### Power BI Dashboard

Three views connected live to Snowflake mart tables:

1. **Competitive Balance 2019-2024** - line chart of average relative_perf by team with a vertical reference line at 2022
2. **Treatment vs Control Group Performance** - clustered bar chart comparing the two groups across all teams
3. **2026 Forecast Tracker** - full timeline with reference lines at 2022 (regulation change) and 2025 (forecast start)

---

## Business Relevance

This project uses F1 data but the analytical framework applies to real business problems involving policy shocks and competitive rebalancing. These situations come up regularly in Canadian financial services, telecommunications, and retail.

The DiD framework is the same approach analysts use to measure the causal impact of a regulatory change, a competitor entering the market, or a pricing intervention. The challenge of separating the true effect from pre-existing trends comes up in policy analysis, marketing mix modeling, and large-scale A/B testing.

The walk-forward forecasting layer demonstrates how to build an adaptive performance model that updates as new data arrives. This is the same pattern used in demand forecasting, churn prediction, and sales pipeline modeling.

**How the F1 concepts map to business:**

| F1 Context | Business Equivalent |
|---|---|
| 2022 regulation overhaul | New regulation, competitor market entry, or pricing policy change |
| Treatment vs control teams | Affected vs unaffected business units or market segments |
| relative_perf convergence | Market share rebalancing after a competitive shock |
| Walk-forward validation | Rolling forecast with live actuals vs predicted tracking |
| 2026 forecast | Forward-looking scenario model for strategic planning |

---

## Limitations

- The 2020 placebo test failed due to the COVID season, which violates the parallel trends assumption for that year. The season is retained with a caveat.
- The 2026 validation set is small since the season is still early. Forecast accuracy will improve as more races complete.
- Constructor budgets are not publicly available. Team financial position is a known confounder that the model cannot capture.
- The DiD coefficient at p = 0.050 is not a strong causal claim. The direction is consistent but the magnitude is modest.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data collection | FastF1, Jolpica/Ergast API |
| Data processing | Python, pandas, NumPy |
| Causal inference | statsmodels (OLS, HC3 robust SEs) |
| Forecasting | scikit-learn (Ridge regression) |
| Data warehouse | Snowflake |
| Transformations | dbt |
| BI and visualization | Power BI, matplotlib |
| Infrastructure | snowflake-connector-python, python-dotenv |
| Version control | Git, GitHub |

---

## Reproducing the Analysis

```bash
# Install dependencies
pip install -r requirements.txt

# Build raw panel (Layer 1)
python src/data_pipeline.py

# Run parallel trends check
python src/parallel_trends.py

# Run DiD model
python src/did_model.py

# Run forecasting (Layer 2)
python src/forecast_model.py

# Run circuit forecast
python src/circuit_forecast.py

# Load to Snowflake (requires .env with credentials)
python src/load_to_snowflake.py

# Run dbt transformations
cd f1_dbt
dbt run
```

---

## Author

**Hetang Patel**
CS Graduate, Dalhousie University (Dec 2025)
[GitHub](https://github.com/hetang2403)
[Portfolio](https://hetangpatel.com)
