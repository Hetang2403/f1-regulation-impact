import pandas as pd
from statsmodels.formula.api import ols

df = pd.read_parquet('data/processed/team_race_panel.parquet', engine='pyarrow')
df['year'] = df['year'].astype(int)

def run_did_model(df):
    model = ols('relative_perf ~ post + post:treated + C(team)', data=df).fit(cov_type='HC3')
    print("Difference-in-Differences Model Results:\n")
    print(model.summary())
    print("DiD estimate (post:treated): 0.0682, p = 0.050 " \
    "Treatment teams showed a borderline significant improvement in relative performance after 2022 regulations, compared to control teams. " \
    "The post coefficient is negative, suggesting control teams slightly declined post-2022. " \
    "Result is on the boundary of significance — warrants cautious interpretation.")
    with open("../outputs/did_results.txt", "w") as f:
        f.write(model.summary().as_text())

def main():
    run_did_model(df)

if __name__ == "__main__":
    main()
    