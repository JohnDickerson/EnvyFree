#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches   # For the proxy twin-axis legend entry

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

XFONT={'fontsize':24}
YFONT={'fontsize':24}
TITLEFONT={'fontsize':24}
TINYFONT={'fontsize':6}

n = range(2,11)
# 99%+ percentage of runs were feasible after m=?
unif_m = [5,8,9,10,12,14,16,18,19]
corr_m = [6,8,10,11,13,14,16,18,19]

fig = plt.figure()
ax = fig.add_subplot(111)

unif = ax.plot(n, unif_m, 'ks', label="Uniform", linewidth=2,)
corr = ax.plot(n, corr_m, 'ko', label="Correlated", linewidth=2,)

ax.set_ylabel("$m$", fontdict=XFONT)
ax.set_xlabel("$n$", fontdict=YFONT)
plt.legend(loc='upper left',)

plt.savefig("with_high_probability.pdf", format='pdf', bbox_inches='tight')
plt.clf()
