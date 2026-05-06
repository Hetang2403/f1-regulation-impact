SELECT
    relative_perf,
    team,
    year,
    treated,
    post
FROM {{ ref('stg_team_race_panel') }}