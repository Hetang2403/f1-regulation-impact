import pandas as pd
from sklearn.linear_model import Ridge
from matplotlib import pyplot as plt

df = pd.read_parquet('data/processed/team_race_panel_forecast.parquet')

def engineer_features(df, race_name):
    circuit = df[df['race'] == race_name].groupby('team')['relative_perf'].mean().reset_index()
    circuit.rename(columns={'relative_perf': 'circuit_perf'}, inplace=True)
    df = df.merge(circuit, on='team', how='left')

    df['rolling_mean'] = df.groupby('team')['relative_perf'].transform(
        lambda x: x.shift(1).rolling(5).mean()
    )
    season_mean = df.groupby(['year', 'team'])['relative_perf'].mean().reset_index()
    season_mean.rename(columns={'relative_perf': 'season_mean'}, inplace=True)
    season_mean['yoy_change'] = season_mean.groupby('team')['season_mean'].diff()
    df = df.merge(season_mean[['year', 'team', 'yoy_change']], on=['year', 'team'])

    season_std = df.groupby(['year', 'team'])['relative_perf'].std().reset_index()
    season_std.rename(columns={'relative_perf': 'season_std'}, inplace=True)
    df = df.merge(season_std[['year', 'team', 'season_std']], on=['year', 'team'])
    return df

def forecast_circuit(df, race_name):
    df = engineer_features(df, race_name)
    train = df[df['year'] < 2026].copy()
    test = df[df['year'] == 2026].groupby('team').last().reset_index().copy()
    test_teams = test['team'].values

    train = pd.get_dummies(train, columns=['team'], drop_first=True)
    test = pd.get_dummies(test, columns=['team'], drop_first=True)
    test = test.reindex(columns=train.columns, fill_value=0)
    test['team'] = test_teams

    team_dummies = [col for col in train.columns if col.startswith('team_')]
    features = ['circuit_perf', 'rolling_mean', 'yoy_change', 'season_std'] + team_dummies

    train = train.dropna(subset=features).copy()
    test = test.dropna(subset=['circuit_perf']).copy()
    test[features] = test[features].fillna(test[features].mean())

    model = Ridge(alpha=1.0)
    model.fit(train[features], train['relative_perf'])

    test['predicted'] = model.predict(test[features])
    test['estimated_position'] = test['predicted'].rank(ascending=False).astype(int)
    print(f"\n--- {race_name} 2026 Forecast ---")
    print(test[['team', 'predicted', 'estimated_position']].sort_values('estimated_position'))

    output_name = race_name.replace(' ', '_').lower()
    result = test[['team', 'predicted', 'estimated_position']].sort_values('estimated_position')
    result.to_csv(f"../outputs/{output_name}_forecast.csv", index=False)
    return result

def main():
    raw_df = pd.read_parquet('data/processed/team_race_panel_forecast.parquet')
    forecast_circuit(raw_df, 'Canadian Grand Prix')
    forecast_circuit(raw_df, 'Monaco Grand Prix')
if __name__ == "__main__":
    main()