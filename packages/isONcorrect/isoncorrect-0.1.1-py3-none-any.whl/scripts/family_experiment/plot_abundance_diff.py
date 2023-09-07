
import sys
import argparse
import os
import random
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except (ImportError, RuntimeError):
    print("COULD not import matplotlib")
# import matplotlib.pyplot as plt
# import matplotlib

import numpy as np
import seaborn as sns
import pandas as pd

sns.set(style="whitegrid")

data=sys.argv[1]
# f = open(data, "r")
indata = pd.read_csv(data)
# y=sys.argv[3]


# g = sns.lmplot(x="abundance", y="switch", col="Depth", # hue="day",
#                 data=indata, col_wrap=2, height=3)

g = sns.catplot(x="abundance", y="switch", col="Depth", col_wrap=3,
            data=indata, hue="type", hue_order= ["exact", "approx", "original"],
            kind="bar", aspect=1)

g.set(ylim=(-0.1,1.0))
# ax.set_ylabel("Abundance after correction")
# ax.set_xlabel("Abundance before correction")

g.set_ylabels("% Read switched transcript")
g.set_xlabels("Abundance before correction")

# ax = sns.boxplot(x="p", y=y, hue = "type", data=indata)
# ax.set_ylim(0,15)
# ax.set_ylabel("Error rate %")

plt.savefig(sys.argv[2])
plt.close()

