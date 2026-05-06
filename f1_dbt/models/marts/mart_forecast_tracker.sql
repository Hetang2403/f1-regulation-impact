SELECT
    relative_perf,
    team,
    year,
    round,
    race
FROM {{ ref('stg_team_race_panel_forecast') }}