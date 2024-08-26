import random
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import seaborn as sns

from RUFAS.input_manager import InputManager

result = pd.DataFrame()
res_summary = pd.DataFrame(columns=["year_month", "average", "std"])

im = InputManager()
net_merit_csv = Path("NetMerit_percentile_HO.csv")
net_merit = im._load_data_from_csv(net_merit_csv)
population_graph_path = "population_graph/"

for date in net_merit.keys():
    if date == "percentile":
        continue
    rand = [random.randint(0, 100) for _ in range(1000000)]
    rand_nm = [net_merit[date][100 - rand_percentile] for rand_percentile in rand]

    mean = np.mean(rand_nm)
    std = np.std(rand_nm)

    result.insert(len(result.columns), date, rand_nm)
    res_summary.loc[len(res_summary.index)] = [date, mean, std]

    fig, axes = plt.subplots(3, 1, sharex=True)
    fig.set_figheight(8)
    fig.set_figwidth(12)

    sns.histplot(rand_nm, ax=axes[0], bins=101, kde=True)
    axes[0].set_title("Population Distribution")
    xmin, xmax = min(rand_nm), max(rand_nm)
    x = np.linspace(xmin, xmax, 101)
    p = scipy.stats.norm.pdf(x, mean, std)
    scaled_p = [val * 25000000 for val in p]
    axes[0].plot(x, scaled_p, 'r')

    axes[1].hist(net_merit[date], bins=101)
    axes[1].set_title("Percentile Distribution")

    axes[2].plot(x, p, 'r')
    axes[2].set_title("PDF")
    plt.savefig(population_graph_path + date+'.png')
    plt.close()

    print(date)

result.to_csv("rand_nm_population.csv", index=False)
res_summary.to_csv("rand_nm_summary.csv", index=False)
