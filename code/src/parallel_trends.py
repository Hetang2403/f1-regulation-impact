import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols


df = pd.read_parquet('data/processed/team_race_panel.parquet', engine='pyarrow')
df['year'] = df['year'].astype(int)

def plot_parallel_trends(df):
    pre_reg = df[df['year'] < 2022]
    pre_reg_agg = pre_reg.groupby(['year', 'treated'])['relative_perf'].mean().reset_index()
    treatment = pre_reg_agg[pre_reg_agg['treated'] == 1]
    control = pre_reg_agg[pre_reg_agg['treated'] == 0]

    # Create the plot
    plt.plot(treatment['year'], treatment['relative_perf'], label='Treatment', color='blue', marker='o')
    plt.plot(control['year'], control['relative_perf'], label='Control', color='red', marker='x')
    plt.xticks([2019, 2020, 2021])  # Ensure x-ticks are at the years in the data

    # Add titles and labels
    plt.title("Pre-Regulation Relative Performance: Treatment vs Control")
    plt.xlabel("years")
    plt.ylabel("Relative Performance")
    plt.legend()
    plt.grid()
    plt.savefig("../outputs/pre_reg_parallel_trends.png", dpi=300)
    plt.show()


def placebo_test(df, placebo_year):
    pre = df[df['year'] < 2022].copy()
    pre['placebo_post'] = (pre['year'] >= placebo_year).astype(int)
    model = ols('relative_perf ~ placebo_post * treated', data=pre).fit(cov_type='HC3')
    print(f"Placebo Test for Year {placebo_year}:\n{model.summary()}\n")


def main():
    plot_parallel_trends(df)
    placebo_test(df, 2020)
    placebo_test(df, 2021)

if __name__ == "__main__":
    main()