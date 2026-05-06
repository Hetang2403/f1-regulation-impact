SELECT
    YEAR as year,
    ROUND as round,
    TEAM as team,
    AVG_POINTS as avg_points,
    AVG_POSITION as avg_position,
    RACE as race,
    RELATIVE_PERF as relative_perf,
    POST as post,
    TREATED as treated
FROM {{ source('raw', 'TEAM_RACE_PANEL') }}

