import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot as plt

df = pd.read_parquet('data/processed/team_race_panel_forecast.parquet')
def engineer_features(df):
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
df = engineer_features(df)

def walk_forward_validate(df):
    results = []
    df = pd.get_dummies(df, columns=['team'], drop_first=True)
    team_dummies = [col for col in df.columns if col.startswith('team_')]
    features = ['rolling_mean', 'yoy_change', 'season_std'] + team_dummies
    for year in range(2022, 2026):
        train = df[df['year'] < year].dropna().copy()
        test = df[df['year'] == year].dropna().copy()
        
        if train.empty or test.empty:
            continue
        
        model = Ridge(alpha=1.0)
        model.fit(train[features], train['relative_perf'])
        
        test['predicted'] = model.predict(test[features])
        mse = mean_squared_error(test['relative_perf'], test['predicted'])
        results.append({'year': year, 'mse': mse})
        print(f"Year {year} - MSE: {mse:.4f}")
    return pd.DataFrame(results)

def seasonal_naive_forecast(df):
    results = []
    season_mean = df.groupby(['year', 'team'])['relative_perf'].mean().reset_index()
    season_mean['naive_pred'] = season_mean.groupby('team')['relative_perf'].shift(1)
    for year in range(2022, 2026):
        test = df[df['year'] == year].copy()
        test = test.merge(season_mean[['year', 'team', 'naive_pred']], on=['year', 'team'])
        mse = mean_squared_error(test['relative_perf'], test['naive_pred'])
        results.append({'year': year, 'mse': mse})
        print(f"Seasonal Naive - Year {year} - MSE: {mse:.4f}")
    return pd.DataFrame(results)

def forecast_2026_ridge(df):
    teams = df[['year', 'team']].copy()
    df = pd.get_dummies(df, columns=['team'], drop_first=True)
    team_dummies = [col for col in df.columns if col.startswith('team_')]
    features = ['rolling_mean', 'yoy_change', 'season_std'] + team_dummies
    train = df[df['year'] < 2026].dropna().copy()
    model = Ridge(alpha=1.0)
    model.fit(train[features], train['relative_perf'])
    
    future = df[df['year'] == 2026].copy()
    future['team'] = teams[teams['year'] == 2026]['team'].values
    future['year'] = 2026
    future[features] = future[features].fillna(future[features].mean())
    future['predicted_2026'] = model.predict(future[features])
    summary = future.groupby('team')[['relative_perf', 'predicted_2026']].mean()
    print(summary)
    return future[['team', 'predicted_2026']]

def plot_model_comparison(ridge_results, naive_results):
    plt.plot(ridge_results['year'], ridge_results['mse'], label='Ridge MSE', marker='o')
    plt.plot(naive_results['year'], naive_results['mse'], label='Seasonal Naive MSE', marker='x')
    plt.title("Model Comparison: Ridge vs Seasonal Naive")
    plt.xticks(ridge_results['year'])  # Ensure x-ticks are at the years in the data
    plt.xlabel("Year")
    plt.ylabel("Mean Squared Error")
    plt.legend()
    plt.grid()
    plt.savefig("../outputs/model_comparison.png", dpi=300)
    plt.show()

def main():
    results = walk_forward_validate(df)
    results.to_csv("../outputs/forecast_results.csv", index=False)
    seasonal_results = seasonal_naive_forecast(df)
    seasonal_results.to_csv("../outputs/seasonal_naive_results.csv", index=False)
    forecast_2026 = forecast_2026_ridge(df)
    forecast_2026.to_csv("../outputs/forecast_2026.csv", index=False)
    plot_model_comparison(results, seasonal_results)
if __name__ == "__main__":
    main()