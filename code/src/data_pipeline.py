import fastf1
import pandas as pd
from utils import BASE_URL, YEARS, CONTROL_TEAMS, TREATMENT_TEAMS, TEAM_NAME_MAP
from pathlib import Path

Path("data/raw/fastf1_cache").mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache("data/raw/fastf1_cache")

def fetch_season(year):
    schedule = fastf1.get_event_schedule(year)
    schedule = schedule[schedule["EventFormat"] != "testing"]
    
    results = []
    for _, event in schedule.iterrows():
        round_no = event["RoundNumber"]
        race_name = event["EventName"]
        
        try:
            session = fastf1.get_session(year, round_no, "R")
            session.load(telemetry=False, weather=False, messages=False)
            
            for _, row in session.results.iterrows():
                raw_team = row["TeamName"]
                team = TEAM_NAME_MAP.get(raw_team, raw_team)
                if team not in CONTROL_TEAMS and team not in TREATMENT_TEAMS:
                    continue
                results.append({
                    "year":     year,
                    "round":    round_no,
                    "race":     race_name,
                    "team":     team,
                    "driver":   row["Abbreviation"],
                    "points":   float(row["Points"]),
                    "position": int(row["Position"]),
                })
        except Exception as e:
            print(f"Skipping {year} round {round_no}: {e}")
            continue
    
    return results


def build_panel():
    all_data = []
    for year in YEARS:
        print(f"Loading {year}...")
        all_data.extend(fetch_season(year))
    
    df = pd.DataFrame(all_data)
    df.sort_values(by=["year", "round"], inplace=True)

    agg_df = df.groupby(["year", "round", "team"]).agg(
        avg_points=("points", "mean"),
        avg_position=("position", "mean"),
        race=("race", "first")
    ).reset_index()

    team_points = df.groupby(["year", "round", "team"])["points"].sum().reset_index(name="team_points")
    team_points["relative_perf"] = team_points["team_points"] / team_points.groupby(
        ["year", "round"])["team_points"].transform("max")

    agg_df = agg_df.merge(team_points[["year", "round", "team", "relative_perf"]], on=["year", "round", "team"])

    agg_df["post"]    = (agg_df["year"] >= 2022).astype(int)
    agg_df["treated"] = agg_df["team"].isin(TREATMENT_TEAMS).astype(int)
    agg_df["new_reg"] = (agg_df["year"] >= 2026).astype(int)
    
    return agg_df

def main():
    panel = build_panel()
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    panel.to_parquet("data/processed/team_race_panel_forecast.parquet", index=False)
    print(f"Saved {len(panel)} rows")

if __name__ == "__main__":
    main()