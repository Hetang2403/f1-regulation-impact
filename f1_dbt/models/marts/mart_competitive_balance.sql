SELECT
    relative_perf,
    team,
    year
FROM {{ ref('stg_team_race_panel') }}