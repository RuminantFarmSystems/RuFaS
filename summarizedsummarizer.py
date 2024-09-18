import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

fileprefix = "test-18"
directory = "E:\\Backup\\RUFAS_SA\\output\\reports\\"
report_prefix = "report_"

filename = "C:\\Users\\joecw\\OneDrive - Cornell University\\RuFaS\\Sensitivity Analyses\\test 18 runs summarized.xlsx"
filename = "C:\\Users\\joecw\\OneDrive - Cornell University\\RuFaS\\Sensitivity Analyses\\test 19 runs summarized.xlsx"

summarized = pd.read_excel(filename)
colnames = list(summarized.columns)

howmansims = 128
howmanydidntrun = 7  # exclude the longest
howmanydidntrun = 0

newarray = []
y = summarized[colnames[1]][0:howmansims - howmanydidntrun]
y = list(y)
newarray.append(list(y))
for columname in colnames:
    print(columname)
    if columname not in colnames[0:4]:
        x = summarized[columname][0:howmansims - howmanydidntrun]
        x = list(x)

        fig = plt.figure()
        plt.scatter(x, y)
        # plt.xscale('log')
        # plt.yscale('log')
        m, b = np.polyfit(x, y, deg=1)
        plt.axline(xy1=(0, b), slope=m, label=f'$y = {m:.1f}x {b:+.1f}$')
        plt.ylabel(colnames[1])
        plt.xlabel(columname)
        # plt.show(block=False)
        fig.savefig(f'pngs/scatter {columname}.png')
        newarray.append(list(y))

        xy = pd.DataFrame([x, y]).T
        xy.columns = ['x', 'y']
        yhigh = xy['y'][xy['x'] > np.mean(xy['x'])]
        ylow = xy['y'][xy['x'] < np.mean(xy['x'])]

        fig = plt.figure()
        _, bins, _ = plt.hist(yhigh, bins=75)
        _ = plt.hist(ylow, bins=bins, alpha=0.5)
        plt.xlabel(colnames[1])
        plt.ylabel(columname)
        # plt.show()
        fig.savefig(f'pngs/hist {columname}.png')

x = summarized[colnames[1]][0:howmansims - howmanydidntrun]
plt.figure()
plt.hist(x)
plt.show(block=False)


df = pd.DataFrame(newarray)
df = df.T
df_norm_col=(df-df.mean())/df.std()

plt.figure()
ax = sns.heatmap(df_norm_col, linewidth=0.5)
plt.show(block=False)



c = ax.pcolormesh(x, y, z, cmap='RdBu', vmin=z_min, vmax=z_max) 